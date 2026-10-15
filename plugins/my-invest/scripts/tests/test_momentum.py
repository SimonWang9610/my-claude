"""momentum.py: returns, averages, volatility and relative strength against hand-computed values (no network)."""
import datetime as dt
import json
import math
import os
import tempfile
import unittest

import momentum


def series(closes, src="S3"):
    d0 = dt.date(2025, 1, 1)
    return {"ticker": "T", "src": src, "dates": [(d0 + dt.timedelta(days=i)).isoformat() for i in range(len(closes))],
            "close": list(closes)}


LINEAR = series([100 + i for i in range(300)])             # last close 399
SPY = series([200 + i for i in range(300)], "S7")          # last close 499


class ComputeTests(unittest.TestCase):
    def setUp(self):
        self.m = momentum.compute(LINEAR, SPY, SPY)

    def test_window_returns(self):
        self.assertAlmostEqual(self.m["return_1m"], 399 / 378 - 1, 6)      # 21 trading days back
        self.assertAlmostEqual(self.m["return_3m"], 399 / 336 - 1, 6)
        self.assertAlmostEqual(self.m["return_6m"], 399 / 273 - 1, 6)
        self.assertAlmostEqual(self.m["return_12m"], 399 / 147 - 1, 6)
        self.assertAlmostEqual(self.m["return_12m_skip_1m"], 378 / 147 - 1, 6)  # t-252 to t-21

    def test_averages_and_flags(self):
        self.assertEqual(self.m["ma50"], 374.5)     # mean of 350..399
        self.assertEqual(self.m["ma200"], 299.5)    # mean of 200..399
        self.assertTrue(self.m["above_ma50"] and self.m["above_ma200"] and self.m["ma50_above_ma200"])
        self.assertEqual(self.m["pct_from_52w_high"], 0.0)

    def test_distance_from_high_after_a_drop(self):
        s = series([100 + i for i in range(299)] + [349])   # high 398, last 349
        self.assertAlmostEqual(momentum.compute(s)["pct_from_52w_high"], 1 - 349 / 398, 6)

    def test_relative_strength_and_inputs(self):
        self.assertAlmostEqual(self.m["rel_strength_spy_6m"], (399 / 273 - 1) - (499 / 373 - 1), 6)
        self.assertEqual(self.m["rel_strength_sector_6m"], self.m["rel_strength_spy_6m"])
        self.assertEqual(self.m["inputs"], ["S3", "S7"])
        self.assertEqual(self.m["missing"], {})
        self.assertEqual(self.m["as_of"], LINEAR["dates"][-1])

    def test_volatility_constant_growth_is_zero(self):
        s = series([100 * 1.01 ** i for i in range(300)])
        m = momentum.compute(s)
        self.assertAlmostEqual(m["realized_vol_30d"], 0.0, 6)
        self.assertAlmostEqual(m["realized_vol_1y"], 0.0, 6)

    def test_volatility_alternating_returns(self):
        s = series([100 if i % 2 == 0 else 110 for i in range(300)])   # log returns alternate +-ln(1.1)
        a = math.log(1.1)
        self.assertAlmostEqual(momentum.compute(s)["realized_vol_30d"], a * math.sqrt(30 / 29) * math.sqrt(252), 5)

    def test_short_history_is_null_with_reason(self):
        m = momentum.compute(series([100 + i for i in range(40)]))
        self.assertIsNone(m["return_6m"])
        self.assertIsNone(m["ma200"])
        self.assertIsNone(m["above_ma200"])
        self.assertIn("needs 127 closes, have 40", m["missing"]["return_6m"])
        self.assertIsNotNone(m["return_1m"])
        self.assertIsNotNone(m["realized_vol_30d"])
        self.assertIn("rel_strength_spy_6m", m["missing"])
        self.assertEqual(m["inputs"], ["S3"])

    def test_null_closes_are_skipped(self):
        s = series([100, None, 101, 102])
        self.assertEqual(momentum.closes_of(s)[1], [100, 101, 102])

    def test_missing_market_series_only_nulls_relative_strength(self):
        m = momentum.compute(LINEAR, None, SPY)
        self.assertIsNone(m["rel_strength_spy_6m"])
        self.assertIn("SPY", m["missing"]["rel_strength_spy_6m"])
        self.assertIsNotNone(m["rel_strength_sector_6m"])


class AnnotateTests(unittest.TestCase):
    def test_reads_files_and_writes_into_facts(self):
        d = tempfile.mkdtemp()
        folder, mdir = os.path.join(d, "stocks", "T"), os.path.join(d, "market")
        os.makedirs(folder)
        os.makedirs(mdir)
        for path, obj in ((os.path.join(folder, "series.json"), LINEAR), (os.path.join(mdir, "SPY.json"), SPY),
                          (os.path.join(mdir, "XLK.json"), SPY),
                          (os.path.join(folder, "facts.json"), {"ticker": "T", "sector_etf": "XLK", "keep": 1})):
            with open(path, "w") as f:
                json.dump(obj, f)
        mom = momentum.annotate(os.path.join(folder, "facts.json"), mdir)
        with open(os.path.join(folder, "facts.json")) as f:
            facts = json.load(f)
        self.assertEqual(facts["momentum"], mom)
        self.assertEqual(facts["keep"], 1)
        self.assertEqual(mom["inputs"], ["S3", "S7"])

    def test_no_series_gives_all_null_block(self):
        d = tempfile.mkdtemp()
        mom = momentum.annotate(os.path.join(d, "facts.json"), os.path.join(d, "market"))
        self.assertIsNone(mom["ma200"])
        self.assertIn("ma200", mom["missing"])
        self.assertFalse(os.path.exists(os.path.join(d, "facts.json")))


if __name__ == "__main__":
    unittest.main()
