#!/usr/bin/env python3
"""momentum.py TICKER [--store DIR] - trend, returns, volatility and relative strength from stored series.

A pure function of files: <store>/stocks/<TICKER>/facts/series.json plus <store>/market/SPY.json and
<store>/market/<sector_etf>.json (the ETF named by facts.json `sector_etf`). Writes the `momentum` block
into <store>/stocks/<TICKER>/facts/facts.json when that file exists, and prints it.

Conventions (all fractions, never percent): windows are trading days 21/63/126/252 on `close`;
`return_12m_skip_1m` = close[-22]/close[-253] - 1; MA50/MA200 are simple means of the last 50/200 closes;
`pct_from_52w_high` = 1 - last / max(last 252 closes) (0 at the high, 0.03 = 3% below it);
realized volatility = sample std of daily log returns over the last 30 / 252 returns x sqrt(252);
`rel_strength_*_6m` = the ticker's 6-month return minus the ETF's. A field that cannot be computed is
null and named in `missing` with the reason.
"""
import json
import math
import os

import common

SCRIPT = "momentum.py"
WINDOWS = (("1m", 21), ("3m", 63), ("6m", 126), ("12m", 252))
SKIP = 21
TRADING_DAYS = 252


def closes_of(series):
    """Non-null (date, close) pairs from a series.json-shaped dict."""
    pairs = [(d, c) for d, c in zip(series.get("dates") or [], series.get("close") or []) if c is not None]
    return [p[0] for p in pairs], [p[1] for p in pairs]


def window_return(closes, n, skip=0):
    """close[-1-skip] / close[-1-skip-n] - 1, or None without n + skip + 1 closes."""
    if len(closes) < n + skip + 1:
        return None
    base = closes[-1 - skip - n]
    return closes[-1 - skip] / base - 1 if base else None


def sma(closes, n):
    return sum(closes[-n:]) / n if len(closes) >= n else None


def realized_vol(closes, n):
    """Annualized sample std of the last n daily log returns; None without n + 1 closes."""
    if len(closes) < n + 1 or n < 2:
        return None
    r = [math.log(closes[i] / closes[i - 1]) for i in range(len(closes) - n, len(closes))]
    mean = sum(r) / n
    return math.sqrt(sum((x - mean) ** 2 for x in r) / (n - 1)) * math.sqrt(TRADING_DAYS)


def rnd(x):
    return None if x is None else round(x, 6)


def compute(series, spy=None, sector=None):
    """series / spy / sector are series.json-shaped dicts (spy, sector optional)."""
    dates, closes = closes_of(series)
    missing = {}
    out = {"as_of": dates[-1] if dates else None}

    def put(field, value, need):
        out[field] = rnd(value) if isinstance(value, float) else value
        if value is None:
            missing[field] = "needs %s closes, have %d" % (need, len(closes))

    for label, n in WINDOWS:
        put("return_" + label, window_return(closes, n), n + 1)
    put("return_12m_skip_1m", window_return(closes, TRADING_DAYS - SKIP, SKIP), TRADING_DAYS + 1)
    ma50, ma200 = sma(closes, 50), sma(closes, 200)
    put("ma50", ma50, 50)
    put("ma200", ma200, 200)
    last = closes[-1] if closes else None
    put("above_ma50", None if ma50 is None else last > ma50, 50)
    put("above_ma200", None if ma200 is None else last > ma200, 200)
    put("ma50_above_ma200", None if ma50 is None or ma200 is None else ma50 > ma200, 200)
    hi = max(closes[-TRADING_DAYS:]) if closes else None
    put("pct_from_52w_high", None if not hi or len(closes) < TRADING_DAYS else 1 - last / hi, TRADING_DAYS)
    put("realized_vol_30d", realized_vol(closes, 30), 31)
    put("realized_vol_1y", realized_vol(closes, TRADING_DAYS), TRADING_DAYS + 1)
    r6 = window_return(closes, 126)
    inputs = [series.get("src")]
    for field, other, name in (("rel_strength_spy_6m", spy, "SPY"), ("rel_strength_sector_6m", sector, "sector ETF")):
        o6 = window_return(closes_of(other)[1], 126) if other else None
        out[field] = None if r6 is None or o6 is None else rnd(r6 - o6)
        if out[field] is None:
            missing[field] = ("ticker 6-month return unavailable" if r6 is None
                              else "no stored %s series with 127 closes" % name)
        else:
            inputs.append(other.get("src"))
    out["inputs"] = sorted({s for s in inputs if s}, key=lambda s: int(s[1:]))
    out["missing"] = missing
    return out


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def annotate(facts_path, market_dir, series=None):
    """Compute momentum for the facts.json at `facts_path`, write it there (when the file exists), return it.
    `series` defaults to series.json beside facts.json."""
    folder = os.path.dirname(os.path.abspath(facts_path))
    series = series if series is not None else load_json(os.path.join(folder, "series.json")) or {}
    facts = load_json(facts_path)
    etf = (facts or {}).get("sector_etf")
    spy = load_json(os.path.join(market_dir, "SPY.json"))
    sector = load_json(os.path.join(market_dir, "%s.json" % etf)) if etf else None
    mom = compute(series, spy, sector)
    if facts is not None:
        facts["momentum"] = mom
        with open(facts_path, "w", encoding="utf-8") as f:
            json.dump(facts, f, indent=2, ensure_ascii=False)
            f.write("\n")
    return mom


def run(argv=None):
    ap = common.base_parser("Momentum block from stored series")
    ap.add_argument("ticker", help="ticker or stock folder path")
    args = ap.parse_args(argv)
    st = common.locate(args.ticker, args)
    out = annotate(st.facts, st.market_dir)
    common.emit(out, args.out)
    return out


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
