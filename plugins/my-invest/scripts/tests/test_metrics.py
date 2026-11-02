"""Hand-computed checks for scripts/metrics.py against tests/fixtures/metrics_fixture.json."""
import copy
import datetime
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)
import metrics  # noqa: E402

FIXTURE = os.path.join(HERE, "fixtures", "metrics_fixture.json")


def load():
    with open(FIXTURE, encoding="utf-8") as fh:
        return json.load(fh)


def row(facts, fy):
    return next(r for r in facts["fundamentals"]["annual"] if r["fy"] == fy)


def two_year(t, p, sector="manufacturer", market_cap=0.0):
    rows = [dict(t, fy=2025, period_end="2025-12-31"), dict(p, fy=2024, period_end="2024-12-31")]
    return {"sector_class": sector, "price": {"market_cap": market_cap, "splits": []},
            "fundamentals": {"annual": rows}, "macro": {}}


class Piotroski(unittest.TestCase):
    def test_nine_signals_fy2025(self):
        p = metrics.compute(load())["piotroski"]
        # ROA_t = 200/1900 (beginning assets), ROA_t-1 = 180/1800; CFO = 260/1900
        roa0, roa1, cfo0 = 200 / 1900, 180 / 1800, 260 / 1900
        expect = {
            "roa": int(roa0 > 0), "cfo": int(cfo0 > 0), "d_roa": int(roa0 > roa1),
            "accrual": int(cfo0 > roa0),
            "d_lever": int(300 / ((2000 + 1900) / 2) < 350 / ((1900 + 1800) / 2)),
            "d_liquid": int(900 / 450 > 800 / 420),
            "eq_offer": 0,  # equity_issued null and split-adjusted shares 100 > 99
            "d_margin": int(810 / 1800 > 640 / 1600),
            "d_turn": int(1800 / 1900 > 1600 / 1800),
        }
        self.assertEqual(p["signals"], expect)
        self.assertEqual(p["score"], 8)
        self.assertIn("fallback", p["note"])

    def test_eq_offer_fallback_and_reported(self):
        f = load()
        row(f, 2025)["shares_diluted"] = 99  # not rising vs 99 → 1
        self.assertEqual(metrics.compute(f)["piotroski"]["signals"]["eq_offer"], 1)
        row(f, 2025)["equity_issued"] = 0
        row(f, 2025)["shares_diluted"] = 150  # reported 0 wins over shares
        self.assertEqual(metrics.compute(f)["piotroski"]["signals"]["eq_offer"], 1)
        row(f, 2025)["equity_issued"] = 5
        self.assertEqual(metrics.compute(f)["piotroski"]["signals"]["eq_offer"], 0)

    def test_split_does_not_count_as_issuance(self):
        f = load()
        # FY2022 reported 48 pre-split; FY2023 98 post-split → adjusted 96 → 98, rising, not doubling
        f["fundamentals"]["annual"] = [r for r in f["fundamentals"]["annual"] if r["fy"] <= 2023]
        row(f, 2023)["shares_diluted"] = 96
        self.assertEqual(metrics.compute(f)["piotroski"]["signals"]["eq_offer"], 1)

    def test_one_year_is_null(self):
        f = load()
        f["fundamentals"]["annual"] = f["fundamentals"]["annual"][:1]
        p = metrics.compute(f)["piotroski"]
        self.assertIsNone(p["score"])
        self.assertIn("reason", p)


class Altman(unittest.TestCase):
    def test_fixture_z(self):
        a = metrics.compute(load())["altman"]
        z = 1.2 * 450 / 2000 + 1.4 * 700 / 2000 + 3.3 * 280 / 2000 + 0.6 * 5000 / 1000 + 1.0 * 1800 / 2000
        self.assertEqual(a["model"], "Z")
        self.assertAlmostEqual(a["value"], z, places=4)
        self.assertEqual(a["zone"], "safe")

    def _z(self, revenue):
        # only X5 = sales / TA is non-zero
        y = {"total_assets": 100, "current_assets": 50, "current_liabilities": 50, "retained_earnings": 0,
             "operating_income": 0, "total_liabilities": 40, "revenue": revenue, "equity": 60}
        return metrics.compute(two_year(y, y))["altman"]

    def test_z_zone_boundaries(self):
        self.assertEqual(self._z(180.99)["zone"], "distress")
        self.assertEqual(self._z(181)["zone"], "grey")
        self.assertEqual(self._z(298.99)["zone"], "grey")
        self.assertEqual(self._z(299)["zone"], "safe")

    def _zpp(self, equity):
        # only X4 = book equity / TL is non-zero: 1.05 * equity / 105
        y = {"total_assets": 1000, "current_assets": 50, "current_liabilities": 50, "retained_earnings": 0,
             "operating_income": 0, "total_liabilities": 105, "revenue": 500, "equity": equity}
        return metrics.compute(two_year(y, y, sector="non-manufacturer", market_cap=1e9))["altman"]

    def test_zpp_zone_boundaries(self):
        self.assertEqual(self._zpp(109.99)["zone"], "distress")
        self.assertEqual(self._zpp(110)["model"], "Z''")
        self.assertEqual(self._zpp(110)["zone"], "grey")
        self.assertEqual(self._zpp(259.99)["zone"], "grey")
        self.assertEqual(self._zpp(260)["zone"], "safe")

    def test_na_sectors(self):
        for s in ("financial", "reit", "utility"):
            f = load()
            f["sector_class"] = s
            m = metrics.compute(f)
            self.assertIsNone(m["altman"]["value"])
            self.assertIn(s, m["altman"]["reason"])
            self.assertIsNone(m["beneish"]["m"])


