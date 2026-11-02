#!/usr/bin/env python3
"""holdings.py (<TICKER> | <stock folder>) (--question TEXT | --json JSON) [--price X] [--fx X]
    [--zones B,BASE,S] [--md] [--store DIR] [--project DIR] [--out FILE]

Parses the holdings a question states (skills/advisor/references/holdings.md) for the folder's ticker only,
writes facts/holdings.json and facts/holdings_tables.json in the stock folder, and prints the tables as JSON (or as a
Markdown part with --md). Tax lines come from skills/standard/references/tax-ca.md, read by row id.
Python 3.9, stdlib only. Any failure prints the error envelope and exits 1.
"""
import datetime as dt
import json
import os
import re
import sys

import common

SCRIPT = "holdings.py"
HERE = os.path.dirname(os.path.abspath(__file__))
TAX_MD = os.path.join(HERE, "..", "skills", "standard", "references", "tax-ca.md")
BOC_URL = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json"
INCLUSION = 0.5  # T-INCL
DISCLAIMER = ("General information, not tax advice: provincial rates and credits differ, the marginal rate is "
              "the user's input, and after-tax figures are estimates.")

# rule id -> (source id, what) for the rules the tables cite; S98 = USD/CAD rate, S99 = this script.
RULE_SRC = {"T-INCL": ("S90", "Income Tax Act s.38(a), capital gains inclusion rate"),
            "T-GAIN": ("S91", "CRA, calculating capital gains (proceeds - ACB - outlays)"),
            "T-TFSA": ("S92", "CRA, what is a TFSA (income and withdrawals tax-free)"),
            "T-RRSP": ("S93", "CRA, RRSP withdrawals taxed as income"),
            "T-FDIV": ("S94", "CRA line 12100, foreign dividends (no dividend tax credit)"),
            "T-TREATY": ("S95", "Canada-US tax convention, Art. X(2)(b) 15% and Art. XXI(2)"),
            "T-TFSA-WHT": ("S96", "CRA Folio S5-F2-C1 para 1.69, no foreign tax credit for TFSA"),
            "T-RRSP-US": ("S97", "IRS PLR-142074-07, RRSP exempt from US dividend withholding")}
TREATMENT = {"NONREG": "T-GAIN", "TFSA": "T-TFSA", "RRSP": "T-RRSP"}
DIVIDENDS = {"NONREG": ["T-FDIV", "T-TREATY"], "TFSA": ["T-TREATY", "T-TFSA-WHT"], "RRSP": ["T-RRSP-US"]}
ACCOUNT_ORDER = ["TFSA", "RRSP", "NONREG"]

# --- parsing -----------------------------------------------------------------------------------
NUM = r"\d[\d,]*(?:\.\d+)?"
ACCOUNTS = [("RRSP", re.compile(r"\b(?:RRSP|RRIF|LIRA|RSP)\b", re.I)),
            ("TFSA", re.compile(r"\b(?:TFSA|FHSA)\b", re.I)),
            ("NONREG", re.compile(r"\bnon[-\s]?(?:registered|reg)\b|\bunregistered\b|\btaxable\b|\bmargin\b"
                                  r"|\bcash\s+account\b", re.I))]
POSITION = re.compile(
    r"(?<![\w.$])(?P<qty>" + NUM + r")\s+(?:(?i:shares?|sh)\s+(?:(?i:of)\s+)?)?(?:(?P<tkr>[A-Z]{1,5}(?:[.-][A-Z])?)\b\s*)?"
    r"(?:(?i:shares?)\s*)?,?\s*(?P<cue>@|(?i:at|bought\s+at|paid|avg\.?\s*cost|avg\.?\s*price|average\s+cost|"
    r"average\s+price|average|cost\s+basis|cost))\s*(?i:of\s+)?[:=]?\s*"
    r"(?P<pre>(?i:US\$|C\$|CA\$|CAD|USD))?\s*\$?\s*(?P<cost>" + NUM + r")(?P<post>\s*(?i:CAD|USD|C\$))?")
