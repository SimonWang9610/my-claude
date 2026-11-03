#!/usr/bin/env python3
"""size.py — the arithmetic behind "how many shares should I sell (or buy), and at what price".

Reads the positions the question states (holdings.py's parser), the stock folder's facts.json (price,
52-week range, moving averages, the options-implied range, the next earnings date) and scorecard.json
(the recommendation cell, trend, levels, gates), and optional fund.json files for look-through exposure
(how much of the stock the user also holds through funds). Writes facts/sizing.json and, with --md, prints
the Markdown part: the position with its outright and look-through weight, the sizing frames (cap at a
weight, sell the gain, recover the cost), the price levels to place orders at, and the account order a
sale should follow. Sources: S98 derived (this script), S99 the fund files; the facts and scorecard ids
are cited as they are. The frames are this standard's own (skills/standard/references/action-matrix.md,
"Sizing frames"), arithmetic on the user's figures, not a published rule.

  size.py AAPL --question "RRSP: 37 shares of AAPL at USD 203; TFSA: 13 shares at USD 213" --total 95070 \
      [--caps 15,12.5,10] [--funds QQQ=8198,VGT=3648] [--md] --project <folder>

--total is the USD value of the accounts in scope (the question or the holdings file gives it); without
it the weight rows are null with a reason. --funds lists fund tickers the user holds with the USD value
of each position; their fund.json must exist (fund.py).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import EnvelopeParser, FetchError, add_common_args, locate, run_main, today  # noqa: E402
from holdings import ACCOUNT_ORDER, TREATMENT, parse_question  # noqa: E402

SCRIPT = "size.py"
DERIVED = "S98"
FUNDS = "S99"
DEFAULT_CAPS = (0.15, 0.125, 0.10)
TAX_NOW = {"TFSA": "no tax on a sale", "RRSP": "no tax on a sale (withdrawals are taxed as income later)",
           "NONREG": "capital gains tax on the gain (half of it is taxable income)"}
# Where to sell from first, and why: taxable accounts last; RRSP before TFSA because TFSA growth stays tax-free for
# good while an RRSP is taxed on withdrawal anyway. This standard's own order (action-matrix.md).
SELL_ORDER = ("RRSP", "TFSA", "NONREG")


def read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def num(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def r2(x):
    return None if x is None else round(x, 2)


def r4(x):
    return None if x is None else round(x, 4)


def money(x):
    return "n/a" if x is None else "$%s" % format(round(x, 2), ",.2f")


def usd0(x):
    return "n/a" if x is None else "$%s" % format(round(x), ",")


def pct(x, nd=1):
    return "n/a" if x is None else ("%%.%df%%%%" % nd) % (x * 100)


def shares_fmt(x):
    return "n/a" if x is None else ("%d" % x if float(x).is_integer() else "%.2f" % x)


def parse_funds(text):
    """'QQQ=8198,VGT=3648' -> [(ticker, value)]; a bare ticker has value None."""
    out = []
    for part in (text or "").split(","):
        part = part.strip()
        if not part:
            continue
        t, _, v = part.partition("=")
        out.append((t.strip().upper(), num(float(v)) if v.strip() else None))
    return out


def frames(shares, price, cost_total, value, total, caps):
    """Each frame: shares to sell (whole shares, rounded down), proceeds, shares kept, what stays invested."""
    out = []
    if shares is None or price is None or price <= 0:
        return out, "shares or price missing"
    gain = value - cost_total if cost_total is not None else None
    for cap in caps:
        if total is None or total <= 0:
            out.append({"frame": "cap at %s of the portfolio" % pct(cap, 1), "cap": cap, "sell_shares": None,
                        "reason": "--total missing: the weight cannot be computed"})
            continue
        target_value = cap * total
        if value <= target_value:
            out.append({"frame": "cap at %s of the portfolio" % pct(cap, 1), "cap": cap, "sell_shares": 0,
                        "proceeds": 0.0, "keep_shares": shares, "note": "already under %s" % pct(cap, 1)})
            continue
        n = math.floor((value - target_value) / price)
        out.append({"frame": "cap at %s of the portfolio" % pct(cap, 1), "cap": cap, "sell_shares": n,
                    "proceeds": r2(n * price), "keep_shares": r4(shares - n),
                    "weight_after": r4((value - n * price) / total)})
    if gain is not None and gain > 0:
        n = math.floor(gain / price)
        out.append({"frame": "sell the gain, keep your cost invested", "sell_shares": n, "proceeds": r2(n * price),
                    "keep_shares": r4(shares - n), "keep_value": r2((shares - n) * price),
                    "note": "what you keep is worth about your %s cost" % usd0(cost_total)})
        n = math.ceil(cost_total / price) if cost_total else None
        if n is not None:
            n = min(n, math.floor(shares))
            out.append({"frame": "recover your cost, keep the gain as house money", "sell_shares": n,
                        "proceeds": r2(n * price), "keep_shares": r4(shares - n), "keep_value": r2((shares - n) * price)})
    elif gain is not None:
        out.append({"frame": "sell the gain, keep your cost invested", "sell_shares": None,
                    "reason": "the position shows a loss (%s): there is no gain to sell" % usd0(gain)})
    return out, None


def levels(facts, sc):
    p = facts.get("price") if isinstance(facts.get("price"), dict) else {}
    mo = facts.get("momentum") if isinstance(facts.get("momentum"), dict) else {}
    o = facts.get("options") if isinstance(facts.get("options"), dict) else {}
    rec = (sc.get("action") or {}).get("recommendation") or {}
    lv = rec.get("levels") or {}
    last = num(p.get("last"))
    imp = num(o.get("implied_move_abs"))
    out = {"price": last, "price_date": p.get("date"), "price_src": p.get("src") or "S3",
           "high_52w": num(p.get("high_52w")), "low_52w": num(p.get("low_52w")),
           "ma50": num(lv.get("ma50")) if lv.get("ma50") is not None else num(mo.get("ma50")),
           "ma200": num(lv.get("ma200")) if lv.get("ma200") is not None else num(mo.get("ma200")),
           "momentum_src": mo.get("src") or (mo.get("inputs") or [None])[0] if isinstance(mo.get("inputs"), list) else mo.get("src"),
           "implied_low": r2(last - imp) if last is not None and imp is not None else None,
           "implied_high": r2(last + imp) if last is not None and imp is not None else None,
           "implied_expiry": o.get("expiry_used"), "implied_move_pct": r4(imp / last) if last and imp is not None else None,
           "next_earnings": o.get("next_earnings_date"), "options_src": o.get("src") or "S9",
           "trend": rec.get("trend"), "holding_cell": rec.get("holding"), "not_holding_cell": rec.get("not_holding"),
           "basis": rec.get("basis"), "expected_return": rec.get("expected_return"),
           "required_return": rec.get("required_return"), "gates_failed": sc.get("gates_failed") or [],
           "strict_cell_holding": ((sc.get("action") or {}).get("cells") or {}).get("holding"),
           "score_src": sc.get("score_src") or "S61", "derived_src": sc.get("derived_src") or "S60",
           "pct_from_52w_high": num(mo.get("pct_from_52w_high"))}
    return out


def look_through(ticker, funds, st, total):
    """Value of `ticker` held through each fund = fund position value x the stock's weight in that fund."""
    rows, missing = [], []
    for ft, fval in funds:
        folder = os.path.join(os.path.dirname(st.root), ft)
        fj = read_json(os.path.join(folder, "facts", "fund.json"))
        if fj is None:
            missing.append({"fund": ft, "reason": "stocks/%s/facts/fund.json missing (run fund.py %s)" % (ft, ft)})
            continue
        w = next((num(h.get("weight")) for h in fj.get("top_holdings") or [] if isinstance(h, dict)
                  and str(h.get("symbol", "")).upper() == ticker), None)
        if w is None:
            missing.append({"fund": ft, "reason": "%s is not among the fund's listed top holdings" % ticker})
            continue
        if fval is None:
            missing.append({"fund": ft, "reason": "no position value given for %s (--funds %s=<USD>)" % (ft, ft)})
            continue
        rows.append({"fund": ft, "fund_value": fval, "weight_in_fund": w, "value_through_fund": r2(fval * w),
                     "weight_of_portfolio": r4(fval * w / total) if total else None, "fund_as_of": fj.get("as_of"),
                     "file": "file://" + os.path.abspath(os.path.join(folder, "facts", "fund.json"))})
    return rows, missing


