"""consensus.py: the block from a trimmed live yfinance response, nulls with reasons, unavailable block (no network)."""
import copy
import datetime as dt
import tempfile
import unittest

import common
import consensus
from tests import fx

RAW = fx.load("consensus_raw.json")
TODAY = dt.date(2026, 10, 14)


def ctx():
    return common.Ctx(tempfile.mkdtemp(), None, now=lambda: dt.datetime(2026, 10, 14, 15, tzinfo=dt.timezone.utc))


class ComputeTests(unittest.TestCase):
    def setUp(self):
        self.b = consensus.compute(RAW, TODAY)

    def test_targets_and_count(self):
        self.assertEqual(self.b["targets"], {"mean": 329.3759, "median": 340.0, "high": 405.0, "low": 215.0, "count": 39})
        self.assertTrue(self.b["available"])
        self.assertEqual(self.b["as_of"], "2026-10-14")

    def test_eps_estimates_and_year_ends(self):
        self.assertEqual(self.b["eps"], {"current_fy": {"estimate": 8.82006, "year_end": "2026-09-27"},
                                         "next_fy": {"estimate": 9.58335, "year_end": "2027-09-27"}})

    def test_growth_revenue_and_recommendations(self):
        self.assertEqual(self.b["growth"]["next_year"], 0.086)
        self.assertIsNone(self.b["growth"]["next_5y_per_year"])           # LTG is NaN for AAPL
        self.assertEqual(self.b["revenue_growth"]["current_fy"], 0.1491)
        self.assertAlmostEqual(self.b["revenue_growth"]["next_fy"], 0.1054, 4)
        self.assertEqual(self.b["recommendation_mean"], 2.20455)
        self.assertEqual(self.b["recommendation_count"], 44)               # 6 + 19 + 13 + 3 + 3 in the 0m row

    def test_revisions_use_the_30_day_counts_and_say_so(self):
        self.assertEqual(self.b["revisions_90d"], {"eps_next_fy_up": 4, "eps_next_fy_down": 3, "window_days": 30})
        self.assertIn("30-day", self.b["note"])

    def test_missing_fields_are_listed_with_reasons_and_note_records_attributes(self):
        self.assertEqual(list(self.b["missing"]), ["growth.next_5y_per_year"])
        self.assertIn("Yahoo lists no long-term growth", self.b["missing"]["growth.next_5y_per_year"])
        self.assertIn("analyst_price_targets, earnings_estimate", self.b["note"])
        self.assertIn("yfinance 1.7.0", self.b["note"])

    def test_partial_data_nulls_fields_not_the_block(self):
        raw = copy.deepcopy(RAW)
        for k in ("targets", "revenue", "revisions"):
            raw[k] = None
        raw["failed"] = {"targets": "analyst_price_targets: empty"}
        raw["info"]["recommendationMean"] = None
        b = consensus.compute(raw, TODAY)
        self.assertTrue(b["available"])
        self.assertIsNone(b["targets"]["mean"])
        self.assertIsNone(b["revisions_90d"])
        self.assertIn("targets.mean", b["missing"])
        self.assertIn("revisions_90d", b["missing"])
        self.assertEqual(b["recommendation_mean"], round((6 * 1 + 19 * 2 + 13 * 3 + 3 * 4 + 3 * 5) / 44, 4))  # fallback
        self.assertIn("unavailable: targets (analyst_price_targets: empty)", b["note"])

    def test_nothing_from_yfinance_is_an_unavailable_block(self):
        raw = {"version": "1.7.0", "worked": [], "failed": {"targets": "analyst_price_targets: empty"}, "info": {}}
        b = consensus.compute(raw, TODAY)
        self.assertEqual(set(b), {"available", "reason"})
        self.assertFalse(b["available"])
        self.assertIn("analyst_price_targets: empty", b["reason"])


class BuildTests(unittest.TestCase):
    def test_source_row_is_secondary_s12(self):
        out = consensus.build(ctx(), "aapl", loader=lambda t: RAW)
        self.assertEqual(out["consensus"]["src"], "S12")
        s = out["sources"]["S12"]
        self.assertEqual((s["class"], s["what"], s["url"]),
                         ("secondary", "Yahoo analyst data via yfinance", "https://finance.yahoo.com/quote/AAPL/analysis/"))

    def test_loader_failure_and_empty_have_no_source(self):
        def boom(t):
            raise common.FetchError("yfinance is not installed")
        out = consensus.build(ctx(), "AAPL", loader=boom)
        self.assertEqual(out["consensus"], {"available": False, "reason": "yfinance is not installed"})
        self.assertEqual(out["sources"], {})
        out = consensus.build(ctx(), "AAPL", loader=lambda t: {"worked": [], "failed": {}, "info": {}})
        self.assertFalse(out["consensus"]["available"])
        self.assertEqual(out["sources"], {})


class ProbeTests(unittest.TestCase):
    def test_probe_falls_back_to_the_next_attribute_name(self):
        class T:
            def get_analyst_price_targets(self):
                return {"mean": 1.0}
            analyst_price_targets = None
        v, name, err = consensus.probe(T(), "targets")
        self.assertEqual((v, name, err), ({"mean": 1.0}, "get_analyst_price_targets", None))
        v, name, err = consensus.probe(object(), "eps")
        self.assertIsNone(v)
        self.assertIn("empty", err)


if __name__ == "__main__":
    unittest.main()
