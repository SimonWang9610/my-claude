#!/usr/bin/env python3
"""facts.py TICKER - refresh one ticker's facts.json (+ series.json, last_run.json) incrementally.

Writes <store>/stocks/<TICKER>/facts/{facts.json, series.json, last_run.json} (store: common.resolve_store; ETF series
in <store>/market). TICKER may also be the stock folder path or, with --out,
facts.json at that path with series/last_run beside it. Order: edgar (or the cached normalization) -> prices ->
macro -> market -> options -> consensus -> news -> metrics.py -> momentum.py. What is refetched follows store.md:
  fundamentals  only when the submissions feed shows a 10-K or 10-Q filed after annual[0].filed (and after the
                one acted on last run), else the previous facts.json normalization is reused (no companyfacts fetch)
  prices        when the cached price date is older than the last completed session (always with fundamentals)
  macro, market, options, news, momentum  every run
`filings_recent` always spans three years of 8-K/10-K/10-Q filings (`filings_window` records from/to and whether the
submissions feed reached back that far); the researcher's news window (last run date, 90 days on the first run)
is `news_since` in last_run.json and the manifest, never a trim of filings_recent.
`--refresh` refetches everything. Stable source ids: S1 companyfacts, S2 submissions, S3 prices, S4 DGS10,
S5 ERP, S7 market ETFs, S8 Bank of Canada FX, S9 options, S12 consensus (S6, S10, S11 stay free: metrics.py and
score.py take the next free ids after the facts sources).
edgar failure is fatal; every other group degrades to null and is listed in `fetch_errors`.
"""
import datetime as dt
import json
import os
import subprocess
import sys

import common
import edgar
import consensus
import macro
import market
import momentum
import news
import options
import prices
from common import FetchError

SCRIPT = "facts.py"
HERE = os.path.dirname(os.path.abspath(__file__))
CLOSE_UTC_HOUR = 21  # US sessions end 20:00 or 21:00 UTC; the later bound avoids reading a partial bar as final
PRICE_IDS, MACRO_IDS, NEWS_IDS = {"S1": "S3"}, {"S1": "S4", "S2": "S5"}, {"S1": "S2"}
MARKET_IDS, OPTIONS_IDS = {"S7": "S7", "S8": "S8"}, {"S9": "S9"}
CONSENSUS_IDS = {"S12": "S12"}
FIRST_RUN_NEWS_DAYS = 90
FILINGS_DAYS = 1095  # gates G1/G2 read three years of 8-K items
FILINGS_FORMS = ["8-K", "10-K", "10-Q"]


# --- incremental decisions (pure) ---------------------------------------------------------------
def last_expected_close(now):
    """Date (ISO) of the most recent session that should be complete at `now`; holidays ignored."""
    d = now.date() if now.hour >= CLOSE_UTC_HOUR else now.date() - dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d.isoformat()


def prices_stale(price_date, last, now):
    """True when the cached prices miss a completed session, or were fetched before that session closed."""
    if not price_date:
        return True
    expected = last_expected_close(now)
    if price_date < expected:  # a holiday leaves it older forever: once checked for `expected`, don't re-ask
        return (last or {}).get("price_checked_for") != expected
    if price_date == expected:
        return ((last or {}).get("price_retrieved") or "") < "%sT%02d:00:00Z" % (expected, CLOSE_UTC_HOUR)
    return False  # a bar dated after the last completed session is today's, still in progress


def decide(prev, last, sub, now, force=False):
    """-> (fetch_fundamentals, fetch_prices). `sub` is the submissions JSON."""
    if force or not edgar.reusable(prev or {}):
        return True, True
    last = last or {}
    fund = edgar.needs_fundamentals(sub, prev["fundamentals"]["annual"][0].get("filed"), last.get("periodic_seen"))
    price_date = (prev.get("price") or {}).get("date")
    return fund, fund or prices_stale(price_date, last, now)


def news_days(last, now, force=False):
    if force or not last or not last.get("retrieved"):
        return FIRST_RUN_NEWS_DAYS
    return max(1, (now.date() - dt.date.fromisoformat(last["retrieved"][:10])).days)


def merge_filings(new, prev_list, today, keep_days=FIRST_RUN_NEWS_DAYS):
    """New window entries plus earlier ones still inside keep_days, deduplicated by url, newest first."""
    cutoff = (today - dt.timedelta(days=keep_days)).isoformat()
    seen, out = set(), []
    for f in list(new) + [p for p in prev_list or [] if p.get("filed", "") >= cutoff]:
        if f.get("url") not in seen:
            seen.add(f.get("url"))
            out.append(f)
    return sorted(out, key=lambda f: f.get("filed", ""), reverse=True)