RATE = [re.compile(r"(?i)marginal\s+(?:tax\s+)?(?:rate|bracket)\s*(?:is|of|=|:|at|around|about)?\s*(\d{1,2}(?:\.\d+)?)\s*%"),
        re.compile(r"(?i)(\d{1,2}(?:\.\d+)?)\s*%\s*(?:marginal|tax\s+bracket|bracket)"),
        re.compile(r"(?i)\btax\s+rate\s*(?:is|of|=|:)?\s*(\d{1,2}(?:\.\d+)?)\s*%")]
EVAL = re.compile(r"(?i)\b(?:hits?|reach(?:es)?|goes\s+to|gets\s+to|rises\s+to|falls\s+to|drops\s+to|climbs\s+to|"
                  r"trades\s+at|sell\s+at|price\s+(?:of|is)|what\s+if\s+(?:it(?:'s|\s+is)\s+)?(?:at\s+)?)\s*"
                  r"(\$?\s*" + NUM + r"(?:\s*(?:,|or|and|/)\s*\$?\s*" + NUM + r")*)")
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "a": 1, "an": 1}
PERIOD = re.compile(r"(?i)\b(?:hold(?:ing)?(?:\s+it)?(?:\s+for)?|for|over|in|within|horizon\s+of)\s+(?:the\s+next\s+|another\s+)?"
                    r"(\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|a|an)\s*"
                    r"(years?|yrs?|months?|mos?|weeks?)\b")
UNTIL = re.compile(r"(?i)\b(?:until|till|by|through)\s+(?:the\s+)?(?:end\s+of\s+)?(\d{4}-\d{2}-\d{2}|(?:19|20)\d{2})\b")


def fnum(s):
    return float(s.replace(",", "").replace("$", "").strip())


def account_for(prefix, after):
    """Account of a position: 'RRSP:' right before it, else the first keyword after it (not a 'X:' label
    of the next position), else the last keyword before it."""
    for name, rx in ACCOUNTS:
        if re.search(r"(?:" + rx.pattern + r")\s*[:\-]\s*$", prefix, re.I):
            return name
    hits = []
    for name, rx in ACCOUNTS:
        for m in rx.finditer(after):
            if not re.match(r"\s*:", after[m.end():]):
                hits.append((m.start(), name))
    if hits:
        return min(hits)[1]
    hits = [(m.start(), name) for name, rx in ACCOUNTS for m in rx.finditer(prefix)]
    return max(hits)[1] if hits else None


def add_period(as_of, n, unit):
    d = dt.date.fromisoformat(as_of)
    unit = unit.lower()
    if unit.startswith("w"):
        return (d + dt.timedelta(weeks=n)).isoformat()
    months = int(round(n * 12)) if unit.startswith("y") else int(round(n))
    y, m = divmod(d.month - 1 + months, 12)
    day = min(d.day, [31, 29 if (d.year + y) % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m])
    return dt.date(d.year + y, m + 1, day).isoformat()


def parse_question(text, ticker, as_of):
    """Return the holdings.json dict for `ticker`, plus a list of parse notes."""
    ticker = ticker.upper()
    text = re.sub(r"(?i)(?<![A-Za-z])" + re.escape(ticker) + r"(?![A-Za-z])", ticker, text)
    matches = list(POSITION.finditer(text))
    positions, notes, spans, last_tkr = [], [], [], None
    for i, m in enumerate(matches):
        tkr = m.group("tkr")
        if tkr and tkr.lower() in ("at", "of", "avg", "cost"):
            tkr = None
        tkr = tkr or last_tkr or ticker
        last_tkr = tkr
        spans.append(m.span())
        if tkr != ticker:
            continue
        prefix = text[matches[i - 1].end() if i else 0:m.start()]
        after = text[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(text)]
        acct = account_for(prefix, after)
        if acct is None:
            acct = "NONREG"
            notes.append("account not stated for %s %s; treated as non-registered" % (m.group("qty"), tkr))
        pos = {"account": acct, "shares": fnum(m.group("qty")), "avg_cost": fnum(m.group("cost"))}
        cur = (m.group("pre") or "") + (m.group("post") or "")
        if re.search(r"(?i)C\$|CA\$|CAD", cur):
            pos["currency"] = "CAD"
        positions.append(pos)
    rate = None
    for rx in RATE:
        r = rx.search(text)
        if r:
            rate = round(float(r.group(1)) / 100, 4)
            break
    evals = []
    for e in EVAL.finditer(text):
        if any(a <= e.start(1) < b for a, b in spans):
            continue
        for n in re.findall(NUM, e.group(1)):
            v = fnum(n)
            if v > 0 and v not in evals:
                evals.append(v)
    horizon = None
    p = PERIOD.search(text)
    if p:
        n = WORDS.get(p.group(1).lower()) or float(p.group(1))
        horizon = add_period(as_of, float(n), p.group(2))
    else:
        u = UNTIL.search(text)
        if u:
            horizon = u.group(1) if "-" in u.group(1) else u.group(1) + "-12-31"
    return ({"ticker": ticker, "as_of": as_of, "currency": "USD", "positions": positions,
             "marginal_rate": rate, "eval_prices": evals, "horizon_end": horizon}, notes)


