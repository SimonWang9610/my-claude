"""store.py: list, show, next-id, path against a temp project (no network)."""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import common
import store


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.proj = tempfile.mkdtemp()
        self.data = tempfile.mkdtemp()
        self.root = os.path.join(self.proj, "data")
        self.aapl = os.path.join(self.root, "stocks", "AAPL")
        os.makedirs(self.aapl)
        os.makedirs(os.path.join(self.root, "market"))
        os.makedirs(os.path.join(self.root, ".cache"))

    def call(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            store.run(list(argv) + ["--data", self.data, "--project", self.proj])
        return json.loads(out.getvalue())

    def write(self, name, text):
        os.makedirs(os.path.dirname(os.path.join(self.aapl, name)), exist_ok=True)
        with open(os.path.join(self.aapl, name), "w", encoding="utf-8") as f:
            f.write(text)

    def test_list_reads_history_date_and_price_and_skips_special_folders(self):
        self.write("facts/facts.json", json.dumps({"price": {"last": 12.5, "date": "2026-10-13"}}))
        self.write("history/log.md", "- 2026-09-01 · q · long · A\n- 2026-10-12 · q2 · long · B\n\n")
        os.makedirs(os.path.join(self.root, "stocks", "MSFT"))
        got = self.call("list")
        self.assertEqual(got["store"], self.root)
        self.assertEqual(got["tickers"], [
            {"ticker": "AAPL", "last_analysis": "2026-10-12", "last_price": 12.5, "price_date": "2026-10-13"},
            {"ticker": "MSFT", "last_analysis": None, "last_price": None, "price_date": None}])

    def test_list_on_missing_store_is_empty(self):
        shutil_root = tempfile.mkdtemp()
        out = io.StringIO()
        with redirect_stdout(out):
            store.run(["list", "--data", self.data, "--project", shutil_root])
        self.assertEqual(json.loads(out.getvalue())["tickers"], [])

    def test_show(self):
        self.write("history/log.md", "line one\n")
        got = self.call("show", "aapl")
        self.assertEqual(got["history"], "line one\n")
        self.assertIsNone(self.call("show", "MSFT")["history"])
        self.assertIn("not been analyzed", self.call("show", "MSFT")["reason"])

    def test_next_id(self):
        self.assertEqual(self.call("next-id", "AAPL")["next_id"], "S100")          # no research.md
        self.write("research/research.md", "Revenue grew [S101]. See S7 and [S103][S100]; XS500 is not an id.\n")
        self.assertEqual(self.call("next-id", "AAPL")["next_id"], "S104")
        self.write("research/research.md", "only script ids S1 S2 S99\n")
        self.assertEqual(self.call("next-id", "AAPL")["next_id"], "S100")

    def test_path_prints_root_or_creates_ticker_folder(self):
        self.assertEqual(self.call("path")["path"], self.root)
        got = self.call("path", "nvda")
        self.assertEqual(got["path"], os.path.join(self.root, "stocks", "NVDA"))
        self.assertTrue(os.path.isdir(got["path"]))

    def test_path_creates_store_with_gitignore(self):
        fresh = tempfile.mkdtemp()
        out = io.StringIO()
        with redirect_stdout(out):
            store.run(["path", "T", "--data", self.data, "--project", fresh])
        with open(os.path.join(fresh, "data", ".gitignore")) as f:
            self.assertEqual(f.read(), ".cache/\n.venv/\nconfig.json\n")

    def test_bad_ticker_refused_but_folder_path_accepted(self):
        with self.assertRaises(common.FetchError):
            self.call("path", "A$B")
        self.assertEqual(self.call("next-id", self.aapl)["next_id"], "S100")

    def test_tree_lists_the_folder_map(self):
        self.write("INDEX.md", "x")
        self.write("facts/facts.json", "{}")
        self.write("research/research.md", "x")
        self.write("history/log.md", "x")
        os.makedirs(os.path.join(self.aapl, "filings", "0001-25-000001"))
        with open(os.path.join(self.aapl, "filings", "0001-25-000001", "full.txt"), "w") as f:
            f.write("x")
        got = self.call("tree", "AAPL")
        self.assertEqual(got["tree"], ["INDEX.md", "facts/", "  facts.json", "filings/", "  0001-25-000001/ (1 files)",
                                       "history/", "  log.md", "research/", "  research.md"])
        with self.assertRaises(common.FetchError):
            self.call("tree", "MSFT")


if __name__ == "__main__":
    unittest.main()
