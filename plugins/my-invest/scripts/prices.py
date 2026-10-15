#!/usr/bin/env python3
"""prices.py TICKER [--years 10] [--dates YYYY-MM-DD,...] - daily prices via yfinance (secondary source).

Prints {ticker, sources, price{...}, close_at{...}}. `close` is split-adjusted but not dividend-adjusted
(auto_adjust=False); `adj_close` also adjusts for dividends and drives the return figures.
`--series` adds the full daily series (used by facts.py for series.json).
Raw history is cached under <data>/cache/prices/ (JSON), TTL 1 trading day.
"""
import bisect
import datetime as dt
import json
import math

import common
from common import FetchError

SCRIPT = "prices.py"
QUOTE_URL = "https://finance.yahoo.com/quote/%s/history/"


def _num(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) or math.isinf(x) else x


def load_yfinance(ticker, years):
    """Fetch history + info from yfinance. Returns {"version", "rows", "info"}. Raises FetchError."""
    try:
        import yfinance as yf
    except ImportError:
        raise FetchError(
            "yfinance is not installed or Python is older than 3.10 (yfinance 1.x needs Python 3.10+): "
            'install Python 3.10+ and re-run, or set "python" in <project>/data/config.json')
    start = (dt.date.today() - dt.timedelta(days=int(years * 365.25) + 14)).isoformat()
    t = yf.Ticker(ticker)
    try:
        h = t.history(start=start, auto_adjust=False, actions=True)
    except Exception as e:  # yfinance raises assorted errors on rate limits / crumb failures
        raise FetchError("yfinance history failed for %s: %s" % (ticker, e))
    if h is None or len(h) == 0:
        raise FetchError("yfinance returned no price history for %s" % ticker)
    rows = []
    for ts, r in h.iterrows():
        rows.append({"date": ts.strftime("%Y-%m-%d"), "close": _num(r.get("Close")),
                     "adj_close": _num(r.get("Adj Close")), "high": _num(r.get("High")), "low": _num(r.get("Low")),
                     "dividends": _num(r.get("Dividends")) or 0.0, "splits": _num(r.get("Stock Splits")) or 0.0})
    info = {}
    try:
        raw = t.info or {}
        info = {k: _num(raw.get(k)) for k in ("sharesOutstanding", "marketCap")}
    except Exception:
        info = {}
    if not any(info.values()):
        try:
            fi = t.fast_info
            info = {"sharesOutstanding": _num(fi.get("shares")), "marketCap": _num(fi.get("marketCap"))}
        except Exception:
            pass
    return {"version": getattr(yf, "__version__", "unknown"), "rows": rows, "info": info}


def get_history(ctx, ticker, years, loader=load_yfinance):
    """Cached history -> (payload dict, retrieved_iso)."""
    cache = ctx.cache("prices")
    key = "yf|%s|%s" % (ticker, years)
    hit = cache.get(key, ctx.refresh)
    if hit:
        return json.loads(hit[0].decode("utf-8")), hit[1]
    payload = loader(ticker, years)
    return payload, cache.put(key, json.dumps(payload).encode("utf-8"))


def _shift_years(d, n):
    try:
        return d.replace(year=d.year - n)
    except ValueError:  # Feb 29
        return d.replace(year=d.year - n, day=28)


class Series:
    def __init__(self, rows):
        self.rows = [r for r in rows if r.get("close") is not None]
        self.dates = [r["date"] for r in self.rows]

    def at_or_before(self, date_str):
        i = bisect.bisect_right(self.dates, date_str) - 1
        return self.rows[i] if i >= 0 else None