def normalize_account(a):
    for name, rx in ACCOUNTS:
        if a and (a.upper() == name or rx.search(a)):
            return name
    raise common.FetchError("unknown account type %r (RRSP, TFSA or NONREG)" % (a,))


def from_json(raw, ticker, as_of):
    try:
        h = json.loads(raw)
    except ValueError as e:
        raise common.FetchError("--json is not valid JSON: %s" % e)
    if h.get("ticker") and h["ticker"].upper() != ticker.upper():
        raise common.FetchError("--json ticker %s does not match folder %s" % (h["ticker"], ticker))
    pos = []
    for p in h.get("positions") or []:
        q = {"account": normalize_account(p.get("account")), "shares": float(p["shares"]),
             "avg_cost": float(p["avg_cost"])}
        if str(p.get("currency", "USD")).upper() == "CAD":
            q["currency"] = "CAD"
        pos.append(q)
    rate = h.get("marginal_rate")
    return {"ticker": ticker.upper(), "as_of": h.get("as_of") or as_of, "currency": "USD", "positions": pos,
            "marginal_rate": None if rate is None else float(rate),
            "eval_prices": [float(x) for x in h.get("eval_prices") or []], "horizon_end": h.get("horizon_end")}


# --- tax rules ---------------------------------------------------------------------------------
def load_rules(path=TAX_MD):
    rules = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) >= 5 and re.fullmatch(r"T-[A-Z0-9-]+", c[0]):
                rules[c[0]] = {"rule": c[1], "url": c[2], "retrieved": c[3]}
    missing = [k for k in list(RULE_SRC) + ["T-FX", "T-SUPER"] if k not in rules]
    if missing:
        raise common.FetchError("tax-ca.md is missing rule rows: %s" % ", ".join(missing))
    return rules


# --- computation -------------------------------------------------------------------------------
def r2(x):
    return None if x is None else round(x, 2)


def aggregate(positions, fx):
    """One row per account: shares, weighted average cost (USD), cost_total (USD), acb_cad."""
    acc = {}
    for p in positions:
        a = acc.setdefault(p["account"], {"shares": 0.0, "cost_usd": 0.0, "acb_cad": 0.0, "usd_ok": True,
                                          "cad_ok": True})
        cost = p["shares"] * p["avg_cost"]
        if p.get("currency") == "CAD":
            a["acb_cad"] += cost
            a["cost_usd"] += cost / fx if fx else 0.0
            a["usd_ok"] = a["usd_ok"] and bool(fx)
        else:
            a["cost_usd"] += cost
            a["acb_cad"] += cost * fx if fx else 0.0
            a["cad_ok"] = a["cad_ok"] and bool(fx)
        a["shares"] += p["shares"]
    rows = []
    for name in sorted(acc, key=ACCOUNT_ORDER.index):
        a = acc[name]
        cost_usd = a["cost_usd"] if a["usd_ok"] else None
        rows.append({"account": name, "shares": a["shares"],
                     "avg_cost": r2(cost_usd / a["shares"]) if cost_usd is not None else None,
                     "cost_total": r2(cost_usd), "acb_cad": r2(a["acb_cad"]) if a["cad_ok"] else None})
    return rows


def price_points(price, zones, evals):
    pts = [("current", price)]
    for key, label in (("buy_below", "buy zone"), ("base_today", "base value"), ("sell_above", "sell zone")):
        if zones and zones.get(key) is not None:
            pts.append((label, float(zones[key])))
    for e in evals:
        pts.append(("named $%s" % fmt_num(e), e))
    return pts


def fmt_num(x):
    return ("%.2f" % x).rstrip("0").rstrip(".")


