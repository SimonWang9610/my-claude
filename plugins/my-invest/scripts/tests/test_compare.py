"""compare.py: peers table from stored facts, no-data columns, source ids, lint-clean Markdown (no network)."""
import contextlib
import copy
import io
import json
import os
import tempfile
import unittest

import common
import compare
import lint
from tests import fx


def make(store, ticker, facts=None, scorecard=None):
    folder = os.path.join(store, "stocks", ticker, "facts")
    os.makedirs(folder)
    with open(os.path.join(folder, "facts.json"), "w") as f:
        json.dump(facts if facts is not None else fx.load("score_aapl_facts.json"), f)
    if scorecard:
        with open(os.path.join(folder, "scorecard.json"), "w") as f:
            json.dump(scorecard, f)
    return os.path.join(store, "stocks", ticker)


def peer_facts():
    f = copy.deepcopy(fx.load("score_aapl_facts.json"))
    f["name"], f["ticker"] = "Peer Inc.", "MSFT"
    f["metrics"]["revenue_cagr_5y"]["value"] = 0.12
    f["metrics"]["roic"][0]["value"] = 0.3
    f["metrics"]["net_debt_to_owner_earnings"]["value"] = -0.5
    del f["metrics"]["owner_earnings"]["yield"]
    f["fundamentals"]["annual"][0].update(operating_income=50.0, revenue=200.0)
    f["price"]["return_1y"] = -0.1
    return f


def run(store, *argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        compare.run(list(argv) + ["--store", store])
    return out.getvalue()


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.store = tempfile.mkdtemp()
        self.aapl = make(self.store, "AAPL", scorecard={"stance": "hold, do not add"})
        make(self.store, "MSFT", peer_facts())

    def test_columns_rows_and_derived_margin(self):
        doc = json.loads(run(self.store, "AAPL", "--peers", "MSFT,GOOG"))
        a, m, g = doc["columns"]
        self.assertEqual([c["ticker"] for c in doc["columns"]], ["AAPL", "MSFT", "GOOG"])
        r = a["rows"]
        self.assertEqual(r["sales_growth_5y"]["value"], 0.0868)
        self.assertAlmostEqual(r["operating_margin"]["value"], 133050000000 / 416161000000, 6)
        self.assertEqual(r["operating_margin"]["inputs"], {"fy": 2025, "operating_income": 133050000000,
                                                           "revenue": 416161000000})
        self.assertEqual((r["roic"]["value"], r["cash_yield"]["value"], r["debt_years"]["value"]),
                         (0.8228, 0.0223, 0.56))
        self.assertEqual((r["return_12m"]["value"], r["stance"]["value"]), (0.3929868001129675, "hold, do not add"))
        self.assertEqual(m["rows"]["operating_margin"]["value"], 0.25)
        self.assertEqual(m["rows"]["stance"]["value"], "not scored")          # peer without a scorecard
        self.assertIsNone(m["rows"]["cash_yield"]["value"])
        self.assertEqual(g["status"], "no data")
        self.assertIn("run facts.py GOOG first", g["reason"])
        self.assertIsNone(g["rows"])

    def test_source_ids_and_peers_json_written(self):
        doc = json.loads(run(self.store, "AAPL", "--peers", "MSFT,GOOG"))
        self.assertEqual(list(doc["sources"]), ["S80", "S81"])           # no row for the missing column
        self.assertEqual([c["src"] for c in doc["columns"]], ["S80", "S81", None])
        s = doc["sources"]["S81"]
        self.assertEqual((s["class"], s["url"]), ("derived", "file://" + os.path.join(self.store, "stocks", "MSFT",
                                                                                      "facts", "facts.json")))
        with open(os.path.join(self.aapl, "facts", "peers.json")) as f:
            self.assertEqual(json.load(f)["columns"][1]["ticker"], "MSFT")

    def test_markdown_lints_as_a_part(self):
        md = run(self.store, "AAPL", "--peers", "MSFT,GOOG", "--md")
        self.assertIn("| | AAPL | MSFT | GOOG |", md)
        self.assertIn("| Sales growth, 5-year CAGR | 8.68% [S80] | 12.00% [S81] | no data: no facts/facts.json for GOOG", md)
        self.assertIn("| Debt years (net debt / owner earnings) | 0.56 years [S80] | net cash (-0.50 years) [S81] |", md)
        self.assertIn("| Model stance | hold, do not add [S80] | not scored [S81] | no data |", md)
        self.assertIn("n/a (metrics.owner_earnings.yield not available) [S81]", md)   # missing field keeps its marker
        path = os.path.join(self.aapl, "compare.md")
        with open(path, "w") as f:
            f.write(md)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = lint.main(["--part", "--facts", os.path.join(self.aapl, "facts", "facts.json"), path])
        self.assertEqual(rc, 0)

    def test_errors(self):
        with self.assertRaises(common.FetchError):
            run(self.store, "NVDA", "--peers", "MSFT")                   # subject has no facts
        with self.assertRaises(common.FetchError):
            run(self.store, "AAPL", "--peers", "AAPL")                    # no peer other than the subject
        with self.assertRaises(common.FetchError):
            run(self.store, "AAPL", "--peers", ",".join("P%d" % i for i in range(10)))
        with self.assertRaises(common.FetchError):
            run(self.store, "AAPL", "--peers", "A$B")


if __name__ == "__main__":
    unittest.main()
