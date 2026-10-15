"""options.py: expiry choice, ATM IV, implied move, OI ratio, max pain, degradation (no network)."""
import copy
import datetime as dt
import math
import tempfile
import unittest

import common
import options
from tests import fx

FIX = fx.load("option_chain.json")
TODAY = dt.date(2026, 10, 14)


def ctx():
    return common.Ctx(tempfile.mkdtemp(), None, now=lambda: dt.datetime(2026, 10, 14, 15, tzinfo=dt.timezone.utc))


class ExpiryTests(unittest.TestCase):
    def test_first_monthly_at_least_20_days_out(self):
        # 2026-11-06 and 2026-11-13 are weeklies; 2026-11-20 is the third Friday
        self.assertEqual(options.choose_expiry(FIX["expiries"], TODAY), "2026-11-20")

    def test_third_friday_rule(self):
        self.assertTrue(options.is_monthly(dt.date(2026, 11, 20)))
        self.assertFalse(options.is_monthly(dt.date(2026, 11, 27)))   # fourth Friday
        self.assertFalse(options.is_monthly(dt.date(2026, 11, 19)))   # Thursday

    def test_without_a_monthly_takes_first_far_expiry(self):
        self.assertEqual(options.choose_expiry(["2026-10-16", "2026-11-06", "2026-11-13"], TODAY), "2026-11-06")

    def test_nothing_far_enough_takes_the_farthest(self):
        self.assertEqual(options.choose_expiry(["2026-10-16", "2026-10-23", "2026-10-30"], TODAY), "2026-10-30")
        self.assertIsNone(options.choose_expiry([], TODAY))


class ComputeTests(unittest.TestCase):
    def setUp(self):
        self.chain = copy.deepcopy(FIX["chain"])
        self.o = options.compute(self.chain, 101.0, TODAY)

    def test_atm_iv_is_mean_of_nearest_call_and_put(self):
        self.assertAlmostEqual(self.o["atm_iv"], 0.32)        # strike 100: call .30, put .34

    def test_implied_move(self):
        pct = 0.32 * math.sqrt(37 / 365)
        self.assertEqual(self.o["days_to_expiry"], 37)
        self.assertAlmostEqual(self.o["implied_move_pct"], pct, 5)
        self.assertAlmostEqual(self.o["implied_move_abs"], 101 * pct, 3)

    def test_open_interest_and_max_pain(self):
        self.assertEqual((self.o["put_oi"], self.o["call_oi"], self.o["put_call_oi_ratio"]), (600, 400, 1.5))
        # total intrinsic value: K=95 -> 2000, K=100 -> 1000, K=105 -> 2000
        self.assertEqual(self.o["max_pain"], 100.0)
        self.assertEqual(options.max_pain(self.chain["calls"], self.chain["puts"]), 100.0)

    def test_earnings_and_no_reason(self):
        self.assertEqual(self.o["next_earnings_date"], "2026-11-02")
        self.assertIsNone(self.o["reason"])
        self.assertEqual(self.o["expiry_used"], "2026-11-20")

    def test_unquoted_iv_nulls_the_move_but_keeps_open_interest(self):
        for side in ("calls", "puts"):
            for r in self.chain[side]:
                r["iv"] = 1e-5       # yfinance reports ~0 when the market is closed
        o = options.compute(self.chain, 101.0, TODAY)
        self.assertIsNone(o["atm_iv"])
        self.assertIsNone(o["implied_move_pct"])
        self.assertIn("implied-volatility", o["reason"])
        self.assertEqual(o["put_oi"], 600)

    def test_one_sided_iv_is_used(self):
        for r in self.chain["puts"]:
            r["iv"] = None
        self.assertAlmostEqual(options.compute(self.chain, 101.0, TODAY)["atm_iv"], 0.30)

    def test_chain_error_is_null_with_reason_and_keeps_earnings(self):
        o = options.compute({"expiry": None, "error": "option chain unavailable: 404", "earnings": "2026-11-02",
                             "calls": [], "puts": []}, 101.0, TODAY)
        self.assertEqual(o["reason"], "option chain unavailable: 404")
        self.assertIsNone(o["atm_iv"])
        self.assertEqual(o["next_earnings_date"], "2026-11-02")

    def test_no_spot_is_reported(self):
        o = options.compute(self.chain, None, TODAY)
        self.assertIsNone(o["implied_move_pct"])
        self.assertIn("no spot", o["reason"])


