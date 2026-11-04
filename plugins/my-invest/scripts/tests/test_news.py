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
import news  # noqa: E402

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "news_two.xml")
NOW = dt.datetime(2025, 11, 4, 12, 0, tzinfo=dt.timezone.utc)


def rss_text():
    with open(FIX) as f:
        return f.read()


class Parsing(unittest.TestCase):
    def test_items_dates_sources_and_summaries(self):
        items = news.parse_rss(rss_text())
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["published"], "2025-10-31T21:05:00Z")
        self.assertEqual(items[1]["published"], "2025-11-03T14:30:00Z")
        self.assertEqual(items[0]["source"], "Reuters")
        self.assertEqual(items[0]["summary"], "Apple reports record September quarter Reuters")
        self.assertEqual(items[1]["url"], "https://news.google.com/rss/articles/BBBB?oc=5")

    def test_select_window_order_and_cap(self):
        items = news.parse_rss(rss_text())
        kept = news.select_items(items, 30, 10, NOW)
        self.assertEqual([i["source"] for i in kept], ["The Motley Fool", "Reuters"])  # newest first
        self.assertEqual(len(news.select_items(items, 30, 1, NOW)), 1)
        self.assertEqual([i["source"] for i in news.select_items(items, 2, 10, NOW)], ["The Motley Fool"])
        self.assertEqual(news.iso_utc("garbage"), None)

    def test_query_defaults_and_url(self):
        c = db.connect(path=":memory:")
        self.assertEqual(news.default_query(c, "AAPL"), "AAPL stock")
        sid = db.source(c, "https://x", "secondary")
        db.upsert(c, "securities", [{"ticker": "AAPL", "name": "Apple Inc.", "updated_at": "t", "source_id": sid}])
        self.assertEqual(news.default_query(c, "AAPL"), '"Apple Inc." OR AAPL stock')
        self.assertEqual(news.default_query(c, "sector:semiconductors"), "semiconductors industry")
        self.assertEqual(news.default_query(c, "market"), "stock market")
        self.assertEqual(news.normalise_subject("Sector:Banks"), "sector:Banks")
        self.assertEqual(news.normalise_subject("aapl"), "AAPL")
        self.assertEqual(news.rss_url("AAPL stock"), "https://news.google.com/rss/search?q=AAPL+stock&hl=en-US&gl=US&ceid=US%3Aen")


class Fetch(unittest.TestCase):
    def test_fetch_stores_by_url_and_keeps_lean(self):
        c = db.connect(path=":memory:")
        saved = news.common.utcnow
        news.common.utcnow = lambda: NOW
        try:
            stored, url = news.fetch(c, "AAPL", "AAPL stock", 30, 10, text=rss_text())
            self.assertEqual(len(stored), 2)
            self.assertTrue(all(r["id"] for r in stored))
            news.set_lean(c, stored[0]["id"], 0.5, "analyst run 1", "record quarter")
            again, _ = news.fetch(c, "AAPL", "AAPL stock", 30, 10, text=rss_text())
        finally:
            news.common.utcnow = saved
        self.assertEqual(c.execute("SELECT COUNT(*) FROM news").fetchone()[0], 2)
        self.assertEqual(again[0]["lean"], 0.5)  # a refetch does not clear the analyst's lean


class Lean(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        c = db.connect(self.tmp.name)
        db.insert(c, "news", {"subject": "AAPL", "url": "https://a", "title": "t", "fetched_at": "now"})
        c.close()

    def tearDown(self):
        self.tmp.cleanup()

    def run_news(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = news.run(list(args) + ["--project", self.tmp.name])
        return code, json.loads(buf.getvalue())

    def test_lean_sets_fields(self):
        code, out = self.run_news("lean", "1", "-0.5", "--by", "analyst run 3", "--note", "weak demand")
        self.assertEqual(code, 0, out)
        r = db.one(db.connect(self.tmp.name), "SELECT lean, lean_by, lean_note FROM news WHERE id = 1")
        self.assertEqual((r["lean"], r["lean_by"], r["lean_note"]), (-0.5, "analyst run 3", "weak demand"))

    def test_lean_rejects_unknown_id_and_out_of_range(self):
        code, out = self.run_news("lean", "99", "0.5", "--by", "x")
        self.assertEqual(code, 1)
        self.assertIn("no news item with id 99", out["error"])
        code, out = self.run_news("lean", "1", "1.5", "--by", "x")
        self.assertEqual(code, 1)
        self.assertIn("between -1 and 1", out["error"])


if __name__ == "__main__":
    unittest.main()
