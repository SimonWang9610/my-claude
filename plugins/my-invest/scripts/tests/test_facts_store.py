"""facts.py incremental orchestration against the store layout (fetchers mocked; no network)."""
import copy
import datetime as dt
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import common
import edgar
import facts
from tests import fx

SUB = fx.load("submissions_aapl.json")   # newest 10-Q filed 2026-07-31, newest filing 2026-10-08
UTC = dt.timezone.utc


def at(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)


def src(what, url, klass="primary"):
    return {"class": klass, "what": what, "url": url, "as_of": "x", "retrieved": "2026-10-14"}


EDGAR = {"ticker": "T", "cik": "0000320193", "name": "T", "sic": "3571", "sector_class": "manufacturer",
         "retrieved": "r",
         "sources": {"S1": src("companyfacts (XBRL) FY2016-FY2025", "http://cf"),
                     "S2": src("submissions: filings index", "http://sub")},
         "fundamentals": {"annual": [{"fy": 2025, "period_end": "2025-09-27", "filed": "2025-10-31", "src": "S1"}],
                          "concept_map": {}, "missing": []},
         "shares_history": [{"fy": 2025, "src": "S1"}]}
PRICES = {"sources": {"S1": src("daily prices (Yahoo)", "http://px", "secondary")}, "retrieved": "2026-10-14T22:00:00Z",
          "price": {"last": 1.0, "date": "2026-10-14", "src": "S1"}, "close_at": {},
          "series": {"src": "S1", "dates": ["2026-10-14"], "close": [1.0]}}
MACRO = {"sources": {"S1": src("dgs", "http://dgs"), "S2": src("erp", "http://erp", "secondary")},
         "macro": {"dgs10": 4.0, "dgs10_date": "2026-10-13", "src": "S1", "erp": 4.2, "erp_src": "S2"}}
MARKET = {"sources": {"S7": src("etfs", "http://etf", "secondary"), "S8": src("boc", "http://boc")},
          "sector_etf": "XLK", "market": {"spy": {"return_1m": 0.1, "src": "S7"}, "fx_usdcad": {"rate": 1.4, "src": "S8"},
                                          "missing": []}}
OPTIONS = {"sources": {"S9": src("chain", "http://opt", "secondary")}, "options": {"as_of": "d", "atm_iv": 0.3, "src": "S9"}}
CONSENSUS = {"sources": {"S12": src("analysts", "http://analysts", "secondary")},
             "consensus": {"available": True, "as_of": "d", "targets": {"mean": 300.0}, "src": "S12"}}
NEWS = {"sources": {"S1": src("submissions: filings index", "http://sub")},
        "window": {"since_days": 1095, "from": "2023-10-15", "to": "2026-10-14", "feed_oldest": "2024-01-02"},
        "filings": [{"form": "8-K", "filed": "2026-10-01", "url": "http://f/1", "src": "S1"}]}
NOW = at("2026-10-14 22:46")


def mk_ctx(now=NOW):
    return common.Ctx(tempfile.mkdtemp(), "ua x@y.z", now=lambda: now)


class Env:
    """Patches every fetcher; records which were called."""

    def __init__(self, test, sub=SUB, **over):
        self.d = dict(edgar=EDGAR, prices=PRICES, macro=MACRO, market=MARKET, options=OPTIONS, consensus=CONSENSUS,
                      news=NEWS)
        self.d.update(over)
        self.sub = sub
        self.calls = []
        self.mocks = {}
        for name, mod in (("edgar", edgar), ("prices", facts.prices), ("macro", facts.macro), ("market", facts.market),
                          ("options", facts.options), ("consensus", facts.consensus), ("news", facts.news)):
            m = mock.patch.object(mod, "build", side_effect=self._fn(name))
            self.mocks[name] = m.start()
            test.addCleanup(m.stop)
        for p in (mock.patch.object(edgar, "resolve_cik", return_value=(320193, "T", "t")),
                  mock.patch.object(common.Ctx, "get_json", side_effect=lambda *a, **k: (copy.deepcopy(self.sub), "2026-10-14T22:46:00Z"))):
            p.start()
            test.addCleanup(p.stop)

    def _fn(self, name):
        def fn(*a, **k):
            self.calls.append(name)
            v = self.d[name]
            if isinstance(v, Exception):
                raise v
            return copy.deepcopy(v)
        return fn


