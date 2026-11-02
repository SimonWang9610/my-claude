"""fund.py: contract, kinds, SPY present/missing, EQUITY refused, missing entries, sources, store paths, raw parsing (no network)."""
import copy
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import common
import fund
import prices
from tests import fx
from tests.test_prices import series as price_rows
from tests.test_run_sh import SYSTEM_PATH, fake

PROFILES = fx.load("fund_profiles.json")
NOW = dt.datetime(2026, 11, 2, 18, tzinfo=dt.timezone.utc)
LAST = "2026-10-30"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ctx(root=None):
    return common.Ctx(root or tempfile.mkdtemp(), None, now=lambda: NOW)


def rows(n_years=11):
    """Weekday rows ending LAST, 10%/yr; under a year is the tail of a long series (the helper needs 200+ rows)."""
    r = price_rows(max(n_years, 2), LAST)
    return r if n_years >= 2 else r[-int(n_years * 261):]


def spy_series(n_years=11):
    """A SPY series.json ending the Monday after the fund's last close, so its window end must be clipped to LAST."""
    return prices.series_json("SPY", price_rows(n_years, "2026-11-02"), "S7", "2026-10-31T00:00:00Z")


def write_spy(store, s):
    os.makedirs(os.path.join(store, "market"), exist_ok=True)
    with open(os.path.join(store, "market", "SPY.json"), "w") as f:
        json.dump(s, f)


def build(ticker, n_years=11, spy=None, profile=None):
    c = ctx()
    if spy is not None:
        write_spy(c.root, spy)
    out, series = fund.build(c, ticker, 10, os.path.join(c.root, "market"),
                             loader=lambda t: copy.deepcopy(profile or PROFILES[t]),
                             price_loader=lambda t, y: {"version": "1.7.0", "rows": rows(n_years), "info": {}})
    return out, series


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.out, self.series = build("QQQ", spy=spy_series())

    def test_top_level_keys_and_identity(self):
        self.assertEqual(list(self.out), [
            "ticker", "quote_type", "name", "as_of", "retrieved", "kind", "kind_reason", "category", "family", "tracks",
            "expense_ratio", "total_assets", "inception", "distribution_yield", "top_holdings", "top_holdings_weight",
            "sector_weights", "asset_classes", "equity_pe", "price", "spy", "flags", "sources", "missing"])
        o = self.out
        self.assertEqual((o["ticker"], o["quote_type"], o["name"], o["as_of"], o["retrieved"]),
                         ("QQQ", "ETF", "Invesco QQQ Trust", LAST, "2026-11-02T18:00:00Z"))
        self.assertEqual((o["category"], o["family"], o["tracks"]), ("Large Growth", "Invesco", "Nasdaq-100 Index"))
        self.assertEqual((o["expense_ratio"], o["total_assets"], o["inception"], o["distribution_yield"], o["equity_pe"]),
                         (0.002, 380000000000.0, "1999-03-10", 0.0042, 28.3))
        self.assertEqual(o["top_holdings"][0], {"symbol": "NVDA", "name": "NVIDIA Corp", "weight": 0.083})
        self.assertAlmostEqual(o["top_holdings_weight"], 0.488, 6)
        self.assertEqual(o["sector_weights"]["technology"], 0.603)
        self.assertEqual(o["asset_classes"]["stock"], 0.996)
        self.assertEqual(o["missing"], [])
        json.dumps(o)

    def test_price_block_follows_prices_and_momentum_conventions(self):
        p = self.out["price"]
        self.assertEqual(set(p), {"last", "date", "currency", "high_52w", "low_52w", "ma50", "ma200", "return_1m",
                                  "return_6m", "return_12m", "return_5y_cagr", "return_10y_cagr", "realized_vol_30d",
                                  "realized_vol_1y", "trend", "trend_rule", "src"})
        r = rows()
        self.assertEqual((p["last"], p["date"], p["currency"], p["src"]), (r[-1]["close"], LAST, "USD", "S1"))
        self.assertAlmostEqual(p["return_12m"], r[-1]["adj_close"] / r[-253]["adj_close"] - 1, 6)   # 252 trading days
        self.assertAlmostEqual(p["return_1m"], r[-1]["adj_close"] / r[-22]["adj_close"] - 1, 6)
        self.assertAlmostEqual(p["return_5y_cagr"], 0.10, 2)                                        # yearly rate
        self.assertAlmostEqual(p["return_10y_cagr"], 0.10, 2)
        self.assertAlmostEqual(p["ma50"], sum(x["close"] for x in r[-50:]) / 50, 6)
        self.assertGreater(p["realized_vol_30d"], 0)
        self.assertGreaterEqual(p["high_52w"], p["last"])
        self.assertEqual((p["trend"], p["trend_rule"][:4]), ("up", "ST1:"))

    def test_sources_block(self):
        s = self.out["sources"]
        self.assertEqual(list(s), ["S1", "S2", "S7"])
        self.assertEqual(s["S1"], {"class": "secondary", "what": "QQQ daily prices, averages, returns, volatility (Yahoo via yfinance 1.7.0)",
                                   "url": "https://finance.yahoo.com/quote/QQQ/history/", "as_of": LAST, "retrieved": "2026-11-02"})
        self.assertEqual(s["S2"]["url"], "https://finance.yahoo.com/quote/QQQ/holdings/")
        self.assertIn("funds_data", s["S2"]["what"])
        self.assertEqual((s["S2"]["class"], s["S2"]["as_of"]), ("secondary", "2026-11-02"))
        self.assertEqual(s["S7"], {"class": "secondary", "what": "SPY adjusted closes for the same windows (market/SPY.json)",
                                   "url": "https://finance.yahoo.com/quote/SPY/history/", "as_of": LAST, "retrieved": "2026-10-31"})

    def test_series_is_prices_series_shape(self):
        s = self.series
        self.assertEqual((s["ticker"], s["src"], len(s["dates"]), len(s["adj_close"])), ("QQQ", "S1", len(rows()), len(rows())))
        self.assertEqual(set(s), {"ticker", "src", "retrieved", "dates", "close", "adj_close", "dividends", "splits"})