class Beneish(unittest.TestCase):
    T = {"revenue": 200, "cogs": 120, "receivables": 40, "current_assets": 100, "ppe_net": 50,
         "total_assets": 300, "da": 10, "sga": 30, "current_liabilities": 60, "lt_debt": 40,
         "net_income": 20, "ocf": 10}
    P = {"revenue": 100, "cogs": 50, "receivables": 10, "current_assets": 80, "ppe_net": 60,
         "total_assets": 250, "da": 12, "sga": 20, "current_liabilities": 50, "lt_debt": 50,
         "net_income": 15, "ocf": 15}

    def test_two_year_toy(self):
        b = metrics.compute(two_year(self.T, self.P))["beneish"]
        v = {"DSRI": (40 / 200) / (10 / 100), "GMI": 0.5 / 0.4, "AQI": (1 - 150 / 300) / (1 - 140 / 250),
             "SGI": 2.0, "DEPI": (12 / 72) / (10 / 60), "SGAI": (30 / 200) / (20 / 100),
             "LVGI": (100 / 300) / (100 / 250), "TATA": (20 - 10) / 300}
        for k, x in v.items():
            self.assertAlmostEqual(b["variables"][k], x, places=4, msg=k)
        m = (-4.84 + 0.920 * v["DSRI"] + 0.528 * v["GMI"] + 0.404 * v["AQI"] + 0.892 * v["SGI"]
             + 0.115 * v["DEPI"] - 0.172 * v["SGAI"] + 4.679 * v["TATA"] - 0.327 * v["LVGI"])
        self.assertAlmostEqual(b["m"], m, places=4)
        self.assertTrue(b["flag"])
        self.assertIn("UNVERIFIED coefficients and cutoff", b["note"])

    def test_missing_variable_nulls_m(self):
        t = dict(self.T, sga=None)
        b = metrics.compute(two_year(t, self.P))["beneish"]
        self.assertIsNone(b["m"])
        self.assertIn("SGAI", b["reason"])


class Sloan(unittest.TestCase):
    def test_with_taxes_payable(self):
        a = metrics.compute(load())["accrual_ratio"]
        acc = (100 - 100) - (30 - (20 - 30) - (25 - 20)) - 60
        self.assertAlmostEqual(a["value"], acc / 1950, places=4)
        self.assertNotIn("note", a)

    def test_without_taxes_payable(self):
        f = load()
        row(f, 2024)["taxes_payable"] = None
        a = metrics.compute(f)["accrual_ratio"]
        acc = (100 - 100) - (30 - (20 - 30) - 0) - 60
        self.assertAlmostEqual(a["value"], acc / 1950, places=4)
        self.assertIn("taxes_payable", a["note"])


class Roic(unittest.TestCase):
    def test_with_and_without_goodwill(self):
        m = metrics.compute(load())
        r0 = m["roic"][0]
        nopat = 280 * (1 - 60 / 260)
        self.assertEqual(r0["fy"], 2025)
        self.assertAlmostEqual(r0["value"], nopat / (1000 + 20 + 300 - 400), places=4)
        self.assertAlmostEqual(r0["value_ex_goodwill"], nopat / (920 - 100), places=4)
        r_loss = next(r for r in m["roic"] if r["fy"] == 2019)
        self.assertEqual(r_loss["tax_rate"], 0.21)  # pretax <= 0 → default
        nopat5 = 180 * (1 - 34 / 170)
        self.assertAlmostEqual(m["roiic_5y"]["value"], (nopat - nopat5) / (920 - 660), places=4)

    def test_tax_rate_clamped(self):
        f = load()
        row(f, 2025)["income_tax"] = 200  # 200/260 > 0.35
        self.assertEqual(metrics.compute(f)["roic"][0]["tax_rate"], 0.35)

    def test_roiic_null_when_capital_shrinks(self):
        f = load()
        row(f, 2020)["equity"] = 2000
        r = metrics.compute(f)["roiic_5y"]
        self.assertIsNone(r["value"])
        self.assertIn("denominator", r["reason"])


