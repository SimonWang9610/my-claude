#!/usr/bin/env python3
"""options.py TICKER [--spot PRICE] - options-implied move, open-interest skew and max pain (secondary, S9).

Expiry: the first monthly (third-Friday) expiry at least 20 days out; else the first expiry at least 20 days
out; else the farthest listed one. From that expiry's chain: ATM IV = mean of the call and put IV at the strikes
nearest the spot (IV <= 1% counts as no quote); implied_move_pct = atm_iv x sqrt(days/365) as a fraction
(0.07 = 7%); implied_move_abs = spot x that; put_call_oi_ratio = put OI / call OI; max_pain = the strike
minimizing the summed intrinsic value of all calls and puts at expiry. next_earnings_date comes from the
yfinance calendar when listed. Chains are often missing: every unavailable field is null and `reason` says why.

`contracts` (skills/score/rules/options-playbook.md, "Contract selection"): for the first monthly expiry at least 30
days out, and for the first monthly at least `--horizon-days` out when given and different, the listed strike
nearest each anchor (price, buy_zone and sell_zone from facts/scorecard.json when it exists, price x 0.90 as
down_10, price x 1.10 as up_10), with BOTH the call and the put at that strike: bid, ask, mid, last, oi, iv,
premium_pct (mid / price), annualized_pct (premium_pct x 365 / days), breakeven (call: strike + mid; put: strike -
mid) and, for puts, protection_cost_pct (mid / price). A missing leg is null with a `reason`.
"""
import datetime as dt
import json
import math

import common
import prices

SCRIPT = "options.py"
SRC_ID = "S9"
MIN_DAYS = 20
CONTRACT_DAYS = 30
ANCHORS = ("price", "buy_zone", "sell_zone", "down_10", "up_10")
MIN_IV = 0.01
FIELDS = ("expiry_used", "days_to_expiry", "atm_iv", "implied_move_pct", "implied_move_abs",
          "put_call_oi_ratio", "put_oi", "call_oi", "max_pain")


def is_monthly(d):
    """Third Friday of its month (day 15-21)."""
    return d.weekday() == 4 and 15 <= d.day <= 21


def choose_expiry(expiries, today, min_days=MIN_DAYS):
    ds = sorted(dt.date.fromisoformat(e) for e in expiries)
    far = [d for d in ds if (d - today).days >= min_days]
    pick = next((d for d in far if is_monthly(d)), far[0] if far else (ds[-1] if ds else None))
    return None if pick is None else pick.isoformat()


def atm_iv(calls, puts, spot):
    """Mean of the call IV and put IV at the strikes nearest `spot`; one side suffices."""
    ivs = []
    for side in (calls, puts):
        quoted = [o for o in side if (o.get("iv") or 0) > MIN_IV]
        if quoted:
            ivs.append(min(quoted, key=lambda o: (abs(o["strike"] - spot), o["strike"]))["iv"])
    return sum(ivs) / len(ivs) if ivs else None


def open_interest(side):
    return int(sum(o.get("oi") or 0 for o in side))


def max_pain(calls, puts):
    """Strike (among listed strikes) with the least total intrinsic value; the lowest on ties."""
    strikes = sorted({o["strike"] for o in calls + puts})
    if not strikes:
        return None

    def pain(k):
        return (sum((o.get("oi") or 0) * max(0.0, k - o["strike"]) for o in calls)
                + sum((o.get("oi") or 0) * max(0.0, o["strike"] - k) for o in puts))
    return min(strikes, key=lambda k: (pain(k), k))


def compute(chain, spot, today):
    """chain = {"expiry", "calls": [{strike, iv, oi}], "puts": [...], "earnings", "error"} -> options dict (no src)."""
    out = {"as_of": today.isoformat(), **{k: None for k in FIELDS},
           "next_earnings_date": chain.get("earnings"), "reason": None}
    if chain.get("error") or not chain.get("expiry"):
        out["reason"] = chain.get("error") or "no listed option expiries"
        return out
    calls, puts = chain["calls"], chain["puts"]
    days = (dt.date.fromisoformat(chain["expiry"]) - today).days
    out.update(expiry_used=chain["expiry"], days_to_expiry=days)
    if not calls and not puts:
        out["reason"] = "empty chain for %s" % chain["expiry"]
        return out
    out.update(put_oi=open_interest(puts), call_oi=open_interest(calls), max_pain=max_pain(calls, puts))
    if out["call_oi"]:
        out["put_call_oi_ratio"] = round(out["put_oi"] / out["call_oi"], 4)
    reasons = []
    iv = atm_iv(calls, puts, spot) if spot else None
    if not spot:
        reasons.append("no spot price")
    elif iv is None:
        reasons.append("no implied-volatility quotes (market closed or illiquid chain)")
    elif days <= 0:
        reasons.append("expiry is not in the future")
    else:
        pct = iv * math.sqrt(days / 365.0)
        out.update(atm_iv=round(iv, 6), implied_move_pct=round(pct, 6), implied_move_abs=round(spot * pct, 4))
    if not out["call_oi"]:
        reasons.append("no call open interest")
    out["reason"] = "; ".join(reasons) or None
    return out


