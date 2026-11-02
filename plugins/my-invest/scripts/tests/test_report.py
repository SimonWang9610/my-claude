"""report.py renders a lint-clean dossier, appends history and prints the chat answer."""
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import lint  # noqa: E402
import metrics  # noqa: E402
import report  # noqa: E402
import score  # noqa: E402

FIX = os.path.join(HERE, "fixtures")
Q = "Is AAPL worth buying for ten years at $343?"


def build(root, narrative=True, research=True, holdings=None, industry=False):
    d = os.path.join(root, "AAPL")
    for sub in ("facts", "research", "history"):
        os.makedirs(os.path.join(d, sub))
    shutil.copy(os.path.join(FIX, "score_aapl_facts.json"), os.path.join(d, "facts", "facts.json"))
    shutil.copy(os.path.join(FIX, "score_evidence.json"), os.path.join(d, "research", "evidence.json"))
    if research:
        shutil.copy(os.path.join(FIX, "report_research.md"), os.path.join(d, "research", "research.md"))
    if industry:
        shutil.copy(os.path.join(FIX, "report_industry.md"), os.path.join(d, "research", "industry.md"))
    if narrative:
        shutil.copy(os.path.join(FIX, "report_narrative.md"), os.path.join(d, "history", "2026-10-14-0900.md"))
    if holdings:
        with open(os.path.join(d, "facts", "holdings.json"), "w", encoding="utf-8") as fh:
            json.dump(holdings, fh)
    return d