class DecisionTests(unittest.TestCase):
    PREV = {"cik": "0000320193", "sources": {"S1": src("companyfacts (XBRL)", "u")},
            "fundamentals": {"annual": [{"filed": "2025-10-31"}]}, "price": {"date": "2026-10-14"}}

    def test_expected_close_by_clock_and_weekend(self):
        self.assertEqual(facts.last_expected_close(at("2026-10-14 22:00")), "2026-10-14")   # Wed after close
        self.assertEqual(facts.last_expected_close(at("2026-10-14 15:00")), "2026-10-13")   # Wed in session
        self.assertEqual(facts.last_expected_close(at("2026-10-18 12:00")), "2026-10-16")   # Sunday -> Friday
        self.assertEqual(facts.last_expected_close(at("2026-10-19 08:00")), "2026-10-16")   # Monday pre-open

    def test_prices_stale_rules(self):
        after = {"price_retrieved": "2026-10-14T22:00:00Z"}
        self.assertFalse(facts.prices_stale("2026-10-14", after, NOW))
        self.assertTrue(facts.prices_stale("2026-10-13", after, NOW))                      # a session is missing
        self.assertFalse(facts.prices_stale("2026-10-13", {"price_checked_for": "2026-10-14"}, NOW))  # holiday: asked once
        self.assertTrue(facts.prices_stale("2026-10-14", {"price_retrieved": "2026-10-14T15:00:00Z"}, NOW))  # pre-close bar
        self.assertFalse(facts.prices_stale("2026-10-14", {}, at("2026-10-14 15:00")))     # in session: today's bar is partial
        self.assertTrue(facts.prices_stale(None, after, NOW))

    def test_new_periodic_filing_triggers_fundamentals_once(self):
        # the feed's newest 10-Q (2026-07-31) is after annual[0].filed (2025-10-31)
        self.assertEqual(facts.decide(self.PREV, {}, SUB, NOW), (True, True))
        # once acted on (periodic_seen), nothing newer -> reuse; prices still fresh
        last = {"periodic_seen": "2026-07-31", "price_retrieved": "2026-10-14T22:00:00Z"}
        self.assertEqual(facts.decide(self.PREV, last, SUB, NOW), (False, False))
        newer = copy.deepcopy(SUB)
        r = newer["filings"]["recent"]
        for k, v in (("filingDate", "2026-10-13"), ("form", "10-Q"), ("accessionNumber", "a"), ("primaryDocument", "d")):
            r[k].insert(0, v)
        self.assertEqual(facts.decide(self.PREV, last, newer, NOW), (True, True))

    def test_non_periodic_filings_do_not_trigger(self):
        sub = {"filings": {"recent": {"filingDate": ["2026-10-08", "2025-10-01"], "form": ["8-K", "4"]}}}
        self.assertFalse(edgar.needs_fundamentals(sub, "2025-10-31"))

    def test_stale_prices_alone(self):
        last = {"periodic_seen": "2026-07-31", "price_retrieved": "2026-10-13T22:00:00Z"}
        prev = dict(self.PREV, price={"date": "2026-10-13"})
        self.assertEqual(facts.decide(prev, last, SUB, NOW), (False, True))

    def test_force_or_unusable_cache_refetches_everything(self):
        self.assertEqual(facts.decide(self.PREV, {}, SUB, NOW, force=True), (True, True))
        self.assertEqual(facts.decide(None, None, SUB, NOW), (True, True))
        self.assertEqual(facts.decide({"cik": "1", "fundamentals": {"annual": []}}, {}, SUB, NOW), (True, True))

    def test_news_window(self):
        self.assertEqual(facts.news_days(None, NOW), 90)
        self.assertEqual(facts.news_days({"retrieved": "2026-10-10T01:00:00Z"}, NOW), 4)
        self.assertEqual(facts.news_days({"retrieved": "2026-10-14T01:00:00Z"}, NOW), 1)
        self.assertEqual(facts.news_days({"retrieved": "2026-10-10T01:00:00Z"}, NOW, force=True), 90)

    def test_merge_filings_dedupes_and_expires(self):
        new = [{"url": "u2", "filed": "2026-10-13"}]
        old = [{"url": "u2", "filed": "2026-10-13"}, {"url": "u1", "filed": "2026-09-01"},
               {"url": "u0", "filed": "2026-01-01"}]
        got = facts.merge_filings(new, old, dt.date(2026, 10, 14))
        self.assertEqual([f["url"] for f in got], ["u2", "u1"])


