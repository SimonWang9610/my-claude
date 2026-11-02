"""holdings.py: question parsing, P&L at price points, Canadian tax lines, FX, Markdown lint (no network)."""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

import holdings
import lint
from tests import fx

AS_OF = "2026-10-14"
SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "holdings.py")
E2E_Q = ("I have 120 AAPL at $150 in my TFSA and 80 at $210 in a non-registered account, "
         "marginal rate 43%, what if it hits 400")


def parse(q, ticker="AAPL"):
    return holdings.parse_question(q, ticker, AS_OF)[0]


def pos(q, ticker="AAPL"):
    return [(p["account"], p["shares"], p["avg_cost"]) for p in parse(q, ticker)["positions"]]


class Parsing(unittest.TestCase):
    def test_account_prefix_and_at_sign(self):
        self.assertEqual(pos("RRSP: 50 AAPL @ 180"), [("RRSP", 50, 180)])

    def test_other_ticker_kept_only_for_its_folder(self):
        q = "200 shares of GOOGL avg cost 135 non-registered"
        self.assertEqual(pos(q, "GOOGL"), [("NONREG", 200, 135)])
        self.assertEqual(pos(q, "AAPL"), [])

    def test_comma_form_average_cost(self):
        self.assertEqual(pos("200 shares of GOOGL, average cost 135, non-registered", "GOOGL"),
                         [("NONREG", 200, 135)])

    def test_two_positions_inherit_ticker_rate_and_named_price(self):
        h = parse(E2E_Q)
        self.assertEqual([(p["account"], p["shares"], p["avg_cost"]) for p in h["positions"]],
                         [("TFSA", 120, 150), ("NONREG", 80, 210)])
        self.assertEqual(h["marginal_rate"], 0.43)
        self.assertEqual(h["eval_prices"], [400.0])
        self.assertEqual((h["ticker"], h["currency"], h["as_of"]), ("AAPL", "USD", AS_OF))

    def test_labelled_accounts_in_sequence(self):
        self.assertEqual(pos("TFSA: 100 AAPL @ 150; RRSP: 50 AAPL @ 180"), [("TFSA", 100, 150), ("RRSP", 50, 180)])

    def test_holding_period_alias_and_lowercase_ticker(self):
        h = parse("I hold 30 aapl at 120 in my FHSA and plan to hold for 3 years")
        self.assertEqual(pos("I hold 30 aapl at 120 in my FHSA"), [("TFSA", 30, 120)])
        self.assertEqual(h["horizon_end"], "2029-10-14")

    def test_cad_cost_and_lira(self):
        h = parse("my LIRA has 10 AAPL avg price 99.5 CAD")
        self.assertEqual(h["positions"], [{"account": "RRSP", "shares": 10, "avg_cost": 99.5, "currency": "CAD"}])

    def test_mixed_tickers_and_several_named_prices(self):
        h = parse("I have 100 GOOGL at 120 in TFSA and 40 AAPL at 170 in RRSP, sell at 250 or 300? 33% bracket")
        self.assertEqual([(p["account"], p["shares"]) for p in h["positions"]], [("RRSP", 40)])
        self.assertEqual(h["eval_prices"], [250.0, 300.0])
        self.assertEqual(h["marginal_rate"], 0.33)

    def test_no_rate_no_prices_no_horizon(self):
        h = parse("RRSP: 50 AAPL @ 180")
        self.assertEqual((h["marginal_rate"], h["eval_prices"], h["horizon_end"]), (None, [], None))