def outcomes(rows, points, fx):
    out = []
    for r in rows:
        pp = []
        for label, p in points:
            value = r["shares"] * p
            gain = value - r["cost_total"] if r["cost_total"] is not None else None
            vcad = value * fx if fx else None
            gcad = vcad - r["acb_cad"] if vcad is not None and r["acb_cad"] is not None else None
            pp.append({"label": label, "price": r2(p), "value": r2(value), "gain_abs": r2(gain),
                       "gain_pct": round(gain / r["cost_total"], 4) if gain is not None and r["cost_total"] else None,
                       "value_cad": r2(vcad), "gain_cad": r2(gcad)})
        out.append({"account": r["account"], "shares": r["shares"], "avg_cost": r["avg_cost"],
                    "cost_total": r["cost_total"], "acb_cad": r["acb_cad"], "price_points": pp})
    return out


def tax_rows(outs, rate, rules):
    rows = []
    for o in outs:
        a = o["account"]
        rid = TREATMENT[a]
        pts = []
        for p in o["price_points"]:
            v, g = p["value_cad"], p["gain_cad"]
            t = {"label": p["label"], "price": p["price"]}
            if a == "NONREG":
                taxable = r2(INCLUSION * g) if g is not None else None
                tax = r2(max(taxable, 0.0) * rate) if taxable is not None and rate is not None else None
                t.update(taxable_amount_cad=taxable, estimated_tax_cad=tax,
                         after_tax_proceeds_cad=r2(v - tax) if tax is not None else None)
            else:
                t.update(taxable_amount_cad=0.0 if v is not None else None, estimated_tax_cad=0.0 if v is not None else None,
                         after_tax_proceeds_cad=v)
                if a == "RRSP":
                    t["if_withdrawn_tax_cad"] = r2(v * rate) if v is not None and rate is not None else None
            pts.append(t)
        row = {"account": a, "treatment": rules[rid]["rule"], "citation": rules[rid]["url"],
               "src": RULE_SRC[rid][0], "points": pts}
        if a == "NONREG":
            row["inclusion_rate"] = INCLUSION
            row["inclusion_src"] = RULE_SRC["T-INCL"][0]
        if a == "RRSP":
            row["note"] = "withdrawal taxed as income; nothing is taxed on a sale inside the plan"
        rows.append(row)
    return rows


def dividend_rows(outs, rules):
    rows = []
    for o in outs:
        ids = DIVIDENDS[o["account"]]
        rows.append({"account": o["account"], "treatment": " ".join(rules[i]["rule"] for i in ids),
                     "citations": [rules[i]["url"] for i in ids], "src": [RULE_SRC[i][0] for i in ids]})
    return rows


# --- inputs ------------------------------------------------------------------------------------
def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def resolve_fx(args, facts, folder, as_of):
    """Return (rate, date, source_row) or (None, None, None). Order: --fx, facts.json, Bank of Canada."""
    if args.fx is not None:
        return args.fx, as_of, {"class": "derived", "what": "USD/CAD rate supplied with --fx",
                                "url": "file://" + os.path.join(folder, "holdings.json"),
                                "as_of": as_of, "retrieved": as_of}
    fx = ((facts or {}).get("market") or {}).get("fx_usdcad") or {}
    if fx.get("rate"):
        s = ((facts or {}).get("sources") or {}).get(fx.get("src"), {})
        row = {"class": s.get("class", "primary"), "what": s.get("what", "Bank of Canada FXUSDCAD daily rate"),
               "url": s.get("url", BOC_URL), "as_of": fx.get("date", ""), "retrieved": s.get("retrieved", as_of)}
        return float(fx["rate"]), fx.get("date"), row
    if args.offline:
        return None, None, None
    try:
        body, retrieved = common.ctx_from(args).get_json(BOC_URL + "?recent=1", "macro")
        ob = body["observations"][-1]
        return float(ob["FXUSDCAD"]["v"]), ob["d"], {
            "class": "primary", "what": "Bank of Canada FXUSDCAD daily rate (CAD per USD)",
            "url": BOC_URL + "?start_date=%s&end_date=%s" % (ob["d"], ob["d"]), "as_of": ob["d"],
            "retrieved": retrieved[:10]}
    except (common.FetchError, KeyError, IndexError, ValueError, TypeError):
        return None, None, None