class CapitalAllocation(unittest.TestCase):
    def test_dilution_with_split(self):
        d = metrics.compute(load())["dilution_5y"]
        # FY2020 reported 46 before the 2023-06-15 2:1 split → 92
        self.assertAlmostEqual(d["value"], 100 / 92 - 1, places=4)
        self.assertEqual(d["rising_years_last3"], 3)  # 96→98→99→100
        self.assertTrue(d["split_adjusted"])

    def test_retained_earnings(self):
        r = metrics.compute(load())["retained_earnings_test"]
        retained = (200 + 180 + 160 + 150 + 140) - (60 + 50 + 40 + 30 + 20)
        self.assertAlmostEqual(r["value"], (5000 - 3000) / retained, places=4)

    def test_retained_earnings_null_when_nothing_retained(self):
        f = load()
        for fy in range(2021, 2026):
            row(f, fy)["dividends_paid"] = 1000
        self.assertIsNone(metrics.compute(f)["retained_earnings_test"]["value"])

    def test_market_cap_5y_ago_derived_from_close(self):
        f = load()
        f["price"]["market_cap_5y_ago"] = None
        f["price"]["close_5y_ago"] = 30.0
        r = metrics.compute(f)["retained_earnings_test"]
        # FY2020 reported 46 shares before the 2023 2:1 split → 92; 30 x 92 = 2760
        self.assertAlmostEqual(r["value"], (5000 - 30 * 92) / 630, places=4)
        self.assertIn("price.close_5y_ago", r["inputs"])
        self.assertIn("market_cap_5y_ago derived", r["note"])
        row(f, 2020)["shares_diluted"] = None
        f["fundamentals"]["shares_history"] = [{"fy": 2020, "period_end": "2020-12-31", "shares_diluted": 46}]
        r = metrics.compute(f)["retained_earnings_test"]
        self.assertAlmostEqual(r["value"], (5000 - 30 * 92) / 630, places=4)
        self.assertIn("fundamentals.shares_history[fy=2020].shares_diluted", r["inputs"])
        f["fundamentals"]["shares_history"] = []
        r = metrics.compute(f)["retained_earnings_test"]
        self.assertIsNone(r["value"])
        self.assertIn("close_5y_ago", r["reason"])

    def test_owner_earnings_and_yields(self):
        m = metrics.compute(load())
        self.assertEqual(m["owner_earnings"]["value"], 200 + 60 - min(50, 60))
        self.assertAlmostEqual(m["shareholder_yield"]["value"], (60 + 90 + (80 - 30)) / 5000, places=4)
        self.assertEqual(m["goodwill_impairment_5y"]["value"], 1)
        self.assertAlmostEqual(m["earnings_yield"]["value"], 280 / (5000 + 20 + 300 - 400), places=4)
        self.assertAlmostEqual(m["return_on_capital"]["value"], 280 / (600 + 450), places=4)

    def test_quality_series(self):
        m = metrics.compute(load())
        self.assertAlmostEqual(m["gross_profitability"]["value"], 810 / 2000, places=4)
        self.assertAlmostEqual(m["gross_margin_5y_change"]["value"], (810 / 1800 - 480 / 1200) * 100, places=4)
        self.assertAlmostEqual(m["revenue_cagr_5y"]["value"], 1.5 ** 0.2 - 1, places=4)
        self.assertEqual(m["revenue_declines_consecutive_10y"]["value"], 2)
        eh = m["earnings_history"]
        self.assertEqual((eh["loss_years_10y"], eh["years_available"]), (1, 10))
        # adjusted EPS: newest 2.0, 1.8, 1.6; oldest 1.8/2, 2.0/2, 1.6/2
        self.assertAlmostEqual(eh["eps_growth_10y"], 1.8 / 0.9 - 1, places=4)


class Graham(unittest.TestCase):
    def test_value(self):
        g = metrics.compute(load())["graham_number"]
        self.assertAlmostEqual(g["value"], math.sqrt(22.5 * 1.8 * 10), places=2)

    def test_null_cases(self):
        f = load()
        row(f, 2025)["eps_diluted"] = -10
        g = metrics.compute(f)["graham_number"]
        self.assertIsNone(g["value"])
        self.assertIn("<= 0", g["reason"])
        f = load()
        row(f, 2025)["equity"] = -5
        self.assertIsNone(metrics.compute(f)["graham_number"]["value"])
        f = load()
        row(f, 2024)["eps_diluted"] = None
        g = metrics.compute(f)["graham_number"]
        self.assertIsNone(g["value"])
        self.assertIn("missing", g["reason"])


def model_v0(cf0, g, r, gt, net_cash, shares):
    """Independent restatement of valuation.md for the test."""
    cf, pv = cf0, 0.0
    for t in range(1, 11):
        cf *= 1 + (g if t <= 5 else g + (gt - g) * (t - 5) / 5)
        pv += cf / (1 + r) ** t
    pv += cf * (1 + gt) / (r - gt) / (1 + r) ** 10
    return (pv + net_cash) / shares