class KindTests(unittest.TestCase):
    def test_index_fund(self):
        out, _ = build("QQQ")
        self.assertEqual((out["kind"], out["kind_reason"], out["flags"]), ("index", "tracks 'Nasdaq-100 Index'", []))

    def test_leveraged_inverse(self):
        out, _ = build("SQQQ")
        self.assertEqual(out["kind"], "inverse")
        self.assertEqual(out["kind_reason"], "name contains 'Ultra', 'Short'; category 'Trading--Inverse Equity' -> leveraged inverse")
        self.assertEqual(out["flags"], ["leveraged or inverse: resets daily, not built for holding (fund's own prospectus governs)"])
        self.assertIsNone(out["tracks"])                     # description says "the index" only

    def test_covered_call(self):
        out, _ = build("JEPI")
        self.assertEqual((out["kind"], out["kind_reason"]), ("covered-call", "name contains 'Premium Income' -> covered-call"))
        self.assertEqual(out["flags"], ["covered-call: gives up upside for income"])
        self.assertEqual(out["tracks"], "S&P 500 Total Return Index")

    def test_bond(self):
        out, _ = build("BND")
        self.assertEqual((out["kind"], out["kind_reason"]), ("bond", "category 'Intermediate Core Bond' names bonds"))
        self.assertEqual(out["tracks"], "Bloomberg U.S. Aggregate Float Adjusted Index")

    def test_classify_rules_and_look_alikes(self):
        c = fund.classify
        self.assertEqual(c("Vanguard Short-Term Bond ETF", "Short-Term Bond", "", None, {"bond": 0.98}, {})[0], "bond")
        self.assertEqual(c("JPMorgan Ultra-Short Income ETF", "Ultrashort Bond", "", None, {"bond": 0.9}, {})[0], "bond")
        self.assertEqual(c("ProShares UltraShort QQQ", "Trading--Inverse Equity", "", None, None, None)[0], "inverse")
        self.assertEqual(c("Direxion Daily Semiconductor Bull 3X Shares", "Trading--Leveraged Equity", "", None, None, None)[0],
                         "leveraged")
        self.assertEqual(c("YieldMax TSLA Option Income Strategy ETF", None, "", None, None, None)[0], "covered-call")
        self.assertEqual(c("Some Fund", "Derivative Income", "", None, None, None)[0], "covered-call")
        self.assertEqual(c("Schwab U.S. Dividend Equity ETF", "Large Value", "", "Dow Jones U.S. Dividend 100 Index", None, None),
                         ("dividend", "name contains 'Dividend'"))
        self.assertEqual(c("Vanguard Information Technology ETF", "Technology", "", "MSCI US IMI Index", None, None)[0], "sector")
        self.assertEqual(c("Global X Robotics ETF", "Miscellaneous Sector", "", None, None, {"technology": 0.85})[0], "sector")
        self.assertEqual(c("Global X Robotics ETF", "Miscellaneous Sector", "", None, None, {"technology": 0.5})[0], "other")
        self.assertEqual(c("Vanguard Total International Stock ETF", "Foreign Large Blend", "", "FTSE Global All Cap ex US Index", None, None),
                         ("international", "category 'Foreign Large Blend' contains 'Foreign'"))
        self.assertEqual(c("iShares MSCI Emerging Markets ETF", "Diversified Emerging Mkts", "", None, None, None)[0], "international")
        self.assertEqual(c("SPDR S&P 500 ETF Trust", "Large Blend", "The fund tracks the S&P 500 Index.", "S&P 500 Index", None, None)[0], "index")
        self.assertEqual(c("Some Core Fund", "Large Blend", "The fund holds large companies.", None, None, None)[0], "index")
        self.assertEqual(c("ARK Innovation ETF", "Mid-Cap Growth", "The fund is actively managed.", None, None, None),
                         ("other", "description says 'actively managed' and names no index"))
        self.assertEqual(c("Some Trust", None, None, None, None, None)[0], "other")

    def test_tracks_from_description(self):
        self.assertEqual(fund.tracks_from("It tracks the S&P 500® Index. The index is broad."), "S&P 500 Index")
        self.assertIsNone(fund.tracks_from("It tracks the Underlying Index."))
        self.assertIsNone(fund.tracks_from("The index includes 100 companies."))
        self.assertIsNone(fund.tracks_from(None))

    def test_concentration_flag_on_top_holdings(self):
        p = copy.deepcopy(PROFILES["QQQ"])
        p["top_holdings"] = [{"symbol": "A", "name": "A", "weight": 0.3}, {"symbol": "B", "name": "B", "weight": 0.25}]
        out, _ = build("QQQ", profile=p)
        self.assertEqual(out["flags"], ["concentrated: top 2 holdings are 55% of the fund"])


