#!/usr/bin/env python3
"""store.py list | show TICKER | next-id TICKER | tree TICKER | path [TICKER] [--store DIR] [--project DIR] - the per-ticker history store.

list     tickers (folders of <store>/stocks) with the date of the last history/log.md line and the last price from
         facts/facts.json.
show     history/log.md of one ticker.
next-id  the next free researcher source id: S100 or one above the highest S<n> (n >= 100) in research/research.md.
tree     the stock folder's files, indented, with the generated INDEX.md first.
path     the store root; `path TICKER` the ticker's folder under <store>/stocks, created when absent.
A TICKER argument may also be the stock folder path.
All commands print JSON. Folders starting with "_" or "." are not tickers.
"""
import json
import os
import re

import common

SCRIPT = "store.py"
FIRST_RESEARCH_ID = 100
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def last_history_date(text):
    """Date at the start of the last non-blank history line (the first date found in it)."""
    for line in reversed((text or "").splitlines()):
        if line.strip():
            m = DATE.search(line)
            return m.group(0) if m else None
    return None


def last_price(stock):
    raw = read_text(stock.facts)
    try:
        p = (json.loads(raw) or {}).get("price") or {} if raw else {}
    except (ValueError, AttributeError):
        return None, None
    return p.get("last"), p.get("date")


def next_id(research_text):
    ids = [int(n) for n in re.findall(r"\bS(\d+)\b", research_text or "")]
    top = max([n for n in ids if n >= FIRST_RESEARCH_ID] or [FIRST_RESEARCH_ID - 1])
    return top + 1


def list_tickers(stocks):
    rows = []
    for name in sorted(os.listdir(stocks)) if os.path.isdir(stocks) else []:
        folder = os.path.join(stocks, name)
        if name.startswith(("_", ".")) or not os.path.isdir(folder):
            continue
        st = common.Stock(folder)
        price, pdate = last_price(st)
        rows.append({"ticker": name, "last_analysis": last_history_date(read_text(st.log)),
                     "last_price": price, "price_date": pdate})
    return rows


def tree_lines(folder):
    """Indented listing of the stock folder: INDEX.md first, then each subfolder's files (filings/ collapsed)."""
    out = []
    if os.path.exists(os.path.join(folder, "INDEX.md")):
        out.append("INDEX.md")
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if name == "INDEX.md":
            continue
        if not os.path.isdir(path):
            out.append(name)
            continue
        out.append(name + "/")
        entries = sorted(os.listdir(path))
        if name == "filings":
            out += ["  %s/ (%d files)" % (e, len(os.listdir(os.path.join(path, e)))) for e in entries
                    if os.path.isdir(os.path.join(path, e))]
        else:
            out += ["  " + e for e in entries]
    return out


def run(argv=None):
    ap = common.EnvelopeParser(prog=SCRIPT, description="Per-ticker data folder")
    sub = ap.add_subparsers(dest="cmd", required=True, parser_class=common.EnvelopeParser)
    for name in ("list", "show", "next-id", "tree", "path"):
        p = sub.add_parser(name)
        common.add_common_args(p)
        if name in ("show", "next-id", "tree"):
            p.add_argument("ticker")
        elif name == "path":
            p.add_argument("ticker", nargs="?", default="")
    args = ap.parse_args(argv)
    store = common.store_from(args)
    if args.cmd == "list":
        out = {"store": store, "tickers": list_tickers(os.path.join(store, "stocks"))}
    elif args.cmd == "path" and not args.ticker:
        common.ensure_store(store)
        out = {"path": store}
    else:
        st = common.locate(args.ticker, args)
        if args.cmd == "path":
            common.ensure_store(store)
            os.makedirs(st.root, exist_ok=True)
            out = {"ticker": st.ticker, "path": st.root}
        elif args.cmd == "show":
            text = read_text(st.log)
            out = {"ticker": st.ticker, "path": st.log, "history": text,
                   "reason": None if text is not None else "no history/log.md: %s has not been analyzed" % st.ticker}
        elif args.cmd == "tree":
            if not os.path.isdir(st.root):
                raise common.FetchError("no folder for %s: %s" % (st.ticker, st.root))
            out = {"ticker": st.ticker, "path": st.root, "tree": tree_lines(st.root)}
        else:
            out = {"ticker": st.ticker,
                   "next_id": "S%d" % next_id(read_text(st.research))}
    common.emit(out, args.out)
    return out


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
