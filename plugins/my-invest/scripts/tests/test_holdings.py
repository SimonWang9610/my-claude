import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import common  # noqa: E402
import db  # noqa: E402
import holdings  # noqa: E402

CSV = os.path.join(HERE, "tests", "fixtures", "holdings_two_accounts.csv")


def seed(conn):
    sid = db.source(conn, "https://yahoo/x", "secondary", "Yahoo")
    db.upsert(conn, "prices", [{"ticker": "AAPL", "date": "2025-12-31", "close": 200.0, "source_id": sid},
                               {"ticker": "QQQ", "date": "2025-12-31", "close": 450.0, "source_id": sid}])
    db.upsert(conn, "securities", [{"ticker": "QQQ", "kind": "fund", "updated_at": "t"}])
    db.upsert(conn, "fund_weights", [{"fund": "QQQ", "kind": "holding", "key": "AAPL", "weight": 0.10, "asof": "2025-12-01", "source_id": sid},
                                     {"fund": "QQQ", "kind": "holding", "key": "MSFT", "weight": 0.09, "asof": "2025-12-01", "source_id": sid},
                                     {"fund": "QQQ", "kind": "holding", "key": "MSFT", "weight": 0.05, "asof": "2025-01-01", "source_id": sid},
                                     {"fund": "QQQ", "kind": "sector", "key": "Technology", "weight": 0.5, "asof": "2025-12-01", "source_id": sid}])
    db.upsert(conn, "stats", [{"ticker": "AAPL", "asof": "2025-12-31", "metric": m, "window": "spot", "value": v, "source_id": sid}
                              for m, v in (("ma50", 195.0), ("ma200", 180.0), ("high_52w", 210.0), ("low_52w", 150.0),
                                           ("range_3m_low", 185.0), ("range_3m_high", 216.0))])
    db.upsert(conn, "estimates", [{"ticker": "AAPL", "asof": "2025-12-30", "next_earnings": "2026-01-29", "source_id": sid}])
    return sid


def counts(conn):
    return {t: conn.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0] for t in db.table_names()}


