import datetime as dt
import io
import json
import os
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from unittest import mock

import common
from tests.fx import FakeResp


def utc(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)


class Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_miss_then_hit_keeps_original_retrieval_time(self):
        clk = Clock(utc("2026-10-14 10:00"))
        c = common.Cache(self.tmp.name, "edgar", clk)
        self.assertIsNone(c.get("u"))
        c.put("u", b"body")
        clk.t = utc("2026-10-14 20:00")
        self.assertEqual(c.get("u"), (b"body", "2026-10-14T10:00:00Z"))
        self.assertTrue(os.path.isdir(os.path.join(self.tmp.name, ".cache", "edgar")))

    def test_ttl_expiry_and_refresh(self):
        clk = Clock(utc("2026-10-14 10:00"))
        c = common.Cache(self.tmp.name, "edgar", clk)
        c.put("u", b"x")
        self.assertIsNone(c.get("u", refresh=True))
        clk.t = utc("2026-10-15 10:01")
        self.assertIsNone(c.get("u"))  # edgar TTL 1 day

    def test_news_ttl_six_hours(self):
        clk = Clock(utc("2026-10-14 10:00"))
        c = common.Cache(self.tmp.name, "news", clk)
        c.put("u", b"x")
        clk.t = utc("2026-10-14 15:59")
        self.assertIsNotNone(c.get("u"))
        clk.t = utc("2026-10-14 16:01")
        self.assertIsNone(c.get("u"))

    def test_prices_trading_day_rule_over_weekend(self):
        # Friday 2026-10-16 close fetched Friday evening; still the latest trading day on Sunday.
        fri, sun, mon = utc("2026-10-16 22:00"), utc("2026-10-18 12:00"), utc("2026-10-19 12:00")
        self.assertTrue(common.is_fresh("prices", fri, sun))
        self.assertFalse(common.is_fresh("prices", fri, mon))
        self.assertFalse(common.is_fresh("edgar", fri, sun))

    def test_ctx_get_uses_cache_second_time(self):
        ctx = common.Ctx(self.tmp.name, "ua x@y.z")
        with mock.patch("urllib.request.urlopen", return_value=FakeResp(b"hello")) as m:
            self.assertEqual(ctx.get("https://example.com/a", "macro")[0], b"hello")
            self.assertEqual(ctx.get("https://example.com/a", "macro")[0], b"hello")
            self.assertEqual(m.call_count, 1)
            ctx.refresh = True
            ctx.get("https://example.com/a", "macro")
            self.assertEqual(m.call_count, 2)