def _num(x):
    return prices._num(x)


def anchors_for(spot, zones=None):
    """[(name, price)] for the anchors that can be computed: zones come from scorecard.json and may be absent."""
    if not spot:
        return []
    z = zones or {}
    vals = {"price": spot, "buy_zone": z.get("buy_below"), "sell_zone": z.get("sell_above"),
            "down_10": spot * 0.90, "up_10": spot * 1.10}
    return [(a, vals[a]) for a in ANCHORS if vals[a]]


def nearest_strike(strikes, target):
    return min(strikes, key=lambda k: (abs(k - target), k)) if strikes else None


def _contract(anchor, anchor_price, kind, strike, expiry, days, spot, row):
    out = {"anchor": anchor, "anchor_price": round(anchor_price, 4), "type": kind, "strike": strike, "expiry": expiry,
           "days": days, "bid": None, "ask": None, "mid": None, "last": None, "oi": None, "iv": None,
           "premium_pct": None, "annualized_pct": None, "breakeven": None, "protection_cost_pct": None, "reason": None}
    if row is None:
        out["reason"] = "no %s listed at strike %s for %s" % (kind, strike, expiry)
        return out
    bid, ask = row.get("bid"), row.get("ask")
    iv = row.get("iv")
    out.update(bid=bid, ask=ask, last=row.get("last"), oi=None if row.get("oi") is None else int(row["oi"]),
               iv=iv if iv and iv > MIN_IV else None)
    if ask and ask > 0 and bid is not None:
        mid = (bid + ask) / 2.0
        pct = mid / spot
        out.update(mid=round(mid, 4), premium_pct=round(pct, 6),
                   annualized_pct=round(pct * 365.0 / days, 6) if days > 0 else None,
                   breakeven=round(strike + mid if kind == "call" else strike - mid, 4),
                   protection_cost_pct=round(pct, 6) if kind == "put" else None)
        if days <= 0:
            out["reason"] = "expiry is not in the future"
    else:
        out["reason"] = "no bid/ask quote (market closed or illiquid)"
    return out


def contracts_for(chains, spot, zones, today):
    """chains = {expiry: {"calls": [...], "puts": [...], "error": optional}} -> list of contract dicts.
    Per expiry and anchor: the strike nearest the anchor among all listed strikes, then both legs at that strike."""
    out = []
    for expiry in sorted(chains):
        ch = chains[expiry]
        days = (dt.date.fromisoformat(expiry) - today).days
        calls = {o["strike"]: o for o in ch.get("calls") or []}
        puts = {o["strike"]: o for o in ch.get("puts") or []}
        strikes = sorted(set(calls) | set(puts))
        for anchor, value in anchors_for(spot, zones):
            k = nearest_strike(strikes, value)
            for kind, side in (("call", calls), ("put", puts)):
                if k is None:
                    c = _contract(anchor, value, kind, None, expiry, days, spot, None)
                    c["reason"] = ch.get("error") or "empty chain for %s" % expiry
                else:
                    c = _contract(anchor, value, kind, k, expiry, days, spot, side.get(k))
                out.append(c)
    return out


def contract_expiries(expiries, today, horizon_days=None):
    """First monthly at least 30 days out, plus the first monthly at least `horizon_days` out when that differs."""
    picks = []
    for min_days in (CONTRACT_DAYS, horizon_days):
        e = choose_expiry(expiries, today, min_days) if min_days else None
        if e and e not in picks:
            picks.append(e)
    return picks


def _side(df):
    out = []
    for _, r in df.iterrows():
        if _num(r.get("strike")) is None:
            continue
        out.append({"strike": _num(r.get("strike")), "iv": _num(r.get("impliedVolatility")),
                    "oi": _num(r.get("openInterest")), "bid": _num(r.get("bid")), "ask": _num(r.get("ask")),
                    "last": _num(r.get("lastPrice"))})
    return out


