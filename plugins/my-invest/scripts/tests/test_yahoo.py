import contextlib
import datetime as dt
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import db  # noqa: E402
import yahoo  # noqa: E402

TODAY = dt.date(2026, 11, 3)


class FakeFrame:
    """The slice of a pandas DataFrame the loaders use: len() and iterrows()."""

    def __init__(self, rows):
        self.rows = rows  # [(index, {column: value})]

    def __len__(self):
        return len(self.rows)

    def iterrows(self):
        return iter(self.rows)


def price_rows(days):
    return [(d, {"Open": 1.0, "High": 2.0, "Low": 0.5, "Close": 1.5, "Adj Close": 1.4, "Volume": 100.0}) for d in days]


class FakeFunds:
    top_holdings = FakeFrame([("NVDA", {"Name": "NVIDIA Corp", "Holding Percent": 0.0866}),
                              ("AAPL", {"Name": "Apple Inc", "Holding Percent": 0.08})])
    sector_weightings = {"technology": 0.5, "communication_services": 0.15}
    fund_overview = {"categoryName": "Large Growth", "family": "Invesco", "legalType": "Exchange Traded Fund"}


class FakeTicker:
    def __init__(self, info, frame=None, funds=None, targets=None, calendar=None):
        self.info_, self.frame, self.calls = info, frame, []
        self.funds_data = funds
        self.analyst_price_targets = targets or {}
        self.calendar = calendar or {}

    def history(self, **kw):
        self.calls.append(kw)
        return self.frame

    def get_info(self):
        return self.info_


STOCK = {"quoteType": "EQUITY", "longName": "Apple Inc.", "exchange": "NMS", "fullExchangeName": "NasdaqGS", "sector": "Technology",
         "industry": "Consumer Electronics", "currency": "USD", "numberOfAnalystOpinions": 40, "recommendationKey": "buy",
         "recommendationMean": 2.0}
FUND = {"quoteType": "ETF", "longName": "Invesco QQQ Trust", "exchange": "NGM", "currency": "USD", "category": "Large Growth",
        "totalAssets": 3.5e11, "fundInceptionDate": 921283200, "annualReportExpenseRatio": 0.002,
        "longBusinessSummary": "The investment seeks investment results that generally correspond to the price and yield "
                               "performance of the Nasdaq-100 Index®. The fund holds all stocks in the index."}