class Parsing(unittest.TestCase):
    def test_columns_accounts_and_skips(self):
        rows, cols, skipped = holdings.parse(CSV)
        self.assertEqual(cols["ticker"], "Symbol")
        self.assertEqual(cols["shares"], "Quantity")
        self.assertEqual(cols["cost"], "Average Cost")
        self.assertEqual(cols["cost_mode"], "per_share")
        self.assertEqual(cols["account"], "Account Type")
        self.assertEqual(cols["value"], "Market Value")
        self.assertEqual(cols["type"], "Description")
        self.assertEqual([r["account"] for r in rows], ["TFSA", "RRSP", "NONREG"])
        self.assertEqual(rows[0]["avg_cost"], 150.0)         # "$150.00"
        self.assertEqual(rows[0]["csv_value"], 2000.0)       # "$2,000.00"
        self.assertTrue(rows[2]["is_fund"])
        self.assertEqual(skipped, [{"symbol": "SHOP.TO", "reason": "not a US listing"}])

    def test_account_mapping_and_symbol_cleaning(self):
        for text, kind in (("RRSP USD", "RRSP"), ("LIRA", "RRSP"), ("RRIF", "RRSP"), ("FHSA", "TFSA"), ("TFSA", "TFSA"),
                           ("Margin", "NONREG"), ("Cash", "NONREG"), ("", "NONREG"), ("Non-registered", "NONREG")):
            self.assertEqual(holdings.account_kind(text), kind, text)
        self.assertEqual(holdings.clean_symbol(" aapl-u "), ("AAPL", None))
        self.assertEqual(holdings.clean_symbol("BRK.B"), ("BRK.B", None))
        self.assertEqual(holdings.clean_symbol("XEQT.TO"), ("XEQT.TO", "not a US listing"))
        self.assertEqual(holdings.clean_symbol(""), (None, "no ticker"))

    def test_total_cost_column_and_missing_shares_column(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.csv")
            with open(p, "w") as f:
                f.write("Account,Ticker,Shares,Book Cost,Market Value\nTFSA,AAPL,10,1500,2000\n")
            rows, cols, _ = holdings.parse(p)
            self.assertEqual(cols["cost_mode"], "total")
            self.assertEqual(rows[0]["avg_cost"], 150.0)
            with open(p, "w") as f:
                f.write("Account,Ticker,Price\nTFSA,AAPL,10\n")
            with self.assertRaises(common.FetchError) as cm:
                holdings.parse(p)
            self.assertIn("shares", str(cm.exception))


class Arithmetic(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")
        seed(self.c)

    def test_aggregation_weights_and_split(self):
        res = holdings.analyse(self.c, CSV, [], [0.15, 0.125, 0.10], None)
        pos = {p["ticker"]: p for p in res["positions"]}
        self.assertEqual(res["portfolio"]["total"], 12000.0)
        self.assertEqual(res["portfolio"]["positions"], 2)
        aapl = pos["AAPL"]
        self.assertEqual(aapl["shares"], 15)
        self.assertEqual(aapl["value"], 3000.0)
        self.assertEqual(aapl["cost"], 2400.0)
        self.assertEqual(aapl["gain"], 600.0)
        self.assertAlmostEqual(aapl["gain_pct"], 0.25)
        self.assertAlmostEqual(aapl["avg_cost"], 160.0)
        self.assertAlmostEqual(aapl["weight"], 0.25)
        self.assertEqual([r["account"] for r in aapl["accounts"]], ["TFSA", "RRSP"])
        self.assertTrue(pos["QQQ"]["is_fund"])
        self.assertAlmostEqual(res["portfolio"]["funds_weight"], 0.75)
        self.assertAlmostEqual(res["portfolio"]["stocks_weight"], 0.25)
        self.assertEqual(res["portfolio"]["top5"][0]["ticker"], "QQQ")

    def test_look_through_sums_direct_and_via_the_fund(self):
        res = holdings.analyse(self.c, CSV, [], [0.15], None)
        lt = {x["ticker"]: x for x in res["look_through"]}
        self.assertAlmostEqual(lt["AAPL"]["direct_weight"], 0.25)
        self.assertAlmostEqual(lt["AAPL"]["via_weight"], 0.075)        # 9000 x 10% / 12000
        self.assertAlmostEqual(lt["AAPL"]["total_weight"], 0.325)
        self.assertEqual(lt["AAPL"]["via"][0]["fund"], "QQQ")
        self.assertAlmostEqual(lt["MSFT"]["via_weight"], 0.0675)       # the latest asof (9%), not the older 5%
        self.assertEqual(lt["MSFT"]["direct"], 0.0)
        self.assertNotIn("QQQ", lt)
        self.assertEqual(res["portfolio"]["funds_looked_through"], [{"fund": "QQQ", "asof": "2025-12-01", "constituents": 2}])

    def test_frames_and_sell_order(self):
        res = holdings.analyse(self.c, CSV, ["AAPL"], [0.15, 0.125, 0.10, 0.30], None)
        fr = {f["frame"]: f for f in res["sizing"]["AAPL"]["frames"]}
        cap15 = fr["cap at 15.0%"]
        self.assertEqual(cap15["shares_to_sell"], 6)                   # (3000 - 1800) / 200
        self.assertEqual(cap15["proceeds"], 1200.0)
        self.assertEqual(cap15["shares_kept"], 9)
        self.assertEqual([(a["account"], a["shares"]) for a in cap15["from_accounts"]], [("RRSP", 5), ("TFSA", 1)])
        self.assertEqual(cap15["from_accounts"][0]["reason"], "no tax on a sale; withdrawals are taxed as income later")
        self.assertEqual(fr["cap at 10.0%"]["shares_to_sell"], 9)
        self.assertEqual(fr["cap at 30.0%"]["shares_to_sell"], 0)
        self.assertEqual(fr["cap at 30.0%"]["note"], "already under the cap")
        self.assertEqual(fr["sell the gain"]["shares_to_sell"], 3)      # 600 / 200
        self.assertEqual(fr["recover cost"]["shares_to_sell"], 12)      # 2400 / 200
        self.assertEqual(fr["recover cost"]["shares_kept"], 3)
        lv = res["sizing"]["AAPL"]["levels"]
        self.assertEqual((lv["ma50"], lv["ma200"], lv["next_earnings"]), (195.0, 180.0, "2026-01-29"))

    def test_sizing_a_ticker_without_stats_or_not_held(self):
        res = holdings.analyse(self.c, CSV, ["QQQ", "MSFT"], [0.15], None)
        self.assertIn({"symbol": "QQQ", "reason": "run stats.py QQQ"}, res["skipped"])
        self.assertEqual(res["sizing"]["MSFT"]["error"], "MSFT is not in the CSV")

    def test_total_flag_for_a_partial_csv(self):
        res = holdings.analyse(self.c, CSV, [], [0.15], 24000.0)
        self.assertAlmostEqual({p["ticker"]: p for p in res["positions"]}["AAPL"]["weight"], 0.125)
        self.assertEqual(res["portfolio"]["total_from"], "flag")

    def test_price_falls_back_to_the_csv_value(self):
        self.c.execute("DELETE FROM prices WHERE ticker = 'QQQ'")
        res = holdings.analyse(self.c, CSV, [], [0.15], None)
        q = {p["ticker"]: p for p in res["positions"]}["QQQ"]
        self.assertEqual((q["price"], q["price_from"]), (450.0, "csv"))

    def test_a_directory_of_csvs_merges_like_accounts(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "tfsa.csv"), "w") as f:
                f.write("Symbol,Quantity,Average Cost,Account\nAAPL,10,150.00,TFSA\nQQQ,20,400.00,TFSA\n")
            with open(os.path.join(d, "rrsp.csv"), "w") as f:
                f.write("Ticker,Shares,Book Cost,Account Name\nAAPL,5,900.00,RRSP\nXEQT.TO,3,100,RRSP\n")
            with open(os.path.join(d, "notes.txt"), "w") as f:
                f.write("ignored\n")
            res = holdings.analyse(self.c, d, ["AAPL"], [0.15], None)
            self.assertEqual([os.path.basename(f) for f in res["files"]], ["rrsp.csv", "tfsa.csv"])
            self.assertEqual(res["columns"]["rrsp.csv"]["cost_mode"], "total")
            self.assertEqual(res["columns"]["tfsa.csv"]["cost_mode"], "per_share")
            aapl = {p["ticker"]: p for p in res["positions"]}["AAPL"]
            self.assertEqual((aapl["shares"], aapl["cost"], aapl["value"]), (15, 2400.0, 3000.0))
            self.assertEqual(sorted((r["account"], r["file"]) for r in aapl["accounts"]), [("RRSP", "rrsp.csv"), ("TFSA", "tfsa.csv")])
            self.assertEqual(res["portfolio"]["total"], 12000.0)
            self.assertEqual(res["sizing"]["AAPL"]["frames"][0]["shares_to_sell"], 6)
            self.assertIn({"symbol": "XEQT.TO", "reason": "not a US listing", "file": "rrsp.csv"}, res["skipped"])
            empty = os.path.join(d, "sub_empty")
            os.mkdir(empty)
            with self.assertRaises(common.FetchError) as cm:
                holdings.analyse(self.c, empty, [], [0.15], None)
            self.assertIn("no *.csv", str(cm.exception))

    def test_database_is_unchanged(self):
        before = counts(self.c)
        db.read_only(self.c)
        holdings.analyse(self.c, CSV, ["AAPL"], [0.15], None)
        self.c.set_authorizer(None)
        self.assertEqual(counts(self.c), before)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = self.tmp.name
        c = db.connect(self.proj)
        seed(c)
        c.close()

    def tearDown(self):
        self.tmp.cleanup()

    def run_h(self, *args_):
        out = subprocess.run([sys.executable, os.path.join(HERE, "holdings.py"), *args_, "--project", self.proj],
                             capture_output=True, text=True)
        return out.returncode, out.stdout

    def test_json_md_and_no_files_written(self):
        code, out = self.run_h(CSV, "--size", "aapl")
        self.assertEqual(code, 0, out)
        obj = json.loads(out)
        self.assertEqual(obj["columns"]["holdings_two_accounts.csv"]["ticker"], "Symbol")
        self.assertEqual(obj["files"], [CSV])
        self.assertEqual(obj["sizing"]["AAPL"]["frames"][0]["shares_to_sell"], 6)
        code, out = self.run_h(CSV, "--size", "AAPL", "--md")
        self.assertIn("| AAPL | stock |", out)
        self.assertIn("**Look-through**", out)
        self.assertIn("| cap at 15.0% | 6 |", out)
        self.assertIn("next earnings 2026-01-29", out)
        self.assertIn("SHOP.TO (not a US listing)", out)
        self.assertEqual(sorted(os.listdir(os.path.join(self.proj, "data"))),
                         sorted(f for f in os.listdir(os.path.join(self.proj, "data")) if f in (".gitignore", "config.json", "invest.db")))
        code, out = self.run_h(os.path.join(self.proj, "missing.csv"))
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