class Valuation(unittest.TestCase):
    def test_fixture_base(self):
        v = metrics.compute(load())["valuation"]
        r, gt = 0.04 + 0.045, 0.025
        cf0 = (210 + 180 + 170) / 3
        nopat0, nopat5 = 280 * (1 - 60 / 260), 180 * (1 - 34 / 170)
        roiic = (nopat0 - nopat5) / (920 - 660)
        reinvest = 1 - (60 + 90) / 210
        g = min(min(max((210 / 136) ** 0.2 - 1, 0), 0.15), roiic * reinvest)
        self.assertAlmostEqual(v["scenarios"]["base"]["g"], g, places=4)
        self.assertAlmostEqual(v["params"]["r_bear"], r + 0.02, places=4)
        base = model_v0(cf0, g, r, gt, 400 - 20 - 300, 100)
        self.assertAlmostEqual(v["fair_value_today"]["base"], base, places=2)
        self.assertAlmostEqual(v["buy_zone_below"], base * 0.7, places=2)
        bear = model_v0((min(210, 210) + min(180, 160) + min(170, 160)) / 3, g / 2, r + 0.02, gt, 80, 100)
        self.assertAlmostEqual(v["fair_value_today"]["bear"], bear, places=2)
        self.assertEqual(v["sell_zone_above"], v["fair_value_today"]["bull"])

    def test_zero_growth_is_perpetuity(self):
        f = load()
        f["macro"]["dgs10"] = 0.0  # terminal g = min(2.5%, 0) = 0
        for r_ in f["fundamentals"]["annual"]:
            r_.update(net_income=100, da=20, capex=20)  # owner earnings 100 every year → CAGR 0
        v = metrics.compute(f, erp=8.0)["valuation"]
        self.assertEqual(v["scenarios"]["base"]["g"], 0.0)
        self.assertAlmostEqual(v["fair_value_today"]["base"], (100 / 0.08 + 80) / 100, places=2)
        # horizon identity V_1 = V_0 (1 + r) - CF_1, per share, CF_1 = 100 / 100
        self.assertAlmostEqual(v["by_horizon"]["1"]["base"], 13.3 * 1.08 - 1.0, places=2)

    def test_horizon_identity_with_growth(self):
        v = metrics.compute(load())["valuation"]
        g, r = v["scenarios"]["bull"]["g"], v["scenarios"]["bull"]["r"]
        cf1 = (210 + 180 + 170) / 3 * (1 + g) / 100
        self.assertAlmostEqual(v["by_horizon"]["1"]["bull"], v["fair_value_today"]["bull"] * (1 + r) - cf1, delta=0.02)

    def test_implied_growth_recovers_g(self):
        f = load()
        v = metrics.compute(f)["valuation"]
        f["price"]["last"] = v["fair_value_today"]["base"]
        v2 = metrics.compute(f)["valuation"]
        self.assertAlmostEqual(v2["implied_growth_at_price"], v["scenarios"]["base"]["g"], delta=5e-4)

    def test_null_when_cf0_not_positive(self):
        f = load()
        for r_ in f["fundamentals"]["annual"]:
            r_["net_income"] = -500
        v = metrics.compute(f)["valuation"]
        self.assertIsNone(v["fair_value_today"]["base"])
        self.assertIn("CF_0", v["reason"])

    def test_erp_override_and_mos(self):
        v = metrics.compute(load(), mos=0.5, erp=6.0)["valuation"]
        self.assertEqual(v["params"]["erp_source"], "--erp")
        self.assertAlmostEqual(v["params"]["r_base"], 0.10, places=4)
        self.assertAlmostEqual(v["buy_zone_below"], v["fair_value_today"]["base"] * 0.5, delta=0.01)


class Series(unittest.TestCase):
    def test_owner_earnings_series(self):
        s = metrics.compute(load())["owner_earnings_series"]
        self.assertEqual([e["fy"] for e in s], list(range(2025, 2015, -1)))
        self.assertEqual((s[0]["value"], s[0]["maintenance_capex"]), (200 + 60 - 50, 50))
        self.assertEqual((s[1]["value"], s[1]["maintenance_capex"]), (180 + 55 - 55, 55))  # capex 70 > da 55
        self.assertEqual(s[0]["method"], "estimate: min(capex, da)")

    def test_fcf_series(self):
        f = load()
        row(f, 2023)["capex"] = None
        s = metrics.compute(f)["fcf_series"]
        self.assertEqual(s[1]["value"], 230 - 70)
        self.assertIsNone(s[2]["value"])
        self.assertIn("reason", s[2])

    def test_cash_returned(self):
        f = load()
        row(f, 2024)["buybacks"] = None
        s = metrics.compute(f)["cash_returned"]
        self.assertEqual((s[0]["dividends_paid"], s[0]["buybacks"], s[0]["total"]), (60, 90, 150))
        self.assertEqual((s[1]["buybacks"], s[1]["total"]), (0, 50))
        self.assertIn("buybacks null treated as 0", s[1]["note"])

    def test_shares_adjusted_for_split(self):
        s = metrics.compute(load())["shares_diluted_adjusted"]
        # 2:1 split on 2023-06-15: FY2023+ unchanged, FY2022 and earlier doubled
        self.assertEqual([e["value"] for e in s[:5]], [100, 99, 98, 96, 94])
        self.assertIn("price.splits", s[0]["inputs"])


