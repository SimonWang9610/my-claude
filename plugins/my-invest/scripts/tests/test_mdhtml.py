"""mdhtml.py converts our Markdown subset under the page contract; report.py --html embeds the charts."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import mdhtml
from tests.test_report import Q, build, quiet
import report
import score

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mdhtml.py")
FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def assert_page_contract(t, page, title):
    t.assertIn("<title>%s</title>" % title, page)
    t.assertIn("@media (prefers-color-scheme: dark)", page)
    t.assertIn(':root:not([data-theme="light"])', page)
    t.assertIn(':root[data-theme="dark"]', page)
    t.assertRegex(page, r"body\{[^}]*background:var\(--page\)")
    t.assertNotIn("<script", page.lower())
    t.assertNotRegex(page, r"<link[^>]+stylesheet")


class MdHtml(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def test_cli_converts_fixture(self):
        out = os.path.join(self.tmp, "o.html")
        r = subprocess.run([sys.executable, SCRIPT, os.path.join(FIX, "mdhtml_sample.md"), "--out", out,
                            "--title", "Sample Dossier Page"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(json.loads(r.stdout)["path"], out)
        with open(out, encoding="utf-8") as f:
            page = f.read()
        assert_page_contract(self, page, "Sample Dossier Page")
        self.assertIn('<h1 id="sample-dossier">Sample dossier</h1>', page)
        self.assertIn('<div class="tw"><table><thead><tr><th>Horizon</th>', page)
        self.assertIn('<tr id="ev-S1"><td>S1</td>', page)
        self.assertIn('<sup class="mk">[<a class="mk" href="#ev-S1">S1</a>, <a class="mk" href="#ev-S3">S3</a>]</sup>',
                      page)
        self.assertIn('<sup class="mk">[S10]</sup>', page)            # no log row -> plain text, no dead link
        self.assertIn("<code>a &lt; b</code>", page)
        self.assertIn("<strong>bold</strong>", page)
        self.assertIn('<a href="https://www.sec.gov/x.htm">link</a>', page)
        self.assertNotIn("javascript:", page)
        self.assertIn("<ol><li>first</li><li>second</li></ol>", page)
        self.assertRegex(page, r"<ul><li>Tier: .*?<ul><li>nested point")
        self.assertIn("<pre><code>raw &lt;code&gt; | not a table</code></pre>", page)
        self.assertRegex(page, r"<blockquote><p>Model-backed research for the owner's own study, not investment advice\. "
                               r"Every figure is as cited and may be wrong or stale\.</p></blockquote>")

    def test_missing_input_error_envelope(self):
        r = subprocess.run([sys.executable, SCRIPT, os.path.join(self.tmp, "none.md"), "--out", "x.html",
                            "--title", "X Y"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)["script"], "mdhtml.py")

    def test_details_sections_collapse(self):
        html = mdhtml.to_html("## A\n\nopen\n\n---\n## Details  (collapsed)\n\n### 1. One\n- a\n\n#### sub\nx\n\n### 2. Two\ny\n")
        self.assertEqual(html.count('<details class="sec">'), 2)
        self.assertIn('<details class="sec"><summary>1. One</summary>', html)
        self.assertLess(html.index("<h4"), html.index("<summary>2. Two"))  # sub-heading stays inside its section
        self.assertNotIn("<details", mdhtml.to_html("## Details of the deal\n\ntext"))

    def test_render_appends_extra_sections_in_order(self):
        page = mdhtml.render("# A\n\ntext [S1]", "A Page", ["<p>one</p>", "<p>two</p>"])
        self.assertLess(page.index("text"), page.index("<p>one</p>"))
        self.assertLess(page.index("<p>one</p>"), page.index("<p>two</p>"))
        self.assertIn("[S1]</sup>", page)


class ReportHtml(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def test_report_html_has_answer_five_panels_and_dossier(self):
        d = build(self.tmp)
        shutil.copy(os.path.join(FIX, "chart_series.json"), os.path.join(d, "facts", "series.json"))
        shutil.copy(os.path.join(FIX, "chart_holdings_tables.json"), os.path.join(d, "facts", "holdings_tables.json"))
        quiet(score.main, [d])
        man = json.loads(quiet(report.main, [d, "--question", Q, "--lens", "long", "--html"]))
        path = man["html"]
        self.assertTrue(re.search(r"AAPL/reports/\d{4}-\d{2}-\d{2}-\d{4}\.html$", path))
        with open(path, encoding="utf-8") as f:
            page = f.read()
        assert_page_contract(self, page, "AAPL Analysis")
        for t in ("Ten-year price and value zones", "Revenue, owner earnings and free cash flow",
                  "ROIC against the discount rate", "Diluted shares and cash returned", "Holdings outcomes"):
            self.assertIn("<h2>%s</h2>" % t, page)
        self.assertEqual(page.count("<svg"), 5)
        order = [page.index(x) for x in ("Answer", "Summary", 'id="charts"', 'id="full-dossier"')]
        self.assertEqual(order, sorted(order))
        self.assertNotIn("Evidence log", page.split('id="charts"')[0])             # the brief carries Sources, not the log
        self.assertNotIn("<details", page.split('id="charts"')[0])                 # the brief is never collapsed
        self.assertIn('href="dossier.html"', page)
        with open(os.path.join(os.path.dirname(path), "dossier.html"), encoding="utf-8") as f:
            dossier = f.read()
        assert_page_contract(self, dossier, "AAPL dossier")
        for h in ("The short answer", "Price outlook", "Thesis", "Facts", "Open questions", "Evidence log"):
            self.assertRegex(dossier, r"<h\d id=\"[^\"]+\">%s</h\d>" % h)
        dead = [m for m in re.findall(r'href="#ev-(S\d+)"', dossier) if 'id="ev-%s"' % m not in dossier]
        self.assertEqual(dead, [])
        self.assertIn('href="https://finance.yahoo.com/quote/AAPL/history/"', page)   # inline markers link on the page

    def test_chat_lists_page_when_html(self):
        d = build(self.tmp)
        quiet(score.main, [d])
        out = quiet(report.main, [d, "--question", Q, "--lens", "long", "--html", "--chat"])
        self.assertRegex(out, r"Files: \[full dossier\]\(file://[^)]+dossier\.md\) · \[page\]\(file://[^)]+\.html\)")
        reports = os.path.join(d, "reports")
        html = [n for n in os.listdir(reports) if n.endswith(".html") and n != "dossier.html"][0]
        with open(os.path.join(reports, html), encoding="utf-8") as f:
            self.assertIn("Charts: no evidence", f.read())


if __name__ == "__main__":
    unittest.main()
