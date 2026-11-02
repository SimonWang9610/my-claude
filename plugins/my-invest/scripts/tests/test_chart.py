"""chart.py: page contract, null handling, split adjustment, downsampling, error envelope (no network)."""
import copy
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

import chart
from tests import fx

TITLES = ["Ten-year price and value zones", "Revenue, owner earnings and free cash flow",
          "ROIC against the discount rate", "Diluted shares and cash returned"]
SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chart.py")


class ChartTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.stock = os.path.join(self.tmp, "stocks", "TST")
        self.folder = os.path.join(self.stock, "facts")
        os.makedirs(self.folder)
        self.facts, self.series = fx.load("chart_facts.json"), fx.load("chart_series.json")

    def write(self, facts=None, series=None, holdings=False):
        for name, obj in (("facts.json", self.facts if facts is None else facts),
                          ("series.json", self.series if series is None else series),
                          ("holdings_tables.json", holdings)):
            if obj is not False:
                with open(os.path.join(self.folder, name), "w", encoding="utf-8") as f:
                    json.dump(obj, f)

    def run_chart(self, *extra):
        buf = io.StringIO()
        with redirect_stdout(buf):
            chart.run(["tst", "--store", self.tmp, *extra])
        man = json.loads(buf.getvalue())
        with open(man["path"], encoding="utf-8") as f:
            return man, f.read()

    def test_page_contract_and_manifest(self):
        self.write()
        man, page = self.run_chart()
        self.assertTrue(os.path.exists(man["path"]))
        self.assertTrue(re.search(r"TST/charts/\d{4}-\d{2}-\d{2}\.html$", man["path"]))
        for t in TITLES:
            self.assertIn("<h2>%s</h2>" % t, page)
        self.assertEqual(page.count("<svg"), 4)
        self.assertIn(chart.DISCLAIMER, page)
        self.assertIn("<title>TST Trend Charts</title>", page)
        self.assertIn("@media (prefers-color-scheme: dark)", page)
        self.assertIn(':root:not([data-theme="light"])', page)
        self.assertIn(':root[data-theme="dark"]', page)
        self.assertNotIn("<script", page.lower())
        self.assertNotRegex(page, r"<link[^>]+stylesheet")
        self.assertIn(chart.OE_LABEL, page)
        self.assertIn("discount rate r_base", page)
        self.assertIn('class="ln s2 dash"', page)                   # ex-goodwill differs -> dashed
        self.assertEqual({s["id"] for s in man["sources"]}, {"S1", "S2", "S3", "S4"})
        self.assertIn("Sources: S1 (https://data.sec.gov/", page)
        self.assertEqual(man["as_of"], {"prices": "2026-10-13", "fundamentals": "FY2024 (period end 2024-12-31)"})

    def test_null_year_draws_no_bar_and_values_gap(self):
        self.write()
        _, page = self.run_chart()
        self.assertNotIn('data-fy="2022"', page)
        self.assertIn('data-fy="2021"', page)
        self.assertNotIn('data-fy="2023" data-series="buybacks"', page)   # one null segment -> absent
        self.assertIn('data-fy="2023" data-series="dividends"', page)
        price_path = re.search(r'<path class="ln s1" d="([^"]+)"', page).group(1)
        self.assertEqual(price_path.count("M"), 2)                      # null closes split the line

    def test_shares_from_metrics_series(self):
        self.write()
        _, page = self.run_chart()
        self.assertIn("<td>FY2021</td><td>104M</td>", page)              # metrics series, not raw 52M
        self.assertIn("<td>FY2023</td><td>102M</td>", page)

    def test_absent_metrics_series_read_no_evidence(self):
        facts = copy.deepcopy(self.facts)
        for k in ("owner_earnings_series", "fcf_series", "cash_returned", "shares_diluted_adjusted"):
            del facts["metrics"][k]
        self.write(facts)
        _, page = self.run_chart()
        self.assertNotIn('data-series="owner_earnings"', page)          # never recomputed from rows
        self.assertNotIn('data-series="fcf"', page)
        self.assertIn('data-series="revenue"', page)
        self.assertIn("%s (no evidence)" % chart.OE_LABEL, page)
        sec = page.split("<h2>%s</h2>" % TITLES[3])[1].split("</section>")[0]
        self.assertIn("no evidence", sec)
        self.assertNotIn("<svg", sec)
        self.assertNotIn("data-fy", sec)

    def test_all_null_panel_reads_no_evidence(self):
        facts = copy.deepcopy(self.facts)
        facts["metrics"]["roic"] = []
        self.write(facts)
        _, page = self.run_chart()
        sec = page.split("<h2>%s</h2>" % TITLES[2])[1].split("</section>")[0]
        self.assertIn("no evidence", sec)
        self.assertNotIn("<svg", sec)
        self.assertEqual(page.count("<svg"), 3)

    def test_downsampled_and_small(self):
        series = copy.deepcopy(self.series)
        n = 2600
        series["dates"] = ["%04d-%02d-%02d" % (2016 + i // 260, 1 + (i % 260) // 22, 1 + i % 22) for i in range(n)]
        series["adj_close"] = series["close"] = [10 + i * 0.1 for i in range(n)]
        self.write(series=series)
        man, page = self.run_chart("--out", os.path.join(self.tmp, "o.html"))
        self.assertEqual(man["path"], os.path.join(self.tmp, "o.html"))
        price_path = re.search(r'<path class="ln s1" d="([^"]+)"', page).group(1)
        self.assertLessEqual(price_path.count("L") + 1, 1001)
        self.assertLess(len(page.encode()), 400 * 1024)

    def test_momentum_averages_overlay_panel_one(self):
        self.write()
        _, page = self.run_chart()
        sec = page.split("<h2>%s</h2>" % TITLES[1])[0]
        self.assertEqual(sec.count('class="ma"'), 2)
        self.assertIn("50-day average $30.50", sec)
        self.assertIn("200-day average $26.00", sec)
        facts = copy.deepcopy(self.facts)
        del facts["momentum"]
        self.write(facts)
        _, page = self.run_chart()
        self.assertNotIn('class="ma"', page)

    def test_holdings_panel_only_when_file_exists(self):
        self.write()
        man, page = self.run_chart()
        self.assertNotIn("Holdings outcomes", page)
        self.assertNotIn("S99", {s["id"] for s in man["sources"]})
        self.write(holdings=fx.load("chart_holdings_tables.json"))
        man, page = self.run_chart()
        sec = page.split("<h2>Holdings outcomes</h2>")[1].split("</section>")[0]
        self.assertEqual(page.count("<svg"), 5)
        self.assertIn('class="cur"', sec)                                 # current price point highlighted
        for lbl in ("current", "buy zone", "base value", "sell zone"):
            self.assertIn('>%s</text>' % lbl, sec)
        self.assertIn('data-label="sell zone" data-series="TFSA"', sec)
        self.assertNotIn('data-label="sell zone" data-series="NONREG"', sec)   # null gain -> no bar
        self.assertIn("S90 (https://laws-lois", sec)
        self.assertIn("S99 (file://", sec)
        self.assertIn("S2 (https://finance.yahoo.com", sec)
        self.assertTrue({"S90", "S99"} <= {s["id"] for s in man["sources"]})

    def test_missing_series_error_envelope(self):
        self.write(series=False)
        r = subprocess.run([sys.executable, SCRIPT, "TST", "--store", self.tmp], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        env = json.loads(r.stdout)
        self.assertEqual(env["script"], "chart.py")
        self.assertIn("series.json", env["error"])


if __name__ == "__main__":
    unittest.main()