class Prices(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")

    def test_full_window_when_nothing_stored(self):
        t = FakeTicker(STOCK, FakeFrame(price_rows(["2021-11-05", "2026-11-02"])))
        res = yahoo.load_prices(self.c, t, "AAPL", 5, TODAY)
        self.assertEqual(t.calls, [{"period": "5y", "auto_adjust": False, "actions": False}])
        self.assertEqual((res["new_rows"], res["stored_days"], res["fetched_from"]), (2, 2, "2021-11-04"))
        r = db.one(self.c, "SELECT * FROM prices WHERE date = '2026-11-02'")
        self.assertEqual((r["close"], r["adj_close"], r["volume"]), (1.5, 1.4, 100))

    def test_incremental_from_day_after_last_stored(self):
        t = FakeTicker(STOCK, FakeFrame(price_rows(["2021-11-05", "2026-10-30"])))
        yahoo.load_prices(self.c, t, "AAPL", 5, TODAY)
        t2 = FakeTicker(STOCK, FakeFrame(price_rows(["2026-10-30", "2026-11-02"])))  # yfinance may repeat the start day
        res = yahoo.load_prices(self.c, t2, "AAPL", 5, TODAY)
        self.assertEqual(t2.calls[0]["start"], "2026-10-31")
        self.assertNotIn("period", t2.calls[0])
        self.assertEqual((res["fetched_from"], res["new_rows"], res["stored_days"]), ("2026-10-31", 1, 3))

    def test_full_window_again_when_stored_history_is_shorter(self):
        t = FakeTicker(STOCK, FakeFrame(price_rows(["2025-01-02", "2026-11-02"])))
        yahoo.load_prices(self.c, t, "AAPL", 5, TODAY)
        t2 = FakeTicker(STOCK, FakeFrame(price_rows(["2021-11-05"])))
        res = yahoo.load_prices(self.c, t2, "AAPL", 5, TODAY)
        self.assertEqual(t2.calls[0]["period"], "5y")
        self.assertEqual(res["stored_days"], 3)

    def test_nothing_to_fetch_when_stored_through_today(self):
        t = FakeTicker(STOCK, FakeFrame(price_rows(["2021-11-05", "2026-11-03"])))
        yahoo.load_prices(self.c, t, "AAPL", 5, TODAY)
        t2 = FakeTicker(STOCK, FakeFrame([]))
        res = yahoo.load_prices(self.c, t2, "AAPL", 5, TODAY)
        self.assertEqual(t2.calls, [])
        self.assertEqual((res["fetched_from"], res["new_rows"]), (None, 0))


class Profile(unittest.TestCase):
    def setUp(self):
        self.c = db.connect(path=":memory:")

    def test_stock_profile(self):
        res = yahoo.load_profile(self.c, FakeTicker(STOCK), "AAPL")
        self.assertEqual(res["kind"], "stock")
        s = db.one(self.c, "SELECT * FROM securities")
        self.assertEqual((s["ticker"], s["name"], s["kind"], s["exchange"], s["sector"]), ("AAPL", "Apple Inc.", "stock", "NasdaqGS", "Technology"))
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM funds").fetchone()[0], 0)

    def test_profile_keeps_cik_from_sec(self):
        sid = db.source(self.c, "https://data.sec.gov/x", "primary")
        db.upsert(self.c, "securities", [{"ticker": "AAPL", "cik": "0000320193", "kind": "stock", "updated_at": "t", "source_id": sid}])
        yahoo.load_profile(self.c, FakeTicker(STOCK), "AAPL")
        self.assertEqual(db.one(self.c, "SELECT cik FROM securities")["cik"], "0000320193")

    def test_fund_profile_with_weights(self):
        res = yahoo.load_profile(self.c, FakeTicker(FUND, funds=FakeFunds()), "QQQ")
        self.assertEqual((res["kind"], res["fund_weights"]), ("fund", 4))
        f = db.one(self.c, "SELECT * FROM funds")
        self.assertEqual((f["category"], f["expense_ratio"], f["net_assets"], f["inception"]), ("Large Growth", 0.002, 3.5e11, "1999-03-13"))
        self.assertEqual(f["tracks"], "Nasdaq-100 Index")
        self.assertEqual(db.one(self.c, "SELECT kind FROM securities")["kind"], "fund")
        w = {(r["kind"], r["key"]): r for r in db.rows(self.c, "SELECT * FROM fund_weights")}
        self.assertEqual(w[("holding", "NVDA")]["weight"], 0.0866)
        self.assertEqual(w[("holding", "NVDA")]["name"], "NVIDIA Corp")
        self.assertEqual(w[("sector", "technology")]["weight"], 0.5)
        urls = {r["url"] for r in db.rows(self.c, "SELECT url FROM sources")}
        self.assertIn("https://finance.yahoo.com/quote/QQQ/holdings/", urls)

    def test_expense_ratio_from_operations_table_then_percent_field(self):
        class Ops(FakeFunds):
            fund_operations = FakeFrame([("Annual Report Expense Ratio", {"QQQ": 0.0018, "Category Average": 0.009}),
                                         ("Annual Holdings Turnover", {"QQQ": 0.0, "Category Average": 0.6})])
        info = {k: v for k, v in FUND.items() if k != "annualReportExpenseRatio"}
        self.assertEqual(yahoo.expense_ratio(info, Ops()), 0.0018)
        self.assertEqual(yahoo.expense_ratio(dict(info, netExpenseRatio=0.18), FakeFunds()), 0.0018)
        self.assertIsNone(yahoo.expense_ratio(info, FakeFunds()))

    def test_tracked_index(self):
        self.assertEqual(yahoo.tracked_index("It tracks the S&P 500 Index. More text."), "S&P 500 Index")
        self.assertIsNone(yahoo.tracked_index("An actively managed fund."))
        self.assertEqual(yahoo.tracked_index("Seeks to track the Dow Jones U.S. Select Dividend Index."), "Dow Jones U.S. Select Dividend Index")


class Estimates(unittest.TestCase):
    def test_estimates_row(self):
        c = db.connect(path=":memory:")
        t = FakeTicker(STOCK, targets={"current": 270.0, "low": 200.0, "high": 350.0, "mean": 290.5, "median": 295.0},
                       calendar={"Earnings Date": [dt.date(2027, 1, 28), dt.date(2027, 2, 1)]})
        res = yahoo.load_estimates(c, t, "AAPL", "2026-11-03")
        e = db.one(c, "SELECT * FROM estimates")
        self.assertEqual((e["asof"], e["target_mean"], e["target_low"], e["analysts"], e["recommendation"], e["recommendation_mean"]),
                         ("2026-11-03", 290.5, 200.0, 40, "buy", 2.0))
        self.assertEqual(e["next_earnings"], "2027-01-28")
        self.assertEqual(res["target_high"], 350.0)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def run_yahoo(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = yahoo.common.run_main(yahoo.SCRIPT, yahoo.run, list(args) + ["--project", self.tmp.name])
        return code, json.loads(buf.getvalue())

    def test_missing_yfinance_message(self):
        saved = sys.modules.get("yfinance")
        sys.modules["yfinance"] = None  # makes `import yfinance` raise ImportError
        try:
            code, out = self.run_yahoo("prices", "AAPL")
        finally:
            if saved is None:
                sys.modules.pop("yfinance", None)
            else:
                sys.modules["yfinance"] = saved
        self.assertEqual(code, 1)
        self.assertEqual(out["error"], "yfinance is not installed: run this script through run.sh so data/.venv is created")

    def test_all_reports_failed_parts_and_skips_fund_estimates(self):
        class Broken(FakeTicker):
            def history(self, **kw):
                raise RuntimeError("Yahoo said no")
        saved = yahoo.make_ticker
        yahoo.make_ticker = lambda s: Broken(FUND, funds=FakeFunds())
        try:
            code, out = self.run_yahoo("all", "qqq")
        finally:
            yahoo.make_ticker = saved
        self.assertEqual(code, 0, out)
        self.assertEqual(out["profile"]["kind"], "fund")
        self.assertIn("Yahoo said no", out["failed"]["prices"])
        self.assertEqual(out["estimates"], "skipped for a fund")


if __name__ == "__main__":
    unittest.main()