def quiet(fn, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(argv)
    return buf.getvalue()


def lint_main(argv):
    with contextlib.redirect_stdout(io.StringIO()):
        return lint.main(argv)


def text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class Report(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def render(self, d, *extra, score_args=()):
        quiet(score.main, [d] + list(score_args))
        return quiet(report.main, [d, "--question", Q, "--lens", "long"] + list(extra))

    def test_dossier_lints_clean_with_all_sections(self):
        d = build(self.tmp)
        out = json.loads(self.render(d))
        self.assertEqual(out["lint"], "OK")
        doc = text(os.path.join(d, "reports", "dossier.md"))
        self.assertEqual(lint.lint_text("dossier.md", doc), [])
        heads = [l for l in doc.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["## The short answer", "## Price outlook", "## Track record", "## Answer", "## Thesis",
                                 "## Why", "## The case against", "## What the news says",
                                 "## Compared with similar companies", "## How the industry is doing",
                                 "## Strengths and weaknesses", "## Options context", "## Business and moat",
                                 "## Management", "## Market trend", "## Facts", "## Scorecard — as of 2026-10-14",
                                 "## Risk evidence", "## News and posts", "## What could not be verified",
                                 "## Open questions", "## History", "## Evidence log"])
        self.assertTrue(doc.rstrip().endswith(lint.DISCLAIMER))
        self.assertIn("| 4 Valuation and margin of safety | 0/20 |", doc)
        self.assertIn("\n\nImplied growth at price 25.43% vs base scenario 10% [S60].", doc)
        self.assertIn("78/100 = 0.5 × coverage 0.9333", doc)
        for sid in ("| S60 | derived |", "| S61 | derived |", "| S62 | derived |", "| S100 | primary |", "| S114 |"):
            self.assertIn(sid, doc)
        self.assertTrue(os.path.exists(out["snapshot"]))
        self.assertRegex(out["snapshot"], r"/reports/\d{4}-\d{2}-\d{2}-\d{4}\.md$")
        self.assertEqual(doc.count("- 2.3 — current ratio"), 1)  # open questions listed once

    def test_history_appends_and_reports_change(self):
        d = build(self.tmp)
        self.render(d)
        self.render(d, score_args=("--mos", "0.5"))
        lines = text(os.path.join(d, "history", "log.md")).splitlines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].endswith("changed: first analysis"))
        self.assertIn("changed: zones buy below $103.97 / sell above $175.77 → buy below $74.2", lines[1])
        self.render(d, score_args=("--mos", "0.5"))
        self.assertIn("no change in tier, score, stance or zones", text(os.path.join(d, "history", "log.md")).splitlines()[2])
        doc = text(os.path.join(d, "reports", "dossier.md"))
        hist = doc.split("## History\n")[1].split("\n\n")[0].splitlines()
        self.assertEqual(len(hist), 3)
        self.assertIn("no change", hist[0])  # newest first

    def test_chat_beginner_shape(self):
        d = build(self.tmp)
        out = self.render(d, "--chat")
        heads = [l for l in out.splitlines() if l.startswith("#")]
        self.assertTrue(heads[0].startswith("## AAPL — the price is far above what the model thinks a share is worth"))
        self.assertEqual(heads[1:8], ["### Answer", "### Summary", "### Why", "### Risks: the case against",
                                      "### Track record", "### What to watch", "### Not verified"])
        self.assertEqual(heads[-2:], ["### Words used here", "### Sources"])
        self.assertIn("### News, what it means", out)                             # wants unset: the news slot stays
        self.assertNotIn("## Details", out)                                        # the detail lives in the dossier
        self.assertIn("*As of 2026-10-14. Every horizon below is counted from that date.*", out)
        self.assertIn("| Price today (2026-10-14) | $343.87 [S3] |", out)
        self.assertIn("| Confidence | 78/100 (solid) — what lowers it", out)
        self.assertIn("- **If you hold it:** ", out)
        self.assertIn("- **If you want to buy:** ", out)
        self.assertIn("| 2026-07-30 | Fiscal Q3 revenue $109.4 billion, up 16% [S103] |", out)   # narrative news slot
        self.assertIn("- a going-concern paragraph (deal-breaker check G4)", out)              # what would break it
        self.assertIn("- **confidence band** —", out)
        self.assertRegex(out, r"- S3 — [^\n]*\(secondary\): <https://finance\.yahoo\.com/quote/AAPL/history/>")
        self.assertRegex(out, r"- S60 — [^\n]*\(a script's arithmetic; its inputs are the sources above\): <file://")
        self.assertIn("- S1 — ", out)                                              # a derived row's raw inputs are listed
        self.assertNotIn("](file://", out.split("### Sources")[0].split("Files:")[0])   # chat markers stay plain
        self.assertEqual(out.rstrip().splitlines()[-1], "> " + lint.DISCLAIMER)
        words = out.split("### Words used here\n")[1].split("\n\n")[0]
        for term in ("call", "put", "premium", "strike"):                           # no options section, no options terms
            self.assertNotIn("- **%s** —" % term, words)
        self.assertNotIn("### Your shares", out)
        self.assertIn("### Compared with similar companies", out)         # the narrative's peers slot, two lines at most
        doc = text(os.path.join(d, "reports", "dossier.md"))
        self.assertIn("`buy zone ◄── $103.97 ──── $148.53 fair ──── $175.77 ──► sell zone      ▲ you are here $343.87` "
                      "[S60, S3]", doc)
    def test_chat_shares_peers_options_and_fallbacks(self):
        hold = {"ticker": "AAPL", "positions": [{"account": "TFSA", "shares": 120.0, "avg_cost": 150.0}]}
        d = build(self.tmp, narrative=False, holdings=hold)
        shutil.copy(os.path.join(FIX, "chart_holdings_tables.json"), os.path.join(d, "facts", "holdings_tables.json"))
        peers = {"ticker": "AAPL", "rows": [{"key": "roic", "label": "ROIC, latest FY"},
                                            {"key": "debt_years", "label": "Debt years"}],
                 "columns": [{"ticker": "AAPL", "status": "ok", "src": "S80", "rows": {"roic": {"value": 0.8228},
                                                                                     "debt_years": {"value": 0.56}}},
                             {"ticker": "MSFT", "status": "ok", "src": "S81", "rows": {"roic": {"value": None},
                                                                                     "debt_years": {"value": 0.14}}},
                             {"ticker": "GOOG", "status": "no data", "src": None, "reason": "no facts", "rows": None}],
                 "sources": {k: {"class": "derived", "what": "compare.py", "url": "https://example.com/" + k,
                                 "as_of": "2026-10-14", "retrieved": "2026-10-14"} for k in ("S80", "S81")}}
        with open(os.path.join(d, "facts", "peers.json"), "w", encoding="utf-8") as fh:
            json.dump(peers, fh)
        out = self.render(d, "--chat")
        self.assertIn("- **If you hold it:** trim or sell — because the outlook could not be computed (", out)
        self.assertIn("### Your shares\n| Account | Shares | You paid | Worth now | Gain | Tax if sold now | You keep | |", out)
        self.assertIn("| TFSA | 100 | $20.00 | $3,150 | +$1,150 | no evidence | no evidence | [S3, S99] |", out)
        self.assertRegex(out, r"\| Your shares \| worth \$[\d,]+, gain [+-]\$[\d,]+ \(TFSA\) \[S3, S61\] \|")
        self.assertNotIn("### Compared with similar companies", out)             # no narrative slot: the table is in the dossier
        news = out.split("### News, what it means\n")[1].split("\n\n")[0].splitlines()
        self.assertTrue(2 < len(news) <= 7 and all(r.endswith("| — |") for r in news[2:]))  # research fallback
        doc = text(os.path.join(d, "reports", "dossier.md"))
        self.assertIn("| | AAPL | MSFT | |", doc)
        self.assertIn("| Return on the money invested (ROIC) | 82.3% | no evidence | [S80, S81] |", doc)
        self.assertIn("| Debt vs that cash (years to repay) | 0.6 years | 0.1 years | [S80, S81] |", doc)
        self.assertIn("Not compared: GOOG (no facts).", doc)
        self.assertIn("| S80 | derived | compare.py |", doc)
        self.assertEqual(lint.lint_text("dossier.md", doc), [])
    def test_request_horizons_what_if_and_wants(self):
        d = build(self.tmp, narrative=False)
        f = json.loads(text(os.path.join(d, "facts", "facts.json")))
        bh = f["metrics"]["valuation"]["by_horizon"]
        f["metrics"]["valuation"]["by_horizon"] = {"3": bh["5"]}
        with open(os.path.join(d, "facts", "facts.json"), "w", encoding="utf-8") as fh:
            json.dump(f, fh)
        with open(os.path.join(d, "request.json"), "w", encoding="utf-8") as fh:
            json.dump({"lens": "long", "what_if": {"price": [400]}, "wants": ["price"]}, fh)
        quiet(score.main, [d])
        out = quiet(report.main, [d, "--question", Q, "--chat", "--html"])
        doc = text(os.path.join(d, "reports", "dossier.md"))
        self.assertIn("| 3 years | $92.44 | $178.83 | $216.93 |", doc)
        self.assertNotIn("| 1 year |", doc)
        self.assertIn("- **3 years** — base value $178.83 against today's $343.87", doc)   # thesis per horizon
        self.assertEqual(lint.lint_text("dossier.md", doc), [])
        self.assertIn("- If it hits $400.00: in the sell zone (it starts at $175.77)", out)   # what-if, in the answer
        self.assertIn("- Within 3 years: the model's base value reaches $178.83", out)
        for gone in ("### News, what it means", "### Options on this stock"):              # not in wants
            self.assertNotIn(gone, out)
        reports = os.path.join(d, "reports")
        page = [n for n in os.listdir(reports) if n.endswith(".html") and n != "dossier.html"][0]
        html = text(os.path.join(reports, page))
        self.assertIn('href="dossier.html"', html)                                         # the detail is one click away
        self.assertIn("What the news says", text(os.path.join(reports, "dossier.html")))
    def test_chat_leads_with_the_outlook(self):
        from tests.test_score import with_outlook
        d = build(self.tmp, narrative=False)
        f = json.loads(text(os.path.join(d, "facts", "facts.json")))
        m = json.loads(text(os.path.join(FIX, "score_momentum.json")))
        for k in ("momentum", "market", "options"):
            f[k] = m[k]
        f["sources"].update(m["sources"])
        f = with_outlook(0.036, "up", facts=f)
        with open(os.path.join(d, "facts", "facts.json"), "w", encoding="utf-8") as fh:
            json.dump(f, fh)
        quiet(score.main, [d, "--holding"])
        out = quiet(report.main, [d, "--question", Q, "--lens", "long", "--chat"])
        self.assertTrue(out.startswith("## AAPL — expensive on fundamentals, rising trend; expect roughly -2% to 9% a "
                                       "year over the 5 years from today (to Oct 2031), below the 9.4% the risk demands"))
        self.assertIn("- **If you hold it:** trim into strength; trailing trigger at the 50-day average — because the "
                      "expected return of about 3.6% a year over the 5 years from today (to Oct 2031) is below the 9.4% "
                      "the risk demands, and the trend is up [S60, S61, S9]", out)
        self.assertIn("- **If you want to buy:** wait; the strict value and the pullback levels are the entry map [S60, S61, S9]", out)
        self.assertIn("- **Limit-order levels the rule points to:** $330.00 (50-day average)", out)
        self.assertIn("| Expected by Oct 2031 (5 years from today) | worst $280.40 · likely $370.20 · best $480.90 — about "
                      "3.6% a year in the likely case [S60, S61] |", out)
        self.assertIn("| Return the risk demands | 9.4% a year (10-year Treasury yield plus an equity risk premium) [S60] |", out)
        self.assertIn("| Next few months | likely range $315.10–$370.80 by 2026-11-20 (one standard deviation); trend up; "
                      "next event 2026-10-29 (next earnings)", out)
        self.assertIn("| Analysts' average 12-month target (secondary; only about 38% of such targets are met) | $352.40 "
                      "from 41 analysts [S9] |", out)
        self.assertIn("| Confidence | ", out)
        doc = text(os.path.join(d, "reports", "dossier.md"))
        self.assertIn("`strict value $148.53 ◄── pullback $330.00 ── today $343.87 ── consensus target $352.40 ──► bull "
                      "5 years $480.90` [S60, S3, S9]", doc)
        self.assertIn("### What the analyst expects, and why", doc)
        self.assertIn("| Analyst consensus (41 analysts, secondary) | $230.00 | $352.40 | $420.00 | — | — | [S9] |", doc)
        self.assertIn("(the company's 5-year record of 10.1%; analysts' 7.9% next-year estimate) [S60, S9]", doc)
        self.assertIn("0.4 × coverage", doc)
        self.assertEqual(lint.lint_text("dossier.md", doc), [])
    def outlook_store(self, name, mutate=None, request=None):
        from tests.test_score import with_outlook
        d = build(os.path.join(self.tmp, name), narrative=False)
        f = json.loads(text(os.path.join(d, "facts", "facts.json")))
        m = json.loads(text(os.path.join(FIX, "score_momentum.json")))
        for k in ("momentum", "market", "options"):
            f[k] = m[k]
        f["sources"].update(m["sources"])
        f = with_outlook(0.036, "up", facts=f)
        if mutate:
            mutate(f)
        with open(os.path.join(d, "facts", "facts.json"), "w", encoding="utf-8") as fh:
            json.dump(f, fh)
        if request:
            with open(os.path.join(d, "request.json"), "w", encoding="utf-8") as fh:
                json.dump(request, fh)
        quiet(score.main, [d])
        return quiet(report.main, [d, "--question", Q, "--lens", "long", "--chat"])

    def test_reference_horizon_consensus_2y_glosses_and_map_order(self):
        def ten_years_low_target(f):
            f["metrics"]["outlook"]["horizons"]["10"] = {"bear": {"price": 240.0, "cagr": -0.035},
                                                         "base": {"price": 600.0, "cagr": 0.058},
                                                         "bull": {"price": 900.0, "cagr": 0.101}}
            f["metrics"]["outlook"]["params"]["g"]["inputs"]["consensus_2y"] = 0.1334
            f["consensus"]["targets"]["mean"] = 329.38
        out = self.outlook_store("default", ten_years_low_target, {"horizon_source": "default", "horizons_years": [1, 5, 10]})
        self.assertIn("a year over the 5 years from today (to ", out.splitlines()[0])      # default -> 5 years, dated
        self.assertIn("| Expected by Oct 2031 (5 years from today) |", out)
        self.assertIn("| Analysts' average 12-month target (secondary; only about 38% of such targets are met) | $329.38 from", out)
        doc = text(os.path.join(self.tmp, "default", "AAPL", "reports", "dossier.md"))
        self.assertIn("| Where is the price likely to go? | 5 years:", doc)
        self.assertIn("| 10 years | $240.00 |", doc)                                       # the table keeps every horizon
        self.assertIn("analysts' 13.3% two-year estimate", doc)
        pm = re.search(r"`(strict value[^`]+)`", doc).group(1)
        vals = [float(v.replace(",", "")) for v in re.findall(r"\$([\d,]+\.\d\d)", pm)]
        self.assertEqual(vals, sorted(vals))                                               # left to right by price
        self.assertLess(pm.index("consensus target $329.38"), pm.index("today $343.87"))
        out = self.outlook_store("asked", ten_years_low_target, {"horizon_source": "question", "horizons_years": [1]})
        self.assertIn("a year over the 1 year from today (to Oct 2027)", out.splitlines()[0])
        self.assertIn("| Expected by Oct 2027 (1 year from today) |", out)

    def test_gloss_not_injected_twice(self):
        self.assertEqual(report.plain("- a restatement (deal-breaker checks G1, G2)"),
                         "- a restatement (deal-breaker checks G1, G2)")
        self.assertEqual(report.plain("- owner earnings, the cash the business really makes, fell"),
                         "- owner earnings, the cash the business really makes, fell")
        self.assertEqual(report.plain("- a going-concern paragraph (G4)"),
                         "- a going-concern paragraph (deal-breaker check G4)")

    def test_missing_narrative_and_holdings_tables(self):
        hold = {"ticker": "AAPL", "positions": [{"account": "TFSA", "shares": 10, "avg_cost": 150.0}]}
        d = build(self.tmp, narrative=False, holdings=hold)
        self.assertEqual(json.loads(self.render(d))["lint"], "OK")
        doc = text(os.path.join(d, "reports", "dossier.md"))
        self.assertIn("narrative pending", doc)
        self.assertIn("## Holdings", doc)
        self.assertIn("holdings_tables.json absent", doc)

    def test_narrative_slots_replace_mechanical_lists(self):
        hold = {"ticker": "AAPL", "positions": [{"account": "TFSA", "shares": 120.0, "avg_cost": 150.0}]}
        d = build(self.tmp, holdings=hold)
        chat = self.render(d, "--chat")
        doc = text(os.path.join(d, "reports", "dossier.md"))
        self.assertIn("- Current ratio 0.8933 [S60] below Graham's floor.", doc)  # narrative weakness
        self.assertNotIn("- 2.3 current ratio 0.8933 [S60]", doc)               # mechanical list dropped
        self.assertNotIn("- 1.1 ROIC >=", doc)
        for out in (doc, chat):
            self.assertNotIn("- Pillar 1 Business quality", out)                    # narrative Why wins
        self.assertIn("| TFSA | 120 | $150.00 |", chat)                               # the shares table in the brief
        d2 = build(os.path.join(self.tmp, "bare"), narrative=False)
        chat = self.render(d2, "--chat")
        self.assertIn("- Quality (business quality and moat): 20/20 [S61]", chat)   # mechanical Why when no narrative
        self.assertIn("- Pillar 1 Business quality and moat: 20/20 [S61]", text(os.path.join(d2, "reports", "dossier.md")))
    def test_short_lens_section(self):
        d = build(self.tmp, narrative=False)
        facts = json.loads(text(os.path.join(d, "facts", "facts.json")))
        m = json.loads(text(os.path.join(FIX, "score_momentum.json")))
        for k in ("momentum", "market", "options"):
            facts[k] = m[k]
        facts["sources"].update(m["sources"])
        with open(os.path.join(d, "facts", "facts.json"), "w", encoding="utf-8") as fh:
            json.dump(facts, fh)
        quiet(score.main, [d, "--lens", "both"])
        quiet(report.main, [d, "--question", "Sell in three months?", "--lens", "both"])
        doc = text(os.path.join(d, "reports", "dossier.md"))
        self.assertIn("## Short-term lens", doc)
        self.assertIn("**Short-term stance:** trend up", doc)
        self.assertIn("| 2026-11-20 | 28.4% | 9.04% ($31.09)", doc)
        self.assertEqual(lint.lint_text("dossier.md", doc), [])



    def test_index_md_lints_as_a_part_and_maps_the_folder(self):
        d = build(self.tmp)
        out = json.loads(self.render(d))
        self.assertEqual(out["index"], os.path.join(d, "INDEX.md"))
        idx = text(out["index"])
        facts = os.path.join(d, "facts", "facts.json")
        self.assertEqual(lint_main(["--part", "--facts", facts, out["index"]]), 0)
        self.assertTrue(idx.startswith("# Apple Inc. (AAPL) — index"))
        self.assertIn("**Industry:** not yet mapped", idx)
        for rel in ("facts/facts.json", "facts/scorecard.json", "research/research.md", "history/log.md",
                    "reports/dossier.md"):
            self.assertIn("](%s)" % rel, idx)
        self.assertIn("`research/industry.md` — industry chain position and related stocks (not yet written)", idx)
        self.assertIn("## Latest decision", idx)
        self.assertRegex(idx, r"Updated `\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC`")
        self.assertRegex(idx, r"Open questions: \d+ \[S\d+\]")

    def test_index_history_table_is_newest_first_and_regenerated(self):
        d = build(self.tmp)
        self.render(d)
        self.render(d, score_args=("--mos", "0.5"))
        idx = text(os.path.join(d, "INDEX.md"))
        rows = [l for l in idx.split("## History\n")[1].split("\n\n")[0].splitlines() if l.startswith("| 20")]
        self.assertEqual(len(rows), 2)
        self.assertIn("zones buy below $103.97 / sell above $175.77 →", rows[0])   # newest first
        self.assertIn("first analysis", rows[1])

    def test_industry_section_index_line_and_chat(self):
        d = build(self.tmp, industry=True)
        chat = self.render(d, "--chat")
        doc = text(os.path.join(d, "reports", "dossier.md"))
        heads = [l for l in doc.splitlines() if l.startswith("## ")]
        i = heads.index("## Industry and related stocks")
        self.assertEqual((heads[i - 1], heads[i + 1]), ("## Market trend", "## Facts"))
        self.assertIn("| Foundry | TSMC | TSM | fabricates the main processors [S100] |", doc)
        self.assertNotIn("# AAPL — industry chain", doc)
        self.assertIn("- Which suppliers sit in the second tier is not disclosed in the filings.", doc)  # merged open question
        self.assertEqual(lint.lint_text("dossier.md", doc), [])
        self.assertNotIn("Industry and peers", chat)                                  # the brief leaves the chain to the dossier
        idx = text(os.path.join(d, "INDEX.md"))
        self.assertIn("**Industry:** Brand owner and integrator – Apple – AAPL [S100]; Foundry – TSMC – TSM [S100]; "
                      "Memory – Micron – MU [S103]", idx)
        self.assertEqual(lint_main(["--part", "--facts", os.path.join(d, "facts", "facts.json"), os.path.join(d, "INDEX.md")]), 0)
    def test_index_industry_line_compact_and_links_this_run(self):
        d = build(self.tmp, industry=True)
        with open(os.path.join(d, "research", "industry.md"), "a", encoding="utf-8") as fh:
            fh.write("\n## Related stocks\n\n| Ticker | Link | Reason |\n|---|---|---|\n"
                     "| TSM | supplier | foundry [S100] |\n| MU | supplier | memory [S103] |\n"
                     "| MSFT | peer | software and devices [S100] |\n| GOOGL | peers | phones [S100] |\n")
        os.makedirs(os.path.join(d, "charts"))
        with open(os.path.join(d, "charts", "2026-10-14.html"), "w", encoding="utf-8") as fh:
            fh.write("<html></html>")
        quiet(score.main, [d])
        man = json.loads(quiet(report.main, [d, "--question", Q, "--lens", "long", "--html"]))
        idx = text(os.path.join(d, "INDEX.md"))
        self.assertIn("**Industry:** suppliers TSM, MU · peers MSFT, GOOGL — The filing names no single supplier above "
                      "one tenth of cost of sales [S100].", idx)
        self.assertIn("| TSM | supplier | foundry [S100] |", text(os.path.join(d, "reports", "dossier.md")))
        self.assertIn("](%s)" % os.path.relpath(man["html"], d), idx)            # this run's page
        self.assertIn("](%s)" % os.path.relpath(man["snapshot"], d), idx)        # this run's snapshot
        self.assertIn("- [`charts/*.html`](charts/2026-10-14.html)", idx)
        self.assertEqual(lint_main(["--part", "--facts", os.path.join(d, "facts", "facts.json"), os.path.join(d, "INDEX.md")]), 0)

    def test_narrative_flag_and_default_newest(self):
        d = build(self.tmp)
        newer = os.path.join(d, "history", "2026-10-15-0800.md")
        with open(newer, "w", encoding="utf-8") as fh:
            fh.write("## Answer\n\n- NEWEST-NARRATIVE answer text.\n")
        quiet(score.main, [d])
        quiet(report.main, [d, "--question", Q, "--lens", "long", "--no-lint"])
        self.assertIn("NEWEST-NARRATIVE", text(os.path.join(d, "reports", "dossier.md")))
        quiet(report.main, [d, "--question", Q, "--lens", "long", "--no-lint", "--narrative",
                            os.path.join(d, "history", "2026-10-14-0900.md")])
        self.assertNotIn("NEWEST-NARRATIVE", text(os.path.join(d, "reports", "dossier.md")))
        self.assertEqual(report.locate(d).newest_narrative(), newer)

    def test_html_lands_in_reports_with_run_stamp(self):
        d = build(self.tmp)
        out = json.loads(self.render(d, "--html"))
        self.assertRegex(out["html"], r"/reports/\d{4}-\d{2}-\d{2}-\d{4}\.html$")
        self.assertTrue(os.path.exists(out["html"]))
        self.assertFalse(os.path.exists(os.path.join(d, "dossiers")))


    def proof_store(self):
        """Store layout <tmp>/stocks/AAPL with <tmp>/market/SPY.json and a calibration record in facts.json."""
        d = build(os.path.join(self.tmp, "stocks"))
        os.makedirs(os.path.join(self.tmp, "market"))
        shutil.copy(os.path.join(FIX, "market_spy.json"), os.path.join(self.tmp, "market", "SPY.json"))
        fp = os.path.join(d, "facts", "facts.json")
        f = json.loads(text(fp))
        f["metrics"]["calibration"] = metrics.compute(f, spy=metrics.load_spy(metrics.market_dir_for(fp)))["calibration"]
        with open(fp, "w", encoding="utf-8") as fh:
            json.dump(f, fh)
        return d

    def test_track_record_case_against_and_not_verified(self):
        d = self.proof_store()
        first = self.render(d, "--chat")
        tr = first.split("### Track record\n")[1].split("\n### ")[0]
        self.assertRegex(tr, r"^- over 5 past years the base case missed realised returns by 5\.1 pp on average .* beat SPY "
                             r"in 6 of 6 windows; simulated with today's method on then-available data \[S60\]\n")
        self.assertNotIn("Last time", tr)                                          # this run's line is not a past call
        ca = first.split("### Risks: the case against\n")[1].split("\n### ")[0]
        self.assertTrue(ca.startswith("- The price $343.87 [S3]"))
        self.assertIn("sales guidance fell short of expectations [S105].", ca)
        self.assertLessEqual(len([l for l in ca.splitlines() if l.startswith("- ")]), 3)
        nv = first.split("### Not verified\n")[1].split("\n### ")[0]
        lines = [l for l in nv.splitlines() if l.startswith("- ")]
        self.assertLessEqual(len(lines), 4)
        self.assertTrue(lines[-1].startswith("- and ") and lines[-1].endswith("more, listed in the dossier [S61]"))
        for l in lines:
            self.assertRegex(l, r"\[S\d+\]\.?$")
        self.assertLess(first.index("### Risks: the case against"), first.index("### Track record"))
        self.assertLess(first.index("### What to watch"), first.index("### Not verified"))
        second = self.render(d, "--chat")
        tr = second.split("### Track record\n")[1].split("\n### ")[0]
        self.assertRegex(tr, r"\n- Last time \(\d{4}-\d{2}-\d{2}\) this advisor said avoid at \$343\.87; now \$343\.87 "
                             r"\(\+0\.0%\), SPY [+-]\d+\.\d% over the same days \[S62\]")
        doc = text(os.path.join(d, "reports", "dossier.md"))
        for h in ("## Track record", "## The case against", "## What could not be verified"):
            self.assertIn(h, doc)
        self.assertIn("| Years ago | FY | Price then | Strict value then | Base case said (per year) | What happened "
                      "(per year) | SPY same window (per year) | |", doc)
        self.assertIn("| 5 | 2020 | $112.28 | $62.37 | 10.7% | 20.9% | 11.4% | [S60] |", doc)
        self.assertIn("| 9 | 2016 | n/a | $23.73 | n/a | n/a | 10.8% | [S60] |", doc)
        self.assertIn("**What this advisor said before about AAPL**", doc)
        self.assertIn("- Item 5.5 (no customer >= 10% of revenue): no evidence — researcher verdict no evidence", doc)
        self.assertIn("- Customer concentration by net sales: the 10-K names no customer and states no threshold [S100].", doc)
        self.assertEqual(lint.lint_text("dossier.md", doc), [])
        idx = text(os.path.join(d, "INDEX.md"))
        self.assertRegex(idx, r"\nTrack record: over 5 past years .* \[S60\]\n")
        self.assertEqual(lint_main(["--part", "--facts", os.path.join(d, "facts", "facts.json"), os.path.join(d, "INDEX.md")]), 0)
        self.assertIn("| Price | Said | Zones | Changed | |", idx)
    def test_proof_sections_fallbacks(self):
        d = build(self.tmp, narrative=False)                                        # fixture metrics: no calibration
        out = self.render(d, "--chat")
        self.assertIn("### Track record\n- No past calls yet; the simulated record needs at least three fiscal years of "
                      "data [S60]\n", out)
        self.assertIn("### Risks: the case against\nThe analyst's note has no case-against section; ask for a refreshed "
                      "analysis [S62].\n", out)
        self.assertNotIn("Track record:", text(os.path.join(d, "INDEX.md")))
        r = report.Report(report.locate(d), Q, "long", "2026-10-14")
        for x in r.sc["items"].values():
            x["status"] = "scored"
        r.m = {"freshness": {"value": 1.0, "price_age_trading_days": 0}}
        self.assertEqual(r.not_verified(), ["*computed by scripts*", "",
                                            "Every input the standard asks for was available this run [S61]."])
        r.sc["gates"]["G1"]["result"] = "pending"
        r.f["price"]["date"] = "2026-10-09"                                         # a Friday, three weekdays before
        nv = r.not_verified()[2:]
        self.assertEqual(len(nv), 2)
        self.assertTrue(nv[0].startswith("- Gate G1 (Bankruptcy or receivership (8-K Item 1.03, 3 yrs)): pending — "))
        self.assertTrue(nv[0].endswith(" [S61]"))
        self.assertEqual(nv[1], "- Price is stale: the last price is dated 2026-10-09, 3 trading days before this run [S60]")
        for v, w in ((80, "strong evidence"), (79, "solid"), (65, "solid"), (64, "mixed"), (45, "mixed"), (44, "thin"), (None, None)):
            self.assertEqual(report.band_word(v), w)

    def test_history_said_expected_and_old_lines(self):
        out = self.outlook_store("hist")
        d = os.path.join(self.tmp, "hist", "AAPL")
        line = text(os.path.join(d, "history", "log.md")).splitlines()[0]
        self.assertIn(" · price $343.87 · said wait; the strict value and the pullback levels are the entry map · "
                      "expected 3.6%/yr at 5 years vs 9.4% required · zones buy below $103.97 / sell above $175.77 · "
                      "changed: first analysis", line)
        self.assertTrue(line.split(" · ")[-1].startswith("changed: "))
        old = ("- 2026-09-01 · question `old` · lens long · tier buy · score 90/100 · stance buy zone · confidence 80/100 · "
               "price $300.00 · zones buy below $103.97 / sell above $175.77 · changed: first analysis")
        with open(os.path.join(d, "history", "log.md"), "a", encoding="utf-8") as fh:
            fh.write(old + "\n")
        p = report.parse_history(old)
        self.assertEqual((p["date"], p["tier"], p["price"], p.get("said"), p["changed"]), ("2026-09-01", "buy", "$300.00", None, "first analysis"))
        quiet(score.main, [d])
        out = quiet(report.main, [d, "--question", Q, "--lens", "long", "--chat"])
        lines = text(os.path.join(d, "history", "log.md")).splitlines()
        self.assertTrue(lines[-1].endswith("changed: tier buy → research deeper; score 90/100 → 63/100; stance buy zone → sell zone"))
        tr = out.split("### Track record\n")[1].split("\n### ")[0]
        self.assertRegex(tr, r"- Last time \(2026-\d{2}-\d{2}\) this advisor said wait; the strict value and the pullback levels "
                             r"are the entry map; expected 3\.6%/yr at 5 years vs 9\.4% required at \$343\.87; now \$343\.87 "
                             r"\(\+0\.0%\), SPY n/a over the same days \[S62\]")           # the newest earlier call
        doc = text(os.path.join(d, "reports", "dossier.md"))
        self.assertIn("| 2026-09-01 | buy zone | $300.00 | $343.87 (+14.6%) | n/a | [S62] |", doc)
        self.assertIn("expected 3.6%/yr at 5 years vs 9.4% required", doc)
        idx = text(os.path.join(d, "INDEX.md"))
        self.assertIn("| 2026-09-01 | `old` | long | buy | 90/100 | buy zone | 80/100 | $300.00 |  | buy below $103.97 / sell above "
                      "$175.77 | first analysis | [S62] |", idx)
        self.assertEqual(lint.lint_text("dossier.md", text(os.path.join(d, "reports", "dossier.md"))), [])