def build(ticker, holdings, facts, sc, total, caps, funds, st, as_of):
    lv = levels(facts, sc)
    price = lv["price"]
    positions = []
    for pos in holdings.get("positions") or []:
        sh, cost = num(pos.get("shares")), num(pos.get("avg_cost"))
        value = sh * price if sh is not None and price is not None else None
        positions.append({"account": pos.get("account"), "shares": sh, "avg_cost": cost, "value": r2(value),
                          "cost_total": r2(sh * cost) if sh is not None and cost is not None else None,
                          "gain": r2(value - sh * cost) if value is not None and cost is not None else None,
                          "tax_on_sale": TAX_NOW.get(pos.get("account"), "unknown account type"),
                          "tax_rule": TREATMENT.get(pos.get("account"))})
    shares = sum(p["shares"] or 0 for p in positions) or None
    cost_total = sum(p["cost_total"] or 0 for p in positions) if positions else None
    value = sum(p["value"] or 0 for p in positions) if positions else None
    fr, fr_reason = frames(shares, price, cost_total, value, total, caps)
    lt_rows, lt_missing = look_through(ticker, funds, st, total)
    through = sum(r["value_through_fund"] for r in lt_rows) if lt_rows else 0.0
    sell_from = [a for a in SELL_ORDER if any(p["account"] == a for p in positions)]
    out = {"ticker": ticker, "as_of": as_of, "price": price, "price_date": lv["price_date"], "total_in_scope": total,
           "positions": positions,
           "position": {"shares": r4(shares), "cost_total": r2(cost_total), "value": r2(value),
                        "gain": r2(value - cost_total) if value is not None and cost_total is not None else None,
                        "weight": r4(value / total) if value is not None and total else None,
                        "weight_reason": None if total else "--total missing"},
           "look_through": {"rows": lt_rows, "value_through_funds": r2(through) if lt_rows else None,
                            "weight_through_funds": r4(through / total) if lt_rows and total else None,
                            "true_weight": r4((value + through) / total) if lt_rows and total and value is not None else None,
                            "missing": lt_missing},
           "frames": fr, "frames_reason": fr_reason, "caps": list(caps),
           "levels": lv,
           "sell_from": {"order": sell_from, "rule": "taxable accounts last; RRSP before TFSA (TFSA growth stays tax-free "
                                                     "for good, an RRSP is taxed on withdrawal anyway); this standard's own order"},
           "sources": {DERIVED: {"class": "derived", "what": "size.py: weights, sizing frames and order levels from the stated "
                                                            "positions, %s, %s, %s and %s" % (lv["price_src"], lv["options_src"],
                                                                                           lv["derived_src"], lv["score_src"]),
                                 "url": "file://" + os.path.abspath(os.path.join(st.facts_dir, "sizing.json")),
                                 "as_of": as_of, "retrieved": as_of}}}
    if lt_rows:
        out["sources"][FUNDS] = {"class": "secondary", "what": "fund.json of %s: top holdings weights (Yahoo via yfinance "
                                                              "funds_data)" % ", ".join(r["fund"] for r in lt_rows),
                                 "url": lt_rows[0]["file"], "as_of": lt_rows[0].get("fund_as_of") or as_of, "retrieved": as_of}
    return out


