#!/usr/bin/env python3
"""stats.py - price statistics for one ticker from the `prices` table into the `stats` table.

Usage: stats.py TICKER [--asof YYYY-MM-DD] [--project P] [--md]

Returns use adj_close when every row has it, else close; levels (moving averages, 52-week range, the
3-month band) use close. Windows are calendar years back from asof: a 1y/3y/5y figure is produced only when
prices reach back that far. Recent moves ret_1d/ret_1w/ret_1m/ret_3m count 1/5/21/63 trading days back. Beta, correlation and the return vs SPY need SPY prices (yahoo.py prices SPY);
without them those three are listed under "skipped" and everything else is still written.
Rerunning for the same asof replaces the ticker's rows. Nothing here chooses or judges; it only counts.
"""
import datetime as dt
import math
import sys

import calc
import common
import db

SCRIPT = "stats.py"
YEARS = {"1y": 1, "3y": 3, "5y": 5}
TRADING_DAYS = 252
RECENT = {"ret_1d": 1, "ret_1w": 5, "ret_1m": 21, "ret_3m": 63}  # trading days back
RETURN_METRICS = {"cagr", "total_return", "volatility", "max_drawdown", "vs_spy", "from_high_52w", "from_ma200",
                  "ytd_return"} | set(RECENT)


def years_before(date_s, n):
    d = dt.date.fromisoformat(date_s)
    try:
        return d.replace(year=d.year - n).isoformat()
    except ValueError:  # Feb 29
        return d.replace(year=d.year - n, day=28).isoformat()


class Series:
    """Dated prices with the level used for returns and the close used for levels."""

    def __init__(self, recs):
        self.dates = [r["date"] for r in recs]
        self.close = [r["close"] for r in recs]
        use_adj = all(r.get("adj_close") is not None for r in recs)
        self.ret = [r["adj_close"] if use_adj else r["close"] for r in recs]
        self.volume = [r.get("volume") for r in recs]
        self.adjusted = use_adj

    def __len__(self):
        return len(self.dates)

    @property
    def asof(self):
        return self.dates[-1]

    def start_index(self, n_years):
        """Index of the last price on or before asof minus n years; None when not covered."""
        cut = years_before(self.asof, n_years)
        idx = None
        for i, d in enumerate(self.dates):
            if d <= cut:
                idx = i
            else:
                break
        return idx

    def returns_from(self, i):
        return calc.log_returns(self.ret[i:])


def load(conn, ticker, asof):
    sql = "SELECT date, close, adj_close, volume FROM prices WHERE ticker = ?"
    params = [ticker]
    if asof:
        sql += " AND date <= ?"
        params.append(asof)
    recs = db.rows(conn, sql + " ORDER BY date", params)
    return Series(recs) if recs else None


def compute(s, spy):
    """-> (metrics {metric: {window: value}}, skipped [{metric, window, reason}])."""
    m, skipped = {}, []

    def put(metric, window, value):
        if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
            return
        m.setdefault(metric, {})[window] = value

    def skip(metric, window, reason):
        skipped.append({"metric": metric, "window": window, "reason": reason})

    close = s.close[-1]
    put("close", "spot", close)

    # windows: cagr, total_return, max_drawdown
    starts = {}
    for w, n in YEARS.items():
        i = s.start_index(n)
        starts[w] = i
        if i is None:
            for metric in ("cagr", "total_return", "max_drawdown"):
                skip(metric, w, "prices do not reach back %d year%s" % (n, "s" if n > 1 else ""))
            continue
        put("total_return", w, s.ret[-1] / s.ret[i] - 1)
        put("cagr", w, calc.cagr(s.ret[i], s.ret[-1], n))
        put("max_drawdown", w, calc.max_drawdown(s.ret[i:]))

    # volatility 1y and the 3-month band
    vol = None
    if starts["1y"] is not None:
        sd = calc.stdev(s.returns_from(starts["1y"]))
        if sd is not None:
            vol = sd * math.sqrt(TRADING_DAYS)
            put("volatility", "1y", vol)
            band = vol * math.sqrt(63.0 / TRADING_DAYS)
            put("range_3m_low", "spot", close * math.exp(-band))
            put("range_3m_high", "spot", close * math.exp(band))
    else:
        skip("volatility", "1y", "prices do not reach back 1 year")
        skip("range_3m_low", "spot", "needs volatility 1y")
        skip("range_3m_high", "spot", "needs volatility 1y")

    # moving averages and trend
    ma = {}
    for n in (50, 200):
        if len(s) >= n:
            ma[n] = calc.mean(s.close[-n:])
            put("ma%d" % n, "spot", ma[n])
        else:
            skip("ma%d" % n, "spot", "needs %d price days, have %d" % (n, len(s)))
    if 200 in ma:
        put("from_ma200", "spot", close / ma[200] - 1)
        if 50 in ma:
            trend = 1 if (close > ma[200] and ma[50] > ma[200]) else (-1 if (close < ma[200] and ma[50] < ma[200]) else 0)
            put("trend", "spot", trend)
        else:
            skip("trend", "spot", "needs ma50")
    else:
        skip("from_ma200", "spot", "needs ma200")
        skip("trend", "spot", "needs ma200")

    # 52-week range
    if starts["1y"] is not None:
        hi, lo = max(s.close[starts["1y"]:]), min(s.close[starts["1y"]:])
        put("high_52w", "spot", hi)
        put("low_52w", "spot", lo)
        put("from_high_52w", "spot", close / hi - 1)
    else:
        for metric in ("high_52w", "low_52w", "from_high_52w"):
            skip(metric, "spot", "prices do not reach back 1 year")

    # recent moves over fixed counts of trading days
    for metric, n in RECENT.items():
        if len(s) > n:
            put(metric, "spot", s.ret[-1] / s.ret[-1 - n] - 1)
        else:
            skip(metric, "spot", "needs %d price days, have %d" % (n + 1, len(s)))

    # year to date: from the last price of the previous calendar year
    jan1 = s.asof[:4] + "-01-01"
    prev = [i for i, d in enumerate(s.dates) if d < jan1]
    if prev:
        put("ytd_return", "spot", s.ret[-1] / s.ret[prev[-1]] - 1)
    else:
        skip("ytd_return", "spot", "no price from the previous year")

    # average volume over the last 63 trading days
    vols = [v for v in s.volume[-63:] if v is not None]
    if vols:
        put("avg_volume_3m", "spot", float(sum(vols)) / len(vols))
    else:
        skip("avg_volume_3m", "spot", "no volume in prices")

    # against SPY
    if spy is None:
        for metric, ws in (("beta", ("1y", "3y")), ("corr", ("1y",)), ("vs_spy", ("1y", "3y", "5y"))):
            for w in ws:
                skip(metric, w, "run yahoo.py prices SPY")
    else:
        spy_ret = dict(zip(spy.dates, spy.ret))
        for w in ("1y", "3y"):
            i = starts[w]
            if i is None:
                skip("beta", w, "prices do not reach back %d year(s)" % YEARS[w])
                continue
            pairs = [(d, s.ret[k]) for k, d in enumerate(s.dates) if k >= i and d in spy_ret]
            if len(pairs) < 20:
                skip("beta", w, "fewer than 20 days overlap with SPY")
                continue
            r = calc.log_returns([p for _, p in pairs])
            mk = calc.log_returns([spy_ret[d] for d, _ in pairs])
            b, c = calc.beta_corr(r, mk)
            put("beta", w, b)
            if w == "1y":
                put("corr", w, c)
        for w, n in YEARS.items():
            i, j = starts[w], spy.start_index(n)
            if i is None or j is None:
                skip("vs_spy", w, "prices (or SPY prices) do not reach back %d year(s)" % n)
                continue
            spy_end = spy_ret.get(s.asof)
            if spy_end is None:
                skip("vs_spy", w, "SPY has no price on %s" % s.asof)
                continue
            put("vs_spy", w, (s.ret[-1] / s.ret[i] - 1) - (spy_end / spy.ret[j] - 1))
    return m, skipped


