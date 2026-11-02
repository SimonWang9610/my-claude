#!/usr/bin/env python3
"""market.py TICKER-SIC - SPY and sector-ETF context plus the Bank of Canada USD/CAD rate.

`market.py --sic 3571 [--store DIR]` prints {sources, sector_etf, market}. SPY and the sector ETF (SIC table in
SECTOR_RANGES) come from yfinance as ten-year daily series (secondary, S7), saved as series.json-shaped files
under <store>/market/<ETF>.json for momentum.py; each block carries 1/3/6/12-month returns (fractions,
trading-day windows 21/63/126/252; SPY also 24 months, 504) and above_200d. USD/CAD is the Bank of Canada
Valet FXUSDCAD observation (primary, keyless, S8). Any failed part is null with its reason in `missing`.
"""
import json
import os

import common
import momentum
import prices
from common import FetchError

SCRIPT = "market.py"
YAHOO_ID, BOC_ID = "S7", "S8"
BOC_URL = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?recent=1"
# First match wins, so exceptions precede the broad manufacturing range.
SECTOR_RANGES = [
    (3570, 3579, "XLK"), (3670, 3679, "XLK"), (7370, 7379, "XLK"),
    (2830, 2836, "XLV"), (2000, 2099, "XLP"), (3711, 3716, "XLY"),
    (1300, 1389, "XLE"), (2900, 2999, "XLE"),
    (2000, 3999, "XLI"),
    (4900, 4999, "XLU"), (4800, 4899, "XLC"),
    (6798, 6798, "XLRE"), (6000, 6799, "XLF"),
    (5000, 5999, "XLY"),
    (1000, 1499, "XLB"),
]
RETURN_WINDOWS = (("return_1m", 21), ("return_3m", 63), ("return_6m", 126), ("return_12m", 252))


def sector_etf(sic):
    try:
        n = int(sic)
    except (TypeError, ValueError):
        return "SPY"
    for lo, hi, etf in SECTOR_RANGES:
        if lo <= n <= hi:
            return etf
    return "SPY"


def summarize(series, extra=()):
    """series.json-shaped dict -> returns and above_200d; None where the history is too short."""
    dates, closes = momentum.closes_of(series)
    out = {"as_of": dates[-1] if dates else None}
    for name, n in tuple(RETURN_WINDOWS) + tuple(extra):
        out[name] = momentum.rnd(momentum.window_return(closes, n))
    ma = momentum.sma(closes, 200)
    out["above_200d"] = None if ma is None else closes[-1] > ma
    return out


def parse_boc(obj):
    """Valet FXUSDCAD JSON -> (rate, date) of the newest observation with a value."""
    for o in sorted(obj.get("observations") or [], key=lambda o: o.get("d", ""), reverse=True):
        try:
            return float(o["FXUSDCAD"]["v"]), o["d"]
        except (KeyError, TypeError, ValueError):
            continue
    raise FetchError("Bank of Canada FXUSDCAD returned no observation")


def save_series(market_dir, etf, series):
    os.makedirs(market_dir, exist_ok=True)
    with open(os.path.join(market_dir, "%s.json" % etf), "w", encoding="utf-8") as f:
        json.dump(series, f, ensure_ascii=False)
        f.write("\n")


def build(ctx, sic, market_dir, years=10, loader=prices.load_yfinance):
    etf = sector_etf(sic)
    prov = common.Provenance()
    missing, blocks, loaded, version, retrieved = [], {}, {}, None, None
    for key, sym in (("spy", "SPY"), ("sector", etf)):
        try:
            if sym not in loaded:
                payload, retrieved = prices.get_history(ctx, sym, years, loader)
                version = payload.get("version")
                loaded[sym] = prices.series_json(sym, payload["rows"], YAHOO_ID, retrieved)
                save_series(market_dir, sym, loaded[sym])
            blk = summarize(loaded[sym], (("return_24m", 504),) if key == "spy" else ())
            blk["src"] = YAHOO_ID
            blocks[key] = dict({"etf": sym}, **blk) if key == "sector" else blk
        except Exception as e:  # noqa: BLE001 - degrade: null block, reason recorded
            blocks[key] = None
            missing.append({"field": key, "reason": str(e)})
    if blocks.get("spy") or blocks.get("sector"):
        asof = (blocks.get("spy") or blocks["sector"])["as_of"]
        prov.add("secondary", "daily prices of SPY and %s (Yahoo via yfinance %s)" % (etf, version),
                 prices.QUOTE_URL % "SPY", asof, retrieved, sid=YAHOO_ID)
    fx = None
    try:
        obj, fx_ret = ctx.get_json(BOC_URL, "macro")
        rate, date = parse_boc(obj)
        prov.add("primary", "Bank of Canada Valet FXUSDCAD, daily average CAD per USD", BOC_URL, date, fx_ret,
                 sid=BOC_ID)
        fx = {"rate": rate, "date": date, "src": BOC_ID}
    except Exception as e:  # noqa: BLE001
        missing.append({"field": "fx_usdcad", "reason": str(e)})
    market = {"spy": blocks.get("spy"), "sector": blocks.get("sector"), "fx_usdcad": fx, "missing": missing}
    return {"sources": prov.sources, "sector_etf": etf, "market": market}


def run(argv=None):
    ap = common.base_parser("SPY, sector ETF and USD/CAD context")
    ap.add_argument("--sic", required=True, help="the company's SIC code (picks the sector ETF)")
    args = ap.parse_args(argv)
    market_dir = os.path.join(common.store_from(args), "market")
    out = build(common.ctx_from(args), args.sic, market_dir)
    common.emit(out, args.out)
    return out


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
