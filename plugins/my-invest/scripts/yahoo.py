#!/usr/bin/env python3
"""yahoo.py {prices|profile|estimates|all} TICKER [--years N] - secondary-source market data through yfinance.

Usage: ./run.sh yahoo.py all AAPL [--years 5] [--md] --project P   (run.sh provides data/.venv with yfinance)
prices    -> prices (incremental: only the days after the last stored date; the full window once when the stored
             history is shorter than --years)
profile   -> securities, and for an ETF also funds and fund_weights (top holdings, sector weights)
estimates -> estimates (analyst targets, recommendation, next earnings date) as of today; skipped for a fund
all       -> profile, prices, estimates. A part that fails is reported under "failed" and the others still run.
Each loader takes a yfinance Ticker-like object so tests can pass fakes.
"""
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import db  # noqa: E402

SCRIPT = "yahoo.py"
NO_YF = "yfinance is not installed: run this script through run.sh so data/.venv is created"
QUOTE = "https://finance.yahoo.com/quote/%s/"
FUND_KINDS = ("ETF", "MUTUALFUND")
HISTORY_SLACK_DAYS = 7  # stored history counts as covering the window when it starts within this of the cutoff


def make_ticker(symbol):
    try:
        import yfinance as yf
    except ImportError:
        raise common.FetchError(NO_YF)
    return yf.Ticker(symbol)


# --- helpers ------------------------------------------------------------------------------------
def _num(v):
    """float or None (NaN, None, '' -> None)."""
    if v is None or v == "":
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f != f else f


def _day(v):
    """YYYY-MM-DD from a Timestamp, date, datetime or string."""
    if hasattr(v, "strftime"):
        return v.strftime("%Y-%m-%d")
    return str(v)[:10]


def _epoch_day(v):
    v = _num(v)
    return dt.datetime.fromtimestamp(v, dt.timezone.utc).strftime("%Y-%m-%d") if v else None


def _cell(row, key):
    try:
        return row.get(key)
    except AttributeError:
        return row[key] if key in row else None


def frame_rows(df):
    """A DataFrame (or a fake with iterrows()) -> [(index, row)]; empty when df is None or has no rows."""
    if df is None or len(df) == 0:
        return []
    return list(df.iterrows())


def tracked_index(summary):
    """The index named in the summary: the capitalised phrase ending in 'Index', else the sentence, else None."""
    if not summary or "Index" not in summary:
        return None
    words = re.sub(r"[\u00ae\u2122]", "", summary).replace(",", " ").split()
    for i, w in enumerate(words):
        if not w.startswith("Index"):
            continue
        j = i
        while j > 0 and i - j < 8:
            prev = words[j - 1]
            joiner = prev in ("of", "the", "and", "&") and j > 1 and words[j - 2][0].isupper()
            if prev[0].isupper() or prev[0].isdigit() or joiner:
                j -= 1
            else:
                break
        if j < i:
            return " ".join(words[j:i + 1]).rstrip(".;:)(")
    for sentence in re.split(r"(?<=[.!?])\s+", summary):
        if "Index" in sentence:
            return sentence.strip()[:200]
    return None


# --- loaders ------------------------------------------------------------------------------------
def load_prices(conn, t, ticker, years, today=None):
    """Store daily prices; only the days after the last stored date unless the stored history is too short."""
    today = today or dt.date.today()
    cutoff = today - dt.timedelta(days=365 * years)
    span = db.one(conn, "SELECT MIN(date) lo, MAX(date) hi, COUNT(*) n FROM prices WHERE ticker = ?", (ticker,))
    covered = span["lo"] and dt.date.fromisoformat(span["lo"]) <= cutoff + dt.timedelta(days=HISTORY_SLACK_DAYS)
    sid = db.source(conn, QUOTE % ticker + "history/", "secondary", "Yahoo Finance %s prices" % ticker)
    if covered:
        start = dt.date.fromisoformat(span["hi"]) + dt.timedelta(days=1)
        df = t.history(start=start.isoformat(), auto_adjust=False, actions=False) if start <= today else None
    else:
        start = cutoff
        df = t.history(period="%dy" % years, auto_adjust=False, actions=False)
    rows = []
    for idx, r in frame_rows(df):
        day = _day(idx)
        close = _num(_cell(r, "Close"))
        if close is None or day < start.isoformat():
            continue
        vol = _num(_cell(r, "Volume"))
        rows.append({"ticker": ticker, "date": day, "open": _num(_cell(r, "Open")), "high": _num(_cell(r, "High")),
                     "low": _num(_cell(r, "Low")), "close": close, "adj_close": _num(_cell(r, "Adj Close")),
                     "volume": int(vol) if vol is not None else None, "source_id": sid})
    db.upsert(conn, "prices", rows)
    stored = db.one(conn, "SELECT MIN(date) lo, MAX(date) hi, COUNT(*) n FROM prices WHERE ticker = ?", (ticker,))
    return {"fetched_from": start.isoformat() if df is not None else None, "new_rows": len(rows),
            "stored_days": stored["n"], "first": stored["lo"], "last": stored["hi"], "source_id": sid}


