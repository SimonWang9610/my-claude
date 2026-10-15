#!/usr/bin/env python3
"""compare.py TICKER --peers A,B,C [--md] [--project DIR] [--store DIR] - side-by-side of stored facts.

Reads facts/facts.json (and facts/scorecard.json when present) of TICKER and of each peer in the same store and
writes TICKER/facts/peers.json. A peer without facts is a column marked "no data" with the reason. Nothing is
computed except the operating margin (latest FY operating_income / revenue, inputs recorded); every other row is a
stored field: sales growth 5-yr CAGR (metrics.revenue_cagr_5y), ROIC latest (metrics.roic[0]), cash yield
(metrics.owner_earnings.yield), debt years (metrics.net_debt_to_owner_earnings), 12-month price change
(price.return_1y), model stance (scorecard.stance, else "not scored").
Each column ticker has one derived source row S80..S89 (class derived, url file://<its facts.json>); with --md the
Markdown table carries that marker in every cell and ends with an Evidence log of those rows, so it lints with
`lint.py --part --facts <TICKER>/facts/facts.json`. At most 9 peers.
"""
import json
import os

import common
from common import FetchError

SCRIPT = "compare.py"
FIRST_ID = 80
MAX_PEERS = 9
ROWS = (("sales_growth_5y", "Sales growth, 5-year CAGR"), ("operating_margin", "Operating margin, latest FY"),
        ("roic", "ROIC, latest FY"), ("cash_yield", "Cash yield (owner earnings)"),
        ("debt_years", "Debt years (net debt / owner earnings)"), ("return_12m", "12-month price change"),
        ("stance", "Model stance"))


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def dig(obj, *path):
    for p in path:
        if isinstance(obj, dict):
            obj = obj.get(p)
        elif isinstance(obj, list) and isinstance(p, int) and -len(obj) <= p < len(obj):
            obj = obj[p]
        else:
            return None
    return obj


def cell(value, reason=None, **extra):
    c = {"value": value}
    if value is None:
        c["reason"] = reason
    c.update(extra)
    return c


def column(facts, scorecard):
    """The rows of one column from a facts.json dict (and scorecard dict or None)."""
    m = facts.get("metrics") or {}
    a0 = dig(facts, "fundamentals", "annual", 0) or {}
    rev, op = a0.get("revenue"), a0.get("operating_income")
    if rev and op is not None:
        margin = cell(round(op / rev, 6), inputs={"fy": a0.get("fy"), "operating_income": op, "revenue": rev})
    else:
        margin = cell(None, "operating_income or revenue missing in the latest fiscal year")

    def stored(value, path):
        return cell(value, dig(m, *path[:1], "reason") or "metrics.%s not available" % ".".join(map(str, path)))
    rows = {
        "sales_growth_5y": stored(dig(m, "revenue_cagr_5y", "value"), ("revenue_cagr_5y", "value")),
        "operating_margin": margin,
        "roic": stored(dig(m, "roic", 0, "value"), ("roic", 0, "value")),
        "cash_yield": stored(dig(m, "owner_earnings", "yield"), ("owner_earnings", "yield")),
        "debt_years": stored(dig(m, "net_debt_to_owner_earnings", "value"), ("net_debt_to_owner_earnings", "value")),
        "return_12m": cell(dig(facts, "price", "return_1y"), "price.return_1y not available"),
        "stance": cell((scorecard or {}).get("stance") or "not scored"),
    }
    return rows


def build(subject, peers, today=None):
    """subject / peers are common.Stock objects. Returns the peers.json dict."""
    today = today or common.today()
    cols, sources = [], {}
    for i, st in enumerate([subject] + peers):
        sid = "S%d" % (FIRST_ID + i)
        facts = read_json(st.facts)
        if not isinstance(facts, dict):
            if i == 0:
                raise FetchError("no facts for %s: %s not found (run facts.py first)" % (st.ticker, st.facts))
            cols.append({"ticker": st.ticker, "status": "no data", "src": None,
                         "reason": "no facts/facts.json for %s (run facts.py %s first)" % (st.ticker, st.ticker),
                         "rows": None})
            continue
        sources[sid] = {"class": "derived",
                        "what": "compare.py reading %s facts/facts.json (metrics, price, fundamentals)" % st.ticker,
                        "url": "file://" + os.path.abspath(st.facts),
                        "as_of": str(facts.get("retrieved") or today)[:10], "retrieved": today}
        cols.append({"ticker": st.ticker, "status": "ok", "src": sid, "name": facts.get("name"),
                     "rows": column(facts, read_json(st.scorecard))})
    return {"ticker": subject.ticker, "as_of": today, "rows": [{"key": k, "label": l} for k, l in ROWS],
            "columns": cols, "sources": sources}


def fmt(key, c, src):
    v = c["value"]
    if v is None:
        return "n/a (%s) [%s]" % (c["reason"], src)
    if key in ("sales_growth_5y", "operating_margin", "roic", "cash_yield", "return_12m"):
        text = "%.2f%%" % (v * 100)
    elif key == "debt_years":
        text = "%.2f years" % v if v >= 0 else "net cash (%.2f years)" % v
    else:
        text = str(v)
    return "%s [%s]" % (text, src)


def render_md(doc):
    cols = doc["columns"]
    out = ["| | " + " | ".join(c["ticker"] for c in cols) + " |", "|---|" + "---|" * len(cols)]
    for key, label in ((r["key"], r["label"]) for r in doc["rows"]):
        cells = []
        for c in cols:
            if c["status"] != "ok":
                cells.append("no data: %s" % c["reason"] if key == doc["rows"][0]["key"] else "no data")
            else:
                cells.append(fmt(key, c["rows"][key], c["src"]))
        out.append("| %s | %s |" % (label, " | ".join(x.replace("|", "/") for x in cells)))
    out += ["", "Operating margin is operating income divided by revenue of the latest fiscal year; every other row is a "
            "stored field read as is.", "", "### Evidence log", "| S | class | what | url | as-of | retrieved |",
            "|---|---|---|---|---|---|"]
    for sid, s in doc["sources"].items():
        out.append("| %s | %s | %s | %s | %s | %s |" % (sid, s["class"], s["what"], s["url"], s["as_of"], s["retrieved"]))
    return "\n".join(out) + "\n"


def run(argv=None):
    ap = common.base_parser("Side-by-side of stored facts for a stock and its peers")
    ap.add_argument("ticker", help="ticker or stock folder path")
    ap.add_argument("--peers", required=True, help="comma-separated peer tickers (same store), at most %d" % MAX_PEERS)
    ap.add_argument("--md", action="store_true", help="print the Markdown table instead of JSON")
    args = ap.parse_args(argv)
    subject = common.locate(args.ticker, args)
    names = []
    for t in args.peers.split(","):
        if t.strip():
            t = common.safe_ticker(t)
            if t != subject.ticker and t not in names:
                names.append(t)
    if not names:
        raise FetchError("--peers needs at least one ticker other than %s" % subject.ticker)
    if len(names) > MAX_PEERS:
        raise FetchError("at most %d peers (source ids S80-S89), got %d" % (MAX_PEERS, len(names)))
    store = os.path.dirname(os.path.dirname(subject.root))
    peers = [common.Stock(common.ticker_dir(store, t)) for t in names]
    doc = build(subject, peers)
    os.makedirs(subject.facts_dir, exist_ok=True)
    path = os.path.join(subject.facts_dir, "peers.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    if args.md:
        print(render_md(doc), end="")
    else:
        common.emit(dict(doc, path=path), args.out)
    return doc


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