def summarize(rows, info, dates=(), years=10):
    """Pure function: history rows -> (price dict without src, close_at dict)."""
    s = Series(rows)
    if not s.rows:
        raise FetchError("no usable price rows")
    last = s.rows[-1]
    last_d = dt.date.fromisoformat(last["date"])
    missing = []
    first_d = dt.date.fromisoformat(s.rows[0]["date"])

    def adj(r):
        return r.get("adj_close") if r.get("adj_close") is not None else r["close"]

    def base_at(target, label):
        """Row at nearest prior trading day to target, only if history reaches back that far."""
        if first_d > target + dt.timedelta(days=7):
            missing.append("%s: history starts %s, after %s" % (label, first_d, target))
            return None
        return s.at_or_before(target.isoformat())

    def total_return(label, target):
        b = base_at(target, label)
        return None if b is None else adj(last) / adj(b) - 1

    def cagr(label, n):
        b = base_at(_shift_years(last_d, n), label)
        if b is None:
            return None
        span = (last_d - dt.date.fromisoformat(b["date"])).days / 365.25
        return (adj(last) / adj(b)) ** (1 / span) - 1 if span > 0 else None

    yr_start = dt.date(last_d.year - 1, 12, 31)
    ytd = None
    if first_d <= yr_start + dt.timedelta(days=7):
        ytd = total_return("ytd_return", yr_start)
    else:
        missing.append("ytd_return: history starts %s, after %s" % (first_d, yr_start))
    win = [r for r in s.rows if r["date"] > (last_d - dt.timedelta(days=365)).isoformat()]
    highs = [r["high"] if r.get("high") is not None else r["close"] for r in win]
    lows = [r["low"] if r.get("low") is not None else r["close"] for r in win]
    five = base_at(_shift_years(last_d, 5), "close_5y_ago")
    shares, cap = (info or {}).get("sharesOutstanding"), (info or {}).get("marketCap")
    if shares is None:
        missing.append("shares_out: not in yfinance info")
    if cap is None:
        missing.append("market_cap: not in yfinance info")
    price = {
        "last": last["close"], "date": last["date"],
        "high_52w": max(highs) if highs else None, "low_52w": min(lows) if lows else None,
        "shares_out": shares, "market_cap": cap,
        "ytd_return": ytd, "return_1y": total_return("return_1y", _shift_years(last_d, 1)),
        "return_5y_cagr": cagr("return_5y_cagr", 5), "return_10y_cagr": cagr("return_10y_cagr", 10),
        "close_5y_ago": five["close"] if five else None,
        "market_cap_5y_ago": None,  # needs shares at that date; compute downstream from close_5y_ago and shares_history
        "splits": [{"date": r["date"], "ratio": r["splits"]} for r in rows if r.get("splits")],
        "missing": missing,
    }
    close_at = {}
    for d in dates:
        r = s.at_or_before(d)
        close_at[d] = None if r is None else {"date": r["date"], "close": r["close"], "adj_close": adj(r)}
    return price, close_at


def series_json(ticker, rows, src, retrieved):
    """Aligned arrays for chart.py; nulls where a value is missing."""
    return {
        "ticker": ticker, "src": src, "retrieved": retrieved,
        "dates": [r["date"] for r in rows],
        "close": [r.get("close") for r in rows],
        "adj_close": [r.get("adj_close") for r in rows],
        "dividends": [{"date": r["date"], "amount": r["dividends"]} for r in rows if r.get("dividends")],
        "splits": [{"date": r["date"], "ratio": r["splits"]} for r in rows if r.get("splits")],
    }


def build(ctx, ticker, years=10, dates=(), loader=load_yfinance, with_series=False):
    ticker = ticker.upper()
    payload, retrieved = get_history(ctx, ticker, years, loader)
    rows = payload["rows"]
    price, close_at = summarize(rows, payload.get("info"), dates, years)
    prov = common.Provenance()
    sid = prov.add("secondary", "daily prices, dividends, splits (Yahoo via yfinance %s)" % payload.get("version"),
                   QUOTE_URL % ticker, price["date"], retrieved)
    price["src"] = sid
    out = {"ticker": ticker, "sources": prov.sources, "price": price, "close_at": close_at,
           "retrieved": retrieved}
    if with_series:
        out["series"] = series_json(ticker, rows, sid, retrieved)
    return out


def run(argv=None):
    ap = common.base_parser("Daily prices via yfinance")
    ap.add_argument("ticker")
    ap.add_argument("--years", type=int, default=10)
    ap.add_argument("--dates", default="", help="comma-separated YYYY-MM-DD for close_at")
    ap.add_argument("--series", action="store_true", help="include the full daily series")
    args = ap.parse_args(argv)
    dates = [d.strip() for d in args.dates.split(",") if d.strip()]
    for d in dates:
        try:
            dt.date.fromisoformat(d)
        except ValueError:
            raise FetchError("bad --dates entry %r (want YYYY-MM-DD)" % d)
    out = build(common.ctx_from(args), args.ticker, args.years, dates, with_series=args.series)
    common.emit(out, args.out)
    return out


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
