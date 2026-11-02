import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import common
import filing
from tests import fx

LINES = filing.html_to_lines(fx.text("tenk_synthetic.html"))


class TextTests(unittest.TestCase):
    def test_conversion_rules(self):
        text = "\n".join(LINES)
        self.assertNotIn("HIDDEN-XBRL-JUNK", text)
        self.assertNotIn("color:red", text)
        self.assertIn("Item 1. | Business | 3", LINES)             # table cells joined by " | "
        self.assertIn("Cash | $1,234)", LINES)                      # lone $ / ) cells merged
        self.assertIn("Debt | 56", LINES)
        self.assertIn("Item 1. Business", LINES)                    # inline spans stay on one line, nbsp collapsed
        self.assertIn("Revenue grew.", LINES)                       # <br/> breaks lines
        self.assertIn("Costs fell.", LINES)
        self.assertIn("Item 7. | Management\u2019s Discussion and Analysis | 20", LINES)


class SectionTests(unittest.TestCase):
    def setUp(self):
        self.secs = filing.split_sections(LINES)

    def text(self, name):
        s, e = self.secs[name]
        return "\n".join(LINES[s:e])

    def test_toc_skipped_body_sections_found(self):
        self.assertTrue(self.text("item-1").startswith("Item 1. Business"))
        self.assertIn("We sell widgets", self.text("item-1"))
        self.assertNotIn("| 3", self.text("item-1"))
        self.assertIn("material weakness could arise", self.text("item-1a"))
        self.assertNotIn("PART II", self.text("item-1a"))            # Part heading ends the section
        self.assertIn("Revenue grew.", self.text("item-7"))
        self.assertNotIn("Controls and Procedures | 60", "\n".join(self.text(n) for n in self.secs if n != "item-9a"))

    def test_item_9a_with_title_on_next_line(self):
        t = self.text("item-9a")
        self.assertIn("Management concluded controls were effective", t)
        self.assertNotIn("Other Information", t)

    def test_auditor_report_bounded_by_balance_sheet(self):
        t = self.text("auditor")
        self.assertTrue(t.startswith("Report of Independent Registered Public Accounting Firm"))
        self.assertIn("Opinion on the Financial Statements", t)
        self.assertNotIn("CONSOLIDATED BALANCE SHEETS", t)

    def test_notes_start_at_note_1(self):
        t = self.text("notes")
        self.assertTrue(t.startswith("Notes to Consolidated Financial Statements"))
        self.assertIn("Revenue is recognized when shipped", t)
        self.assertNotIn("Changes in and Disagreements", t)

    def test_pick_filing(self):
        sub = {"filings": {"recent": {"accessionNumber": ["a-1", "a-2", "a-3"], "form": ["8-K", "10-K", "10-K"],
                                      "filingDate": ["2026-01-01", "2024-11-01", "2025-11-01"],
                                      "reportDate": ["", "2024-09-28", "2025-09-27"],
                                      "primaryDocument": ["x.htm", "k24.htm", "k25.htm"]}}}
        self.assertEqual(filing.pick_filing(sub, "10-K")["doc"], "k25.htm")
        self.assertEqual(filing.pick_filing(sub, "10-K", "a-2")["period"], "2024-09-28")
        with self.assertRaises(filing.FetchError):
            filing.pick_filing(sub, "10-Q")


class WriteAndGrepTests(unittest.TestCase):
    def test_write_index_and_grep_with_sections(self):
        d = os.path.join(tempfile.mkdtemp(), "0000000001-25-000001")
        meta = {"form": "10-K", "filed": "2025-10-31", "period": "2025-09-27", "accn": "0000000001-25-000001"}
        idx = filing.write_all(d, "http://u", meta, "2026-10-14T00:00:00Z", LINES, filing.split_sections(LINES),
                               {"1", "1A", "7", "7A", "8", "9A", "auditor"})
        for f in ("full.txt", "item-1.txt", "item-1a.txt", "item-7.txt", "item-8.txt", "item-9a.txt", "auditor.txt",
                  "notes.txt", "index.json"):
            self.assertTrue(os.path.exists(os.path.join(d, f)), f)
        self.assertFalse(os.path.exists(os.path.join(d, "item-9b.txt")))  # not requested
        loaded = json.load(open(os.path.join(d, "index.json")))
        self.assertEqual({k for k in loaded if k != "sections"}, {"url", "form", "filed", "period", "accn", "retrieved", "chars"})
        a = loaded["sections"]["auditor"]
        self.assertEqual(set(a), {"chars", "head", "lines", "file"})
        self.assertLessEqual(len(a["head"]), 120)
        self.assertEqual(filing.manifest(idx, d)["sections"]["item-9a"], loaded["sections"]["item-9a"]["chars"])
        hits = filing.grep(d, loaded, "material weakness")
        by_text = {h["text"][:20]: h["sections"] for h in hits}
        self.assertEqual(len(hits), 3)
        self.assertIn(["item-1a"], by_text.values())
        self.assertIn(["item-8", "auditor"], by_text.values())
        self.assertIn(["item-9a"], by_text.values())
        h = hits[0]
        self.assertEqual(set(h), {"line", "sections", "before", "text", "after"})
        self.assertTrue(h["before"] and h["after"])


class StorePathTests(unittest.TestCase):
    def test_filing_lands_under_store_stocks_ticker(self):
        proj = tempfile.mkdtemp()
        sub = {"filings": {"recent": {"accessionNumber": ["0000000001-25-000001"], "form": ["10-K"],
                                      "filingDate": ["2025-11-01"], "reportDate": ["2025-09-27"],
                                      "primaryDocument": ["k.htm"]}}}
        body = fx.text("tenk_synthetic.html").encode()
        with mock.patch.object(filing.edgar, "resolve_cik", return_value=(1, "T", "t")), \
                mock.patch.object(common.Ctx, "get_json", return_value=(sub, "t")), \
                mock.patch.object(common.Ctx, "get", return_value=(body, "2026-10-14T00:00:00Z")), \
                redirect_stdout(io.StringIO()) as out:
            filing.run(["t", "--data", tempfile.mkdtemp(), "--project", proj, "--ua", "a b@c.d"])
        folder = os.path.join(proj, "data", "stocks", "T", "filings", "0000000001-25-000001")
        self.assertTrue(os.path.exists(os.path.join(folder, "index.json")))
        self.assertEqual(json.loads(out.getvalue())["dir"], folder)


if __name__ == "__main__":
    unittest.main()