class ScorerInputs(unittest.TestCase):
    def test_goodwill_impairment_all_null_vs_partial(self):
        f = load()
        for fy in range(2021, 2026):
            row(f, fy)["goodwill_impairment"] = None
        g = metrics.compute(f)["goodwill_impairment_5y"]
        self.assertIsNone(g["value"])
        self.assertIn("null in every year", g["reason"])
        row(f, 2022)["goodwill_impairment"] = 15
        g = metrics.compute(f)["goodwill_impairment_5y"]
        self.assertEqual(g["value"], 1)
        self.assertIn("4 of 5 years null", g["note"])

    def test_gate_inputs(self):
        f = load()
        m = metrics.compute(f)
        self.assertEqual(m["owner_earnings_series"][1]["value_full_capex"], 180 + 55 - 70)
        gi = m["gate_inputs"]
        self.assertEqual(gi["owner_earnings_negative_years_5y_full_capex"], 0)
        self.assertEqual((gi["current_ratio"], gi["net_current_assets"]), (2.0, 450))
        self.assertAlmostEqual(gi["lt_debt_to_net_current_assets"], 300 / 450, places=4)
        self.assertEqual(gi["loss_years_10y"], 1)
        for fy in (2025, 2023, 2021):
            row(f, fy)["net_income"] = -100
        row(f, 2025)["current_liabilities"] = 900
        gi = metrics.compute(f)["gate_inputs"]
        self.assertEqual(gi["owner_earnings_negative_years_5y_full_capex"], 3)
        self.assertIsNone(gi["lt_debt_to_net_current_assets"])
        self.assertIn("net current assets <= 0", gi["reason"])

    def test_agreement(self):
        v = metrics.compute(load())["valuation"]
        fv = v["fair_value_today"]
        self.assertAlmostEqual(v["agreement"], max(0, min(1, 1 - (fv["bull"] - fv["bear"]) / fv["base"])), delta=1e-3)

    def test_freshness(self):
        f = load()  # price 2026-10-13, retrieved 2026-10-14, annual[0] filed 2026-02-15
        fr = metrics.compute(f)["freshness"]
        self.assertEqual((fr["value"], fr["price_age_trading_days"], fr["newer_10k_exists"]), (1.0, 1, False))
        f["filings_recent"] = [{"form": "10-Q", "filed": "2026-08-01"}]
        self.assertEqual(metrics.compute(f)["freshness"]["value"], 1.0)  # 10-Qs do not count
        f["filings_recent"].append({"form": "10-K", "filed": "2026-03-01"})
        self.assertEqual(metrics.compute(f)["freshness"]["value"], 0.5)
        f["filings_recent"] = []
        f["price"]["date"] = "2026-10-09"  # Fri → Mon, Tue, Wed = 3 trading days
        self.assertEqual(metrics.compute(f)["freshness"]["value"], 0.5)
        f["price"]["date"] = "2026-10-05"  # 7 trading days
        fr = metrics.compute(f)["freshness"]
        self.assertEqual((fr["value"], fr["price_age_trading_days"]), (0.0, 7))

    def test_revenue_declines_meaning(self):
        r = metrics.compute(load())["revenue_declines_consecutive_10y"]
        self.assertEqual(r["meaning"], "longest run of consecutive annual declines")


class Multiples(unittest.TestCase):
    def test_pe_stats_and_ratios(self):
        mu = metrics.compute(load())["multiples"]
        # P/E at FY ends: 40/2.0, 32.4/1.8, 35.2/1.6, 24/1.5, 33.6/1.4, 19.5/1.3, FY2019 EPS < 0, 18/0.9, 14/1.0, 20/0.8
        pe = mu["pe"]
        self.assertEqual((pe["current"], pe["median_10y"], pe["p25"], pe["p75"], pe["low"], pe["high"],
                          pe["years_available"]), (25.0, 20.0, 16.0, 22.0, 14.0, 25.0, 9))
        y0 = mu["years"][0]
        self.assertAlmostEqual(y0["ps"], 40 * 100 / 1800, places=4)
        self.assertAlmostEqual(y0["pfcf"], 4000 / (260 - 50), places=4)
        self.assertAlmostEqual(y0["ev_ebit"], (4000 + 20 + 300 - 400) / 280, places=4)
        y22 = next(y for y in mu["years"] if y["fy"] == 2022)  # pre-split EPS 3.00 and shares 48 → 1.50, 96
        self.assertAlmostEqual(y22["pe"], 24 / 1.5, places=4)
        self.assertAlmostEqual(y22["ps"], 24 * 96 / 1400, places=4)
        self.assertIsNone(next(y for y in mu["years"] if y["fy"] == 2019)["pe"])
        self.assertIn("split-adjusted", mu["basis_note"])


