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
import fred  # noqa: E402

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "fredgraph_dgs10.csv")
TODAY = dt.date(2026, 11, 3)


def csv_text():
    with open(FIX) as f:
        return f.read()


class Parsing(unittest.TestCase):
    def test_csv_drops_missing_and_header(self):
        obs = fred.parse_csv(csv_text())
        self.assertEqual(obs, [("2015-01-02", 2.12), ("2024-01-02", 3.95), ("2024-01-03", 3.91), ("2025-01-02", 4.57)])

    def test_csv_old_header_name(self):
        self.assertEqual(fred.parse_csv("DATE,UNRATE\n2024-01-01,3.7\n"), [("2024-01-01", 3.7)])

    def test_json_drops_missing(self):
        data = {"observations": [{"date": "2024-01-02", "value": "3.95"}, {"date": "2024-01-15", "value": "."}]}
        self.assertEqual(fred.parse_json(data), [("2024-01-02", 3.95)])

    def test_url_choice(self):
        self.assertEqual(fred.series_url("DGS10", ""), "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10")
        self.assertIn("api_key=SECRET", fred.series_url("DGS10", "SECRET"))


class Store(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")

    def test_store_window_and_metadata(self):
        sid, n = fred.store(self.c, "DGS10", fred.series_url("DGS10", ""), fred.parse_csv(csv_text()), 5, TODAY)
        self.assertEqual(n, 3)  # 2015 is outside five years
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM macro").fetchone()[0], 3)
        m = db.one(self.c, "SELECT * FROM macro_series")
        self.assertEqual((m["title"], m["units"], m["frequency"], m["source_id"]),
                         ("10-Year Treasury constant maturity yield", "percent", "daily", sid))

    def test_api_key_redacted_in_stored_url(self):
        url = fred.series_url("UNRATE", "SECRETKEY")
        sid, _ = fred.store(self.c, "UNRATE", url, [("2026-01-01", 4.1)], 5, TODAY)
        stored = db.one(self.c, "SELECT url FROM sources WHERE id = ?", (sid,))["url"]
        self.assertNotIn("SECRETKEY", stored)
        self.assertIn("api_key=REDACTED", stored)

    def test_summary_year_ago_and_change(self):
        fred.store(self.c, "DGS10", fred.series_url("DGS10", ""), fred.parse_csv(csv_text()), 5, TODAY)
        s = fred.summary(self.c, ["DGS10"])[0]
        self.assertEqual((s["latest_date"], s["latest"], s["year_ago"]), ("2025-01-02", 4.57, 3.91))
        self.assertAlmostEqual(s["change"], 0.66)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_default_series_capped_and_failures_reported(self):
        def fake_get_text(url, ua=None, timeout=30):
            if "VIXCLS" in url:
                raise fred.common.FetchError("HTTP 500")
            return csv_text()
        saved = fred.common.get_text
        fred.common.get_text = fake_get_text
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                code = fred.run(["--project", self.tmp.name])
        finally:
            fred.common.get_text = saved
        out = json.loads(buf.getvalue())
        self.assertEqual(code, 0, out)
        self.assertEqual(len(out["series"]), 7)
        self.assertEqual(list(out["failed"]), ["VIXCLS"])
        self.assertEqual(out["endpoint"], "csv")


if __name__ == "__main__":
    unittest.main()
