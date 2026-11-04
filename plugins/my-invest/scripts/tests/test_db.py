import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import db  # noqa: E402


class Schema(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")

    def test_every_table_and_view_exists(self):
        names = {r[0] for r in self.c.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
        for t in db.table_names():
            self.assertIn(t, names)
        for v in db.VIEWS:
            self.assertIn(v, names)
        self.assertEqual(db.current_version(self.c), db.SCHEMA_VERSION)

    def test_migrate_is_idempotent(self):
        db.migrate(self.c)
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0], 1)

    def test_pk_columns(self):
        self.assertEqual(db.pk_columns("prices"), ["ticker", "date"])
        self.assertEqual(db.pk_columns("fundamentals"), ["ticker", "concept", "unit", "period_end", "period_start"])
        self.assertEqual(db.pk_columns("securities"), ["ticker"])
        self.assertEqual(db.pk_columns("calls"), ["id"])

    def test_schema_md_matches_checked_in_reference(self):
        ref = os.path.join(os.path.dirname(HERE), "skills", "data", "references", "schema.md")
        with open(ref) as f:
            self.assertEqual(f.read().rstrip("\n"), db.schema_md().rstrip("\n"),
                             "regenerate with: db.py schema --md > skills/data/references/schema.md")


class Writes(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")
        self.sid = db.source(self.c, "https://data.sec.gov/api/x?api_key=K", "primary", "SEC")

    def test_source_redacts_and_dedupes(self):
        self.assertEqual(db.one(self.c, "SELECT url FROM sources")["url"], "https://data.sec.gov/api/x?api_key=REDACTED")
        again = db.source(self.c, "https://data.sec.gov/api/x?api_key=K", "primary", None, "2026-01-01T00:00:00Z")
        self.assertEqual(again, self.sid)
        self.assertEqual(db.one(self.c, "SELECT title, fetched_at FROM sources")["title"], "SEC")
        with self.assertRaises(ValueError):
            db.source(self.c, "https://x", "guess")

    def test_upsert_updates_non_key_columns(self):
        db.upsert(self.c, "prices", [{"ticker": "AAPL", "date": "2026-01-02", "close": 1.0, "source_id": self.sid}])
        db.upsert(self.c, "prices", [{"ticker": "AAPL", "date": "2026-01-02", "close": 2.0, "volume": 5, "source_id": self.sid}])
        r = db.one(self.c, "SELECT * FROM prices")
        self.assertEqual((r["close"], r["volume"]), (2.0, 5))
        self.assertEqual(db.latest_price(self.c, "aapl")["close"], 2.0)

    def test_upsert_rejects_unknown_columns_and_missing_keys(self):
        with self.assertRaises(ValueError):
            db.upsert(self.c, "prices", [{"ticker": "AAPL", "date": "2026-01-02", "close": 1.0, "source_id": self.sid, "bogus": 1}])
        with self.assertRaises(ValueError):
            db.upsert(self.c, "prices", [{"ticker": "AAPL", "close": 1.0, "source_id": self.sid}])

    def test_id_tables_insert_and_json_columns(self):
        rid = db.insert(self.c, "runs", {"asked_at": "t", "question": "q", "intent": "stock", "subjects": ["AAPL"]})
        n = db.upsert(self.c, "views", [{"run_id": rid, "subject": "AAPL", "dimension": "valuation", "stance": "for",
                                         "strength": 2, "sentence": "s", "evidence": [self.sid], "created_at": "t"}])
        self.assertEqual(n, 1)
        v = db.one(self.c, "SELECT * FROM views")
        self.assertEqual(json.loads(v["evidence"]), [self.sid])
        self.assertEqual(json.loads(db.one(self.c, "SELECT subjects FROM runs")["subjects"]), ["AAPL"])

    def test_check_constraints_hold(self):
        rid = db.insert(self.c, "runs", {"asked_at": "t", "question": "q", "intent": "stock", "subjects": "[]"})
        with self.assertRaises(sqlite3.IntegrityError):
            db.insert(self.c, "views", {"run_id": rid, "subject": "A", "dimension": "vibes", "stance": "for",
                                        "strength": 1, "sentence": "s", "evidence": "[]", "created_at": "t"})
        with self.assertRaises(sqlite3.IntegrityError):
            db.insert(self.c, "calls", {"run_id": rid, "ticker": "A", "tier": "moderate", "action": "buy", "horizon_months": 12,
                                        "confidence": 140, "confidence_parts": "{}", "evidence": "[]", "made_at": "d", "due_at": "d"})
        with self.assertRaises(sqlite3.IntegrityError):  # foreign key
            db.insert(self.c, "prices", {"ticker": "A", "date": "d", "close": 1.0, "source_id": 999})

    def test_fundamental_views_split_annual_and_quarterly(self):
        rows = [{"ticker": "A", "concept": "Revenues", "unit": "USD", "period_start": "2025-01-01", "period_end": "2025-12-31",
                 "days": 364, "fp": "FY", "value": 10, "source_id": self.sid},
                {"ticker": "A", "concept": "Revenues", "unit": "USD", "period_start": "2025-10-01", "period_end": "2025-12-31",
                 "days": 91, "fp": "FY", "value": 3, "source_id": self.sid},
                {"ticker": "A", "concept": "Assets", "unit": "USD", "period_start": "", "period_end": "2025-12-31",
                 "fp": "FY", "value": 50, "source_id": self.sid}]
        db.upsert(self.c, "fundamentals", rows)
        self.assertEqual([r["value"] for r in db.rows(self.c, "SELECT value FROM fundamentals_annual ORDER BY value")], [10, 50])
        self.assertEqual([r["value"] for r in db.rows(self.c, "SELECT value FROM fundamentals_quarterly")], [3])

    def test_read_only_refuses_writes(self):
        db.read_only(self.c)
        with self.assertRaises(sqlite3.DatabaseError):
            self.c.execute("DELETE FROM sources")
        self.assertEqual(len(db.rows(self.c, "SELECT * FROM sources")), 1)


class Cli(unittest.TestCase):
    def run_db(self, *args):
        out = subprocess.run([sys.executable, os.path.join(HERE, "db.py"), *args, "--project", self.proj],
                             capture_output=True, text=True)
        return out.returncode, out.stdout

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_creates_db_config_and_gitignore_without_user_steps(self):
        code, out = self.run_db("init")
        self.assertEqual(code, 0, out)
        obj = json.loads(out)
        self.assertTrue(os.path.exists(obj["path"]))
        self.assertEqual(obj["version"], db.SCHEMA_VERSION)
        data = os.path.join(self.proj, "data")
        self.assertTrue(os.path.exists(os.path.join(data, "config.json")))
        with open(os.path.join(data, ".gitignore")) as f:
            self.assertIn("invest.db", f.read())

    def test_write_query_exec_and_refusals(self):
        rows = json.dumps([{"url": "https://a", "grade": "primary", "fetched_at": "t"}])
        code, out = self.run_db("write", "sources", "--json", rows)
        self.assertEqual(json.loads(out)["written"], 1, out)
        code, out = self.run_db("query", "SELECT url FROM sources", "--md")
        self.assertIn("| https://a |", out)
        code, out = self.run_db("query", "DELETE FROM sources")
        self.assertEqual(code, 1)
        self.assertIn("not authorized", json.loads(out)["error"])
        code, out = self.run_db("exec", "UPDATE sources SET title = 'x'")
        self.assertEqual(json.loads(out)["changed"], 1)
        code, out = self.run_db("write", "nope", "--json", "[]")
        self.assertEqual(code, 1)
        code, out = self.run_db("describe", "calls", "--md")
        self.assertIn("confidence_parts", out)
        code, out = self.run_db("source", "https://example.com/report", "--grade", "secondary", "--title", "A report")
        self.assertEqual(json.loads(out)["marker"], "[S2]")
        code, out = self.run_db("tables")
        self.assertEqual(len(json.loads(out)["tables"]), len(db.TABLES))


if __name__ == "__main__":
    unittest.main()