def load_profile(conn, t, ticker):
    """Store the securities row; for a fund also funds and fund_weights. Returns what was stored."""
    info = t.get_info() or {}
    kind = "fund" if str(info.get("quoteType", "")).upper() in FUND_KINDS else "stock"
    sid = db.source(conn, QUOTE % ticker, "secondary", "Yahoo Finance %s profile" % ticker)
    now = common.iso()
    db.upsert(conn, "securities", [{"ticker": ticker, "name": info.get("longName") or info.get("shortName"), "kind": kind,
                                    "exchange": info.get("fullExchangeName") or info.get("exchange"),
                                    "sector": info.get("sector"), "industry": info.get("industry"),
                                    "currency": info.get("currency"), "source_id": sid, "updated_at": now}])
    out = {"kind": kind, "name": info.get("longName") or info.get("shortName"), "source_id": sid}
    if kind != "fund":
        return out
    fd = getattr(t, "funds_data", None)
    summary = (info.get("longBusinessSummary") or "")[:600] or None
    db.upsert(conn, "funds", [{"ticker": ticker, "category": info.get("category"), "tracks": tracked_index(summary),
                               "expense_ratio": expense_ratio(info, fd), "net_assets": _num(info.get("totalAssets")),
                               "inception": _epoch_day(info.get("fundInceptionDate")), "summary": summary,
                               "asof": common.today(), "source_id": sid}])
    hid = db.source(conn, QUOTE % ticker + "holdings/", "secondary", "Yahoo Finance %s holdings" % ticker)
    weights = []
    asof = common.today()
    try:
        for sym, r in frame_rows(getattr(fd, "top_holdings", None)):
            w = _num(_cell(r, "Holding Percent"))
            if w is not None:
                weights.append({"fund": ticker, "kind": "holding", "key": str(sym).upper(), "name": _cell(r, "Name"),
                                "weight": w, "asof": asof, "source_id": hid})
        for sector, w in (getattr(fd, "sector_weightings", None) or {}).items():
            w = _num(w)
            if w is not None:
                weights.append({"fund": ticker, "kind": "sector", "key": str(sector), "weight": w, "asof": asof, "source_id": hid})
    except Exception as e:  # Yahoo's holdings page is flaky; the funds row is still worth keeping
        out["weights_error"] = str(e)
    db.upsert(conn, "fund_weights", weights)
    out.update({"fund_weights": len(weights), "holdings_source_id": hid})
    return out


def expense_ratio(info, fd):
    """Yearly cost as a fraction: info annualReportExpenseRatio, else the fund overview or operations table
    (first column = this fund), else info netExpenseRatio, which Yahoo gives in percent."""
    v = _num(info.get("annualReportExpenseRatio"))
    if v is not None:
        return v
    try:
        for k, val in (getattr(fd, "fund_overview", None) or {}).items():
            if "expense" in str(k).lower() and _num(val) is not None:
                return _num(val)
        for label, r in frame_rows(getattr(fd, "fund_operations", None)):
            if "expense ratio" in str(label).lower():
                vals = [_num(x) for x in (list(r.values()) if isinstance(r, dict) else list(r.values))]
                vals = [x for x in vals if x is not None]
                if vals:
                    return vals[0]
    except Exception:
        pass
    v = _num(info.get("netExpenseRatio"))
    return v / 100 if v is not None else None