class HttpTests(unittest.TestCase):
    def test_sec_requires_user_agent(self):
        with self.assertRaises(common.FetchError) as cm:
            common.http_get("https://data.sec.gov/x", ua=None)
        self.assertIn("sec_user_agent", str(cm.exception))

    def test_user_agent_header_sent(self):
        with mock.patch("urllib.request.urlopen", return_value=FakeResp(b"{}")) as m:
            common.http_get("https://example.com/", ua="App a@b.c")
        self.assertEqual(m.call_args[0][0].get_header("User-agent"), "App a@b.c")

    def test_retry_on_429_then_success(self):
        err = urllib.error.HTTPError("u", 429, "slow", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=[err, FakeResp(b"ok")]) as m, \
                mock.patch("time.sleep") as sl:
            self.assertEqual(common.http_get("https://example.com/", ua="a"), b"ok")
        self.assertEqual(m.call_count, 2)
        sl.assert_called_once()

    def test_404_not_retried(self):
        err = urllib.error.HTTPError("u", 404, "nf", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=err) as m, mock.patch("time.sleep"):
            with self.assertRaises(common.FetchError):
                common.http_get("https://example.com/", ua="a")
        self.assertEqual(m.call_count, 1)

    def test_error_envelope_on_http_failure(self):
        err = urllib.error.HTTPError("u", 503, "down", {}, None)
        out = io.StringIO()

        def fn(argv):
            common.http_get("https://example.com/", ua="a")

        with mock.patch("urllib.request.urlopen", side_effect=err), mock.patch("time.sleep"), \
                redirect_stdout(out), self.assertRaises(SystemExit) as cm:
            common.run_main("demo.py", fn)
        self.assertEqual(cm.exception.code, 1)
        obj = json.loads(out.getvalue())
        self.assertEqual(obj["script"], "demo.py")
        self.assertIn("503", obj["error"])
        self.assertEqual(set(obj), {"error", "script"})

    def test_api_key_redacted_in_errors(self):
        err = urllib.error.HTTPError("u", 400, "bad", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(common.FetchError) as cm:
                common.http_get("https://api.example.com/x?api_key=SECRET&a=1", ua="a")
        self.assertNotIn("SECRET", str(cm.exception))


class ThrottleTests(unittest.TestCase):
    def test_token_bucket_spaces_requests(self):
        t = [0.0]
        slept = []

        def sleep(s):
            slept.append(s)
            t[0] += s

        b = common.TokenBucket(rate=5, capacity=2, clock=lambda: t[0], sleep=sleep)
        for _ in range(7):
            b.acquire()
        self.assertAlmostEqual(t[0], 1.0, places=6)  # 2 burst + 5 more at 5/s
        self.assertTrue(common.is_sec("https://data.sec.gov/a") and common.is_sec("https://www.sec.gov/a"))
        self.assertFalse(common.is_sec("https://notsec.gov.example.com/"))


class ProvenanceTests(unittest.TestCase):
    def test_stable_ids_and_dedupe(self):
        p = common.Provenance()
        a = p.add("primary", "w1", "http://a", "FY2025", "2026-10-14T01:00:00Z")
        b = p.add("secondary", "w2", "http://b", "2026-10-13", "2026-10-14T01:00:00Z")
        self.assertEqual((a, b), ("S1", "S2"))
        self.assertEqual(p.add("primary", "w1", "http://a", "FY2025", "2026-10-14T05:00:00Z"), "S1")
        self.assertEqual(p.sources["S1"]["retrieved"], "2026-10-14")
        self.assertEqual(set(p.sources["S1"]), {"class", "what", "url", "as_of", "retrieved"})

    def test_merge_and_remap(self):
        main = common.Provenance()
        main.add("primary", "w1", "http://a", "x", "2026-10-14")
        other = {"S1": {"class": "primary", "what": "w1", "url": "http://a", "as_of": "x", "retrieved": "2026-10-14"},
                 "S2": {"class": "secondary", "what": "w3", "url": "http://c", "as_of": "y", "retrieved": "2026-10-14"}}
        ids = main.merge(other)
        self.assertEqual(ids, {"S1": "S1", "S2": "S2"})
        o2 = {"S1": {"class": "primary", "what": "z", "url": "http://z", "as_of": "", "retrieved": ""}}
        ids2 = main.merge(o2)
        self.assertEqual(ids2, {"S1": "S3"})
        obj = {"price": {"src": "S1", "rows": [{"src": "S1"}]}, "macro": {"erp_src": "S1"}}
        common.remap_src(obj, ids2)
        self.assertEqual((obj["price"]["src"], obj["price"]["rows"][0]["src"], obj["macro"]["erp_src"]),
                         ("S3", "S3", "S3"))

    def test_pinned_ids_leave_gaps_and_auto_ids_go_above(self):
        p = common.Provenance()
        row = ("primary", "w", "http://a", "x", "2026-10-14")
        self.assertEqual(p.add(*row, sid="S7"), "S7")
        self.assertEqual(p.add(*row, sid="S9"), "S7")  # same (class, what, url): existing id wins
        self.assertEqual(p.add("primary", "w2", "http://b", "x", "2026-10-14"), "S8")
        ids = p.merge({"S1": {"class": "secondary", "what": "z", "url": "http://z", "as_of": "", "retrieved": ""}},
                      {"S1": "S3"})
        self.assertEqual(ids, {"S1": "S3"})
        self.assertEqual(list(p.ordered()), ["S3", "S7", "S8"])


class SettingsTests(unittest.TestCase):
    """flag > <project>/data/config.json > default; MY_INVEST_STORE hidden override; nothing else."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.proj = os.path.join(self.tmp.name, "p")
        self.mine = os.path.join(self.proj, "data")
        os.makedirs(self.mine)

    def cfg(self, text):
        with open(os.path.join(self.mine, "config.json"), "w", encoding="utf-8") as f:
            f.write(text if isinstance(text, str) else json.dumps(text))

    def get(self, key, flag="", env=None):
        return common.resolve_setting(key, flag, None, env or {}, self.proj)

    def test_order_flag_config_default(self):
        self.assertIsNone(self.get("sec_user_agent"))                     # no file, no default
        self.cfg({"sec_user_agent": "cfg a@b.c"})
        self.assertEqual(self.get("sec_user_agent"), "cfg a@b.c")
        self.assertEqual(self.get("sec_user_agent", "flag a@b.c"), "flag a@b.c")

    def test_defaults(self):
        self.assertEqual(self.get("margin_of_safety"), 0.30)
        self.assertEqual(common.resolve_mos(None, None, {}, self.proj), 0.30)
        for k in ("fred_api_key", "finnhub_api_key", "python", "store_dir"):
            self.assertIsNone(self.get(k))

    def test_all_keys_come_from_the_file_and_unknown_keys_are_ignored(self):
        self.cfg({"sec_user_agent": "A a@b.c", "margin_of_safety": 0.2, "store_dir": "/s", "fred_api_key": "fk",
                  "finnhub_api_key": "hk", "python": "/py", "mystery": 1})
        got = [self.get(k) for k in ("sec_user_agent", "margin_of_safety", "store_dir", "fred_api_key",
                                     "finnhub_api_key", "python")]
        self.assertEqual(got, ["A a@b.c", 0.2, "/s", "fk", "hk", "/py"])
        self.assertEqual(common.resolve_mos(None, None, {}, self.proj), 0.2)
        self.assertEqual(common.resolve_store(None, "", {}, self.proj), "/s")

    def test_env_does_not_override_settings_except_store(self):
        self.cfg({"sec_user_agent": "cfg a@b.c", "store_dir": "/cfgstore"})
        env = {"MY_INVEST_SEC_UA": "env a@b.c", "MY_INVEST_MOS": "0.9", "FRED_API_KEY": "x"}
        self.assertEqual(self.get("sec_user_agent", env=env), "cfg a@b.c")
        self.assertEqual(common.resolve_mos(None, None, env, self.proj), 0.30)
        self.assertIsNone(self.get("fred_api_key", env=env))
        self.assertEqual(self.get("store_dir", env={"MY_INVEST_STORE": "/env/store"}), "/env/store")
        self.assertEqual(self.get("store_dir", "/flag", {"MY_INVEST_STORE": "/env/store"}), "/flag")

    def test_dotenv_and_legacy_data_config_are_not_read(self):
        with open(os.path.join(self.proj, ".env"), "w") as f:
            f.write("MY_INVEST_SEC_UA=nope a@b.c\n")
        with open(os.path.join(self.mine, ".env"), "w") as f:
            f.write("MY_INVEST_SEC_UA=nope a@b.c\n")
        self.assertIsNone(self.get("sec_user_agent"))
        self.assertFalse(hasattr(common, "parse_env_file"))

    def test_placeholder_counts_as_absent(self):
        self.cfg({"sec_user_agent": "${user_config.sec_user_agent}", "margin_of_safety": ""})
        self.assertIsNone(self.get("sec_user_agent", "${x}"))
        self.assertEqual(common.resolve_mos(None, "${user_config.mos}", {}, self.proj), 0.30)

    def test_malformed_json_names_file_and_line(self):
        self.cfg('{\n  "sec_user_agent": "A a@b.c",\n  "margin_of_safety": 0.2,,\n}')
        with self.assertRaises(common.FetchError) as cm:
            self.get("sec_user_agent")
        msg = str(cm.exception)
        self.assertIn(os.path.join(self.mine, "config.json"), msg)
        self.assertIn("line 3", msg)

    def test_non_object_json_is_an_error(self):
        self.cfg("[1, 2]")
        with self.assertRaises(common.FetchError):
            self.get("sec_user_agent")

    def test_project_order(self):
        self.assertEqual(common.resolve_project("/p", {"MY_INVEST_PROJECT": "/e"}), "/p")
        self.assertEqual(common.resolve_project("", {"MY_INVEST_PROJECT": "/e"}), "/e")
        self.assertEqual(common.resolve_project("${user_config.project}", {}), os.getcwd())

    def test_store_default_is_project_my_invest(self):
        self.assertEqual(common.resolve_store(None, "", {}, self.proj), self.mine)
        self.assertEqual(common.resolve_store(None, "", {"MY_INVEST_PROJECT": "/proj"}), "/proj/data")
        self.assertEqual(common.resolve_store(None, "${user_config.store_dir}", {}, self.proj), self.mine)
        self.assertEqual(common.ticker_dir("/s", "AAPL"), "/s/stocks/AAPL")

    def test_new_store_gets_gitignore_once(self):
        store = os.path.join(self.tmp.name, "other", "data")
        common.Cache(store, "edgar").put("k", b"x")
        gi = os.path.join(store, ".gitignore")
        self.assertEqual(open(gi).read(), ".cache/\n.venv/\nconfig.json\n")
        with open(gi, "w") as f:
            f.write("custom\n")
        common.Cache(store, "news").put("k", b"x")
        self.assertEqual(open(gi).read(), "custom\n")  # only a newly created store is written

    def test_stock_paths_and_locate(self):
        import argparse
        st = common.Stock("/s/stocks/AAPL")
        got = {k: os.path.relpath(getattr(st, k), "/s/stocks/AAPL") for k in (
            "facts", "series", "scorecard", "holdings", "holdings_tables", "last_run", "research", "evidence",
            "industry", "log", "dossier", "index", "filings", "charts_dir", "reports_dir", "history_dir")}
        self.assertEqual(got, {
            "facts": "facts/facts.json", "series": "facts/series.json", "scorecard": "facts/scorecard.json",
            "holdings": "facts/holdings.json", "holdings_tables": "facts/holdings_tables.json",
            "last_run": "facts/last_run.json", "research": "research/research.md", "evidence": "research/evidence.json",
            "industry": "research/industry.md", "log": "history/log.md", "dossier": "reports/dossier.md",
            "index": "INDEX.md", "filings": "filings", "charts_dir": "charts", "reports_dir": "reports",
            "history_dir": "history"})
        self.assertEqual((st.ticker, st.market_dir), ("AAPL", "/s/market"))
        ns = argparse.Namespace(data="", store="", project=self.proj)
        self.assertEqual(common.locate("aapl", ns).root, os.path.join(self.mine, "stocks", "AAPL"))
        self.assertEqual(common.locate("/x/stocks/MSFT", ns).ticker, "MSFT")
        self.assertEqual(common.locate("./stocks/MSFT", ns).ticker, "MSFT")
        with self.assertRaises(common.FetchError):
            common.locate("A$B", ns)
        self.assertRegex(common.stamp(), r"^\d{4}-\d{2}-\d{2}-\d{4}$")

    def test_safe_ticker(self):
        self.assertEqual(common.safe_ticker(" brk-b "), "BRK-B")
        for bad in ("../x", "A/B", "", "A" * 11):
            with self.assertRaises(common.FetchError):
                common.safe_ticker(bad)

    def test_mos_validation(self):
        with self.assertRaises(common.FetchError):
            common.resolve_mos(None, "1.5", {}, self.proj)
        with self.assertRaises(common.FetchError):
            common.resolve_mos(None, "abc", {}, self.proj)

    def test_ctx_from_and_setting_read_the_project_file(self):
        import argparse
        self.cfg({"sec_user_agent": "Cfg App c@x.y", "fred_api_key": "abc"})
        ns = argparse.Namespace(data="", ua="", refresh=False, store="", project=self.proj)
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("MY_INVEST_STORE", None)
            ctx = common.ctx_from(ns)
        self.assertEqual(ctx.ua, "Cfg App c@x.y")
        self.assertEqual(ctx.root, self.mine)
        self.assertEqual(ctx.setting("fred_api_key"), "abc")
        self.assertEqual(ctx.setting("finnhub_api_key"), "")
        self.assertEqual(ctx.with_refresh().setting("fred_api_key"), "abc")
        ctx.cache("edgar").put("k", b"x")
        self.assertTrue(os.path.isdir(os.path.join(self.mine, ".cache", "edgar")))

    def test_missing_ua_message(self):
        self.assertEqual(common.NO_UA_MSG, 'no SEC User-Agent configured: create <project>/data/config.json with '
                                           '{"sec_user_agent": "AppName you@example.com"}')
        with self.assertRaises(common.FetchError) as cm:
            common.http_get("https://data.sec.gov/x")
        self.assertIn("config.json", str(cm.exception))




class GitignoreOnExistingStore(unittest.TestCase):
    def test_gitignore_written_for_existing_store(self):
        import tempfile, os, common
        d = tempfile.mkdtemp()
        store = os.path.join(d, "data")
        os.makedirs(store)
        open(os.path.join(store, "config.json"), "w").write("{}")
        common.ensure_store(store)
        gi = open(os.path.join(store, ".gitignore")).read()
        self.assertIn("config.json", gi)
        self.assertIn(".venv/", gi)


if __name__ == "__main__":
    unittest.main()