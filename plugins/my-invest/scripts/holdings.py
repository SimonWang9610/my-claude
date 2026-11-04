#!/usr/bin/env python3
"""holdings.py - arithmetic over the user's broker CSV for this run only: positions, weights, look-through
through the ETFs held, and sizing frames for the tickers named. Reads the database (prices, stats, fund
weights, estimates), writes nothing anywhere: holdings are never stored.

Usage: holdings.py CSV|DIR [--size T1,T2] [--caps 15,12.5,10] [--total USD] [--project P] [--md]

A directory means every *.csv in it (one export per account), merged; the files read are listed under
"files" and each file's column mapping under "columns". A CSV's columns are found by header keywords (symbol/ticker, quantity/shares/units, average cost/book cost/
cost basis, account, market value, currency, description/type) and the mapping used is reported under
"columns". Accounts map to RRSP (RRIF, LIRA, LRSP), TFSA (FHSA) or NONREG (everything else). Only US tickers are
priced; a .TO/.V/.CN/.NE symbol is listed under "skipped". Frames: cap at each --caps weight, sell the gain,
recover the cost; shares to sell are whole shares, taken from RRSP, then TFSA, then NONREG.
"""
import csv
import io
import math
import os
import re
import sys

import calc
import common
import db

SCRIPT = "holdings.py"
DEFAULT_CAPS = "15,12.5,10"
COLUMN_KEYS = {
    "ticker": ("symbol", "ticker"),
    "shares": ("quantity", "shares", "units", "qty"),
    "cost": ("average cost", "avg cost", "avg price", "average price", "book cost", "cost basis", "book value",
             "adjusted cost", "acb", "cost"),
    "account": ("account",),
    "value": ("market value", "mkt value", "current value", "value"),
    "currency": ("currency",),
    "type": ("security type", "asset type", "asset class", "type", "description", "name"),
}
PER_SHARE_WORDS = ("price", "per share", "/share", "avg", "average")
ACCOUNT_ORDER = ("RRSP", "TFSA", "NONREG")
ACCOUNT_REASON = {
    "RRSP": "no tax on a sale; withdrawals are taxed as income later",
    "TFSA": "no tax on a sale or withdrawal",
    "NONREG": "a sale realises a capital gain; half of it is taxable in Canada",
}
CANADIAN_SUFFIXES = (".TO", ".V", ".CN", ".NE")
LEVELS = ("ma50", "ma200", "high_52w", "low_52w", "range_3m_low", "range_3m_high")