def load_chain_yfinance(ticker, expiry):
    """{"calls","puts"} of one expiry from yfinance; raises on any failure."""
    import yfinance as yf
    ch = yf.Ticker(ticker).option_chain(expiry)
    return {"calls": _side(ch.calls), "puts": _side(ch.puts)}


def load_yfinance(ticker, today, spot=None):
    """Live chain for the chosen expiry. Returns {"version","spot","expiry","calls","puts","earnings","error"};
    chain problems land in "error" so the earnings date still reaches the caller."""
    try:
        import yfinance as yf
    except ImportError:
        raise common.FetchError(
            "yfinance is not installed or Python is older than 3.10 (yfinance 1.x needs Python 3.10+): "
            'install Python 3.10+ and re-run, or set "python" in <project>/data/config.json')
    t = yf.Ticker(ticker)
    out = {"version": getattr(yf, "__version__", "unknown"), "spot": spot, "expiry": None, "calls": [], "puts": [],
           "earnings": None, "error": None, "expiries": []}
    try:
        cal = t.calendar
        dates = (cal or {}).get("Earnings Date") or []
        future = sorted(d.isoformat() for d in dates if hasattr(d, "isoformat") and d >= today)
        out["earnings"] = future[0] if future else None
    except Exception:  # noqa: BLE001 - calendar is optional
        pass
    try:
        if out["spot"] is None:
            out["spot"] = _num(t.fast_info.get("lastPrice"))
        expiries = list(t.options or [])
        out["expiries"] = expiries
        out["expiry"] = choose_expiry(expiries, today)
        if out["expiry"] is None:
            out["error"] = "yfinance lists no option expiries for %s" % ticker
        else:
            ch = t.option_chain(out["expiry"])
            out["calls"], out["puts"] = _side(ch.calls), _side(ch.puts)
    except Exception as e:  # noqa: BLE001 - yfinance raises assorted errors; chains are often missing
        out["error"] = "option chain unavailable: %s" % e
    return out


def build(ctx, ticker, spot=None, loader=load_yfinance, zones=None, horizon_days=None, chain_loader=load_chain_yfinance):
    ticker = ticker.upper()
    today = ctx.now().date()
    prov = common.Provenance()
    try:
        chain = loader(ticker, today, spot)
        version = chain.get("version")
    except Exception as e:  # noqa: BLE001
        chain, version = {"error": str(e)}, None
    px = spot if spot else chain.get("spot")
    opts = compute(chain, px, today)
    opts["src"] = None
    if chain.get("expiry") or chain.get("earnings"):
        opts["src"] = prov.add("secondary", "option chain and earnings calendar (Yahoo via yfinance %s)" % version,
                               "https://finance.yahoo.com/quote/%s/options/" % ticker, today.isoformat(),
                               common.iso(ctx.now()), sid=SRC_ID)
    chains = {}
    for expiry in contract_expiries(chain.get("expiries") or [], today, horizon_days) if px else []:
        if expiry == chain.get("expiry") and not chain.get("error"):
            chains[expiry] = {"calls": chain["calls"], "puts": chain["puts"]}
            continue
        try:
            chains[expiry] = chain_loader(ticker, expiry)
        except Exception as e:  # noqa: BLE001 - one missing chain nulls its contracts, not the block
            chains[expiry] = {"calls": [], "puts": [], "error": "option chain unavailable for %s: %s" % (expiry, e)}
    opts["contracts"] = contracts_for(chains, px, zones, today)
    return {"ticker": ticker, "sources": prov.sources, "options": opts}


def run(argv=None):
    ap = common.base_parser("Options-implied move, put/call OI, max pain and contract selection")
    ap.add_argument("ticker", help="ticker or stock folder path")
    ap.add_argument("--spot", type=float, default=None, help="spot price (else yfinance last price)")
    ap.add_argument("--horizon-days", type=int, default=None,
                    help="also list contracts for the first monthly expiry at least this many days out")
    args = ap.parse_args(argv)
    st = common.locate(args.ticker, args)
    zones = None
    try:
        with open(st.scorecard, "r", encoding="utf-8") as f:
            zones = json.load(f).get("zones")
    except (OSError, ValueError):
        pass
    out = build(common.ctx_from(args), st.ticker, args.spot, zones=zones, horizon_days=args.horizon_days)
    common.emit(out, args.out)
    return out


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