class Tables(unittest.TestCase):
    def setUp(self):
        self.rules = holdings.load_rules()
        self.zones = fx.load("holdings_scorecard.json")["zones"]

    def tables(self, q, fxr=1.4, zones=True):
        h = parse(q)
        return holdings.build("/tmp/AAPL", h, 300.0, fxr, AS_OF, {"class": "primary", "what": "BoC",
                              "url": holdings.BOC_URL, "as_of": AS_OF, "retrieved": AS_OF},
                              self.zones if zones else None, self.rules)

    @staticmethod
    def point(t, section, account, label):
        row = next(r for r in t[section] if r["account"] == account)
        return next(p for p in row["price_points" if section == "outcomes" else "points"] if p["label"] == label)

    def test_price_points_and_pnl(self):
        t = self.tables(E2E_Q)
        tfsa = next(o for o in t["outcomes"] if o["account"] == "TFSA")
        self.assertEqual([p["label"] for p in tfsa["price_points"]],
                         ["current", "buy zone", "base value", "sell zone", "named $400"])
        self.assertEqual(tfsa["cost_total"], 18000.0)
        cur = self.point(t, "outcomes", "TFSA", "current")
        self.assertEqual((cur["value"], cur["gain_abs"], cur["gain_pct"]), (36000.0, 18000.0, 1.0))
        buy = self.point(t, "outcomes", "NONREG", "buy zone")
        self.assertEqual((buy["value"], buy["gain_abs"], buy["gain_pct"]), (16000.0, -800.0, -0.0476))

    def test_fx_conversion(self):
        cur = self.point(self.tables(E2E_Q), "outcomes", "NONREG", "current")
        self.assertEqual((cur["value_cad"], cur["gain_cad"]), (33600.0, 10080.0))

    def test_cad_cost_basis(self):
        t = self.tables("100 AAPL at C$300 in my TFSA", fxr=1.5)
        o = t["outcomes"][0]
        self.assertEqual((o["avg_cost"], o["cost_total"], o["acb_cad"]), (200.0, 20000.0, 30000.0))
        self.assertEqual(o["price_points"][0]["gain_cad"], 15000.0)

    def test_tfsa_zero_tax(self):
        t = self.tables(E2E_Q)
        for p in next(r for r in t["tax"] if r["account"] == "TFSA")["points"]:
            self.assertEqual((p["taxable_amount_cad"], p["estimated_tax_cad"]), (0.0, 0.0))
            self.assertIsNotNone(p["after_tax_proceeds_cad"])

    def test_nonreg_half_inclusion_with_rate(self):
        t = self.tables(E2E_Q)
        p = self.point(t, "tax", "NONREG", "current")
        self.assertEqual((p["taxable_amount_cad"], p["estimated_tax_cad"], p["after_tax_proceeds_cad"]),
                         (5040.0, 2167.2, 31432.8))
        loss = self.point(t, "tax", "NONREG", "buy zone")
        self.assertEqual((loss["taxable_amount_cad"], loss["estimated_tax_cad"]), (-560.0, 0.0))
        self.assertTrue(any("superficial loss" in n for n in t["notes"]))
        row = next(r for r in t["tax"] if r["account"] == "NONREG")
        self.assertEqual(row["citation"], self.rules["T-GAIN"]["url"])
        self.assertEqual(row["inclusion_rate"], 0.5)

    def test_nonreg_without_rate(self):
        t = self.tables("80 AAPL at 210 non-registered")
        p = self.point(t, "tax", "NONREG", "current")
        self.assertEqual((p["taxable_amount_cad"], p["estimated_tax_cad"], p["after_tax_proceeds_cad"]),
                         (5040.0, None, None))
        self.assertTrue(any("no marginal rate" in n for n in t["notes"]))

    def test_rrsp_note_and_if_withdrawn(self):
        t = self.tables("RRSP: 50 AAPL @ 180, marginal rate 43%")
        row = t["tax"][0]
        self.assertIn("withdrawal taxed as income", row["note"])
        p = row["points"][0]
        self.assertEqual((p["taxable_amount_cad"], p["estimated_tax_cad"], p["after_tax_proceeds_cad"],
                          p["if_withdrawn_tax_cad"]), (0.0, 0.0, 21000.0, 9030.0))
        self.assertEqual(t["dividends"][0]["src"], ["S97"])

    def test_no_fx_leaves_cad_null(self):
        t = holdings.build("/tmp/AAPL", parse(E2E_Q), 300.0, None, None, None, None, self.rules)
        p = self.point(t, "tax", "NONREG", "current")
        self.assertIsNone(p["taxable_amount_cad"])
        self.assertNotIn("S98", t["sources"])

    def test_source_ids_in_range_and_markdown_lints(self):
        for q in (E2E_Q, "RRSP: 50 AAPL @ 180", "80 AAPL at 210 non-registered"):
            t = self.tables(q)
            self.assertTrue(all(90 <= int(s[1:]) <= 99 for s in t["sources"]))
            md = holdings.render_md(t)
            self.assertEqual(lint.lint_text("h.md", md, part=True), [], md)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.folder = os.path.join(self.tmp, "stocks", "AAPL")
        self.facts = os.path.join(self.folder, "facts")
        os.makedirs(self.facts)
        shutil.copy(os.path.join(fx.DIR, "holdings_facts.json"), os.path.join(self.facts, "facts.json"))
        shutil.copy(os.path.join(fx.DIR, "holdings_scorecard.json"), os.path.join(self.facts, "scorecard.json"))

    def test_writes_both_files_with_defaults(self):
        with redirect_stdout(io.StringIO()):
            t = holdings.run([self.folder, "--question", E2E_Q, "--offline", "--data", self.tmp])
        self.assertEqual(t["fx_usdcad"], {"rate": 1.4, "date": "2026-10-14", "src": "S98"})
        self.assertEqual(t["outcomes"][0]["price_points"][0]["price"], 300.0)
        with open(os.path.join(self.facts, "holdings.json")) as f:
            h = json.load(f)
        self.assertEqual(set(h), {"ticker", "as_of", "currency", "positions", "marginal_rate", "eval_prices",
                                  "horizon_end"})
        self.assertTrue(os.path.exists(os.path.join(self.facts, "holdings_tables.json")))

    def test_json_input_and_md(self):
        js = json.dumps({"ticker": "AAPL", "positions": [{"account": "rrif", "shares": 5, "avg_cost": 100}]})
        buf = io.StringIO()
        with redirect_stdout(buf):
            holdings.run([self.folder, "--json", js, "--md", "--fx", "1.3", "--zones", "1,2,3", "--data", self.tmp])
        self.assertEqual(lint.lint_text("h.md", buf.getvalue(), part=True), [])
        self.assertIn("| RRSP | 5 |", buf.getvalue())

    def test_nothing_parses_is_error_envelope(self):
        p = subprocess.run([sys.executable, SCRIPT, self.folder, "--question", "200 shares of GOOGL avg cost 135",
                            "--offline", "--data", self.tmp], capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertEqual(json.loads(p.stdout)["script"], "holdings.py")
        self.assertFalse(os.path.exists(os.path.join(self.facts, "holdings.json")))


if __name__ == "__main__":
    unittest.main()
