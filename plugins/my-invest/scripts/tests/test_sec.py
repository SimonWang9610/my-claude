import contextlib
import datetime as dt
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import db  # noqa: E402
import sec  # noqa: E402

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "companyfacts_small.json")
TODAY = dt.date(2026, 11, 3)


def load_fixture():
    with open(FIX) as f:
        return json.load(f)


class Facts(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")
        self.sid = db.source(self.c, "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json", "primary", "SEC")
        self.counts, self.latest, self.missing = sec.store_facts(self.c, "AAPL", load_fixture(), 5, self.sid, TODAY)

    def row(self, concept, end, start=""):
        return db.one(self.c, "SELECT * FROM fundamentals WHERE concept = ? AND period_end = ? AND period_start = ?",
                      (concept, end, start))

    def test_restatement_wins(self):
        r = self.row("Revenues", "2023-09-30", "2022-09-25")
        self.assertEqual(r["value"], 383286000000.0)
        self.assertEqual(r["filed"], "2024-11-01")
        self.assertEqual(r["accession"], "0000320193-24-000123")
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM fundamentals WHERE concept = 'Revenues' AND period_end = '2023-09-30'").fetchone()[0], 1)

    def test_days_and_instant_period_start(self):
        self.assertEqual(self.row("Revenues", "2024-09-28", "2023-10-01")["days"], 363)
        self.assertEqual(self.row("Revenues", "2024-09-28", "2024-06-30")["days"], 90)
        a = self.row("Assets", "2024-09-28")
        self.assertEqual(a["period_start"], "")
        self.assertIsNone(a["days"])
        self.assertEqual(a["frame"], "CY2024Q3I")

    def test_years_window_but_latest_filing_always_kept(self):
        self.assertIsNone(self.row("Revenues", "2015-09-26", "2014-09-28"))  # old, from an old filing
        self.assertIsNotNone(self.row("Revenues", "2016-09-24", "2015-09-27"))  # old, but in the latest filing

    def test_units_kept_and_counts(self):
        self.assertEqual(self.row("EarningsPerShareDiluted", "2024-09-28", "2023-10-01")["unit"], "USD/shares")
        self.assertEqual(self.row("EntityCommonStockSharesOutstanding", "2024-10-18")["unit"], "shares")
        self.assertEqual(self.counts["Revenues"], 4)
        self.assertEqual((self.latest["fy"], self.latest["form"]), (2024, "10-K"))
        self.assertIn("NetIncomeLoss", self.missing)
        self.assertNotIn("Assets", self.missing)

    def test_annual_view_and_md_rows(self):
        recs = sec.latest_annual(self.c, "AAPL")
        by = {(r["concept"], r["unit"]): r for r in recs}
        self.assertEqual(by[("Revenues", "USD")]["period_end"], "2024-09-28")
        self.assertEqual(by[("Revenues", "USD")]["value"], 391035000000.0)
        self.assertIn(("Assets", "USD"), by)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved = dict(sec._TICKERS)
        sec._TICKERS.clear()
        sec._TICKERS.update({"AAPL": "0000320193"})

    def tearDown(self):
        sec._TICKERS.clear()
        sec._TICKERS.update(self.saved)
        self.tmp.cleanup()

    def run_sec(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = sec.run(list(args) + ["--project", self.tmp.name])
        return code, json.loads(buf.getvalue())

    def test_not_a_registrant_fails(self):
        code, out = self.run_sec("QQQ")
        self.assertEqual(code, 1)
        self.assertEqual(out["error"], "QQQ is not an SEC registrant (a fund?); use yahoo.py profile")

    def test_run_stores_facts_and_security(self):
        orig = sec.common.get_json
        sec.common.get_json = lambda url, ua=None, timeout=30: load_fixture()
        try:
            code, out = self.run_sec("aapl")
        finally:
            sec.common.get_json = orig
        self.assertEqual(code, 0, out)
        self.assertEqual(out["ticker"], "AAPL")
        self.assertEqual(out["latest_fy"], 2024)
        conn = db.connect(self.tmp.name)
        s = db.one(conn, "SELECT * FROM securities WHERE ticker = 'AAPL'")
        self.assertEqual((s["cik"], s["kind"], s["name"]), ("0000320193", "stock", "Apple Inc."))
        self.assertEqual(db.one(conn, "SELECT url FROM sources WHERE id = ?", (out["source_id"],))["url"],
                         "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json")


if __name__ == "__main__":
    unittest.main()