class SpyTests(unittest.TestCase):
    def test_spy_present_uses_market_json_clipped_to_the_fund_date(self):
        out, _ = build("QQQ", spy=spy_series())
        s = out["spy"]
        self.assertEqual(set(s), {"return_1m", "return_6m", "return_12m", "return_5y_cagr", "return_10y_cagr", "as_of", "basis", "src"})
        self.assertEqual((s["as_of"], s["basis"], s["src"]), (LAST, "market/SPY.json adj_close", "S7"))
        self.assertAlmostEqual(s["return_5y_cagr"], 0.10, 2)
        r = rows()
        self.assertAlmostEqual(s["return_12m"], r[-1]["adj_close"] / r[-253]["adj_close"] - 1, 6)  # same window, same end
        self.assertIn("S7", out["sources"])

    def test_spy_missing_is_null_with_reason_and_no_source(self):
        out, _ = build("QQQ")
        self.assertIsNone(out["spy"])
        self.assertEqual(out["missing"], [{"field": "spy", "reason": "no market/SPY.json in the store (market.py writes it)"}])
        self.assertEqual(list(out["sources"]), ["S1", "S2"])

    def test_short_spy_nulls_fields_not_the_block(self):
        out, _ = build("QQQ", spy=fx.load("market_spy.json"))        # 13 yearly closes, ends 2026-10-14
        s = out["spy"]
        self.assertEqual(s["as_of"], "2026-10-14")
        self.assertIsNone(s["return_1m"])
        self.assertIsNotNone(s["return_5y_cagr"])
        self.assertIn({"field": "spy.return_12m", "reason": "needs 253 closes, have 13"}, out["missing"])


