#!/usr/bin/env python3
"""consensus.py TICKER - analyst consensus from Yahoo via yfinance (secondary, S12), the `consensus` block of facts.json.

Block (skills/score/rules/outlook.md section 3; all growth figures are fractions):
{"available": true, "as_of", "src": "S12", "targets": {mean, median, high, low, count},
 "eps": {current_fy: {estimate, year_end}, next_fy: {...}}, "growth": {next_year, next_5y_per_year},
 "revenue_growth": {current_fy, next_fy}, "recommendation_mean", "recommendation_count",
 "revisions_90d": {eps_next_fy_up, eps_next_fy_down, window_days} | null, "missing": {field: reason}, "note"}.
When yfinance has nothing the block is {"available": false, "reason": ...}. Not cached: every facts.py run asks again.
Attribute names vary between yfinance versions, so each source is probed under its known names and `note` records
which attributes worked. Yahoo reports EPS revisions over 7 and 30 days only: `revisions_90d` holds the 30-day
counts and says so in `window_days`. The next fiscal year's end date is the current one plus one year.
"""
import datetime as dt
import math

import common
import prices

SCRIPT = "consensus.py"
SRC_ID = "S12"
SRC_WHAT = "Yahoo analyst data via yfinance"
ATTRS = {  # key -> yfinance attribute / getter names, newest first
    "targets": ("analyst_price_targets", "get_analyst_price_targets"),
    "eps": ("earnings_estimate", "get_earnings_estimate"),
    "revenue": ("revenue_estimate", "get_revenue_estimate"),
    "growth": ("growth_estimates", "get_growth_estimates"),
    "revisions": ("eps_revisions", "get_eps_revisions"),
    "recs": ("recommendations_summary", "get_recommendations_summary", "recommendations"),
}


def _num(x):
    return prices._num(x)


def _frame(df, by_period=True):
    """DataFrame -> {period: {col: number|str|None}} (or a list of row dicts) with NaN as None."""
    rows = []
    for idx, r in df.iterrows():
        d = {str(k): (_num(v) if not isinstance(v, str) else v) for k, v in r.items()}
        rows.append((str(idx), d))
    if by_period:
        return {k: v for k, v in rows}
    return [dict(v) for _, v in rows]


def probe(t, key):
    """(value, attribute used, failure) for one source, trying each known name."""
    errs = []
    for name in ATTRS[key]:
        try:
            v = getattr(t, name, None)
            v = v() if callable(v) else v
        except Exception as e:  # noqa: BLE001 - yfinance raises assorted errors
            errs.append("%s: %s" % (name, e))
            continue
        if v is None or (hasattr(v, "empty") and v.empty) or (isinstance(v, dict) and not v):
            errs.append("%s: empty" % name)
            continue
        return v, name, None
    return None, None, "; ".join(errs) or "no attribute"


def load_yfinance(ticker):
    """Raw consensus data as plain Python: {"version","targets","eps","revenue","growth","revisions","recs","info",
    "worked","failed"}. Raises FetchError when yfinance is missing."""
    try:
        import yfinance as yf
    except ImportError:
        raise common.FetchError(
            "yfinance is not installed or Python is older than 3.10 (yfinance 1.x needs Python 3.10+): "
            'install Python 3.10+ and re-run, or set "python" in <project>/data/config.json')
    t = yf.Ticker(ticker)
    out = {"version": getattr(yf, "__version__", "unknown"), "worked": [], "failed": {}}
    for key in ATTRS:
        v, name, err = probe(t, key)
        if err:
            out["failed"][key] = err
            out[key] = None
            continue
        out["worked"].append(name)
        if key == "targets":
            out[key] = {k: _num(x) for k, x in dict(v).items()}
        else:
            out[key] = _frame(v, by_period=key != "recs")
    info = {}
    try:
        raw = t.get_info() if hasattr(t, "get_info") else t.info
        for k in ("recommendationMean", "numberOfAnalystOpinions", "lastFiscalYearEnd", "nextFiscalYearEnd"):
            info[k] = _num((raw or {}).get(k))
        out["worked"].append("info")
    except Exception as e:  # noqa: BLE001
        out["failed"]["info"] = str(e)
    out["info"] = info
    return out


def _date(epoch):
    try:
        return dt.datetime.fromtimestamp(float(epoch), dt.timezone.utc).date()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def _plus_year(d):
    try:
        return d.replace(year=d.year + 1)
    except ValueError:  # Feb 29
        return d.replace(year=d.year + 1, day=28)


