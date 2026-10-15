"""market.py: SIC -> ETF table, returns, Bank of Canada parse, saved series, degradation (no network)."""
import datetime as dt
import json
import os
import tempfile
import unittest
from unittest import mock

import common
import market
from tests import fx


def rows(n, start=100.0):
    d0 = dt.date(2025, 1, 1)
    return [{"date": (d0 + dt.timedelta(days=i)).isoformat(), "close": start + i, "adj_close": start + i,
             "high": start + i, "low": start + i, "dividends": 0.0, "splits": 0.0} for i in range(n)]


def loader(n=300):
    return lambda ticker, years: {"version": "1.7.0", "rows": rows(n), "info": {}}


def ctx():
    return common.Ctx(tempfile.mkdtemp(), None, now=lambda: dt.datetime(2026, 10, 14, 15, tzinfo=dt.timezone.utc))


class SectorTests(unittest.TestCase):
    def test_table(self):
        cases = {3571: "XLK", 3576: "XLK", 3674: "XLK", 7372: "XLK", 2834: "XLV", 2080: "XLP", 3711: "XLY",
                 3714: "XLY", 3711.0: "XLY", 3523: "XLI", 2000: "XLP", 2100: "XLI", 3999: "XLI", 2911: "XLE",
                 1311: "XLE", 4911: "XLU", 4813: "XLC", 6798: "XLRE", 6021: "XLF", 6799: "XLF", 5731: "XLY",
                 1040: "XLB", 1500: "SPY", 8000: "SPY", 7000: "SPY"}
        for sic, etf in cases.items():
            self.assertEqual(market.sector_etf(int(sic)), etf, sic)

    def test_string_and_garbage_sic(self):
        self.assertEqual(market.sector_etf("3571"), "XLK")
        self.assertEqual(market.sector_etf(""), "SPY")
        self.assertEqual(market.sector_etf(None), "SPY")


class SummarizeTests(unittest.TestCase):
    def test_returns_and_above_200d(self):
        s = {"dates": [r["date"] for r in rows(300)], "close": [r["close"] for r in rows(300)]}
        m = market.summarize(s, (("return_24m", 504),))
        self.assertAlmostEqual(m["return_1m"], 399 / 378 - 1, 6)
        self.assertAlmostEqual(m["return_12m"], 399 / 147 - 1, 6)
        self.assertIsNone(m["return_24m"])      # 300 closes < 505
        self.assertTrue(m["above_200d"])

    def test_below_200d(self):
        closes = [200.0] * 250 + [150.0]
        m = market.summarize({"dates": [str(i) for i in range(251)], "close": closes})
        self.assertFalse(m["above_200d"])


class BocTests(unittest.TestCase):
    def test_parse_live_fixture(self):
        rate, date = market.parse_boc(fx.load("boc_fxusdcad.json"))
        self.assertEqual(date, fx.load("boc_fxusdcad.json")["observations"][0]["d"])
        self.assertGreater(rate, 1.0)
        self.assertLess(rate, 2.0)

    def test_picks_newest_valued_observation(self):
        obj = {"observations": [{"d": "2026-10-12", "FXUSDCAD": {"v": "1.40"}}, {"d": "2026-10-13", "FXUSDCAD": {}},
                                {"d": "2026-10-09", "FXUSDCAD": {"v": "1.39"}}]}
        self.assertEqual(market.parse_boc(obj), (1.40, "2026-10-12"))

    def test_empty_raises(self):
        with self.assertRaises(common.FetchError):
            market.parse_boc({"observations": []})


class BuildTests(unittest.TestCase):
    def build(self, c, mdir, boc=None, ld=None):
        boc = boc if boc is not None else fx.load("boc_fxusdcad.json")
        with mock.patch.object(c, "get_json", return_value=(boc, "2026-10-14T15:00:00Z")):
            return market.build(c, 3571, mdir, loader=ld or loader())

    def test_build_blocks_sources_and_saved_series(self):
        mdir = os.path.join(tempfile.mkdtemp(), "market")
        out = self.build(ctx(), mdir)
        self.assertEqual(out["sector_etf"], "XLK")
        m = out["market"]
        self.assertEqual((m["spy"]["src"], m["sector"]["src"], m["fx_usdcad"]["src"]), ("S7", "S7", "S8"))
        self.assertEqual(m["sector"]["etf"], "XLK")
        self.assertTrue(m["spy"]["above_200d"])
        self.assertEqual(m["missing"], [])
        self.assertEqual(set(out["sources"]), {"S7", "S8"})
        self.assertEqual((out["sources"]["S7"]["class"], out["sources"]["S8"]["class"]), ("secondary", "primary"))
        self.assertIn("bankofcanada.ca/valet", out["sources"]["S8"]["url"])
        self.assertEqual(sorted(os.listdir(mdir)), ["SPY.json", "XLK.json"])
        with open(os.path.join(mdir, "XLK.json")) as f:
            s = json.load(f)
        self.assertEqual((s["ticker"], s["src"], len(s["dates"]), len(s["close"])), ("XLK", "S7", 300, 300))

    def test_spy_sector_share_one_download(self):
        calls = []

        def ld(ticker, years):
            calls.append(ticker)
            return {"version": "1.7.0", "rows": rows(300), "info": {}}
        c = ctx()
        with mock.patch.object(c, "get_json", return_value=(fx.load("boc_fxusdcad.json"), "t")):
            out = market.build(c, 9999, os.path.join(tempfile.mkdtemp(), "m"), loader=ld)
        self.assertEqual(out["sector_etf"], "SPY")
        self.assertEqual(calls, ["SPY"])

    def test_fx_failure_nulls_only_fx(self):
        c = ctx()
        with mock.patch.object(c, "get_json", side_effect=common.FetchError("HTTP 503")):
            out = market.build(c, 3571, os.path.join(tempfile.mkdtemp(), "m"), loader=loader())
        self.assertIsNone(out["market"]["fx_usdcad"])
        self.assertEqual(out["market"]["missing"], [{"field": "fx_usdcad", "reason": "HTTP 503"}])
        self.assertIsNotNone(out["market"]["spy"])
        self.assertEqual(set(out["sources"]), {"S7"})

    def test_etf_failure_nulls_blocks_and_source(self):
        def bad(ticker, years):
            raise common.FetchError("no history")
        out = self.build(ctx(), os.path.join(tempfile.mkdtemp(), "m"), ld=bad)
        self.assertIsNone(out["market"]["spy"])
        self.assertIsNone(out["market"]["sector"])
        self.assertEqual({x["field"] for x in out["market"]["missing"]}, {"spy", "sector"})
        self.assertEqual(set(out["sources"]), {"S8"})


if __name__ == "__main__":
    unittest.main()