class ParseResearchHeadings(unittest.TestCase):
    def test_parse_research_h2_log(self):
        import report
        text = "## Management\n- 2026-10-14 — x [S100]\n\n## Open questions\n- q\n\n## Evidence log\n| S | class | what | url | as-of | retrieved |\n|---|---|---|---|---|---|\n| S100 | primary | 10-K | https://sec.gov/x | FY2025 | 2026-10-14 |\n"
        secs, oq, log = report.parse_research(text)
        self.assertIn("Management", secs)
        self.assertNotIn("Open questions", secs)
        self.assertEqual(len(oq), 1)
        self.assertEqual(len(log), 1)


if __name__ == "__main__":
    unittest.main()

class FundBrief(unittest.TestCase):
    """A fund (facts/fund.json, no scorecard) renders the fund brief, a lint-clean dossier, a log line and INDEX.md."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.d = os.path.join(self.tmp, "stocks", "QQQ")
        os.makedirs(os.path.join(self.d, "facts"))
        shutil.copy(os.path.join(FIX, "fund_qqq.json"), os.path.join(self.d, "facts", "fund.json"))

    def test_fund_brief_dossier_and_index(self):
        out = quiet(report.main, [self.d, "--question", "should I keep QQQ?", "--chat", "--html"])
        heads = [l for l in out.splitlines() if l.startswith("#")]
        self.assertEqual(heads[0], "## QQQ — Invesco QQQ Trust, an index fund tracking the Nasdaq-100 index; trend up; "
                                   "12 months +8.8% (SPY +16.0%)")
        self.assertEqual(heads[1:], ["### Answer", "### Summary", "### What to watch", "### Not verified",
                                     "### Words used here", "### Sources"])
        self.assertIn("- **If you hold it:** hold; add on a dip toward the 200-day average ($679.82) [S1]", out)
        self.assertIn("| Yearly cost (expense ratio) | 0.18% [S2] |", out)
        self.assertIn("| Biggest holdings | NVDA 8.3%, AAPL 7.4%, MSFT 5.8%, MU 5%, AMD 4.2% — top 6 = 47% of the fund [S2] |", out)
        self.assertIn("| 5 years / 10 years, per year | 12.5% a year (SPY 14% a year) / 20.3% a year (SPY 13% a year) [S1, S7] |", out)
        self.assertIn("- inception: not in Yahoo info [S2]", out)
        self.assertIn("- S2 — QQQ fund profile", out)
        self.assertNotIn("scorecard", out.lower().split("### sources")[0].replace("a fund has no scorecard", ""))
        doc = text(os.path.join(self.d, "reports", "dossier.md"))
        self.assertEqual(lint.lint_text("dossier.md", doc), [])
        self.assertIn("## Holdings", doc)
        self.assertIn("| NVDA NVIDIA Corp | 8.3% | [S2] |", doc)
        log = text(os.path.join(self.d, "history", "log.md")).splitlines()
        self.assertEqual(len(log), 1)
        self.assertIn(" · fund index · price $681.09 · trend up · said hold", log[0])
        idx = text(os.path.join(self.d, "INDEX.md"))
        self.assertTrue(idx.startswith("# QQQ — Invesco QQQ Trust (fund)"))
        self.assertIn("| 2026-", idx)
        reports = os.path.join(self.d, "reports")
        page = [n for n in os.listdir(reports) if n.endswith(".html") and n != "dossier.html"][0]
        html = text(os.path.join(reports, page))
        self.assertIn("Charts: none for a fund yet", html)
        self.assertIn('href="https://finance.yahoo.com/quote/QQQ/holdings/"', html)
        self.assertTrue(os.path.exists(os.path.join(reports, "dossier.html")))

    def test_leveraged_fund_rule(self):
        fp = os.path.join(self.d, "facts", "fund.json")
        f = json.loads(text(fp))
        f.update(ticker="SQQQ", name="ProShares UltraPro Short QQQ", kind="inverse",
                 kind_reason="name contains 'UltraPro Short'", flags=["leveraged or inverse: resets daily, not built for holding"])
        with open(fp, "w", encoding="utf-8") as fh:
            json.dump(f, fh)
        out = quiet(report.main, [self.d, "--question", "SQQQ?", "--chat", "--no-lint"])
        self.assertIn("- **If you hold it:** not built for holding: it resets daily", out)
        self.assertIn("- **If you want to buy:** do not buy to hold [S1]", out)
        self.assertIn("- **Watch out:** leveraged or inverse: resets daily, not built for holding [S2]", out)