class AssembleTests(unittest.TestCase):
    def first(self, **over):
        env = Env(self, **over)
        ctx = mk_ctx()
        f, s, st = facts.assemble(ctx, "T", os.path.join(ctx.root, "market"))
        return env, ctx, f, s, st

    def test_first_run_fetches_everything_with_stable_ids(self):
        env, ctx, f, s, st = self.first()
        self.assertEqual(env.calls, ["edgar", "prices", "macro", "market", "options", "consensus", "news"])
        self.assertEqual(list(f["sources"]), ["S1", "S2", "S3", "S4", "S5", "S7", "S8", "S9", "S12"])   # S6 reserved
        self.assertEqual(f["price"]["src"], "S3")
        self.assertEqual((f["macro"]["src"], f["macro"]["erp_src"]), ("S4", "S5"))
        self.assertEqual(f["filings_recent"][0]["src"], "S2")        # news submissions dedupes onto edgar's S2
        self.assertEqual((f["market"]["spy"]["src"], f["market"]["fx_usdcad"]["src"], f["options"]["src"]),
                         ("S7", "S8", "S9"))
        self.assertEqual(s["src"], "S3")
        self.assertEqual(f["sector_etf"], "XLK")
        self.assertEqual((f["consensus"]["src"], f["consensus"]["targets"]["mean"]), ("S12", 300.0))
        self.assertEqual(f["changed"], ["prices", "fundamentals", "filings", "macro", "market", "options", "consensus"])
        self.assertEqual(st["last_run"]["news_since"], "2026-07-16")             # researcher window: 90 days
        kw = env.mocks["news"].call_args[1]
        self.assertEqual((kw["since"], kw["forms"]), (1095, ["8-K", "10-K", "10-Q"]))   # filings_recent: three years
        self.assertEqual(f["filings_window"], {"from": "2023-10-15", "to": "2026-10-14", "complete": False})
        self.assertEqual(st["reused"], [])
        self.assertEqual(st["last_run"]["periodic_seen"], "2026-07-31")
        self.assertEqual(st["last_run"]["annual_filed"], "2025-10-31")
        self.assertEqual(st["last_run"]["price_date"], "2026-10-14")
        self.assertNotIn("fetch_errors", f)
        self.assertIsNone(f["insiders"])

    def test_second_run_reuses_fundamentals_and_prices(self):
        env, ctx, f, s, st = self.first()
        env2 = Env(self)
        f2, s2, st2 = facts.assemble(ctx, "T", os.path.join(ctx.root, "market"), prev=f, last=st["last_run"],
                                     series_prev=s)
        self.assertEqual(env2.calls, ["macro", "market", "options", "consensus", "news"])    # no edgar, no prices
        self.assertEqual(st2["reused"], ["fundamentals", "prices"])
        self.assertEqual(f2["changed"], [])
        self.assertEqual(f2["fundamentals"]["annual"], f["fundamentals"]["annual"])
        self.assertEqual(f2["fundamentals"]["shares_history"], f["fundamentals"]["shares_history"])
        self.assertEqual(f2["price"], f["price"])
        self.assertEqual(s2, s)
        self.assertEqual(list(f2["sources"]), list(f["sources"]))
        self.assertEqual(f2["filings_recent"], f["filings_recent"])
        self.assertEqual(st2["last_run"]["news_since"], "2026-10-13")           # researcher window: since last run
        self.assertEqual(env2.mocks["news"].call_args[1]["since"], 1095)        # filings_recent is not trimmed to it
        self.assertEqual(st2["last_run"]["periodic_seen"], "2026-07-31")

    def test_new_filing_and_changed_options_are_reported(self):
        env, ctx, f, s, st = self.first()
        news2 = copy.deepcopy(NEWS)
        news2["filings"] = [{"form": "8-K", "filed": "2026-10-14", "url": "http://f/2", "src": "S1"}]
        opt2 = copy.deepcopy(OPTIONS)
        opt2["options"]["atm_iv"] = 0.35
        Env(self, news=news2, options=opt2)
        f2, _, _ = facts.assemble(ctx, "T", os.path.join(ctx.root, "market"), prev=f, last=st["last_run"], series_prev=s)
        self.assertEqual(f2["changed"], ["filings", "options"])
        self.assertEqual([x["url"] for x in f2["filings_recent"]], ["http://f/2", "http://f/1"])

    def test_new_10q_refetches_fundamentals_and_prices(self):
        env, ctx, f, s, st = self.first()
        sub2 = copy.deepcopy(SUB)
        r = sub2["filings"]["recent"]
        for k, v in (("filingDate", "2026-10-14"), ("form", "10-Q"), ("accessionNumber", "a"), ("primaryDocument", "d")):
            r[k].insert(0, v)
        env2 = Env(self, sub=sub2)
        _, _, st2 = facts.assemble(ctx, "T", os.path.join(ctx.root, "market"), prev=f, last=st["last_run"], series_prev=s)
        self.assertEqual(env2.calls[:2], ["edgar", "prices"])
        self.assertEqual(st2["last_run"]["periodic_seen"], "2026-10-14")

    def test_refresh_forces_everything(self):
        env, ctx, f, s, st = self.first()
        env2 = Env(self)
        f2, _, _ = facts.assemble(ctx, "T", os.path.join(ctx.root, "market"), prev=f, last=st["last_run"],
                                  series_prev=s, force=True)
        self.assertEqual(env2.calls, ["edgar", "prices", "macro", "market", "options", "consensus", "news"])
        self.assertEqual(env2.mocks["news"].call_args[1]["since"], 1095)
        self.assertEqual(len(f2["changed"]), 7)

    def test_filings_window_complete_when_feed_reaches_back_three_years(self):
        news2 = copy.deepcopy(NEWS)
        news2["window"]["feed_oldest"] = "2023-01-05"
        env, ctx, f, s, st = self.first(news=news2)
        self.assertEqual(f["filings_window"], {"from": "2023-10-15", "to": "2026-10-14", "complete": True})
        # a later run whose feed has rolled forward keeps the earlier completeness and the older rows
        old = dict(NEWS["filings"][0], url="http://f/old", filed="2024-02-01")
        f["filings_recent"].append(old)
        Env(self)
        f2, _, _ = facts.assemble(ctx, "T", os.path.join(ctx.root, "market"), prev=f, last=st["last_run"], series_prev=s)
        self.assertTrue(f2["filings_window"]["complete"])
        self.assertEqual([x["url"] for x in f2["filings_recent"]], ["http://f/1", "http://f/old"])   # deduped by url

    def test_group_failure_degrades_and_keeps_other_ids(self):
        env, ctx, f, s, st = self.first(prices=common.FetchError("yfinance missing"), market=common.FetchError("down"))
        self.assertIsNone(f["price"])
        self.assertIsNone(s)
        self.assertIsNone(f["market"])
        self.assertEqual([e["script"] for e in f["fetch_errors"]], ["prices.py", "market.py"])
        self.assertEqual(f["macro"]["src"], "S4")            # ids do not shift
        self.assertEqual(list(f["sources"]), ["S1", "S2", "S4", "S5", "S9", "S12"])