def compute(raw, today):
    """raw (load_yfinance shape) -> the consensus block without src. {"available": False, ...} when empty."""
    got = [k for k in ATTRS if raw.get(k)]
    if not got:
        return {"available": False, "reason": "yfinance returned no analyst data (%s)" % (
            "; ".join("%s: %s" % kv for kv in sorted((raw.get("failed") or {}).items())) or "no attributes")}
    miss = {}
    info = raw.get("info") or {}

    def need(field, value, why):
        if value is None:
            miss[field] = why
        return value
    tg = raw.get("targets") or {}
    targets = {k: need("targets." + k, tg.get(k), "analyst_price_targets has no %s" % k) for k in ("mean", "median", "high", "low")}
    cnt = info.get("numberOfAnalystOpinions")
    targets["count"] = need("targets.count", None if cnt is None else int(cnt), "numberOfAnalystOpinions not in Yahoo info")
    fy_end = _date(info.get("nextFiscalYearEnd"))
    est = raw.get("eps") or {}
    rev = raw.get("revenue") or {}
    eps = {}
    for name, per, end in (("current_fy", "0y", fy_end), ("next_fy", "+1y", _plus_year(fy_end) if fy_end else None)):
        eps[name] = {"estimate": need("eps.%s.estimate" % name, (est.get(per) or {}).get("avg"),
                                      "earnings_estimate has no %s average" % per),
                     "year_end": need("eps.%s.year_end" % name, end.isoformat() if end else None,
                                      "nextFiscalYearEnd not in Yahoo info")}
    gr = raw.get("growth") or {}
    nxt = (gr.get("+1y") or {}).get("stockTrend")
    if nxt is None:
        nxt = (est.get("+1y") or {}).get("growth")
    growth = {"next_year": need("growth.next_year", nxt, "growth_estimates and earnings_estimate list no +1y growth"),
              "next_5y_per_year": need("growth.next_5y_per_year", (gr.get("LTG") or {}).get("stockTrend"),
                                       "Yahoo lists no long-term growth (LTG) for the stock")}
    revg = {n: need("revenue_growth." + n, (rev.get(p) or {}).get("growth"), "revenue_estimate has no %s growth" % p)
            for n, p in (("current_fy", "0y"), ("next_fy", "+1y"))}
    rows = raw.get("recs") or []
    cur = next((r for r in rows if r.get("period") == "0m"), rows[0] if rows else None)
    counts = [cur.get(k) for k in ("strongBuy", "buy", "hold", "sell", "strongSell")] if cur else None
    rec_n = int(sum(counts)) if counts and all(c is not None for c in counts) else None
    rec_mean = info.get("recommendationMean")
    if rec_mean is None and rec_n:
        rec_mean = round(sum(w * c for w, c in zip((1, 2, 3, 4, 5), counts)) / rec_n, 4)   # fallback: 1 = strong buy
    need("recommendation_mean", rec_mean, "no recommendationMean in Yahoo info and no recommendations_summary")
    need("recommendation_count", rec_n, "no recommendations_summary row")
    rv = (raw.get("revisions") or {}).get("+1y")
    revisions = None
    if rv and rv.get("upLast30days") is not None and rv.get("downLast30days") is not None:
        revisions = {"eps_next_fy_up": int(rv["upLast30days"]), "eps_next_fy_down": int(rv["downLast30days"]),
                     "window_days": 30}
    else:
        miss["revisions_90d"] = "eps_revisions has no +1y counts"
    note = "yfinance %s; attributes used: %s" % (raw.get("version"), ", ".join(raw.get("worked") or []) or "none")
    if raw.get("failed"):
        note += "; unavailable: " + "; ".join("%s (%s)" % kv for kv in sorted(raw["failed"].items()))
    note += "; revisions are Yahoo's 30-day counts; next fiscal year end = current + 1 year"
    return {"available": True, "as_of": today.isoformat(), "targets": targets, "eps": eps, "growth": growth,
            "revenue_growth": revg, "recommendation_mean": rec_mean, "recommendation_count": rec_n,
            "revisions_90d": revisions, "missing": miss, "note": note}


def build(ctx, ticker, loader=load_yfinance):
    ticker = ticker.upper()
    today = ctx.now().date()
    prov = common.Provenance()
    try:
        raw = loader(ticker)
    except Exception as e:  # noqa: BLE001
        return {"ticker": ticker, "sources": {}, "consensus": {"available": False, "reason": str(e)}}
    block = compute(raw, today)
    if block["available"]:
        block["src"] = prov.add("secondary", SRC_WHAT, "https://finance.yahoo.com/quote/%s/analysis/" % ticker,
                                today.isoformat(), common.iso(ctx.now()), sid=SRC_ID)
    return {"ticker": ticker, "sources": prov.sources, "consensus": block}


def run(argv=None):
    ap = common.base_parser("Analyst consensus via yfinance")
    ap.add_argument("ticker", help="ticker or stock folder path")
    args = ap.parse_args(argv)
    out = build(common.ctx_from(args), common.locate(args.ticker, args).ticker)
    common.emit(out, args.out)
    return out


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