class RefusalAndMissingTests(unittest.TestCase):
    def test_equity_ticker_is_refused_before_prices(self):
        calls = []
        c = ctx()
        with self.assertRaises(common.FetchError) as cm:
            fund.build(c, "AAPL", 10, None, loader=lambda t: PROFILES["AAPL"],
                       price_loader=lambda t, y: calls.append(t))
        self.assertEqual(str(cm.exception), "AAPL is quoteType EQUITY, not a fund: use facts.py for a company")
        self.assertEqual(calls, [])

    def test_nothing_from_yahoo_is_an_error(self):
        with self.assertRaises(common.FetchError) as cm:
            fund.build(ctx(), "ZZZZ", 10, None, loader=lambda t: {"version": "1.7.0", "info": {}, "failed": {"info": "404"}},
                       price_loader=lambda t, y: None)
        self.assertIn("no fund data for ZZZZ (info: 404)", str(cm.exception))

    def test_missing_entries_for_absent_fields(self):
        out, _ = build("SQQQ", n_years=0.5)                  # ~130 closes: 1m and 6m windows only, no MA200
        miss = {m["field"]: m["reason"] for m in out["missing"]}
        self.assertEqual(miss["tracks"], "description names no index")
        self.assertEqual(miss["equity_pe"], "equity_holdings: topHoldings has no equityHoldings")
        self.assertEqual(miss["top_holdings"], "Yahoo lists no holdings")
        self.assertEqual(miss["sector_weights"], "Yahoo lists no sector weights")
        self.assertEqual(miss["top_holdings_weight"], "no holding weights")
        self.assertEqual(miss["price.return_12m"], "needs 253 closes, have %d" % len(rows(0.5)))
        self.assertIn("history starts", miss["price.return_5y_cagr"])
        self.assertIn("price.realized_vol_1y", miss)
        self.assertEqual(miss["price.trend"], "needs the 50- and 200-day averages")
        self.assertEqual(miss["spy"], "no market/SPY.json in the store (market.py writes it)")
        for f in ("tracks", "equity_pe", "top_holdings", "sector_weights", "top_holdings_weight"):
            self.assertIsNone(out[f])
        for f in ("return_12m", "return_10y_cagr", "ma200", "trend"):
            self.assertIsNone(out["price"][f])
        self.assertIsNotNone(out["price"]["return_6m"])
        self.assertIsNotNone(out["price"]["ma50"])

    def test_unknown_quote_type_passes_with_a_missing_entry(self):
        p = copy.deepcopy(PROFILES["QQQ"])
        p["quote_type"] = p["info"]["quoteType"] = None
        p["info"]["currency"] = None
        out, _ = build("QQQ", profile=p)
        self.assertIsNone(out["quote_type"])
        self.assertIn({"field": "quote_type", "reason": "Yahoo reports no quoteType"}, out["missing"])
        self.assertIn({"field": "price.currency", "reason": "currency not in Yahoo info"}, out["missing"])


class RunTests(unittest.TestCase):
    def test_run_writes_fund_and_series_under_store(self):
        store = tempfile.mkdtemp()
        write_spy(store, spy_series())
        with mock.patch.object(fund, "load_profile", lambda t: copy.deepcopy(PROFILES[t])), \
             mock.patch.object(prices, "load_yfinance", lambda t, y: {"version": "1.7.0", "rows": rows(), "info": {}}), \
             mock.patch("builtins.print") as pr:
            m = fund.run(["qqq", "--store", store])
        self.assertEqual(m["out"], os.path.join(store, "stocks", "QQQ", "facts", "fund.json"))
        self.assertEqual(m["series"], os.path.join(store, "stocks", "QQQ", "facts", "series.json"))
        self.assertEqual((m["ok"], m["ticker"], m["kind"], m["spy"], m["missing"]), (True, "QQQ", "index", True, []))
        self.assertEqual(json.loads(pr.call_args[0][0]), m)
        with open(m["out"]) as f:
            doc = json.load(f)
        self.assertEqual((doc["ticker"], doc["kind"], doc["spy"]["src"]), ("QQQ", "index", "S7"))
        with open(m["series"]) as f:
            self.assertEqual(json.load(f)["ticker"], "QQQ")
        self.assertTrue(os.path.exists(os.path.join(store, ".gitignore")))
        self.assertTrue(os.path.isdir(os.path.join(store, ".cache", "prices")))

    def test_profile_is_cached_one_trading_day(self):
        c, calls = ctx(), []

        def loader(t):
            calls.append(t)
            return PROFILES["QQQ"]
        fund.get_profile(c, "QQQ", loader)
        fund.get_profile(c, "QQQ", loader)
        self.assertEqual(calls, ["QQQ"])
        fund.get_profile(c.with_refresh(), "QQQ", loader)
        self.assertEqual(calls, ["QQQ", "QQQ"])

    def test_equity_refusal_is_an_error_envelope(self):
        store = tempfile.mkdtemp()
        with mock.patch.object(fund, "load_profile", lambda t: PROFILES["AAPL"]), mock.patch("builtins.print") as pr:
            with self.assertRaises(SystemExit):
                common.run_main("fund.py", fund.run, ["AAPL", "--store", store])
        env = json.loads(pr.call_args[0][0])
        self.assertEqual(env["script"], "fund.py")
        self.assertIn("use facts.py", env["error"])
        self.assertFalse(os.path.exists(os.path.join(store, "stocks", "AAPL", "facts", "fund.json")))

    def test_run_sh_provisions_the_venv_for_fund_py(self):
        tmp = tempfile.mkdtemp()
        proj, bin_ = os.path.join(tmp, "p"), os.path.join(tmp, "bin")
        os.makedirs(proj)
        fake(os.path.join(bin_, "python3.12"))
        r = subprocess.run(["bash", os.path.join(HERE, "run.sh"), tmp, "fund.py", "QQQ", "--project", proj],
                           capture_output=True, text=True,
                           env={"PATH": bin_ + ":" + SYSTEM_PATH, "HOME": tmp, "PIPLOG": os.path.join(tmp, "pip.log")}, cwd=tmp)
        self.assertIn("created data/.venv", r.stderr)
        self.assertTrue(r.stdout.startswith("FAKE %s/fund.py QQQ" % HERE), r.stdout)