def build(folder, holdings, price, fx, fx_date, fx_row, zones, rules, parse_notes=()):
    as_of = holdings["as_of"]
    rows = aggregate(holdings["positions"], fx)
    outs = outcomes(rows, price_points(price, zones, holdings["eval_prices"]), fx)
    sources = {}
    for rid, (sid, what) in RULE_SRC.items():
        sources[sid] = {"class": "primary", "what": what, "url": rules[rid]["url"], "as_of": rules[rid]["retrieved"],
                        "retrieved": rules[rid]["retrieved"]}
    if fx_row:
        sources["S98"] = fx_row
    sources["S99"] = {"class": "derived", "what": "holdings.py gain/loss and tax estimates from facts.json price, "
                      "scorecard.json zones, holdings.json and S90-S98",
                      "url": "file://" + os.path.join(folder, "holdings_tables.json"), "as_of": as_of,
                      "retrieved": as_of}
    notes = list(parse_notes)
    if any(p.get("currency") != "CAD" for p in holdings["positions"]):
        notes.append("ACB uses the current FX rate as an approximation; CRA requires the rate on each purchase "
                     "date (%s)" % rules["T-FX"]["url"])
    if fx is None:
        notes.append("no USD/CAD rate available (facts.json has none and Bank of Canada was not reached); "
                     "CAD and tax figures are null; pass --fx")
    if holdings["marginal_rate"] is None:
        notes.append("no marginal rate stated; estimated tax omitted")
    if not zones:
        notes.append("zones not available (no scorecard.json); price points are current and named prices only")
    if any(p["gain_cad"] is not None and p["gain_cad"] < 0 for o in outs if o["account"] == "NONREG"
           for p in o["price_points"]):
        notes.append("a non-registered loss is a capital loss; the superficial loss rule denies it if the same "
                     "shares are bought within thirty days before or after the sale and still held (%s)" % rules["T-SUPER"]["url"])
    notes.append("outlays and expenses of sale (commissions) are not stated and are taken as zero")
    notes.append(DISCLAIMER)
    tax, divs = tax_rows(outs, holdings["marginal_rate"], rules), dividend_rows(outs, rules)
    used = {"S98", "S99"} | {r["src"] for r in tax} | {r.get("inclusion_src") for r in tax} | \
        {s for d in divs for s in d["src"]}
    return {"ticker": holdings["ticker"], "as_of": as_of, "currency": "USD",
            "fx_usdcad": {"rate": fx, "date": fx_date, "src": "S98" if fx_row else None},
            "marginal_rate": holdings["marginal_rate"], "horizon_end": holdings["horizon_end"],
            "outcomes": outs, "tax": tax, "dividends": divs,
            "sources": {k: v for k, v in sources.items() if k in used}, "notes": notes}


# --- markdown ----------------------------------------------------------------------------------
def money(x, signed=False):
    if x is None:
        return "n/a"
    s = "-" if x < 0 else ("+" if signed and x > 0 else "")
    return "%s$%s" % (s, "{:,.2f}".format(abs(x)))


def pct(x):
    return "n/a" if x is None else "%+.1f%%" % (x * 100)