class Outlook(unittest.TestCase):
    def test_five_year_prices_and_cagr(self):
        o = metrics.compute(load())["outlook"]
        g = (2.0 / 1.3) ** 0.2 - 1  # adjusted EPS FY2025 vs FY2020; no consensus → history alone
        sy = (60 + 90) / 5000
        exp = {"bear": (g - 0.03, 16.0), "base": (g, 25 + (20 - 25) * 0.5), "bull": (g + 0.03, 25 + (22 - 25) * 3 / 8)}
        h5 = o["horizons"]["5"]
        for s, (gg, mult) in exp.items():
            price = 2.0 * (1 + gg) ** 5 * mult
            self.assertAlmostEqual(h5[s]["price"], price, places=2, msg=s)
            self.assertAlmostEqual(h5[s]["cagr"], (price / 50) ** 0.2 - 1 + sy, places=4, msg=s)
        self.assertEqual(h5["verdict"], metrics.verdict(h5["base"]["cagr"], 0.085))
        self.assertEqual(o["horizons"]["2"]["bull"]["multiple"], 25.0)  # held through year 2
        self.assertEqual(o["horizons"]["10"]["bull"]["multiple"], 22.0)  # p75 at year 10
        self.assertEqual(sorted(o["horizons"]), ["1", "10", "2", "5"])
        self.assertIn("Bogle and Nolan 2015", o["method_note"])
        self.assertNotIn("UNVERIFIED", o["method_note"])
        self.assertIn("38% of twelve-month analyst targets", o["consensus_base_rate"])

    def test_consensus_blend(self):
        f = load()
        f["consensus"] = {"available": True, "growth": {"next_year": 0.05, "next_5y_per_year": 0.08},
                          "eps": {"next_fy": {"estimate": 2.42}}}
        g = metrics.compute(f)["outlook"]["params"]["g"]
        hist, cons2 = (2.0 / 1.3) ** 0.2 - 1, (2.42 / 2.0) ** 0.5 - 1
        self.assertAlmostEqual(g["base"], (hist + cons2) / 2, places=4)
        self.assertAlmostEqual(g["bear"], min(hist, 0.05) - 0.03, places=4)
        self.assertAlmostEqual(g["bull"], max(hist, cons2) + 0.03, places=4)

    def test_verdict_boundaries(self):
        r = 0.085
        self.assertEqual(metrics.verdict(0.105, r), "attractive")
        self.assertEqual(metrics.verdict(0.1049, r), "fair")
        self.assertEqual(metrics.verdict(0.065, r), "fair")
        self.assertEqual(metrics.verdict(0.0649, r), "expensive")
        self.assertIsNone(metrics.verdict(None, r))

    def test_ps_fallback_when_eps_not_positive(self):
        f = load()
        row(f, 2025)["eps_diluted"] = -1.0
        o = metrics.compute(f)["outlook"]
        p = o["params"]
        self.assertEqual(p["multiple"]["basis"], "ps")
        self.assertEqual(p["sales_per_share_0"], 18.0)
        self.assertAlmostEqual(p["multiple"]["current"], 5000 / 1800, places=4)
        self.assertAlmostEqual(p["g"]["inputs"]["sales_per_share_cagr_5y"], (18.0 / (1200 / 92)) ** 0.2 - 1, places=4)
        self.assertIn("price-to-sales", o["note"])
        self.assertIsNotNone(o["horizons"]["5"]["base"]["price"])

    def test_months_range(self):
        f = load()  # iv 0.30, expiry 129 days out: not the expiry after a 90-day horizon → iv-scaled
        mo = metrics.compute(f)["outlook"]["months"]
        mv = 50 * 0.30 * math.sqrt(90 / 365)
        self.assertEqual((mo["range_1sd"]["low"], mo["range_1sd"]["high"]), (round(50 - mv, 2), round(50 + mv, 2)))
        self.assertEqual((mo["trend"], mo["regime"]), ("trend up", "normal"))
        self.assertTrue(mo["events"][0]["inside_horizon"])
        f["options"]["days_to_expiry"] = 100  # first expiry after the horizon → options implied move
        mo = metrics.compute(f)["outlook"]["months"]
        self.assertEqual((mo["range_1sd"]["low"], mo["range_1sd"]["high"]), (43.0, 57.0))
        mo = metrics.compute(f, horizons=(0.25, 1.0))["outlook"]["months"]
        self.assertEqual(mo["horizon_days"], 91)

    def test_regime_and_trend_states(self):
        f = load()
        f["market"]["spy"]["return_24m"] = -0.1
        f["momentum"]["realized_vol_30d"] = 0.35
        f["momentum"]["ma50"] = 43.0
        f["price"]["last"] = 40.0
        mo = metrics.compute(f)["outlook"]["months"]
        self.assertEqual((mo["trend"], mo["regime"]), ("trend down", "crash regime"))