def changed_groups(prev, facts, fundamentals_fetched):
    """Names of the groups whose content differs from the previous facts.json (all of them on a first run)."""
    prev = prev or {}
    ch = []

    def differs(key, f=lambda x: x):
        return f(prev.get(key)) != f(facts.get(key))
    if (prev.get("price") or {}).get("date") != (facts.get("price") or {}).get("date"):
        ch.append("prices")
    if fundamentals_fetched and (prev.get("fundamentals") or {}).get("annual") != facts["fundamentals"]["annual"]:
        ch.append("fundamentals")
    old_urls = {f.get("url") for f in prev.get("filings_recent") or []}
    if any(f.get("url") not in old_urls for f in facts.get("filings_recent") or []):
        ch.append("filings")
    if (prev.get("macro") or {}).get("dgs10_date") != (facts.get("macro") or {}).get("dgs10_date"):
        ch.append("macro")
    if differs("market"):
        ch.append("market")
    if differs("options", lambda o: {k: v for k, v in (o or {}).items() if k != "as_of"}):
        ch.append("options")
    if differs("consensus", lambda o: {k: v for k, v in (o or {}).items() if k != "as_of"}):
        ch.append("consensus")
    return ch


# --- assembly -----------------------------------------------------------------------------------
def _reuse_source(prov, prev, sid, starts):
    row = (prev.get("sources") or {}).get(sid)
    if not row or not row["what"].startswith(starts):
        return False
    prov.add(row["class"], row["what"], row["url"], row["as_of"], row["retrieved"], sid=sid)
    return True


def assemble(ctx, ticker, market_dir, years=10, erp=None, prev=None, last=None, series_prev=None, force=False,
             zones=None, horizon_days=None):
    """-> (facts, series, state) where state = {"reused": [...], "last_run": {...}}."""
    now = ctx.now()
    cik, _, _ = edgar.resolve_cik(ctx, ticker) if not (prev or {}).get("cik") else (int(prev["cik"]), 0, 0)
    sub = ctx.get_json(edgar.SUBMISSIONS_URL % ("%010d" % cik), "news")
    fetch_fund, fetch_px = decide(prev, last, sub[0], now, force)
    reused = []
    if fetch_fund:
        e = edgar.build(ctx, ticker, sub)
    else:
        e = edgar.reuse(ctx, prev, sub[0], sub[1])
        reused.append("fundamentals")
    prov = common.Provenance()
    common.remap_src(e, prov.merge(e["sources"], {"S1": "S1", "S2": "S2"}))
    errors = []
    facts = {k: e[k] for k in ("ticker", "cik", "name", "sic", "sector_class")}
    facts["sector_etf"] = market.sector_etf(e["sic"])
    facts["retrieved"] = e["retrieved"]
    fund = e["fundamentals"]
    fund["shares_history"] = e["shares_history"]
    fresh = ctx.with_refresh()  # bypass the 1-day price cache once a refetch is due

    price, series, px_retrieved = None, None, (last or {}).get("price_retrieved")
    if not fetch_px and series_prev and _reuse_source(prov, prev, "S3", "daily prices"):
        price, series = prev["price"], series_prev
        reused.append("prices")
    else:
        try:
            p = prices.build(fresh, ticker, years, [r["period_end"] for r in fund["annual"]], with_series=True)
            price = common.remap_src(p["price"], prov.merge(p["sources"], PRICE_IDS))
            price["close_at"] = p["close_at"]
            series = common.remap_src(p["series"], prov.merge(p["sources"], PRICE_IDS))
            px_retrieved = p["retrieved"]
        except Exception as ex:  # noqa: BLE001 - degrade, record
            errors.append({"script": "prices.py", "error": str(ex)})

    macro_obj = None
    try:
        m = macro.build(ctx) if erp is None else macro.build(ctx, *erp)
        macro_obj = common.remap_src(m["macro"], prov.merge(m["sources"], MACRO_IDS))
    except Exception as ex:  # noqa: BLE001
        errors.append({"script": "macro.py", "error": str(ex)})

    market_obj = None
    try:
        mk = market.build(fresh if fetch_px else ctx, e["sic"], market_dir, years)
        prov.merge(mk["sources"], MARKET_IDS)
        market_obj = mk["market"]
    except Exception as ex:  # noqa: BLE001
        errors.append({"script": "market.py", "error": str(ex)})

    options_obj = None
    try:
        o = options.build(ctx, ticker, (price or {}).get("last"), zones=zones, horizon_days=horizon_days)
        options_obj = common.remap_src(o["options"], prov.merge(o["sources"], OPTIONS_IDS))
    except Exception as ex:  # noqa: BLE001
        errors.append({"script": "options.py", "error": str(ex)})

    consensus_obj = None
    try:
        c = consensus.build(ctx, ticker)
        prov.merge(c["sources"], CONSENSUS_IDS)
        consensus_obj = c["consensus"]
    except Exception as ex:  # noqa: BLE001
        errors.append({"script": "consensus.py", "error": str(ex)})

    filings = (prev or {}).get("filings_recent") or []
    fwindow = (prev or {}).get("filings_window")
    try:
        n = news.build(ctx, ticker, since=FILINGS_DAYS, forms=FILINGS_FORMS, sub=sub)
        window = common.remap_src(n["filings"], prov.merge(n["sources"], NEWS_IDS))
        filings = merge_filings(window, filings, now.date(), FILINGS_DAYS)
        w = n["window"]
        oldest = w.get("feed_oldest")
        fwindow = {"from": w["from"], "to": w["to"],
                   "complete": bool(oldest and oldest <= w["from"]) or bool((fwindow or {}).get("complete"))}
    except Exception as ex:  # noqa: BLE001
        errors.append({"script": "news.py", "error": str(ex)})

    facts.update({"sources": prov.ordered(), "price": price, "fundamentals": fund, "macro": macro_obj,
                  "market": market_obj, "options": options_obj, "filings_recent": filings,
                  "filings_window": fwindow,
                  "insiders": None, "consensus": consensus_obj})
    facts["changed"] = changed_groups(None if force else prev, facts, fetch_fund)
    if errors:
        facts["fetch_errors"] = errors
    news_since = (now.date() - dt.timedelta(days=news_days(last, now, force))).isoformat()
    state = {"retrieved": common.iso(now), "news_since": news_since, "annual_filed": fund["annual"][0].get("filed"),
             "price_date": (price or {}).get("date"), "price_retrieved": px_retrieved,
             "price_checked_for": last_expected_close(now) if fetch_px else (last or {}).get("price_checked_for"),
             "periodic_seen": edgar.latest_periodic(sub[0]) if fetch_fund else (last or {}).get("periodic_seen", "")}
    return facts, series, {"reused": reused, "last_run": state}


