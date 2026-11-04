import argparse
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import common  # noqa: E402
import db  # noqa: E402
import dcf  # noqa: E402

CFG = {"equity_risk_premium": 4.2, "max_horizon_years": 5}


def fact(ticker, concept, value, end, start=None, unit="USD", sid=1):
    r = {"ticker": ticker, "concept": concept, "unit": unit, "period_end": end, "fp": "FY", "value": value, "source_id": sid}
    if start:
        r.update({"period_start": start, "days": 365})
    else:
        r["period_start"] = ""
    return r


def seed_simple(conn, sid):
    """One fiscal year, the numbers a reader can check by hand (see test_value_by_hand)."""
    rows = [fact("ONE", "Revenues", 1000.0, "2025-12-31", "2025-01-01", sid=sid),
            fact("ONE", "OperatingIncomeLoss", 200.0, "2025-12-31", "2025-01-01", sid=sid),
            fact("ONE", "IncomeTaxExpenseBenefit", 42.0, "2025-12-31", "2025-01-01", sid=sid),
            fact("ONE", "DepreciationDepletionAndAmortization", 50.0, "2025-12-31", "2025-01-01", sid=sid),
            fact("ONE", "PaymentsToAcquirePropertyPlantAndEquipment", 50.0, "2025-12-31", "2025-01-01", sid=sid),
            fact("ONE", "WeightedAverageNumberOfDilutedSharesOutstanding", 100.0, "2025-12-31", "2025-01-01", unit="shares", sid=sid),
            fact("ONE", "CashAndCashEquivalentsAtCarryingValue", 100.0, "2025-12-31", sid=sid)]
    db.upsert(conn, "fundamentals", rows)


def seed_two_years(conn, sid):
    rows = []
    for fy, rev, op in (("2024", 1000.0, 150.0), ("2025", 1210.0, 242.0)):
        rows += [fact("TWO", "RevenueFromContractWithCustomerExcludingAssessedTax", rev, fy + "-12-31", fy + "-01-01", sid=sid),
                 fact("TWO", "OperatingIncomeLoss", op, fy + "-12-31", fy + "-01-01", sid=sid)]
    rows.append(fact("TWO", "EntityCommonStockSharesOutstanding", 50.0, "2025-12-31", unit="shares", sid=sid))
    rows.append(fact("TWO", "LongTermDebtNoncurrent", 300.0, "2025-12-31", sid=sid))
    db.upsert(conn, "fundamentals", rows)
    db.upsert(conn, "macro_series", [{"series": "DGS10", "updated_at": "t"}])
    db.upsert(conn, "macro", [{"series": "DGS10", "date": "2025-12-30", "value": 4.0}])
    db.upsert(conn, "stats", [{"ticker": "TWO", "asof": "2025-12-31", "metric": "beta", "window": "3y", "value": 1.5, "source_id": sid}])


def args(**kw):
    base = dict(growth="", margin="", discount="", terminal=None, years=5, sims=200, seed=7, run_id=None)
    base.update(kw)
    return argparse.Namespace(**base)