class Calibration(unittest.TestCase):
    def test_fixture(self):
        c = metrics.compute(load())["calibration"]
        self.assertEqual(c["fy_then"], 2020)
        # strict: CF_0 = mean OE FY2020/19/18 = (136, -20, 90); g = min(clamp(CAGR 4y), 0.10) = 0.10
        v = model_v0((136 - 20 + 90) / 3, 0.10, 0.085, 0.025, 150 - 10 - 200, 92)
        self.assertAlmostEqual(c["strict_value_then"], v, places=2)
        self.assertAlmostEqual(c["ratio_price_to_value"], 19.5 / c["strict_value_then"], places=3)
        yrs = (datetime.date(2026, 10, 13) - datetime.date(2020, 12, 31)).days / 365.25
        realized = (50 / 17.55) ** (1 / yrs) - 1
        self.assertAlmostEqual(c["realized_cagr_since"], realized, places=4)
        g = (1.3 / 0.8) ** 0.25 - 1  # FY2020 EPS vs FY2016 (FY2015 absent)
        mult = 15 + (17.5 - 15) * yrs / 10  # P/E then 19.5/1.3, median of 15, 20, 14, 25
        fc = (1.3 * (1 + g) ** yrs * mult / 19.5) ** (1 / yrs) - 1 + 20 / (19.5 * 92)
        self.assertAlmostEqual(c["base_forecast_then"]["cagr"], fc, places=4)
        self.assertAlmostEqual(c["error_pp"], (realized - fc) * 100, places=3)
        self.assertIn("returned", c["note"])

    def test_short_history_null(self):
        f = load()
        f["fundamentals"]["annual"] = f["fundamentals"]["annual"][:3]
        c = metrics.compute(f)["calibration"]
        self.assertIsNone(c["fy_then"])
        self.assertIn("reason", c)

    KEYS = {"years_back", "fy_then", "price_then", "price_then_date", "strict_value_then", "ratio_price_to_value",
            "base_forecast_cagr", "realized_cagr_since", "realized_basis", "spy_cagr_same_window", "spy_basis",
            "error_pp", "years_elapsed"}

    def test_record_one_entry_per_year_back(self):
        c = metrics.compute(load())["calibration"]
        rec = c["record"]
        self.assertEqual([e["years_back"] for e in rec], [3, 4, 5, 6, 7, 8, 9])   # FY2016..2025: 3..9 all present
        for e in rec:
            self.assertTrue(self.KEYS <= set(e), e)
            self.assertEqual(e["fy_then"], 2025 - e["years_back"])
            self.assertIsNone(e["spy_cagr_same_window"])                            # no market/SPY.json passed
            self.assertIn("missing", e["spy_basis"])
            if e["base_forecast_cagr"] is None:
                self.assertIn("reason", e)
        five = rec[2]
        self.assertEqual(five["base_forecast_cagr"], c["base_forecast_then"]["cagr"])  # k=5 mirrors the top level
        self.assertEqual(five["realized_cagr_since"], c["realized_cagr_since"])
        self.assertAlmostEqual(five["error_pp"], c["error_pp"], places=6)        # record: realised minus forecast, same sign as the top level
        rs = c["record_summary"]
        self.assertEqual(rs["n"], len([e for e in rec if e["base_forecast_cagr"] is not None]))
        self.assertIsNone(rs["beat_spy_count"])
        self.assertIn("simulated", rs["note"])
        self.assertTrue(any("not as first filed" in a for a in c["assumptions"]))
        f = load()
        del f["fundamentals"]["annual"][6]                                           # FY2019 gone -> k=6 skipped
        self.assertEqual([e["years_back"] for e in metrics.compute(f)["calibration"]["record"]], [3, 4, 5, 7, 8, 9])

    def test_record_spy_from_series(self):
        with open(os.path.join(HERE, "fixtures", "market_spy.json"), encoding="utf-8") as fh:
            spy = json.load(fh)
        c = metrics.compute(load(), spy=spy)["calibration"]
        five = c["record"][2]
        yrs = (datetime.date(2026, 10, 13) - datetime.date(2020, 12, 31)).days / 365.25
        self.assertAlmostEqual(five["spy_cagr_same_window"], (280.0 / 161.05) ** (1 / yrs) - 1, places=4)
        self.assertTrue(five["spy_basis"].startswith("SPY total return (adj_close) 2020-12-31 to 2026-10-13"))
        rs = c["record_summary"]
        self.assertEqual((rs["spy_windows"], rs["beat_spy_count"]), (7, 7))
        self.assertIn("beat SPY in 7 of 7 windows", rs["note"])
        close_only = {"dates": spy["dates"], "close": list(spy["adj_close"])}
        close_only["close"][-2] = 300.0                                             # 2026-10-13
        five = metrics.compute(load(), spy=close_only)["calibration"]["record"][2]
        self.assertAlmostEqual(five["spy_cagr_same_window"], (300.0 / 161.05) ** (1 / yrs) - 1, places=4)
        self.assertIn("price return only (close", five["spy_basis"])
        stale = {"dates": spy["dates"][:-2], "adj_close": spy["adj_close"][:-2]}   # ends 2025-12-31: not covering now
        five = metrics.compute(load(), spy=stale)["calibration"]["record"][2]
        self.assertIsNone(five["spy_cagr_same_window"])
        self.assertIn("does not cover", five["spy_basis"])

    def test_market_dir_resolution_and_cli(self):
        with tempfile.TemporaryDirectory() as d:
            facts = os.path.join(d, "stocks", "X", "facts", "facts.json")
            os.makedirs(os.path.dirname(facts))
            self.assertEqual(metrics.market_dir_for(facts), os.path.join(d, "market"))   # store layout by default
            os.makedirs(os.path.join(d, "x", "market"))
            self.assertEqual(metrics.market_dir_for(os.path.join(d, "x", "o.json")), os.path.join(d, "x", "market"))
            os.makedirs(os.path.join(d, "market"))
            self.assertIsNone(metrics.load_spy(os.path.join(d, "market")))
            shutil.copy(os.path.join(HERE, "fixtures", "market_spy.json"), os.path.join(d, "market", "SPY.json"))
            shutil.copy(FIXTURE, facts)
            p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "metrics.py"), facts], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            with open(facts) as fh:
                rec = json.load(fh)["metrics"]["calibration"]["record"]
            self.assertIsNotNone(rec[2]["spy_cagr_same_window"])