class RunTests(unittest.TestCase):
    def run_facts(self, *extra, here=None):
        out = io.StringIO()
        with mock.patch.object(facts, "HERE", here or tempfile.mkdtemp()), redirect_stdout(out):
            facts.run(["T", "--data", self.data, "--ua", "x y@z.w", *extra])
        return json.loads(out.getvalue())

    def setUp(self):
        self.data, self.proj = tempfile.mkdtemp(), tempfile.mkdtemp()
        self.env = Env(self)

    def test_run_writes_store_layout_then_second_run_is_incremental(self):
        m1 = self.run_facts("--project", self.proj)
        folder = os.path.join(self.proj, "data", "stocks", "T")
        self.assertEqual(m1["facts"], os.path.join(folder, "facts", "facts.json"))
        for name in ("facts.json", "series.json", "last_run.json"):
            self.assertTrue(os.path.exists(os.path.join(folder, "facts", name)), name)
        self.assertEqual(m1["metrics"], "skipped")
        self.assertEqual(len(m1["changed"]), 7)
        with open(os.path.join(folder, "facts", "facts.json")) as f:
            written = json.load(f)
        self.assertEqual(written["changed"], m1["changed"])
        self.assertIn("momentum", written)
        self.assertEqual(os.listdir(self.data), [])                 # nothing written under --data
        self.env.calls.clear()
        m2 = self.run_facts("--project", self.proj)
        self.assertNotIn("edgar", self.env.calls)
        self.assertNotIn("prices", self.env.calls)
        self.assertEqual(m2["changed"], [])
        self.assertEqual(m2["reused"], ["fundamentals", "prices"])

    def test_store_flag_and_out(self):
        store = os.path.join(self.proj, "elsewhere")
        m = self.run_facts("--store", store)
        self.assertEqual(m["facts"], os.path.join(store, "stocks", "T", "facts", "facts.json"))
        outp = os.path.join(self.proj, "o", "T.json")
        self.run_facts("--out", outp)
        self.assertTrue(os.path.exists(outp))
        self.assertTrue(os.path.exists(os.path.join(self.proj, "o", "T.series.json")))
        self.assertTrue(os.path.exists(os.path.join(self.proj, "o", "T.last_run.json")))

    def test_bad_ticker_refused_but_folder_path_accepted(self):
        with self.assertRaises(common.FetchError):
            facts.run(["A$B", "--data", self.data])
        folder = os.path.join(self.proj, "data", "stocks", "T")
        out = io.StringIO()
        with mock.patch.object(facts, "HERE", tempfile.mkdtemp()), redirect_stdout(out):
            facts.run([folder, "--data", self.data, "--ua", "x y@z.w"])
        self.assertEqual(json.loads(out.getvalue())["facts"], os.path.join(folder, "facts", "facts.json"))


if __name__ == "__main__":
    unittest.main()