class LoaderTests(unittest.TestCase):
    """load_profile against a fake yfinance module: frames are read through to_dict(), failures are recorded."""

    class Frame:
        def __init__(self, d):
            self.d = d

        def to_dict(self):
            return self.d

    def fake_yf(self, info, funds, version="1.7.0"):
        class FundsData:
            def __init__(self, f):
                for k, v in f.items():
                    setattr(self, k, v)
        class Ticker:
            def __init__(self, t):
                self.info = info
                self.funds_data = FundsData(funds)
        return type("yf", (), {"Ticker": Ticker, "__version__": version})

    def test_parses_frames_and_dicts(self):
        funds = {"description": "Tracks the Nasdaq-100 Index.",
                 "fund_overview": {"categoryName": "Large Growth", "family": "Invesco", "legalType": "Exchange Traded Fund"},
                 "fund_operations": self.Frame({"QQQ": {"Annual Report Expense Ratio": 0.002, "Annual Holdings Turnover": 0.08,
                                                         "Total Net Assets": 316000.0},
                                                "Category Average": {"Annual Report Expense Ratio": 0.009}}),
                 "equity_holdings": self.Frame({"QQQ": {"Price/Earnings": 28.3}, "Category Average": {"Price/Earnings": 25.0}}),
                 "top_holdings": self.Frame({"Name": {"NVDA": "NVIDIA Corp", "AAPL": "Apple Inc"},
                                             "Holding Percent": {"NVDA": 0.083, "AAPL": float("nan")}}),
                 "sector_weightings": {"technology": 0.603, "realestate": float("nan")},
                 "asset_classes": {"cashPosition": 0.004, "stockPosition": 0.996, "bondPosition": None}}
        info = {"longName": "Invesco QQQ Trust", "quoteType": "ETF", "category": "Large Growth", "fundFamily": "Invesco",
                "fundInceptionDate": 921024000, "totalAssets": 3.8e11, "yield": 0.0042, "navPrice": 681.2, "currency": "USD"}
        with mock.patch.dict(sys.modules, {"yfinance": self.fake_yf(info, funds)}):
            raw = fund.load_profile("QQQ")
        self.assertEqual((raw["version"], raw["quote_type"], raw["failed"]), ("1.7.0", "ETF", {}))
        self.assertEqual(raw["info"]["longName"], "Invesco QQQ Trust")
        self.assertEqual(raw["info"]["shortName"], None)
        self.assertEqual((raw["expense_ratio"], raw["equity_pe"]), (0.002, 28.3))
        self.assertEqual(raw["top_holdings"], [{"symbol": "NVDA", "name": "NVIDIA Corp", "weight": 0.083},
                                               {"symbol": "AAPL", "name": "Apple Inc", "weight": None}])
        self.assertEqual(raw["sector_weights"], {"technology": 0.603})
        self.assertEqual(raw["asset_classes"], {"cash": 0.004, "stock": 0.996})
        self.assertEqual(raw["overview"]["category"], "Large Growth")
        json.dumps(raw)

    def test_non_fund_records_failures_and_keeps_quote_type(self):
        class Boom:
            def __getattr__(self, name):
                raise ValueError("Only ETFs and Mutual Funds have funds data.")
        class Ticker:
            def __init__(self, t):
                self.info = {"longName": "Apple Inc.", "quoteType": "EQUITY", "currency": "USD"}
                self.funds_data = Boom()
        yf = type("yf", (), {"Ticker": Ticker, "__version__": "1.7.0"})
        with mock.patch.dict(sys.modules, {"yfinance": yf}):
            raw = fund.load_profile("AAPL")
        self.assertEqual(raw["quote_type"], "EQUITY")
        self.assertIsNone(raw["description"])
        self.assertIn("Only ETFs", raw["failed"]["description"])
        self.assertIn("top_holdings", raw["failed"])

    def test_missing_yfinance_gives_setup_hint(self):
        with mock.patch.dict(sys.modules, {"yfinance": None}):
            with self.assertRaises(common.FetchError) as cm:
                fund.load_profile("QQQ")
        self.assertIn("Python 3.10+", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