class FetchFailure(unittest.TestCase):
    def test_price_null(self):
        f = load()
        f["price"] = None
        f["fetch_errors"] = ["prices: timeout"]
        m = metrics.compute(f)
        self.assertEqual(m["owner_earnings"]["value"], 210.0)  # needs no price
        for key in ("dilution_5y", "retained_earnings_test", "graham_number", "earnings_yield",
                    "shareholder_yield", "altman"):
            self.assertIsNone(m[key]["value"], key)
            self.assertIn("price null", m[key]["reason"], key)
        self.assertIsNone(m["owner_earnings"]["yield"])
        self.assertIsNone(m["piotroski"]["signals"]["eq_offer"])  # fallback needs split-adjusted shares
        self.assertIsNone(m["valuation"]["fair_value_today"]["base"])
        self.assertIn("price null", m["valuation"]["reason"])

    def test_macro_null(self):
        f = load()
        f["macro"] = None
        v = metrics.compute(f)["valuation"]
        self.assertIsNone(v["buy_zone_below"])
        self.assertIn("macro null", v["reason"])


class WhatIf(unittest.TestCase):
    def test_parse_horizons(self):
        self.assertEqual(metrics.parse_horizons("1, 3,7.5,3"), (1.0, 3.0, 7.5))
        self.assertEqual(metrics.parse_horizons("0.25"), (0.25,))
        for bad in ("", "0", "11", "x", "-1"):
            with self.assertRaises(ValueError):
                metrics.parse_horizons(bad)

    def test_by_horizon_keys_equal_request(self):
        v = metrics.compute(load(), horizons=metrics.parse_horizons("1,3,7.5,0.25"))["valuation"]
        self.assertEqual(sorted(v["by_horizon"]), sorted(["1", "3", "7.5", "0.25"]))
        self.assertEqual(v["params"]["horizons"], ["1", "3", "7.5", "0.25"])
        self.assertIn("pro-rated", v["params"]["horizon_method"])
        self.assertEqual(sorted(metrics.compute(load())["valuation"]["by_horizon"]), ["1", "10", "2", "5"])

    def test_fractional_horizon(self):
        f = load()
        f["macro"]["dgs10"] = 0.0
        for r_ in f["fundamentals"]["annual"]:
            r_.update(net_income=100, da=20, capex=20)  # flat CF 100, r = 8%, V_0 = 13.3 per share
        v = metrics.compute(f, erp=8.0, horizons=(0.25, 2.5))["valuation"]
        v0 = (100 / 0.08 + 80) / 100
        self.assertAlmostEqual(v["by_horizon"]["0.25"]["base"], v0 * 1.08 ** 0.25 - 0.25 * 1.0, places=2)
        v25 = v0 * 1.08 ** 2.5 - 1.0 * 1.08 ** 1.5 - 1.0 * 1.08 ** 0.5 - 0.5 * 1.0
        self.assertAlmostEqual(v["by_horizon"]["2.5"]["base"], v25, places=2)

    def test_g_base_override(self):
        v = metrics.compute(load(), g_base=0.12)["valuation"]
        sc = v["scenarios"]
        self.assertEqual((sc["base"]["g"], sc["bear"]["g"], sc["bull"]["g"]), (0.12, 0.06, 0.15))
        self.assertEqual(v["params"]["g_base_source"], "what-if")
        self.assertEqual(metrics.compute(load(), g_base=0.19)["valuation"]["scenarios"]["bull"]["g"], 0.20)
        self.assertEqual(metrics.compute(load())["valuation"]["params"]["g_base_source"], "model")

    def test_cli_flags(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "o.json")
            p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "metrics.py"), FIXTURE, "--out", out,
                                "--horizons", "0.25,3", "--g-base", "0.05"], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            with open(out) as fh:
                v = json.load(fh)["metrics"]["valuation"]
        self.assertEqual(sorted(v["by_horizon"]), ["0.25", "3"])
        self.assertEqual(v["scenarios"]["base"]["g"], 0.05)
        p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "metrics.py"), FIXTURE, "--out", out,
                            "--horizons", "12"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertIn("--horizons", json.loads(p.stdout)["error"])


class Cli(unittest.TestCase):
    def test_writes_out_and_never_raises_on_empty(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = os.path.join(d, "f.json"), os.path.join(d, "o.json")
            with open(src, "w") as fh:
                json.dump({"ticker": "X"}, fh)
            p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "metrics.py"), src, "--out", out],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            with open(out) as fh:
                m = json.load(fh)["metrics"]
            self.assertIsNone(m["valuation"]["fair_value_today"]["base"])
            self.assertIn("reason", m["altman"])

    def test_unreadable_input_exits_1(self):
        p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "metrics.py"), "/nonexistent/facts.json"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertIn("error", json.loads(p.stdout))


if __name__ == "__main__":
    unittest.main()