# --- reading the CSV ----------------------------------------------------------------------------
def read_csv(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            text = f.read()
    except OSError as e:
        raise common.FetchError("cannot read %s: %s" % (path, e.strerror or e))
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rows_ = [r for r in csv.reader(io.StringIO(text), dialect)]
    for i, r in enumerate(rows_[:20]):  # some brokers put a preamble above the header
        low = [c.strip().lower() for c in r]
        if any(any(k in c for k in COLUMN_KEYS["ticker"]) for c in low):
            return r, [x for x in rows_[i + 1:] if any(c.strip() for c in x)]
    raise common.FetchError("no header with a symbol/ticker column in %s" % path)


def map_columns(header):
    """{field: header text} by keyword; longer keywords win so 'book value' is cost, not value."""
    low = [h.strip().lower() for h in header]
    taken, mapping = set(), {}
    for field, keys in COLUMN_KEYS.items():
        for k in sorted(keys, key=len, reverse=True):
            hit = next((i for i, h in enumerate(low) if k in h and i not in taken), None)
            if hit is not None:
                mapping[field] = header[hit]
                taken.add(hit)
                break
    return mapping


def number(s):
    if s is None:
        return None
    s = str(s).strip().replace("$", "").replace(",", "").replace(" ", "")
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    if s in ("", "-", "—", "N/A", "n/a"):
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def account_kind(text):
    t = (text or "").upper()
    if any(k in t for k in ("RRSP", "RRIF", "LIRA", "LRSP")):
        return "RRSP"
    if any(k in t for k in ("TFSA", "FHSA")):
        return "TFSA"
    return "NONREG"


def clean_symbol(raw):
    """-> (ticker, skip reason)."""
    s = (raw or "").strip().upper().replace("$", "")
    if not s:
        return None, "no ticker"
    if s.endswith(CANADIAN_SUFFIXES):
        return s, "not a US listing"
    if "." not in s and s.endswith("-U"):
        s = s[:-2]
    return s, None


def parse(path):
    """-> (rows [{ticker, shares, avg_cost, account, csv_value, is_fund, currency}], columns, skipped)."""
    header, data = read_csv(path)
    cols = map_columns(header)
    missing = [f for f in ("ticker", "shares") if f not in cols]
    if missing:
        raise common.FetchError("cannot find the %s column(s) in the CSV header %s" % (" and ".join(missing), header))
    idx = {f: header.index(h) for f, h in cols.items()}
    cost_mode = None
    if "cost" in cols:
        cost_mode = "per_share" if any(w in cols["cost"].lower() for w in PER_SHARE_WORDS) else "total"
    out, skipped = [], []
    for r in data:
        get = lambda f: r[idx[f]] if f in idx and idx[f] < len(r) else None
        ticker, why = clean_symbol(get("ticker"))
        type_text = (get("type") or "")
        if why:
            if why == "no ticker" and "CASH" in type_text.upper():
                why = "cash row"
            skipped.append({"symbol": (get("ticker") or type_text or "").strip(), "reason": why})
            continue
        shares = number(get("shares"))
        if not shares:
            skipped.append({"symbol": ticker, "reason": "no shares"})
            continue
        cost = number(get("cost"))
        avg = None if cost is None else (cost if cost_mode == "per_share" else cost / shares)
        out.append({"ticker": ticker, "shares": shares, "avg_cost": avg, "account": account_kind(get("account")),
                    "account_text": (get("account") or "").strip(), "csv_value": number(get("value")),
                    "file": os.path.basename(path),
                    "currency": (get("currency") or "").strip().upper() or None,
                    "is_fund": bool(re.search(r"\b(ETF|EXCHANGE[_ ]TRADED[_ ]FUND|FUND)\b", type_text.upper()))})
    columns = dict(cols)
    if cost_mode:
        columns["cost_mode"] = cost_mode
    return out, columns, skipped


def parse_paths(path):
    """A CSV, or a directory of them -> (rows, files, {basename: columns}, skipped)."""
    if os.path.isdir(path):
        files = sorted(os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(".csv"))
        if not files:
            raise common.FetchError("no *.csv in %s" % path)
    else:
        files = [path]
    rows_, columns, skipped = [], {}, []
    for f in files:
        r, c, s = parse(f)
        rows_ += r
        columns[os.path.basename(f)] = c
        skipped += [dict(x, file=os.path.basename(f)) for x in s]
    return rows_, files, columns, skipped


# --- pricing and aggregation --------------------------------------------------------------------
def price_rows(conn, rows_, skipped):
    kinds = {r["ticker"]: r["kind"] for r in db.rows(conn, "SELECT ticker, kind FROM securities")}
    funds = {r["ticker"] for r in db.rows(conn, "SELECT ticker FROM funds")}
    priced = []
    for r in rows_:
        lp = db.latest_price(conn, r["ticker"])
        if lp:
            r["price"], r["price_from"], r["price_date"] = lp["close"], "db", lp["date"]
        elif r["csv_value"]:
            r["price"], r["price_from"], r["price_date"] = r["csv_value"] / r["shares"], "csv", None
        else:
            skipped.append({"symbol": r["ticker"], "reason": "no price; run yahoo.py prices %s" % r["ticker"]})
            continue
        if not r["is_fund"]:
            r["is_fund"] = kinds.get(r["ticker"]) == "fund" or r["ticker"] in funds
        r["value"] = r["shares"] * r["price"]
        r["cost"] = r["shares"] * r["avg_cost"] if r["avg_cost"] is not None else None
        r["gain"] = r["value"] - r["cost"] if r["cost"] is not None else None
        r["gain_pct"] = r["gain"] / r["cost"] if r["cost"] else None
        priced.append(r)
    return priced


def aggregate(rows_, total):
    by = {}
    for r in rows_:
        a = by.setdefault(r["ticker"], {"ticker": r["ticker"], "shares": 0.0, "value": 0.0, "cost": 0.0, "cost_known": True,
                                        "price": r["price"], "price_from": r["price_from"], "is_fund": r["is_fund"],
                                        "accounts": []})
        a["shares"] += r["shares"]
        a["value"] += r["value"]
        if r["cost"] is None:
            a["cost_known"] = False
        else:
            a["cost"] += r["cost"]
        a["is_fund"] = a["is_fund"] or r["is_fund"]
        a["accounts"].append(r)
    out = []
    for a in by.values():
        a["avg_cost"] = a["cost"] / a["shares"] if a["cost_known"] and a["shares"] else None
        if not a["cost_known"]:
            a["cost"] = None
        a["gain"] = a["value"] - a["cost"] if a["cost"] is not None else None
        a["gain_pct"] = a["gain"] / a["cost"] if a["cost"] else None
        a["weight"] = a["value"] / total if total else None
        for r in a["accounts"]:
            r["weight"] = r["value"] / total if total else None
        out.append(a)
    out.sort(key=lambda x: -x["value"])
    return out


def look_through(conn, positions, total):
    """Per constituent: direct weight + the share of each fund's value that its holdings rows assign."""
    direct = {p["ticker"]: p["value"] for p in positions}
    via = {}
    funds_used = []
    for p in positions:
        if not p["is_fund"]:
            continue
        latest = db.one(conn, "SELECT MAX(asof) asof FROM fund_weights WHERE fund = ? AND kind = 'holding'", (p["ticker"],))
        if not latest or not latest["asof"]:
            funds_used.append({"fund": p["ticker"], "asof": None, "constituents": 0})
            continue
        recs = db.rows(conn, "SELECT key, weight FROM fund_weights WHERE fund = ? AND kind = 'holding' AND asof = ?",
                       (p["ticker"], latest["asof"]))
        funds_used.append({"fund": p["ticker"], "asof": latest["asof"], "constituents": len(recs)})
        for r in recs:
            k = r["key"].upper()
            via.setdefault(k, []).append({"fund": p["ticker"], "value": p["value"] * r["weight"],
                                          "weight": p["value"] * r["weight"] / total if total else None})
    out = []
    for t in set(direct) | set(via):
        d = direct.get(t, 0.0) if not any(p["ticker"] == t and p["is_fund"] for p in positions) else 0.0
        v = sum(x["value"] for x in via.get(t, []))
        if d == 0 and v == 0:
            continue
        out.append({"ticker": t, "direct": d, "via": via.get(t, []), "via_value": v, "total_value": d + v,
                    "direct_weight": d / total if total else None, "via_weight": v / total if total else None,
                    "total_weight": (d + v) / total if total else None})
    out.sort(key=lambda x: -x["total_value"])
    return out[:10], funds_used


# --- sizing -------------------------------------------------------------------------------------
def from_accounts(position, shares_to_sell):
    plan, left = [], shares_to_sell
    for acct in ACCOUNT_ORDER:
        for r in sorted((x for x in position["accounts"] if x["account"] == acct), key=lambda x: -x["shares"]):
            if left <= 0:
                break
            take = min(r["shares"], left)
            plan.append({"account": acct, "account_text": r["account_text"], "shares": take, "reason": ACCOUNT_REASON[acct]})
            left -= take
    return plan


def frames(position, caps, total):
    p, s, v = position["price"], position["shares"], position["value"]
    out = []

    def frame(name, shares, note=None):
        shares = min(s, max(0, shares))
        out.append({"frame": name, "shares_to_sell": shares, "proceeds": shares * p, "shares_kept": s - shares,
                    "from_accounts": from_accounts(position, shares) if shares else [], "note": note})

    for cap in caps:
        target = cap * total
        if v <= target:
            frame("cap at %s" % calc.pct_plain(cap, 1), 0, "already under the cap")
        else:
            frame("cap at %s" % calc.pct_plain(cap, 1), math.ceil((v - target) / p - 1e-9),
                  "cap on today's total of %s" % calc.money(total, 0))
    if position["gain"] is None:
        frame("sell the gain", 0, "no cost basis in the CSV")
        frame("recover cost", 0, "no cost basis in the CSV")
    else:
        if position["gain"] <= 0:
            frame("sell the gain", 0, "no gain to take out")
        else:
            frame("sell the gain", math.ceil(position["gain"] / p - 1e-9), "takes out the dollar gain of %s" % calc.money(position["gain"], 0))
        if position["cost"] >= v:
            frame("recover cost", s, "selling everything does not recover the cost")
        else:
            frame("recover cost", math.ceil(position["cost"] / p - 1e-9), "takes out the cost basis of %s" % calc.money(position["cost"], 0))
    return out


def levels(conn, ticker, skipped):
    asof = db.one(conn, "SELECT MAX(asof) asof FROM stats WHERE ticker = ?", (ticker,))
    out = {}
    if asof and asof["asof"]:
        for r in db.rows(conn, "SELECT metric, value FROM stats WHERE ticker = ? AND asof = ? AND window = 'spot'", (ticker, asof["asof"])):
            if r["metric"] in LEVELS:
                out[r["metric"]] = r["value"]
        out["asof"] = asof["asof"]
    else:
        skipped.append({"symbol": ticker, "reason": "run stats.py %s" % ticker})
    e = db.one(conn, "SELECT next_earnings FROM estimates WHERE ticker = ? AND next_earnings IS NOT NULL ORDER BY asof DESC LIMIT 1", (ticker,))
    if e:
        out["next_earnings"] = e["next_earnings"]
    return out


# --- rendering ----------------------------------------------------------------------------------
def md(res):
    recs = []
    for p in res["positions"]:
        recs.append({"ticker": p["ticker"], "kind": "fund" if p["is_fund"] else "stock", "shares": calc.num(p["shares"], 2),
                     "avg cost": calc.money(p["avg_cost"]), "price": calc.money(p["price"]) + ("*" if p["price_from"] == "csv" else ""),
                     "value": calc.money(p["value"], 0), "gain": calc.money(p["gain"], 0), "gain %": calc.pct(p["gain_pct"]),
                     "weight": calc.pct_plain(p["weight"]), "accounts": ", ".join("%s %s" % (r["account"], calc.num(r["shares"], 0)) for r in p["accounts"])})
    pf = res["portfolio"]
    out = ["**Positions** (total %s; %d positions; funds %s, stocks %s)" % (
        calc.money(pf["total"], 0), pf["positions"], calc.pct_plain(pf["funds_weight"]), calc.pct_plain(pf["stocks_weight"])),
        "", db.md_table(recs)]
    if any(p["price_from"] == "csv" for p in res["positions"]):
        out.append("\\* price from the CSV's market value, not the database")
    if res["look_through"]:
        lt = [{"ticker": x["ticker"], "direct": calc.pct_plain(x["direct_weight"]),
               "via funds": ", ".join("%s %s" % (v["fund"], calc.pct_plain(v["weight"])) for v in x["via"]) or "",
               "total": calc.pct_plain(x["total_weight"])} for x in res["look_through"]]
        out += ["", "**Look-through** (top 10)", "", db.md_table(lt)]
    for t, sz in res["sizing"].items():
        if "error" in sz:
            out += ["", "**%s**: %s" % (t, sz["error"])]
            continue
        fr = [{"frame": f["frame"], "shares to sell": calc.num(f["shares_to_sell"], 0), "proceeds": calc.money(f["proceeds"], 0),
               "shares kept": calc.num(f["shares_kept"], 0),
               "from accounts": "; ".join("%s %s (%s)" % (a["account"], calc.num(a["shares"], 0), a["reason"]) for a in f["from_accounts"]) or (f["note"] or "")}
              for f in sz["frames"]]
        out += ["", "**%s** sizing (%s shares, %s, %s of the total)" % (t, calc.num(sz["position"]["shares"], 0),
                                                                     calc.money(sz["position"]["value"], 0), calc.pct_plain(sz["position"]["weight"])),
                "", db.md_table(fr)]
        lv = sz["levels"]
        if "asof" in lv:
            line = "Levels as of %s: " % lv["asof"] + " · ".join("%s %s" % (k, calc.money(lv[k])) for k in LEVELS if k in lv)
        else:
            line = "Levels: none (run stats.py %s)" % t
        if lv.get("next_earnings"):
            line += " · next earnings %s" % lv["next_earnings"]
        out.append(line)
    if res["skipped"]:
        out += ["", "Skipped: " + "; ".join("%s (%s)" % (x["symbol"], x["reason"]) for x in res["skipped"])]
    return "\n".join(out)


def analyse(conn, path, size, caps, total_flag):
    rows_, files, columns, skipped = parse_paths(path)
    priced = price_rows(conn, rows_, skipped)
    if not priced:
        raise common.FetchError("no priced US positions in %s" % path)
    total = total_flag or sum(r["value"] for r in priced)
    positions = aggregate(priced, total)
    lt, funds_used = look_through(conn, positions, total)
    fund_value = sum(p["value"] for p in positions if p["is_fund"])
    stock_value = sum(p["value"] for p in positions if not p["is_fund"])
    portfolio = {"total": total, "total_from": "flag" if total_flag else "sum of values", "positions": len(positions),
                 "top5": [{"ticker": p["ticker"], "weight": p["weight"]} for p in positions[:5]],
                 "funds_value": fund_value, "funds_weight": fund_value / total if total else None,
                 "stocks_value": stock_value, "stocks_weight": stock_value / total if total else None,
                 "funds_looked_through": funds_used}
    sizing = {}
    for t in size:
        pos = next((p for p in positions if p["ticker"] == t), None)
        if not pos:
            sizing[t] = {"error": "%s is not in the CSV" % t}
            continue
        sizing[t] = {"position": {k: pos[k] for k in ("shares", "avg_cost", "price", "value", "cost", "gain", "gain_pct", "weight")},
                     "frames": frames(pos, caps, total), "levels": levels(conn, t, skipped)}
    return {"ok": True, "script": SCRIPT, "files": files, "columns": columns, "positions": positions, "portfolio": portfolio,
            "look_through": lt, "sizing": sizing, "skipped": skipped}


def run(argv=None):
    p = common.parser(SCRIPT, "arithmetic over a broker CSV: positions, look-through, sizing frames; stores nothing")
    p.add_argument("csv", help="the broker's positions export, or a folder of them (one per account)")
    p.add_argument("--size", default="", help="tickers to size, comma-separated")
    p.add_argument("--caps", default=DEFAULT_CAPS, help="cap weights in percent (default %s)" % DEFAULT_CAPS)
    p.add_argument("--total", type=float, default=None, help="portfolio total in USD when the CSV is partial")
    a = p.parse_args(argv)
    try:
        caps = [float(c) / 100.0 for c in a.caps.split(",") if c.strip()]
    except ValueError:
        return common.fail(SCRIPT, "--caps wants percents like 15,12.5,10, got %r" % a.caps)
    size = [t.strip().upper() for t in a.size.split(",") if t.strip()]
    conn = db.connect(a.project)
    db.read_only(conn)
    res = analyse(conn, a.csv, size, caps, a.total)
    return common.emit(res, md=md(res) if a.md else None)


if __name__ == "__main__":
    sys.exit(common.run_main(SCRIPT, run))
