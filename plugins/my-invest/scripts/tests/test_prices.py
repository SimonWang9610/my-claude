import datetime as dt
import json
import sys
import tempfile
import unittest
from unittest import mock

import common
import prices


def series(n_years=11, last="2026-10-14"):
    """Weekday rows, close grows 10%/yr compounding, one 4:1 split, one dividend."""
    end = dt.date.fromisoformat(last)
    d = end - dt.timedelta(days=int(365.25 * n_years))
    rows, i = [], 0
    while d <= end:
        if d.weekday() < 5:
            c = 100 * (1.1 ** ((d - (end - dt.timedelta(days=int(365.25 * n_years)))).days / 365.25))
            rows.append({"date": d.isoformat(), "close": c, "adj_close": c, "high": c + 1, "low": c - 1,
                         "dividends": 0.0, "splits": 0.0})
        d += dt.timedelta(days=1)
    rows[100]["splits"] = 4.0
    rows[200]["dividends"] = 0.5
    return rows


class SummarizeTests(unittest.TestCase):
    def setUp(self):
        self.rows = series()
        self.price, self.close_at = prices.summarize(self.rows, {"sharesOutstanding": 10.0, "marketCap": 1000.0},
                                                    ["2026-10-10", "2026-10-11", "1990-01-01"])

    def test_last_and_range(self):
        self.assertEqual(self.price["date"], "2026-10-14")
        self.assertEqual(self.price["last"], self.rows[-1]["close"])
        self.assertGreaterEqual(self.price["high_52w"], self.price["last"])
        self.assertLess(self.price["low_52w"], self.price["high_52w"])
        self.assertEqual((self.price["shares_out"], self.price["market_cap"]), (10.0, 1000.0))

    def test_returns(self):
        self.assertAlmostEqual(self.price["return_1y"], 0.10, places=2)
        self.assertAlmostEqual(self.price["return_5y_cagr"], 0.10, places=2)
        self.assertAlmostEqual(self.price["return_10y_cagr"], 0.10, places=2)
        self.assertGreater(self.price["ytd_return"], 0)
        self.assertIsNone(self.price["market_cap_5y_ago"])
        self.assertEqual(self.price["splits"], [{"date": self.rows[100]["date"], "ratio": 4.0}])

    def test_close_at_nearest_prior_trading_day(self):
        self.assertEqual(self.close_at["2026-10-10"]["date"], "2026-10-09")   # Saturday -> Friday
        self.assertEqual(self.close_at["2026-10-11"]["date"], "2026-10-09")   # Sunday -> Friday
        self.assertIsNone(self.close_at["1990-01-01"])

    def test_short_history_nulls_with_reason(self):
        p, _ = prices.summarize(series(2), {}, [])
        self.assertIsNone(p["return_5y_cagr"])
        self.assertIsNone(p["return_10y_cagr"])
        self.assertTrue(any("return_10y_cagr" in m for m in p["missing"]))
        self.assertTrue(any("shares_out" in m for m in p["missing"]))
        self.assertIsNone(p["shares_out"])

    def test_series_json_aligned(self):
        s = prices.series_json("AAPL", self.rows, "S3", "2026-10-14T00:00:00Z")
        self.assertEqual(len(s["dates"]), len(s["close"]))
        self.assertEqual(len(s["dates"]), len(s["adj_close"]))
        self.assertEqual(s["dividends"], [{"date": self.rows[200]["date"], "amount": 0.5}])
        self.assertEqual(s["splits"][0]["ratio"], 4.0)
        self.assertEqual((s["src"], s["ticker"]), ("S3", "AAPL"))


class BuildTests(unittest.TestCase):
    def test_build_caches_history_and_marks_secondary(self):
        ctx = common.Ctx(tempfile.mkdtemp(), None)
        calls = []

        def loader(t, y):
            calls.append(t)
            return {"version": "1.7.0", "rows": series(), "info": {"sharesOutstanding": 1.0, "marketCap": 2.0}}

        out = prices.build(ctx, "aapl", 10, ["2025-09-27"], loader=loader, with_series=True)
        prices.build(ctx, "AAPL", 10, [], loader=loader)
        self.assertEqual(len(calls), 1)  # second call served from cache
        s = out["sources"]["S1"]
        self.assertEqual(s["class"], "secondary")
        self.assertEqual(s["url"], "https://finance.yahoo.com/quote/AAPL/history/")
        self.assertIn("yfinance 1.7.0", s["what"])
        self.assertEqual(out["price"]["src"], "S1")
        self.assertIn("2025-09-27", out["close_at"])
        self.assertIn("series", out)
        json.dumps(out)

    def test_missing_yfinance_gives_setup_hint(self):
        with mock.patch.dict(sys.modules, {"yfinance": None}):
            with self.assertRaises(common.FetchError) as cm:
                prices.load_yfinance("AAPL", 10)
        self.assertIn("Python 3.10+", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