def store(conn, ticker, asof, metrics):
    sid = db.source(conn, "derived://stats.py?ticker=%s&asof=%s" % (ticker, asof), "derived",
                    "stats.py over prices rows of %s and SPY" % ticker)
    conn.execute("DELETE FROM stats WHERE ticker = ? AND asof = ?", (ticker, asof))
    recs = [{"ticker": ticker, "asof": asof, "metric": k, "window": w, "value": float(v), "source_id": sid}
            for k, ws in metrics.items() for w, v in ws.items()]
    return db.upsert(conn, "stats", recs), sid


def fmt_value(metric, value):
    if metric in RETURN_METRICS:
        return calc.pct(value)
    if metric in ("beta", "corr"):
        return calc.num(value, 2)
    if metric == "trend":
        return "%+d" % int(value)
    if metric == "avg_volume_3m":
        return calc.money(value, 0)
    return calc.money(value, 2)


def md(ticker, asof, metrics, skipped, days):
    order = ["close", "ret_1d", "ret_1w", "ret_1m", "ret_3m", "ma50", "ma200", "from_ma200", "trend", "high_52w",
             "low_52w", "from_high_52w", "range_3m_low", "range_3m_high", "ytd_return", "total_return", "cagr",
             "volatility", "max_drawdown",
             "beta", "corr", "vs_spy", "avg_volume_3m"]
    recs = []
    for metric in order + [k for k in metrics if k not in order]:
        for w in sorted(metrics.get(metric, {}), key=lambda x: (x != "spot", x)):
            recs.append({"metric": metric, "window": w, "value": fmt_value(metric, metrics[metric][w])})
    out = ["**%s** price statistics as of %s (%d price days)" % (ticker, asof, days), "", db.md_table(recs)]
    if skipped:
        out += ["", "Skipped: " + "; ".join("%s %s (%s)" % (x["metric"], x["window"], x["reason"]) for x in skipped)]
    return "\n".join(out)


def run(argv=None):
    p = common.parser(SCRIPT, "price statistics for a ticker, written to the stats table")
    p.add_argument("ticker")
    p.add_argument("--asof", default="", help="use prices up to this date (YYYY-MM-DD); default: the latest")
    a = p.parse_args(argv)
    ticker = a.ticker.upper()
    conn = db.connect(a.project)
    s = load(conn, ticker, a.asof)
    if s is None:
        return common.fail(SCRIPT, "no prices for %s; run yahoo.py prices %s" % (ticker, ticker))
    spy = load(conn, "SPY", s.asof) if ticker != "SPY" else s
    metrics, skipped = compute(s, spy)
    n, sid = store(conn, ticker, s.asof, metrics)
    out = {"ok": True, "script": SCRIPT, "ticker": ticker, "asof": s.asof, "days": len(s), "adjusted": s.adjusted,
           "metrics": metrics, "skipped": skipped, "stored": n, "source_id": sid}
    return common.emit(out, md=md(ticker, s.asof, metrics, skipped, len(s)) if a.md else None)


if __name__ == "__main__":
    sys.exit(common.run_main(SCRIPT, run))
