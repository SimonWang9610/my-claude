import datetime as dt
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import calc  # noqa: E402
import db  # noqa: E402
import stats  # noqa: E402

ASOF = dt.date(2025, 12, 31)


def weekdays(start, end):
    d = start
    while d <= end:
        if d.weekday() < 5:
            yield d
        d += dt.timedelta(days=1)


def seed_prices(conn, ticker, levels, sid, volume=1000):
    db.upsert(conn, "prices", [{"ticker": ticker, "date": d.isoformat(), "close": p, "adj_close": p, "volume": volume,
                                "source_id": sid} for d, p in levels])


def smooth(rate, years=6):
    """A series growing exactly `rate` a year in calendar time, ending at ASOF."""
    start = ASOF - dt.timedelta(days=int(365.25 * years))
    return [(d, 100.0 * (1 + rate) ** ((d - start).days / 365.25)) for d in weekdays(start, ASOF)]


class Metrics(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")
        self.sid = db.source(self.c, "https://yahoo/x", "secondary", "Yahoo")

    def compute(self, ticker, with_spy=True):
        s = stats.load(self.c, ticker, "")
        spy = stats.load(self.c, "SPY", s.asof) if with_spy else None
        return stats.compute(s, spy)

    def test_cagr_and_total_return_on_a_known_series(self):
        seed_prices(self.c, "GRW", smooth(0.10), self.sid)
        m, skipped = self.compute("GRW", with_spy=False)
        for w in ("1y", "3y", "5y"):
            self.assertAlmostEqual(m["cagr"][w], 0.10, places=2)
        self.assertAlmostEqual(m["total_return"]["3y"], 1.1 ** 3 - 1, places=2)
        self.assertAlmostEqual(m["max_drawdown"]["5y"], 0.0, places=6)
        self.assertEqual(m["trend"]["spot"], 1)
        self.assertGreater(m["ma50"]["spot"], m["ma200"]["spot"])
        self.assertAlmostEqual(m["from_ma200"]["spot"], m["close"]["spot"] / m["ma200"]["spot"] - 1)
        self.assertEqual(m["avg_volume_3m"]["spot"], 1000)
        self.assertAlmostEqual(m["ytd_return"]["spot"], 0.10, places=2)

    def test_recent_moves_count_trading_days(self):
        start = ASOF - dt.timedelta(days=200)
        levels = [(d, 100.0 * 1.001 ** i) for i, d in enumerate(weekdays(start, ASOF))]  # +0.1% every trading day
        seed_prices(self.c, "STEP", levels, self.sid)
        m, skipped = self.compute("STEP", with_spy=False)
        for metric, n in (("ret_1d", 1), ("ret_1w", 5), ("ret_1m", 21), ("ret_3m", 63)):
            self.assertAlmostEqual(m[metric]["spot"], 1.001 ** n - 1, places=10, msg=metric)
        seed_prices(self.c, "SHORT", levels[-30:], self.sid)
        m, skipped = self.compute("SHORT", with_spy=False)
        self.assertIn("ret_1m", m)
        self.assertNotIn("ret_3m", m)
        self.assertTrue(any(x["metric"] == "ret_3m" for x in skipped))

    def test_windows_not_covered_are_skipped_not_invented(self):
        seed_prices(self.c, "NEW", smooth(0.10, years=2), self.sid)
        m, skipped = self.compute("NEW", with_spy=False)
        self.assertIn("1y", m["cagr"])
        self.assertNotIn("3y", m["cagr"])
        self.assertTrue(any(x["metric"] == "cagr" and x["window"] == "5y" for x in skipped))

    def test_max_drawdown_and_flat_cagr(self):
        start = ASOF - dt.timedelta(days=400)
        levels = []
        for d in weekdays(start, ASOF):
            age = (ASOF - d).days
            levels.append((d, 80.0 if 1 <= age <= 90 else 100.0))  # a 20% dip over the last quarter, back to 100 today
        seed_prices(self.c, "DIP", levels, self.sid)
        m, _ = self.compute("DIP", with_spy=False)
        self.assertAlmostEqual(m["max_drawdown"]["1y"], -0.20)
        self.assertAlmostEqual(m["cagr"]["1y"], 0.0)
        self.assertAlmostEqual(m["high_52w"]["spot"], 100.0)
        self.assertAlmostEqual(m["low_52w"]["spot"], 80.0)
        self.assertLess(m["ma50"]["spot"], m["ma200"]["spot"])
        self.assertGreater(m["close"]["spot"], m["ma200"]["spot"])
        self.assertEqual(m["trend"]["spot"], 0)  # close above ma200 but ma50 below it: mixed, so 0

    def test_beta_two_and_corr_one_against_spy(self):
        rng = random.Random(1)
        start = ASOF - dt.timedelta(days=int(365.25 * 4))
        spy, tk, lvl = [], [], 100.0
        for d in weekdays(start, ASOF):
            lvl *= math.exp(rng.gauss(0.0003, 0.01))
            spy.append((d, lvl))
            tk.append((d, 50.0 * (lvl / 100.0) ** 2))  # log returns exactly twice SPY's
        seed_prices(self.c, "SPY", spy, self.sid)
        seed_prices(self.c, "TWO", tk, self.sid)
        m, skipped = self.compute("TWO")
        self.assertAlmostEqual(m["beta"]["1y"], 2.0, places=6)
        self.assertAlmostEqual(m["beta"]["3y"], 2.0, places=6)
        self.assertAlmostEqual(m["corr"]["1y"], 1.0, places=6)
        self.assertIn("1y", m["vs_spy"])
        self.assertNotIn("5y", m["vs_spy"])
        self.assertAlmostEqual(m["vs_spy"]["1y"], m["total_return"]["1y"] - (spy[-1][1] / spy[[d for d, _ in spy].index(
            max(d for d, _ in spy if d <= ASOF.replace(year=2024)))][1] - 1))

    def test_spy_missing_skips_only_the_relative_metrics(self):
        seed_prices(self.c, "GRW", smooth(0.10), self.sid)
        m, skipped = self.compute("GRW")
        self.assertNotIn("beta", m)
        self.assertIn("cagr", m)
        reasons = {(x["metric"], x["window"]): x["reason"] for x in skipped}
        self.assertEqual(reasons[("beta", "1y")], "run yahoo.py prices SPY")
        self.assertEqual(reasons[("vs_spy", "5y")], "run yahoo.py prices SPY")
        self.assertIn(("corr", "1y"), reasons)

    def test_falling_series_has_trend_minus_one_and_a_band(self):
        seed_prices(self.c, "DWN", smooth(-0.20), self.sid)
        m, _ = self.compute("DWN", with_spy=False)
        self.assertEqual(m["trend"]["spot"], -1)
        self.assertLess(m["range_3m_low"]["spot"], m["close"]["spot"])
        self.assertGreater(m["range_3m_high"]["spot"], m["close"]["spot"])
        self.assertLess(m["from_high_52w"]["spot"], 0)

    def test_store_replaces_rows_for_the_same_asof(self):
        seed_prices(self.c, "GRW", smooth(0.10), self.sid)
        m, _ = self.compute("GRW", with_spy=False)
        n, sid = stats.store(self.c, "GRW", ASOF.isoformat(), m)
        n2, _ = stats.store(self.c, "GRW", ASOF.isoformat(), m)
        self.assertEqual(n, n2)
        self.assertEqual(db.one(self.c, "SELECT COUNT(*) n FROM stats WHERE ticker = 'GRW'")["n"], n)
        self.assertEqual(db.one(self.c, "SELECT grade FROM sources WHERE id = ?", (sid,))["grade"], "derived")

    def test_calc_helpers(self):
        self.assertAlmostEqual(calc.cagr(100, 121, 2), 0.10)
        self.assertAlmostEqual(calc.max_drawdown([1, 2, 1, 3]), -0.5)
        self.assertEqual(calc.percentile([1, 2, 3, 4, 5], 50), 3)
        self.assertAlmostEqual(calc.percentile([1, 2, 3, 4, 5], 10), 1.4)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = self.tmp.name
        c = db.connect(self.proj)
        sid = db.source(c, "https://yahoo/x", "secondary", "Yahoo")
        seed_prices(c, "GRW", smooth(0.10), sid)
        c.close()

    def tearDown(self):
        self.tmp.cleanup()

    def run_stats(self, *args):
        out = subprocess.run([sys.executable, os.path.join(HERE, "stats.py"), *args, "--project", self.proj],
                             capture_output=True, text=True)
        return out.returncode, out.stdout

    def test_json_then_md_and_the_no_prices_failure(self):
        code, out = self.run_stats("grw")
        self.assertEqual(code, 0, out)
        obj = json.loads(out)
        self.assertEqual(obj["asof"], ASOF.isoformat())
        self.assertAlmostEqual(obj["metrics"]["cagr"]["5y"], 0.10, places=2)
        code, out = self.run_stats("GRW", "--md")
        self.assertIn("| cagr | 1y | +10.0% |", out)
        self.assertIn("run yahoo.py prices SPY", out)
        code, out = self.run_stats("NOPE")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["error"], "no prices for NOPE; run yahoo.py prices NOPE")


if __name__ == "__main__":
    unittest.main()