def render_md(t):
    D, lv = DERIVED, t["levels"]
    P, O, S = lv["price_src"], lv["options_src"], lv["score_src"]
    pos, lt = t["position"], t["look_through"]
    out = ["## %s — sizing a trim at %s (%s)" % (t["ticker"], money(t["price"]), t["price_date"]), "",
           "*computed by size.py; the frames are this standard's own arithmetic on your positions, not a published rule*", "",
           "| Position | |", "|---|---|",
           "| Shares, cost, worth, gain | %s sh · cost %s · worth %s · gain %s [%s, %s] |" % (
               shares_fmt(pos["shares"]), usd0(pos["cost_total"]), usd0(pos["value"]), usd0(pos["gain"]), P, D),
           "| Outright weight of the accounts in scope (%s) | %s [%s] |" % (usd0(t["total_in_scope"]),
                                                                            pct(pos["weight"]) if pos["weight"] is not None else "n/a (%s)" % pos["weight_reason"], D)]
    if lt["rows"]:
        out.append("| Also held through funds | %s — true weight %s [%s, %s] |" % (
            "; ".join("%s %s of the fund = %s" % (r["fund"], pct(r["weight_in_fund"]), usd0(r["value_through_fund"])) for r in lt["rows"]),
            pct(lt["true_weight"]), FUNDS, D))
    for m in lt["missing"]:
        out.append("| Look-through %s | %s |" % (m["fund"], m["reason"]))
    out += ["", "| Frame | Sell | Proceeds | Keep | |", "|---|---|---|---|---|"]
    for f in t["frames"]:
        if f.get("sell_shares") is None:
            out.append("| %s | n/a (%s) | | | [%s] |" % (f["frame"], f.get("reason"), D))
        elif f["sell_shares"] == 0:
            out.append("| %s | nothing: %s | | %s sh | [%s] |" % (f["frame"], f.get("note"), shares_fmt(f["keep_shares"]), D))
        else:
            extra = f.get("note") or ("weight after %s" % pct(f["weight_after"]) if f.get("weight_after") is not None else "")
            out.append("| %s | %d sh | about %s | %s sh%s | [%s] |" % (
                f["frame"], f["sell_shares"], usd0(f["proceeds"]), shares_fmt(f["keep_shares"]), " — " + extra if extra else "", D))
    if t["frames_reason"]:
        out.append("| frames | n/a: %s | | | [%s] |" % (t["frames_reason"], D))
    out += ["", "| Level | Price | |", "|---|---|---|",
            "| 50-day average | %s [%s] |" % (money(lv["ma50"]), D),
            "| 200-day average | %s [%s] |" % (money(lv["ma200"]), D),
            "| 52-week high / low | %s / %s%s [%s] |" % (money(lv["high_52w"]), money(lv["low_52w"]),
                                                       " (%s below the high)" % pct(lv["pct_from_52w_high"]) if lv["pct_from_52w_high"] is not None else "", P)]
    if lv["implied_low"] is not None:
        out.append("| Options-implied range to %s (one standard deviation) | %s to %s (± %s) [%s] |" % (
            lv["implied_expiry"], money(lv["implied_low"]), money(lv["implied_high"]), pct(lv["implied_move_pct"]), O))
    if lv["next_earnings"]:
        out.append("| Next earnings | %s [%s] |" % (lv["next_earnings"], O))
    out += ["| The rule's cell for a holder | %s; trend %s%s [%s] |" % (
        lv["holding_cell"] or "n/a", lv["trend"] or "unknown",
        "; strict value lens: %s" % lv["strict_cell_holding"] if lv["strict_cell_holding"] else "", S)]
    if lv["gates_failed"]:
        out.append("| Deal-breaker checks failed | %s: sell, do not size a trim [%s] |" % (", ".join(lv["gates_failed"]), S))
    out += ["", "Sell from: %s — %s [%s]" % (" then ".join(t["sell_from"]["order"]) or "n/a", t["sell_from"]["rule"], D)]
    for p in t["positions"]:
        out.append("- %s: %s sh at %s cost, worth %s, gain %s — %s [%s, %s]" % (
            p["account"], shares_fmt(p["shares"]), money(p["avg_cost"]), usd0(p["value"]), usd0(p["gain"]), p["tax_on_sale"], P, D))
    return "\n".join(out) + "\n"