class BuildTests(unittest.TestCase):
    def test_build_adds_pinned_secondary_source(self):
        out = options.build(ctx(), "aapl", 101.0, loader=lambda t, today, spot: dict(FIX["chain"], version="1.7.0"))
        self.assertEqual(out["options"]["src"], "S9")
        self.assertEqual(out["sources"]["S9"]["class"], "secondary")
        self.assertIn("1.7.0", out["sources"]["S9"]["what"])
        self.assertEqual(out["options"]["as_of"], "2026-10-14")

    def test_loader_failure_degrades_without_source(self):
        def boom(t, today, spot):
            raise common.FetchError("yfinance is not installed")
        out = options.build(ctx(), "AAPL", 101.0, loader=boom)
        self.assertIsNone(out["options"]["src"])
        self.assertEqual(out["sources"], {})
        self.assertIn("not installed", out["options"]["reason"])
        self.assertIsNone(out["options"]["atm_iv"])


class ContractTests(unittest.TestCase):
    ZONES = {"buy_below": 94.0, "sell_above": 110.0}

    def chain_loader(self, ticker, expiry):
        ch = copy.deepcopy(FIX["chain"])
        return {"calls": ch["calls"], "puts": ch["puts"]}

    def build(self, zones=None, horizon=None, loader=None, chain_loader=None):
        loader = loader or (lambda t, today, spot: dict(FIX["chain"], version="1.7.0"))
        return options.build(ctx(), "AAPL", 101.0, loader=loader, zones=zones, horizon_days=horizon,
                             chain_loader=chain_loader or self.chain_loader)["options"]

    def pick(self, contracts, anchor, kind, expiry="2026-11-20"):
        return next(c for c in contracts if (c["anchor"], c["type"], c["expiry"]) == (anchor, kind, expiry))

    def test_nearest_listed_strike_at_each_anchor_for_both_legs(self):
        cs = self.build(self.ZONES)["contracts"]
        self.assertEqual(len(cs), 10)       # five anchors x call and put, one expiry
        # listed strikes 95/100/105: price 101 -> 100; buy 94 -> 95; sell 110 -> 105; 90.9 -> 95; 111.1 -> 105
        want = {"price": 100.0, "buy_zone": 95.0, "sell_zone": 105.0, "down_10": 95.0, "up_10": 105.0}
        for anchor, strike in want.items():
            for kind in ("call", "put"):
                c = self.pick(cs, anchor, kind)
                self.assertEqual(c["strike"], strike, (anchor, kind))
                self.assertEqual((c["expiry"], c["days"]), ("2026-11-20", 37))
        self.assertAlmostEqual(self.pick(cs, "down_10", "put")["anchor_price"], 90.9)
        self.assertEqual([c["anchor"] for c in cs[:2]], ["price", "price"])

    def test_derived_numbers_for_one_call_and_one_put(self):
        cs = self.build(self.ZONES)["contracts"]
        call = self.pick(cs, "price", "call")        # strike 100, bid 4.9 ask 5.1 -> mid 5.0
        self.assertEqual((call["bid"], call["ask"], call["mid"], call["last"], call["oi"], call["iv"]),
                         (4.9, 5.1, 5.0, 5.0, 200, 0.30))
        self.assertAlmostEqual(call["premium_pct"], 5.0 / 101, 6)
        self.assertAlmostEqual(call["annualized_pct"], 5.0 / 101 * 365 / 37, 5)
        self.assertEqual(call["breakeven"], 105.0)
        self.assertIsNone(call["protection_cost_pct"])
        self.assertIsNone(call["reason"])
        put = self.pick(cs, "price", "put")          # strike 100, bid 3.0 ask 3.2 -> mid 3.1
        self.assertEqual(put["mid"], 3.1)
        self.assertEqual(put["breakeven"], 96.9)
        self.assertAlmostEqual(put["protection_cost_pct"], 3.1 / 101, 6)
        self.assertAlmostEqual(put["premium_pct"], put["protection_cost_pct"], 9)
        self.assertEqual(put["oi"], 200)

    def test_missing_scorecard_drops_only_the_zone_anchors(self):
        o = self.build(zones=None)
        self.assertEqual(sorted({c["anchor"] for c in o["contracts"]}), ["down_10", "price", "up_10"])
        self.assertEqual(len(o["contracts"]), 6)
        self.assertEqual(self.build(zones={"buy_below": 94.0})["contracts"][2]["anchor"], "buy_zone")
        # everything else in `options` is unchanged
        self.assertEqual((o["expiry_used"], o["max_pain"], o["put_call_oi_ratio"], o["src"]),
                         ("2026-11-20", 100.0, 1.5, "S9"))

    def test_horizon_adds_a_second_monthly_expiry(self):
        o = self.build(self.ZONES, horizon=60)
        self.assertEqual(sorted({c["expiry"] for c in o["contracts"]}), ["2026-11-20", "2026-12-18"])
        self.assertEqual(self.pick(o["contracts"], "price", "call", "2026-12-18")["days"], 65)
        self.assertEqual(len(o["contracts"]), 20)
        same = self.build(self.ZONES, horizon=31)       # first monthly >= 31 days is the same expiry: no duplicate
        self.assertEqual(len(same["contracts"]), 10)

    def test_missing_leg_is_null_with_reason(self):
        ch = copy.deepcopy(FIX["chain"])
        ch["puts"] = [r for r in ch["puts"] if r["strike"] != 100.0]
        o = self.build(self.ZONES, loader=lambda t, today, spot: dict(ch, version="1.7.0", expiries=FIX["expiries"]))
        put = self.pick(o["contracts"], "price", "put")
        self.assertEqual(put["strike"], 100.0)
        self.assertIsNone(put["mid"])
        self.assertIsNone(put["breakeven"])
        self.assertIn("no put listed at strike 100.0", put["reason"])
        self.assertIsNone(self.pick(o["contracts"], "price", "call")["reason"])

    def test_no_quote_gives_null_premium_with_reason(self):
        ch = copy.deepcopy(FIX["chain"])
        for r in ch["calls"]:
            r["bid"], r["ask"] = 0.0, 0.0
        o = self.build(self.ZONES, loader=lambda t, today, spot: dict(ch, version="1.7.0", expiries=FIX["expiries"]))
        call = self.pick(o["contracts"], "price", "call")
        self.assertIsNone(call["premium_pct"])
        self.assertIn("no bid/ask", call["reason"])
        self.assertEqual(call["oi"], 200)

    def test_extra_chain_failure_nulls_only_that_expiry(self):
        def boom(ticker, expiry):
            raise common.FetchError("HTTP 404")
        o = self.build(self.ZONES, horizon=60, chain_loader=boom)
        by = {c["expiry"]: c for c in o["contracts"] if c["anchor"] == "price" and c["type"] == "call"}
        self.assertIsNone(by["2026-11-20"]["reason"])                  # chosen chain reused, no extra fetch
        self.assertIn("HTTP 404", by["2026-12-18"]["reason"])
        self.assertIsNone(by["2026-12-18"]["strike"])

    def test_no_chain_gives_empty_contracts(self):
        o = options.build(ctx(), "AAPL", 101.0, loader=lambda t, today, spot: {"error": "down"})["options"]
        self.assertEqual(o["contracts"], [])
        self.assertEqual(o["reason"], "down")


if __name__ == "__main__":
    unittest.main()
