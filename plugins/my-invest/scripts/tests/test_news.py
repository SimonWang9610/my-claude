import datetime as dt
import tempfile
import unittest
from unittest import mock

import common
import news
from tests import fx

TODAY = dt.date(2026, 10, 14)
SUB = fx.load("submissions_aapl.json")


class FilingTests(unittest.TestCase):
    def test_url_construction(self):
        self.assertEqual(news.filing_url(320193, "0000320193-25-000079", "aapl-20250927.htm"),
                         "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm")

    def test_window_and_default_forms(self):
        out, _ = news.recent_filings(SUB, 320193, 120, TODAY)
        self.assertNotIn("4", {f["form"] for f in out})            # Form 4 is noise by default
        self.assertTrue(all(f["filed"] >= "2026-06-16" for f in out))
        self.assertEqual([f["form"] for f in out], ["10-Q", "8-K"])  # 2026-07-31, 2026-07-30
        first = out[0]
        self.assertTrue(first["url"].startswith("https://www.sec.gov/Archives/edgar/data/320193/"))
        self.assertEqual(set(first), {"form", "filed", "items", "url", "src"})

    def test_wide_window_includes_annual_and_proxy(self):
        out, _ = news.recent_filings(SUB, 320193, 1095, TODAY)
        self.assertEqual({"10-K", "10-Q", "8-K", "DEF 14A"}, {f["form"] for f in out})
        self.assertEqual([f["filed"] for f in out], sorted([f["filed"] for f in out], reverse=True))

    def test_8k_item_filter(self):
        out, _ = news.recent_filings(SUB, 320193, 1095, TODAY, items=["5.02"])
        self.assertEqual({f["form"] for f in out}, {"8-K"})
        self.assertEqual([f["filed"] for f in out], ["2026-04-20", "2026-01-02"])
        out, _ = news.recent_filings(SUB, 320193, 1095, TODAY, items=["2.02", "5.07"])
        self.assertEqual(len(out), 4)

    def test_forms_override(self):
        out, _ = news.recent_filings(SUB, 320193, 30, TODAY, forms=["4"])
        self.assertEqual({f["form"] for f in out}, {"4"})
        out, _ = news.recent_filings(SUB, 320193, 30, TODAY, forms="all")
        self.assertIn("4", {f["form"] for f in out})

    def test_fts_hits_filtered_by_window(self):
        obj = {"hits": {"hits": [
            {"_id": "0000320193-26-000010:ex991.htm",
             "_source": {"ciks": ["0000320193"], "file_date": "2026-04-30", "form": "8-K", "items": ["2.02", "9.01"],
                         "file_type": "EX-99.1"}},
            {"_id": "0000320193-18-000067:old.htm",
             "_source": {"ciks": ["0000320193"], "file_date": "2018-05-01", "form": "8-K", "items": ["2.02"]}}]}}
        hits = news.fts_hits(obj, "2026-01-01")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["url"], "https://www.sec.gov/Archives/edgar/data/320193/000032019326000010/ex991.htm")
        self.assertEqual(hits[0]["items"], "2.02,9.01")

    def test_rss_parse(self):
        xml = (b"<rss><channel><item><title>Apple up</title><link>http://n/1</link>"
               b"<pubDate>Tue, 13 Oct 2026 10:00:00 GMT</pubDate><source>Reuters</source></item></channel></rss>")
        self.assertEqual(news.parse_rss(xml), [{"title": "Apple up", "url": "http://n/1",
                                                "published": "Tue, 13 Oct 2026 10:00:00 GMT", "outlet": "Reuters"}])

    def test_build_tolerates_rss_failure(self):
        ctx = common.Ctx(tempfile.mkdtemp(), "ua a@b.c", now=lambda: dt.datetime(2026, 10, 14, tzinfo=dt.timezone.utc))

        def get_json(url, source, **kw):
            if url.endswith("company_tickers.json"):
                return fx.load("company_tickers_subset.json"), "2026-10-14T00:00:00Z"
            return SUB, "2026-10-14T00:00:00Z"

        with mock.patch.object(ctx, "get_json", side_effect=get_json), \
                mock.patch.object(ctx, "get", side_effect=common.FetchError("HTTP 503")):
            out = news.build(ctx, "AAPL", since=120, rss=True)
        self.assertEqual(out["rss"], [])
        self.assertIn("503", out["rss_error"])
        self.assertEqual(len(out["filings"]), 2)
        self.assertEqual(out["filings"][0]["src"], "S1")


    def test_build_with_shared_submissions_needs_no_cik_lookup(self):
        ctx = common.Ctx(tempfile.mkdtemp(), "ua a@b.c", now=lambda: dt.datetime(2026, 10, 14, tzinfo=dt.timezone.utc))
        with mock.patch.object(ctx, "get_json", side_effect=AssertionError("no fetch expected")):
            out = news.build(ctx, "AAPL", since=120, sub=(SUB, "2026-10-14T00:00:00Z"))
        self.assertEqual(out["cik"], "0000320193")
        self.assertEqual(len(out["filings"]), 2)


if __name__ == "__main__":
    unittest.main()