def run(argv=None):
    ap = EnvelopeParser(description="Sizing frames and order levels for a trim or a buy, from the stated positions")
    ap.add_argument("target", help="ticker (resolved in the store) or the stock folder path")
    ap.add_argument("--question", required=True, help="the holdings text (holdings.py phrasing)")
    ap.add_argument("--total", type=float, default=None, help="USD value of the accounts in scope")
    ap.add_argument("--caps", default="", help="weight caps as percents, e.g. 15,12.5,10 (default 15,12.5,10)")
    ap.add_argument("--funds", default="", help="funds held, with USD position values: QQQ=8198,VGT=3648")
    ap.add_argument("--md", action="store_true", help="print the Markdown part instead of JSON")
    add_common_args(ap)
    a = ap.parse_args(argv)
    st = locate(a.target, a)
    facts, sc = read_json(st.facts), read_json(st.scorecard)
    if facts is None:
        raise FetchError("facts/facts.json missing in %s (run facts.py first)" % st.root)
    sc = sc if isinstance(sc, dict) else {}
    ticker = facts.get("ticker") or st.ticker
    as_of = today()
    holdings, notes = parse_question(a.question, ticker, as_of)
    if not holdings.get("positions"):
        raise FetchError("no %s position found in the question text (holdings.md phrasing)" % ticker)
    caps = tuple(float(c) / 100 for c in a.caps.split(",") if c.strip()) if a.caps.strip() else DEFAULT_CAPS
    t = build(ticker, holdings, facts, sc, a.total, caps, parse_funds(a.funds), st, as_of)
    t["parse_notes"] = notes
    os.makedirs(st.facts_dir, exist_ok=True)
    path = os.path.join(st.facts_dir, "sizing.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(t, fh, indent=1)
    if a.md:
        print(render_md(t))
    else:
        print(json.dumps({"ok": True, "out": path, "ticker": ticker, "frames": len(t["frames"]),
                          "look_through": len(t["look_through"]["rows"]), "missing": t["look_through"]["missing"]}))


if __name__ == "__main__":
    run_main(SCRIPT, run)