def load_estimates(conn, t, ticker, today=None):
    """Store one estimates row keyed by today's date."""
    today = today or common.today()
    targets = getattr(t, "analyst_price_targets", None) or {}
    info = t.get_info() or {}
    nxt = None
    try:
        cal = getattr(t, "calendar", None) or {}
        dates = sorted(_day(d) for d in (cal.get("Earnings Date") or []) if d is not None)
        future = [d for d in dates if d >= today]
        nxt = (future or dates or [None])[0]
    except Exception:
        pass
    sid = db.source(conn, QUOTE % ticker + "analysis/", "secondary", "Yahoo Finance %s analysis" % ticker)
    row = {"ticker": ticker, "asof": today, "target_mean": _num(targets.get("mean")), "target_median": _num(targets.get("median")),
           "target_high": _num(targets.get("high")), "target_low": _num(targets.get("low")),
           "analysts": int(_num(info.get("numberOfAnalystOpinions")) or 0) or None,
           "recommendation": info.get("recommendationKey"), "recommendation_mean": _num(info.get("recommendationMean")),
           "next_earnings": nxt, "source_id": sid}
    db.upsert(conn, "estimates", [row])
    return dict(row)


# --- CLI ----------------------------------------------------------------------------------------
def run(argv=None):
    p = common.parser(SCRIPT, "Yahoo Finance prices, profile and analyst estimates through yfinance")
    p.add_argument("command", choices=["prices", "profile", "estimates", "all"])
    p.add_argument("ticker")
    p.add_argument("--years", type=int, default=0, help="price history window (default: config depth.price_years)")
    a = p.parse_args(argv)
    ticker = a.ticker.upper()
    project = common.resolve_project(a.project)
    cfg = common.load_config(project)
    years = a.years or common.depth(cfg, "price_years")
    conn = db.connect(project)
    try:
        t = make_ticker(ticker)
    except common.FetchError as e:
        return common.fail(SCRIPT, e)

    out = {"ok": True, "script": SCRIPT, "ticker": ticker, "command": a.command}
    failed = {}
    parts = {"all": ["profile", "prices", "estimates"]}.get(a.command, [a.command])
    kind = None
    for part in parts:
        if part == "estimates" and a.command == "all":
            kind = kind or (db.one(conn, "SELECT kind FROM securities WHERE ticker = ?", (ticker,)) or {}).get("kind")
            if kind == "fund":
                out["estimates"] = "skipped for a fund"
                continue
        try:
            if part == "prices":
                res = load_prices(conn, t, ticker, years)
                out.update({k: res[k] for k in ("fetched_from", "new_rows", "stored_days")})
            elif part == "profile":
                res = load_profile(conn, t, ticker)
                kind = res["kind"]
            else:
                res = load_estimates(conn, t, ticker)
            out[part] = res
        except Exception as e:  # one vendor part failing must not kill the others
            failed[part] = "%s: %s" % (type(e).__name__, e) if not isinstance(e, common.FetchError) else str(e)
    if failed:
        out["failed"] = failed
    stored = [k for k in parts if k in out and k not in failed and out[k] != "skipped for a fund"]
    if not stored:
        return common.fail(SCRIPT, "nothing stored for %s" % ticker, failed=failed)
    md = None
    if a.md:
        recs = []
        if "prices" in out:
            recs.append({"part": "prices", "detail": "%s rows new, %s stored (%s..%s)" % (
                out["prices"]["new_rows"], out["prices"]["stored_days"], out["prices"]["first"], out["prices"]["last"])})
        if "profile" in out:
            recs.append({"part": "profile", "detail": "%s (%s)" % (out["profile"]["name"], out["profile"]["kind"])})
        if isinstance(out.get("estimates"), dict):
            e = out["estimates"]
            recs.append({"part": "estimates", "detail": "mean target %s (%s analysts), %s, next earnings %s" % (
                e["target_mean"], e["analysts"], e["recommendation"], e["next_earnings"])})
        for k, v in failed.items():
            recs.append({"part": k, "detail": "FAILED: " + v})
        md = db.md_table(recs)
    return common.emit(out, md)


if __name__ == "__main__":
    sys.exit(common.run_main(SCRIPT, run))