class Arithmetic(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")
        self.sid = db.source(self.c, "https://data.sec.gov/api/xbrl/companyfacts/x", "primary", "SEC")

    def test_value_by_hand(self):
        # FCF1 = 1000 x 20% x (1 - 21%) + 50 - 50 = 158; PV = 158/1.1 = 143.636
        # TV = 158 x 1.02 / (0.10 - 0.02) = 2014.5; PV(TV) = 1831.364; equity = +100 cash = 2075.0; / 100 shares
        seed_simple(self.c, self.sid)
        inp = dcf.gather(self.c, "ONE", CFG, args(growth="0,0,0", margin="20,20,20", discount="10,10,10", terminal="2", years=1))
        self.assertAlmostEqual(inp["tax_rate"], 0.21)
        self.assertEqual(inp["years"], 1)
        rows = dcf.scenarios(inp)
        for r in rows:
            self.assertAlmostEqual(r["value_per_share"], 20.75, places=6)
        self.assertEqual(inp["overridden"], ["growth", "margin", "discount", "terminal"])
        self.assertTrue(any(a.startswith("debt 0") for a in inp["assumed"]))

    def test_defaults_from_history_capm_and_horizon_cap(self):
        seed_two_years(self.c, self.sid)
        inp = dcf.gather(self.c, "TWO", CFG, args(years=10))
        self.assertAlmostEqual(inp["growth"]["base"], 0.21, places=6)   # 1000 -> 1210 in one year
        self.assertAlmostEqual(inp["growth"]["high"], 0.26, places=6)
        self.assertAlmostEqual(inp["margin"]["low"], 0.15)
        self.assertAlmostEqual(inp["margin"]["high"], 0.20)
        self.assertAlmostEqual(inp["margin"]["base"], 0.175)
        self.assertAlmostEqual(inp["discount"]["base"], 0.04 + 1.5 * 0.042)   # CAPM with beta 1.5 from stats
        self.assertAlmostEqual(inp["discount"]["low"], inp["discount"]["base"] - 0.015)
        self.assertEqual(inp["years"], 5)
        self.assertEqual(inp["debt"], 300.0)
        self.assertEqual(inp["shares"], 50.0)
        self.assertEqual(inp["overridden"], [])
        rows = dcf.scenarios(inp)
        v = {r["scenario"]: r["value_per_share"] for r in rows}
        self.assertLess(v["low"], v["base"])
        self.assertLess(v["base"], v["high"])

    def test_terminal_growth_stays_a_point_below_the_discount_rate(self):
        seed_simple(self.c, self.sid)
        inp = dcf.gather(self.c, "ONE", CFG, args(growth="0,0,0", margin="20,20,20", discount="3,3,3"))
        rows = dcf.scenarios(inp)
        self.assertAlmostEqual(inp["terminal_requested"], 0.025)
        for r in rows:
            self.assertAlmostEqual(r["terminal"], 0.02)
        inp = dcf.gather(self.c, "ONE", CFG, args(growth="0,0,0", margin="20,20,20", discount="8,10,12"))
        self.assertAlmostEqual(dcf.scenarios(inp)[1]["terminal"], 0.025)

    def test_monte_carlo_reproduces_with_the_seed(self):
        seed_two_years(self.c, self.sid)
        inp = dcf.gather(self.c, "TWO", CFG, args())
        a = dcf.monte_carlo(inp, 300, 7)
        b = dcf.monte_carlo(inp, 300, 7)
        c = dcf.monte_carlo(inp, 300, 8)
        self.assertEqual((a["p10"], a["p50"], a["p90"]), (b["p10"], b["p50"], b["p90"]))
        self.assertNotEqual(a["p50"], c["p50"])
        self.assertLessEqual(a["p10"], a["p50"])
        self.assertLessEqual(a["p50"], a["p90"])

    def test_missing_revenue_and_missing_risk_free_fail_with_the_next_step(self):
        with self.assertRaises(common.FetchError) as cm:
            dcf.gather(self.c, "NONE", CFG, args())
        self.assertIn("run sec.py NONE", str(cm.exception))
        self.assertIn("Revenues", str(cm.exception))
        seed_simple(self.c, self.sid)
        with self.assertRaises(common.FetchError) as cm:
            dcf.gather(self.c, "ONE", CFG, args())  # no DGS10 seeded
        self.assertIn("run fred.py", str(cm.exception))

    def test_store_writes_three_rows_with_band_on_base_only(self):
        seed_simple(self.c, self.sid)
        db.upsert(self.c, "prices", [{"ticker": "ONE", "date": "2025-12-31", "close": 16.6, "source_id": self.sid}])
        inp = dcf.gather(self.c, "ONE", CFG, args(growth="0,0,0", margin="20,20,20", discount="10,10,10", terminal="2", years=1))
        rows = dcf.scenarios(inp)
        mc = dcf.monte_carlo(inp, 50, 7)
        ids, sid = dcf.store(self.c, "ONE", "2025-12-31", inp, rows, mc, 16.6, None)
        self.assertEqual(len(ids), 3)
        recs = db.rows(self.c, "SELECT * FROM valuations ORDER BY id")
        self.assertEqual([r["scenario"] for r in recs], ["low", "base", "high"])
        self.assertIsNone(recs[0]["p50"])
        self.assertAlmostEqual(recs[1]["p50"], 20.75, places=6)
        self.assertAlmostEqual(recs[1]["upside"], 20.75 / 16.6 - 1)
        self.assertEqual(json.loads(recs[1]["inputs"])["years"], 1)
        self.assertEqual(db.one(self.c, "SELECT url FROM sources WHERE id = ?", (sid,))["url"],
                         "derived://dcf.py?ticker=ONE&asof=2025-12-31")


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = self.tmp.name
        c = db.connect(self.proj)
        sid = db.source(c, "https://data.sec.gov/api/xbrl/companyfacts/x", "primary", "SEC")
        seed_simple(c, sid)
        seed_two_years(c, sid)
        db.upsert(c, "prices", [{"ticker": "ONE", "date": "2025-12-31", "close": 16.6, "source_id": sid}])
        c.close()

    def tearDown(self):
        self.tmp.cleanup()

    def run_dcf(self, *args_):
        out = subprocess.run([sys.executable, os.path.join(HERE, "dcf.py"), *args_, "--project", self.proj],
                             capture_output=True, text=True)
        return out.returncode, out.stdout

    def test_json_md_and_failure(self):
        code, out = self.run_dcf("one", "--growth", "0,0,0", "--margin", "20,20,20", "--discount", "10,10,10",
                                 "--terminal", "2", "--years", "1", "--sims", "100")
        self.assertEqual(code, 0, out)
        obj = json.loads(out)
        self.assertAlmostEqual(obj["scenarios"][1]["value_per_share"], 20.75, places=6)
        self.assertEqual(obj["asof"], "2025-12-31")
        code, out = self.run_dcf("TWO", "--md", "--sims", "100")
        self.assertEqual(code, 0, out)
        self.assertIn("| base |", out)
        self.assertIn("Monte Carlo", out)
        self.assertIn("no price", out)
        code, out = self.run_dcf("NONE")
        self.assertEqual(code, 1)
        self.assertIn("run sec.py NONE", json.loads(out)["error"])


if __name__ == "__main__":
    unittest.main()


def qfact(ticker, value, end, start, sid):
    return {"ticker": ticker, "concept": "EarningsPerShareDiluted", "unit": "USD/shares", "period_end": end, "period_start": start,
            "days": 90, "fp": "Q1", "value": value, "source_id": sid}


class CrossChecks(unittest.TestCase):
    """ONE: one fiscal year of P&L (seed_simple) plus EPS, cash flow, prices and two peers for the P/E cross-checks."""

    def setUp(self):
        self.c = db.connect(path=":memory:")
        self.sid = db.source(self.c, "https://data.sec.gov/x", "primary", "SEC")
        seed_simple(self.c, self.sid)
        rows = [fact("ONE", "EarningsPerShareDiluted", 1.0, "2024-12-31", "2024-01-01", unit="USD/shares", sid=self.sid),
                fact("ONE", "EarningsPerShareDiluted", 1.5, "2025-12-31", "2025-01-01", unit="USD/shares", sid=self.sid),
                fact("ONE", "NetCashProvidedByUsedInOperatingActivities", 300.0, "2025-12-31", "2025-01-01", sid=self.sid),
                qfact("ONE", 0.3, "2025-03-31", "2025-01-01", self.sid), qfact("ONE", 0.5, "2026-03-31", "2026-01-01", self.sid)]
        db.upsert(self.c, "fundamentals", rows)
        db.upsert(self.c, "prices", [{"ticker": "ONE", "date": "2025-01-02", "close": 15.0, "source_id": self.sid},
                                     {"ticker": "ONE", "date": "2025-12-31", "close": 16.6, "source_id": self.sid},
                                     {"ticker": "ONE", "date": "2026-04-01", "close": 17.0, "source_id": self.sid}])
        self.inp = dcf.gather(self.c, "ONE", CFG, args(growth="0,0,0", margin="20,20,20", discount="10,10,10", terminal="2", years=1))
        self.fx = dcf.facts(self.c, "ONE")

    def test_trailing_eps_adjusts_the_fiscal_year_by_the_quarters_since(self):
        eps, note, annual = dcf.trailing_eps(self.c, "ONE", self.fx)
        self.assertAlmostEqual(eps, 1.5 + 0.5 - 0.3)
        self.assertIn("1 quarter(s) since", note)
        self.assertEqual(sorted(annual), ["2024-12-31", "2025-12-31"])

    def test_pe_now_range_pfcf_ev_ebit(self):
        cc = dcf.cross_checks(self.c, "ONE", self.inp, self.fx, 17.0)
        self.assertAlmostEqual(cc["pe"], 10.0)
        rng = cc["pe_range"]
        self.assertEqual(rng["n"], 3)                       # FY2024 at 15.0/1.0, FY2025 at 16.6/1.5, now 17/1.7
        self.assertAlmostEqual(rng["min"], 10.0)
        self.assertAlmostEqual(rng["max"], 15.0)
        self.assertAlmostEqual(rng["median"], 16.6 / 1.5)
        self.assertAlmostEqual(cc["value_at_median_pe"], 1.7 * 16.6 / 1.5)
        self.assertAlmostEqual(cc["p_fcf"], 17.0 * 100 / (300 - 50))
        self.assertAlmostEqual(cc["ev_ebit"], (17.0 * 100 - 100) / 200)
        self.assertIsNone(cc["peers"]["median"])
        self.assertTrue(any(p.startswith("peers' P/E") for p in cc["not_applicable"]))

    def test_peers_median_needs_two_stored_peers(self):
        db.upsert(self.c, "securities", [{"ticker": t, "kind": "stock", "industry": "Widgets", "updated_at": "t"} for t in ("ONE", "PA", "PB", "PC")])
        for t, eps, px in (("PA", 2.0, 40.0), ("PB", 1.0, 30.0), ("PC", -1.0, 10.0)):
            db.upsert(self.c, "fundamentals", [fact(t, "EarningsPerShareDiluted", eps, "2025-12-31", "2025-01-01", unit="USD/shares", sid=self.sid)])
            db.upsert(self.c, "prices", [{"ticker": t, "date": "2026-04-01", "close": px, "source_id": self.sid}])
        peers, med, note = dcf.peers_pe(self.c, "ONE")
        self.assertEqual(sorted(p["ticker"] for p in peers), ["PA", "PB"])   # PC has negative earnings
        self.assertAlmostEqual(med, 25.0)
        cc = dcf.cross_checks(self.c, "ONE", self.inp, self.fx, 17.0)
        self.assertAlmostEqual(cc["value_at_peers_pe"], 1.7 * 25.0)

    def test_negative_earnings_are_not_applicable(self):
        db.upsert(self.c, "fundamentals", [qfact("ONE", -3.0, "2026-03-31", "2026-01-01", self.sid)])
        cc = dcf.cross_checks(self.c, "ONE", self.inp, self.fx, 17.0)
        self.assertIsNone(cc["pe"])
        self.assertIn("P/E: earnings are zero or negative", cc["not_applicable"])

    def test_reverse_dcf_recovers_a_known_growth(self):
        inp = dcf.gather(self.c, "ONE", CFG, args(growth="0,5,10", margin="20,20,20", discount="10,10,10", terminal="2", years=5))
        target = dcf.value_per_share(inp, 0.08, 0.20, 0.10, 0.02)[0]
        g, note = dcf.reverse_dcf(inp, target)
        self.assertAlmostEqual(g, 0.08, places=6)
        self.assertIn("8.0%", note)
        g2, note2 = dcf.reverse_dcf(inp, 1e9)
        self.assertIsNone(g2)
        self.assertIn("no growth between", note2)

    def test_sensitivity_grid_centre_is_the_base_value(self):
        grid = dcf.sensitivity(self.inp)
        base = [r for r in dcf.scenarios(self.inp) if r["scenario"] == "base"][0]["value_per_share"]
        centre = grid["rows"][1]["values"]["%.4f" % self.inp["growth"]["base"]]
        self.assertAlmostEqual(centre, base)
        self.assertEqual(len(grid["rows"]), 3)
        self.assertEqual(len(grid["growths"]), 3)
        self.assertLess(grid["rows"][2]["values"]["%.4f" % grid["growths"][0]], centre)  # higher discount, lower growth -> lower value

    def test_store_adds_reverse_and_pe_rows_with_methods(self):
        rows = dcf.scenarios(self.inp)
        mc = dcf.monte_carlo(self.inp, 20, 7)
        cc = dcf.cross_checks(self.c, "ONE", self.inp, self.fx, 17.0)
        extra = {"reverse": {"growth": 0.03, "note": "n"}, "cross": cc, "sensitivity": dcf.sensitivity(self.inp)}
        ids, _ = dcf.store(self.c, "ONE", "2026-04-01", self.inp, rows, mc, 17.0, None, extra)
        recs = db.rows(self.c, "SELECT method, scenario, value_per_share FROM valuations ORDER BY id")
        self.assertEqual([r["method"] for r in recs], ["dcf", "dcf", "dcf", "reverse_dcf", "pe_range"])
        self.assertIsNone(recs[3]["scenario"])
        self.assertAlmostEqual(recs[3]["value_per_share"], 17.0)
        self.assertAlmostEqual(recs[4]["value_per_share"], cc["value_at_median_pe"])
        text = dcf.md("ONE", "2026-04-01", self.inp, rows, mc, 17.0, extra)
        self.assertIn("What the price assumes", text)
        self.assertIn("trailing P/E", text)
        self.assertIn("Base value if growth or the discount rate differ", text)
