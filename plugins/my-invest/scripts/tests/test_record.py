import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import db  # noqa: E402
import record  # noqa: E402


def seed(c):
    sec = db.source(c, "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json", "primary", "SEC companyfacts AAPL")
    yh = db.source(c, "https://finance.yahoo.com/quote/AAPL/history/", "secondary", "Yahoo prices AAPL")
    db.upsert(c, "prices", [{"ticker": "AAPL", "date": "2026-01-02", "close": 200.0, "source_id": yh},
                            {"ticker": "AAPL", "date": "2026-07-06", "close": 240.0, "source_id": yh},
                            {"ticker": "SPY", "date": "2026-01-02", "close": 500.0, "source_id": yh},
                            {"ticker": "SPY", "date": "2026-07-06", "close": 525.0, "source_id": yh}])
    rid = record.open_run(c, "how about apple?", "stock", ["aapl"])
    return rid, sec, yh


class Confidence(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")
        self.rid, self.sec, self.yh = seed(self.c)

    def view(self, dim, stance, strength, evidence):
        db.insert(self.c, "views", {"run_id": self.rid, "subject": "AAPL", "dimension": dim, "stance": stance,
                                    "strength": strength, "sentence": "s", "evidence": evidence, "created_at": "t"})

    def test_no_views_gives_only_the_neutral_record_prior(self):
        c = record.confidence(self.c, self.rid, "AAPL", "buy")
        self.assertEqual((c["parts"]["evidence"]["score"], c["parts"]["agreement"]["score"], c["parts"]["record"]["score"]), (0, 0, 15))
        self.assertEqual(c["band"], "thin")
        self.assertIn("valuation", c["parts"]["evidence"]["reason"])

    def test_full_agreement_on_primary_sources(self):
        for d in record.REQUIRED_DIMENSIONS["stock"]:
            self.view(d, "for", 3, [self.sec])
        c = record.confidence(self.c, self.rid, "AAPL", "buy")
        self.assertEqual(c["parts"]["evidence"]["score"], 35)
        self.assertEqual(c["parts"]["agreement"]["score"], 35)
        self.assertEqual(c["total"], 85)
        self.assertEqual(c["band"], "strong evidence")

    def test_split_views_and_wide_dcf_lower_agreement(self):
        self.view("valuation", "for", 2, [self.sec])
        self.view("statistics", "against", 2, [self.yh])
        c = record.confidence(self.c, self.rid, "AAPL")
        self.assertEqual(c["parts"]["agreement"]["score"], 0)
        self.view("fundamentals", "for", 2, [self.sec])
        src = db.source(self.c, "derived://dcf.py?ticker=AAPL", "derived", "dcf")
        for sc, v in (("low", 100.0), ("base", 200.0), ("high", 400.0)):
            db.insert(self.c, "valuations", {"run_id": self.rid, "ticker": "AAPL", "asof": "d", "scenario": sc, "inputs": "{}",
                                             "value_per_share": v, "source_id": src, "created_at": "t"})
        c2 = record.confidence(self.c, self.rid, "AAPL")
        # stance (2+2-2)/6 = 0.33; spread 1.5 -> factor 0.6 -> 35*0.333*0.6 = 7
        self.assertEqual(c2["parts"]["agreement"]["score"], 7)
        self.assertIn("spread 150%", c2["parts"]["agreement"]["reason"])

    def test_record_part_uses_settled_calls_of_the_same_side(self):
        for outcome in ("right", "right", "wrong"):
            db.insert(self.c, "calls", {"run_id": self.rid, "ticker": "MSFT", "tier": "moderate", "action": "buy", "horizon_months": 6,
                                        "confidence": 50, "confidence_parts": "{}", "evidence": "[]", "made_at": "2025-01-01",
                                        "due_at": "2025-07-01", "outcome": outcome})
        score, reason = record.record_part(self.c, "add")
        self.assertEqual(score, round(30 * 4.5 / 8))
        self.assertIn("2 of 3", reason)
        self.assertEqual(record.record_part(self.c, "sell")[0], 15)


class Calls(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")
        self.rid, self.sec, self.yh = seed(self.c)
        self.row = {"ticker": "aapl", "tier": "moderate", "action": "buy", "horizon_months": 6, "confidence": 60,
                    "confidence_parts": {"evidence": 20}, "evidence": [self.sec], "limit_price": 195.0}

    def test_store_fills_prices_and_due_date(self):
        out = record.store_calls(self.c, self.rid, [self.row], today="2026-01-02")
        r = db.one(self.c, "SELECT * FROM calls")
        self.assertEqual((r["ticker"], r["price_at_call"], r["spy_at_call"], r["due_at"]), ("AAPL", 240.0, 525.0, "2026-07-02"))
        self.assertEqual(json.loads(r["confidence_parts"]), {"evidence": 20})
        self.assertEqual(out[0]["id"], r["id"])
        with self.assertRaises(ValueError):
            record.store_calls(self.c, self.rid, [{"ticker": "AAPL", "tier": "moderate"}])

    def test_add_months_handles_month_ends(self):
        import datetime as dt
        self.assertEqual(record.add_months(dt.date(2026, 8, 31), 6).isoformat(), "2027-02-28")
        self.assertEqual(record.add_months(dt.date(2026, 1, 15), 12).isoformat(), "2027-01-15")

    def test_score_settles_against_spy(self):
        # buy made at 200 (SPY 500) due 2026-07-02; realised 240 vs SPY 525 -> stock +20% beat SPY +5% -> right
        db.insert(self.c, "calls", dict(self.row, ticker="AAPL", run_id=self.rid, confidence_parts="{}", evidence="[]",
                                        price_at_call=200.0, spy_at_call=500.0, made_at="2026-01-02", due_at="2026-07-02"))
        db.insert(self.c, "calls", dict(self.row, ticker="AAPL", action="trim", run_id=self.rid, confidence_parts="{}", evidence="[]",
                                        price_at_call=200.0, spy_at_call=500.0, made_at="2026-01-02", due_at="2026-07-02"))
        db.insert(self.c, "calls", dict(self.row, ticker="MSFT", run_id=self.rid, confidence_parts="{}", evidence="[]",
                                        price_at_call=300.0, spy_at_call=500.0, made_at="2026-01-02", due_at="2026-07-02"))
        db.insert(self.c, "calls", dict(self.row, ticker="AAPL", run_id=self.rid, confidence_parts="{}", evidence="[]",
                                        price_at_call=200.0, spy_at_call=500.0, made_at="2026-06-02", due_at="2026-12-02"))
        settled, waiting = record.score_calls(self.c, today="2026-07-10")
        outcomes = {(s["ticker"], s.get("action")): s["outcome"] for s in settled}
        self.assertEqual(outcomes[("AAPL", "buy")], "right")
        self.assertEqual(outcomes[("AAPL", "trim")], "wrong")
        self.assertEqual(waiting[0]["need"], "yahoo.py prices MSFT")
        self.assertEqual(db.one(self.c, "SELECT COUNT(*) n FROM calls WHERE outcome = 'open'")["n"], 2)
        rows, summary = record.track_record(self.c, ticker="AAPL")
        self.assertEqual(rows[0]["ticker"], "AAPL")
        self.assertTrue(any(s["right_n"] == 1 for s in summary))


DRAFT = """# AAPL: hold, moderate
*As of 2026-07-06.*

## What to do
| level | action | limit | believe |
|---|---|---|---|
| moderate | hold | $230 [S2] | growth holds at 8% [S1] |

## Why
- Revenue grew 8% [S1].

## Supporting analysis
Price $240 [S2].

## The case against
- Multiple is high [S2].

## Track record
No settled calls yet.

## Not verified
- Buyback pace.
"""


class Report(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")
        self.rid, self.sec, self.yh = seed(self.c)
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_lint_accepts_cited_draft_and_rejects_bare_figures(self):
        problems, used = record.lint(DRAFT, {1, 2})
        self.assertEqual(problems, [])
        self.assertEqual(used, {1, 2})
        bad = DRAFT.replace("Price $240 [S2].", "Price $240.").replace("## Why", "## Reasons") + "\nSee [S9].\n"
        problems, _ = record.lint(bad, {1, 2})
        self.assertTrue(any("without a source" in p for p in problems))
        self.assertTrue(any("missing section: Why" in p for p in problems))
        self.assertTrue(any("unknown source S9" in p for p in problems))

    def test_lint_ignores_code_blocks_quotes_and_table_rules(self):
        text = DRAFT + "\n```\nx = 42\n```\n> 99 problems\n"
        self.assertEqual(record.lint(text, {1, 2})[0], [])

    def test_finalise_links_markers_and_writes_the_report(self):
        rel, problems = record.finalise(self.c, self.tmp.name, self.rid, DRAFT, today="2026-07-06")
        self.assertEqual(problems, [])
        self.assertEqual(rel, os.path.join("data", "reports", "2026-07-06-stock-aapl.html"))
        with open(os.path.join(self.tmp.name, rel)) as f:
            text = f.read()
        self.assertTrue(text.startswith("<!doctype html>"))
        self.assertIn('<a href="https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json">S1</a>', text)
        self.assertIn("<h2>Sources</h2>", text)
        self.assertIn("S2: Yahoo prices AAPL (secondary)", text)
        self.assertIn("<table><thead><tr><th>level</th>", text)
        self.assertIn("not licensed financial advice", text)
        self.assertIn("prefers-color-scheme:dark", text)
        self.assertNotIn("<svg", text)  # only two price days stored: no chart
        run = db.one(self.c, "SELECT status, report_path FROM runs WHERE id = ?", (self.rid,))
        self.assertEqual((run["status"], run["report_path"]), ("answered", rel))

    def test_page_gets_a_price_chart_when_enough_prices_exist(self):
        import datetime as dt
        day = dt.date(2026, 1, 5)
        rows = []
        for i in range(260):
            rows.append({"ticker": "AAPL", "date": (day + dt.timedelta(days=i)).isoformat(), "close": 200 + i * 0.1, "source_id": self.yh})
        db.upsert(self.c, "prices", rows)
        svg = record.price_svg(self.c, "AAPL", years=50)
        self.assertIn("<polyline", svg)
        self.assertIn("200-day average", svg)
        self.assertIn("261 trading days stored", svg)
        html = record.page("t", record.md_to_html(DRAFT), [svg])
        self.assertLess(html.index("Price history"), html.index("<h2>What to do</h2>"))

    def test_md_to_html_covers_the_subset(self):
        h = record.md_to_html("# T\n\npara **b** `c` [x](http://u)\n\n- a\n- b\n\n| h |\n|---|\n| 1 |\n\n> q\n\n```\n<x>\n```\n")
        for frag in ("<h1>T</h1>", "<strong>b</strong>", "<code>c</code>", '<a href="http://u">x</a>', "<ul>\n<li>a</li>\n<li>b</li>\n</ul>",
                     "<th>h</th>", "<td>1</td>", "<blockquote>q</blockquote>", "&lt;x&gt;"):
            self.assertIn(frag, h)

    def test_finalise_refuses_a_draft_with_problems(self):
        rel, problems = record.finalise(self.c, self.tmp.name, self.rid, DRAFT.replace("[S1]", ""), today="2026-07-06")
        self.assertIsNone(rel)
        self.assertTrue(problems)
        self.assertEqual(db.one(self.c, "SELECT status FROM runs")["status"], "open")


if __name__ == "__main__":
    unittest.main()