def write_json(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def run(argv=None):
    ap = common.base_parser("Refresh facts.json for one ticker")
    ap.add_argument("ticker", help="ticker or stock folder path")
    ap.add_argument("--mos", default="", help="margin of safety for metrics.py (else env/config, default 0.30)")
    ap.add_argument("--erp", default="", help="equity risk premium in percent for metrics.py (else macro.erp)")
    ap.add_argument("--horizons", default="", help="metrics.py valuation horizons in years, e.g. 0.25,1,3,7.5")
    ap.add_argument("--g-base", default="", help="metrics.py what-if base growth (decimal)")
    ap.add_argument("--years", type=int, default=10, help="price history years")
    ap.add_argument("--horizon-days", type=int, default=None,
                    help="options contracts also for the first monthly expiry at least this many days out")
    args = ap.parse_args(argv)
    st = common.locate(args.ticker, args)   # a bare ticker or the stock folder path
    ticker = st.ticker
    ctx = common.ctx_from(args)
    if args.out:
        path = args.out
        stem = os.path.splitext(path)[0]
        spath, lpath = stem + ".series.json", stem + ".last_run.json"
        mdir = os.path.join(os.path.dirname(os.path.abspath(path)), "market")
    else:
        common.ensure_store(os.path.dirname(os.path.dirname(st.root)))
        path, spath, lpath, mdir = st.facts, st.series, st.last_run, st.market_dir
    facts, series, state = assemble(ctx, ticker, mdir, args.years, prev=read_json(path), last=read_json(lpath),
                                    series_prev=read_json(spath), force=args.refresh,
                                    zones=(read_json(st.scorecard) or {}).get("zones"), horizon_days=args.horizon_days)
    write_json(path, facts)
    if series is not None:
        write_json(spath, series)
    metrics_py = os.path.join(HERE, "metrics.py")
    metrics = "skipped"
    if os.path.exists(metrics_py):
        mos = common.resolve_mos(args.data, args.mos, project=args.project)
        cmd = [sys.executable, metrics_py, path, "--mos", str(mos)]
        for flag, val in (("--erp", args.erp), ("--horizons", args.horizons), ("--g-base", args.g_base)):
            if val:
                cmd += [flag, val]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise FetchError("metrics.py failed (facts.json written without metrics): %s"
                             % (r.stdout.strip() or r.stderr.strip())[:500])
        metrics = "ok"
    else:
        print("note: scripts/metrics.py not found; facts.json written without the metrics section", file=sys.stderr)
    mom = momentum.annotate(path, mdir, series)
    write_json(lpath, state["last_run"])
    manifest = {"ticker": ticker, "facts": path, "series": spath if series is not None else None,
                "sources": len(facts["sources"]), "annual_rows": len(facts["fundamentals"]["annual"]),
                "metrics": metrics, "momentum_missing": sorted(mom["missing"]), "changed": facts["changed"],
                "news_since": state["last_run"]["news_since"], "reused": state["reused"], "fetch_errors": facts.get("fetch_errors", [])}
    print(json.dumps(manifest))
    return manifest


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