def render_md(t):
    fx = t["fx_usdcad"]
    m = ["### Holdings — %s, as of %s" % (t["ticker"], t["as_of"]), ""]
    if fx["rate"]:
        m += ["USD/CAD %.4f on %s [S98]." % (fx["rate"], fx["date"]), ""]
    m += ["#### Outcomes (USD; CAD at the current rate)", "",
          "| Account | Shares | Avg cost | Point | Price | Value | Gain | Gain % | Value CAD | Gain CAD | Src |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for o in t["outcomes"]:
        for p in o["price_points"]:
            m.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | [S99] |" % (
                o["account"], fmt_num(o["shares"]), money(o["avg_cost"]), p["label"], money(p["price"]),
                money(p["value"]), money(p["gain_abs"], True), pct(p["gain_pct"]), money(p["value_cad"]),
                money(p["gain_cad"], True)))
    m += ["", "#### Tax (CAD, federal rules; estimates)", "",
          "| Account | Point | Taxable | Est. tax | After-tax proceeds | If withdrawn, tax | Src |",
          "|---|---|---|---|---|---|---|"]
    for r in t["tax"]:
        src = "[%s, %s, S99]" % (r["src"], r["inclusion_src"]) if r["account"] == "NONREG" else "[%s, S99]" % r["src"]
        for p in r["points"]:
            m.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                r["account"], p["label"], money(p["taxable_amount_cad"]), money(p["estimated_tax_cad"]),
                money(p["after_tax_proceeds_cad"]),
                money(p.get("if_withdrawn_tax_cad")) if r["account"] == "RRSP" else "—", src))
    rate = t["marginal_rate"]
    m += ["", "Marginal rate %s as stated by the user [S99]." % ("%.1f%%" % (rate * 100)) if rate is not None
          else "No marginal rate stated; estimated tax is n/a.", ""]
    for r in t["tax"]:
        m.append("- **%s** — %s [%s]" % (r["account"], r["treatment"], r["src"]))
    m += ["", "#### US dividends by account", ""]
    for d in t["dividends"]:
        m.append("- **%s** — %s [%s]" % (d["account"], d["treatment"], ", ".join(d["src"])))
    m += ["", "#### Notes", ""]
    for n in t["notes"]:
        m.append("- %s" % n)
    m += ["", "### Evidence log", "", "| S | class | what | url | as-of | retrieved |", "|---|---|---|---|---|---|"]
    for sid in sorted(t["sources"], key=lambda s: int(s[1:])):
        s = t["sources"][sid]
        m.append("| %s | %s | %s | %s | %s | %s |" % (sid, s["class"], s["what"], s["url"], s["as_of"], s["retrieved"]))
    return "\n".join(m) + "\n"


# --- CLI ---------------------------------------------------------------------------------------
def write(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def run(argv=None):
    ap = common.EnvelopeParser(prog=SCRIPT, description="Holdings outcome and Canadian tax tables for one ticker")
    ap.add_argument("target", help="ticker (resolved in the store) or the stock folder path")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--question", help="the user's question text")
    g.add_argument("--json", help="holdings JSON (holdings.md shape)")
    ap.add_argument("--price", type=float, help="current price (default facts.json price.last)")
    ap.add_argument("--fx", type=float, help="USD/CAD (default facts.json market.fx_usdcad.rate, else Bank of Canada)")
    ap.add_argument("--zones", default="", help="buy_below,base_today,sell_above (default scorecard.json zones)")
    ap.add_argument("--md", action="store_true", help="print the Markdown part instead of JSON")
    ap.add_argument("--offline", action="store_true", help="never fetch the Bank of Canada rate")
    common.add_common_args(ap)
    args = ap.parse_args(argv)
    st = common.locate(args.target, args)
    if not os.path.isdir(st.root):
        raise common.FetchError("ticker folder not found: %s" % st.root)
    if not args.store and os.path.basename(os.path.dirname(st.root)) == "stocks":
        args.store = os.path.dirname(os.path.dirname(st.root))  # HTTP cache goes to <store>/.cache
    ticker, folder = st.ticker, st.facts_dir
    facts = read_json(st.facts)
    as_of = common.today()
    notes = []
    if args.question is not None:
        holdings, notes = parse_question(args.question, ticker, as_of)
    else:
        holdings = from_json(args.json, ticker, as_of)
    if not holdings["positions"]:
        raise common.FetchError("no %s position (shares, average cost, account) found in the input" % ticker)
    price = args.price if args.price is not None else ((facts or {}).get("price") or {}).get("last")
    if price is None:
        raise common.FetchError("no current price: facts.json price.last is missing; pass --price")
    if args.zones:
        try:
            b, base, s = [float(x) for x in args.zones.split(",")]
        except ValueError:
            raise common.FetchError("--zones must be buy_below,base_today,sell_above")
        zones = {"buy_below": b, "base_today": base, "sell_above": s}
    else:
        zones = (read_json(st.scorecard) or {}).get("zones")
    fx, fx_date, fx_row = resolve_fx(args, facts, folder, as_of)
    tables = build(folder, holdings, float(price), fx, fx_date, fx_row, zones, load_rules(), notes)
    write(st.holdings, holdings)
    write(st.holdings_tables, tables)
    if args.md:
        sys.stdout.write(render_md(tables))
    else:
        common.emit(tables, args.out)
    return tables


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
