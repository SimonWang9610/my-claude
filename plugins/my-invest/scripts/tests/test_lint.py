"""Checks for scripts/lint.py: one passing dossier and one mutation per rule."""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)
import lint  # noqa: E402

with open(os.path.join(HERE, "fixtures", "lint_pass.md"), encoding="utf-8") as _fh:
    PASS = _fh.read()


def rules(text):
    return [v.split(": ", 2)[1].split(" — ")[0] for v in lint.lint_text("t.md", text)]


def mutate(old, new):
    assert old in PASS, old
    return PASS.replace(old, new, 1)


class Passing(unittest.TestCase):
    def test_sample_passes(self):
        self.assertEqual(lint.lint_text("t.md", PASS), [])

    def test_cli_exit_codes(self):
        script = os.path.join(SCRIPTS, "lint.py")
        ok = subprocess.run([sys.executable, script, os.path.join(HERE, "fixtures", "lint_pass.md")],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stdout)
        self.assertIn("lint: OK", ok.stdout)
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "bad.md")
            with open(bad, "w", encoding="utf-8") as fh:
                fh.write(mutate("[S1]. Gross margin", ". Gross margin"))
            p = subprocess.run([sys.executable, script, bad], capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertRegex(p.stdout, r"bad\.md:\d+: uncited-figure — ")
        self.assertIn("lint: 1 violation(s) in 1 file(s)", p.stdout)
        ex = subprocess.run([sys.executable, script, "--explain"], capture_output=True, text=True)
        self.assertEqual(ex.returncode, 0)
        self.assertIn("Figure rules", ex.stdout)


class LogRule(unittest.TestCase):
    def test_row_without_http_url(self):
        self.assertEqual(rules(mutate("| https://data.sec.gov/submissions/CIK0000000000.json |", "| data.sec.gov |")),
                         ["log-row", "unresolved-marker"])

    def test_row_with_bad_id(self):
        self.assertIn("log-row", rules(mutate("| S4 | derived", "| 4 | derived")))

    def test_missing_log(self):
        text = PASS.split("## Evidence log")[0] + PASS.split("| S4 |")[1].split("\n", 1)[1]
        self.assertIn("no-log", rules(text))


class MarkerRule(unittest.TestCase):
    def test_unresolved_marker(self):
        self.assertEqual(rules(mutate("up 12.5% on the year [S1]", "up 12.5% on the year [S9]")),
                         ["unresolved-marker"])

    def test_marker_list(self):
        self.assertEqual(rules(mutate("[S1][S3]", "[S1, S7]")), ["unresolved-marker"])


class FigureRule(unittest.TestCase):
    def check(self, line, expect_flag):
        text = mutate("## Business and moat\n", "## Business and moat\n\n%s\n" % line)
        self.assertEqual("uncited-figure" in rules(text), expect_flag, line)

    def test_flags_figures(self):
        for line in ("Revenue was $1.8 billion.", "Margin rose to 45%.", "It trades at 12.3x earnings.",
                     "Net debt is 1.5 times owner earnings.", "The company has 12 plants.",
                     "Price 42 vs fair value 44, see https://example.com/1234"):
            self.check(line, True)

    def test_does_not_flag_identifiers(self):
        for line in ("Filed on 2026-10-02 for FY2025 and fiscal 2024.", "See the 10-K, 10-Q and 8-K, and Form 4.",
                     "Items 1.03 and 4.02 were absent; Item 9A is clean.", "Gate G1 and decision D-12 apply.",
                     "- 1.3 — gross profitability needs the 10-K Item 7 passage",
                     "Source: https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/a.htm",
                     "Pillar 3 is unscored."):
            self.check(line, False)

    def test_heading_and_separator_ignored(self):
        self.check("### Fair value at 10 years", False)

    def test_fraction_outside_scorecard_needs_marker(self):
        self.check("The tally was 14/20.", True)
        self.check("Score 14/20 overall.", False)


class ScorecardRule(unittest.TestCase):
    def test_section_without_any_marker(self):
        sc = PASS.split("## Scorecard")[1].split("## Evidence log")[0]
        stripped = sc.replace("[S1]", "").replace("[S2]", "").replace("[S3]", "").replace("[S4]", "")
        # remove the price line too, its dollar figures would be flagged separately
        stripped = "\n".join(l for l in stripped.splitlines() if not l.startswith("Price ")
                             and "1.95" not in l and "G1 " not in l)
        r = rules(PASS.replace(sc, stripped))
        self.assertEqual(r, ["scorecard-unanchored"])


class DisclaimerRule(unittest.TestCase):
    def test_missing(self):
        self.assertEqual(rules(mutate("Every figure is as cited", "Every figure is cited")), ["disclaimer"])

    def test_curly_apostrophe_accepted(self):
        self.assertEqual(rules(mutate("owner's own", "owner’s own")), [])


class PartAndDerivedRows(unittest.TestCase):
    def test_part_skips_disclaimer_and_accepts_file_url_for_derived(self):
        from lint import lint_text
        text = (
            "## Facts\nRevenue $416,161M [S1]; base fair value $148.53 [S2]\n\n"
            "### Evidence log\n| S | class | what | url | as-of | retrieved |\n|---|---|---|---|---|---|\n"
            "| S1 | primary | FY2025 10-K | https://www.sec.gov/x | FY2025 | 2026-10-14 |\n"
            "| S2 | derived | metrics.py from S1 | file:///tmp/w/AAPL/facts.json | 2026-10-14 | 2026-10-14 |\n"
        )
        self.assertEqual(lint_text("p.md", text, part=True), [])
        full = lint_text("p.md", text)
        self.assertTrue(any("disclaimer" in v for v in full))

    def test_extra_ids_resolve_markers(self):
        from lint import lint_text
        text = "Revenue $416,161M [S1]; macro 5.21 percent [S4]\n\n| S | class | what | url | as-of | retrieved |\n|---|---|---|---|---|---|\n| S1 | primary | x | https://a | 2026 | 2026 |\n"
        self.assertTrue(any("unresolved" in v for v in lint_text("p.md", text, part=True)))
        self.assertEqual(lint_text("p.md", text, part=True, extra_ids={"S4"}), [])
        nolog = "Price $1.00 [S3]\n"
        self.assertTrue(any("no-log" in v for v in lint_text("p.md", nolog, part=True)))
        self.assertEqual(lint_text("p.md", nolog, part=True, extra_ids={"S3"}), [])

    def test_file_url_rejected_for_primary(self):
        from lint import lint_text
        text = (
            "x $1.00 [S1]\n\n| S | class | what | url | as-of | retrieved |\n|---|---|---|---|---|---|\n"
            "| S1 | primary | thing | file:///tmp/x | 2026 | 2026 |\n"
        )
        self.assertTrue(any("log-row" in v for v in lint_text("p.md", text, part=True)))

    def test_facts_option_resolves_ids_across_the_stock_layout(self):
        import io
        import json
        from contextlib import redirect_stdout
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "facts"))
        os.makedirs(os.path.join(d, "research"))
        for name, ids in (("facts.json", ["S1"]), ("scorecard.json", ["S6"]), ("holdings_tables.json", ["S99"])):
            with open(os.path.join(d, "facts", name), "w") as f:
                json.dump({"sources": {i: {} for i in ids}}, f)
        with open(os.path.join(d, "research", "research.md"), "w") as f:
            f.write("| S | class | what | url |\n|---|---|---|---|\n| S101 | primary | x | https://a.b/c |\n")
        part = os.path.join(d, "part.md")
        with open(part, "w") as f:
            f.write("Price $1.00 [S1] and $2.00 [S6] and $3.00 [S99] and $4.00 [S101].\n")
        facts = os.path.join(d, "facts", "facts.json")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(lint.main(["--part", "--facts", facts, part]), 0)
            with open(part, "w") as f:
                f.write("Price $1.00 [S102].\n")
            self.assertEqual(lint.main(["--part", "--facts", facts, part]), 1)
        self.assertEqual(lint.facts_ids(facts), {"S1", "S6", "S99", "S101"})




class PeersIdsResolve(unittest.TestCase):
    def test_peers_ids_resolve(self):
        import tempfile, os, json, lint
        d = tempfile.mkdtemp(); f = os.path.join(d, "facts"); os.makedirs(f)
        json.dump({"sources": {"S1": {}}}, open(os.path.join(f, "facts.json"), "w"))
        json.dump({"sources": {"S80": {}}}, open(os.path.join(f, "peers.json"), "w"))
        ids = lint.facts_ids(os.path.join(f, "facts.json"))
        self.assertIn("S80", ids)


if __name__ == "__main__":
    unittest.main()
