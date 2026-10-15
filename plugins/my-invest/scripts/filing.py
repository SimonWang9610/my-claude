#!/usr/bin/env python3
"""filing.py TICKER [--form 10-K] [--accn ACCESSION] [--store DIR] [--sections 1,1A,7,7A,8,9A,auditor] [--grep REGEX]

Downloads the latest filing of --form (or --accn) from EDGAR, converts it to plain text and splits a 10-K into
its Items, so sections WebFetch truncates (Item 9A, the auditor's report, the notes) stay reachable.
Writes <store>/stocks/<TICKER>/filings/<accn>/{full.txt, item-*.txt, auditor.txt, notes.txt, index.json} and prints a
manifest {url, filed, accn, sections{name: chars}, dir}. With --grep it prints matching lines (JSON lines:
line, sections, before, text, after) from the stored text, fetching and writing only when the files do not exist.

Text rules: scripts/styles/ix:header dropped, table cells joined by " | ", whitespace collapsed, one block per line.
Sections: the LAST "Item N. <expected title>" heading line per item (the table of contents comes first and is skipped);
a section ends at the next Item or Part heading. Auditor: the "Report of Independent Registered Public Accounting Firm"
heading inside Item 8 through the next Item heading or the balance-sheet heading. Notes: Item 8 from "Note 1" on.
"""
import html.parser
import json
import os
import re
import sys

import common
import edgar
import news
from common import FetchError

SCRIPT = "filing.py"
DEFAULT_SECTIONS = "1,1A,7,7A,8,9A,auditor"
BLOCK = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "table", "section", "article",
         "body", "hr", "pre", "center", "blockquote", "dl", "dt", "dd"}
SKIP = {"script", "style", "head", "noscript", "ix:header"}
WS = re.compile(r"[\s\xa0​]+")


def _clean(s):
    return WS.sub(" ", s).strip()


class _Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines, self.buf, self.skip, self.cell, self.row = [], [], 0, None, None

    def _flush(self):
        t = _clean("".join(self.buf))
        self.buf = []
        if t:
            self.lines.append(t)

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        elif self.skip:
            return
        elif tag == "tr":
            self._flush()
            self.row = []
        elif tag in ("td", "th"):
            if self.row is not None:
                self.cell = []
        elif tag in BLOCK:
            if self.cell is not None:
                self.cell.append(" ")
            else:
                self._flush()

    def handle_startendtag(self, tag, attrs):
        if tag == "br" and not self.skip:
            self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self.skip:
            return
        (self.cell if self.cell is not None else self.buf).append(data)

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        elif self.skip:
            return
        elif tag in ("td", "th"):
            if self.cell is not None and self.row is not None:
                self.row.append(_clean("".join(self.cell)))
            self.cell = None
        elif tag == "tr":
            if self.row is not None:
                self._emit_row()
            self.row = None
        elif tag in BLOCK and self.cell is None:
            self._flush()

    def _emit_row(self):
        out, prefix = [], ""
        for c in self.row:
            if not c:
                continue
            if c in (")", "%", ")%", "%)"):
                if out:
                    out[-1] += c
                continue
            if c in ("$", "(", "US$", "$("):
                prefix += c
                continue
            out.append(prefix + c)
            prefix = ""
        if prefix:
            out.append(prefix)
        if out:
            self.lines.append(" | ".join(out))


def html_to_lines(page):
    p = _Text()
    p.feed(page)
    p.close()
    p._flush()
    return p.lines


# --- sections -------------------------------------------------------------------------------
ITEM_RE = re.compile(r"^item\s*(\d{1,2}[abc]?)\s*[\.:\-–—]*\s*(.*)$", re.I)
PART_RE = re.compile(r"^part\s+(i{1,3}|iv)\b[\s\.\-–—:]*$", re.I)
TITLES = {"1": r"business", "1A": r"risk factors", "1B": r"unresolved", "1C": r"cybersecurity", "2": r"properties",
          "3": r"legal proceedings", "4": r"mine safety", "5": r"market for", "6": r"(reserved|selected)",
          "7": r"management", "7A": r"quantitative", "8": r"(consolidated )?financial statements",
          "9": r"changes in and disagreements", "9A": r"controls and procedures", "9B": r"other information",
          "9C": r"disclosure regarding", "10": r"directors", "11": r"executive compensation",
          "12": r"security ownership", "13": r"certain relationships", "14": r"principal account",
          "15": r"exhibit", "16": r"form 10-k summary"}
TITLE_RES = {k: re.compile(v, re.I) for k, v in TITLES.items()}
AUDITOR_RE = re.compile(r"report of independent registered public accounting firm", re.I)
BALANCE_RE = re.compile(r"^(consolidated\s+)?(balance sheets?|statements? of financial (position|condition))\b", re.I)
NOTES_RE = re.compile(r"^notes to (the )?(consolidated )?financial statements", re.I)
NOTE1_RE = re.compile(r"^note\s*1\b", re.I)


def _norm(line):
    return line.replace(" | ", " ")


def find_items(lines):
    """{item_id: line_index} - the last heading line per item whose title matches the expected one."""
    found = {}
    for i, raw in enumerate(lines):
        l = _norm(raw)
        if len(l) > 200:
            continue
        m = ITEM_RE.match(l)
        if not m:
            continue
        iid, title = m.group(1).upper(), m.group(2)
        rx = TITLE_RES.get(iid)
        if rx is None:
            continue
        if not re.sub(r"[\[\]\.\s]", "", title) and i + 1 < len(lines) and len(lines[i + 1]) <= 120:
            title = _norm(lines[i + 1])
        if rx.match(re.sub(r"^[^A-Za-z]+", "", title)):
            found[iid] = i
    return found


def split_sections(lines):
    """-> {name: (start, end)} line ranges for items, 'auditor' and 'notes'. Names: item-1a, auditor, notes."""
    items = find_items(lines)
    bounds = sorted(set(items.values()) | {i for i, l in enumerate(lines) if len(l) < 30 and PART_RE.match(l)})
    n = len(lines)

    def end_after(start):
        return next((b for b in bounds if b > start), n)

    secs = {"item-" + k.lower(): (s, end_after(s)) for k, s in items.items()}
    if "item-8" in secs:
        lo, hi = secs["item-8"]
    else:
        lo, hi = 0, n
    cands = [i for i in range(lo, hi) if len(lines[i]) <= 150 and AUDITOR_RE.search(lines[i])
             and not lines[i].lower().startswith("item")]
    pick = next((i for i in cands if re.search(r"opinion|^to the ", " ".join(lines[i + 1:i + 7]).lower())),
                cands[-1] if cands else None)
    if pick is not None:
        end = min(end_after(pick), next((j for j in range(pick + 2, hi) if len(lines[j]) <= 80
                                         and BALANCE_RE.match(lines[j])), hi), hi)
        secs["auditor"] = (pick, max(end, pick + 1))
    if "item-8" in secs:
        n1 = [i for i in range(lo, hi) if NOTES_RE.match(_norm(lines[i])) and len(lines[i]) <= 100
              and any(NOTE1_RE.match(x) for x in lines[i + 1:i + 4])]
        if not n1:
            n1 = [i for i in range(lo, hi) if NOTE1_RE.match(lines[i]) and len(lines[i]) <= 150]
        if n1:
            ns, ne = n1[0], hi
            if "auditor" in secs and secs["auditor"][0] > ns:
                ne = secs["auditor"][0]
            secs["notes"] = (ns, ne)
    return secs


def pick_filing(sub, form, accn=None):
    r = sub.get("filings", {}).get("recent", {})
    want = accn.replace("-", "") if accn else None
    best = None
    for i, a in enumerate(r.get("accessionNumber", [])):
        if want:
            ok = a.replace("-", "") == want
        else:
            ok = r["form"][i] == form
        if ok and (best is None or r["filingDate"][i] > r["filingDate"][best]):
            best = i
    if best is None:
        raise FetchError("no %s in the recent submissions feed%s" % (
            "filing %s" % accn if accn else form, "" if accn else " (older filings: pass --accn)"))
    return {"accn": r["accessionNumber"][best], "form": r["form"][best], "filed": r["filingDate"][best],
            "period": r.get("reportDate", [""] * (best + 1))[best], "doc": r["primaryDocument"][best]}


def section_file(name):
    return name + ".txt"


def write_all(folder, url, meta, retrieved, lines, secs, wanted):
    os.makedirs(folder, exist_ok=True)

    def put(fname, ls):
        with open(os.path.join(folder, fname), "w", encoding="utf-8") as f:
            f.write("\n".join(ls) + "\n")

    put("full.txt", lines)
    index_secs = {}
    for name, (s, e) in sorted(secs.items(), key=lambda kv: kv[1]):
        text = "\n".join(lines[s:e])
        index_secs[name] = {"chars": len(text), "head": text[:120], "lines": [s, e], "file": None}
        key = "auditor" if name == "auditor" else ("8" if name == "notes" else name[5:].upper())
        if key in wanted:
            index_secs[name]["file"] = section_file(name)
            put(section_file(name), lines[s:e])
    index = {"url": url, "form": meta["form"], "filed": meta["filed"], "period": meta["period"], "accn": meta["accn"],
             "retrieved": retrieved[:10], "chars": sum(len(l) + 1 for l in lines), "sections": index_secs}
    with open(os.path.join(folder, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    return index


def manifest(index, folder):
    return {"url": index["url"], "filed": index["filed"], "accn": index["accn"],
            "sections": {k: v["chars"] for k, v in index["sections"].items()}, "dir": folder}


def grep(folder, index, pattern):
    rx = re.compile(pattern, re.I)
    with open(os.path.join(folder, "full.txt"), "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
    ranges = {k: v["lines"] for k, v in index["sections"].items()}
    out = []
    for i, l in enumerate(lines):
        if rx.search(l):
            out.append({"line": i + 1, "sections": [k for k, (s, e) in ranges.items() if s <= i < e],
                        "before": lines[i - 1] if i else "", "text": l,
                        "after": lines[i + 1] if i + 1 < len(lines) else ""})
    return out


def run(argv=None):
    ap = common.base_parser("Fetch a filing, convert to text and split into Items")
    ap.add_argument("ticker", help="ticker or stock folder path")
    ap.add_argument("--form", default="10-K")
    ap.add_argument("--accn", default="")
    ap.add_argument("--sections", default=DEFAULT_SECTIONS, help="comma list of items / auditor to write as files")
    ap.add_argument("--grep", default="", help="regex; print matching lines with context and section names")
    args = ap.parse_args(argv)
    st = common.locate(args.ticker, args)
    ticker = st.ticker
    wanted = {s.strip().upper() if s.strip().lower() != "auditor" else "auditor" for s in args.sections.split(",") if s.strip()}
    common.ensure_store(os.path.dirname(os.path.dirname(st.root)))
    base = st.filings
    index = None
    if args.accn and not args.refresh:
        folder = os.path.join(base, args.accn)
        if os.path.exists(os.path.join(folder, "index.json")):
            index = json.load(open(os.path.join(folder, "index.json"), encoding="utf-8"))
    if index is None:
        ctx = common.ctx_from(args)
        cik, _, _ = edgar.resolve_cik(ctx, ticker)
        sub, _ = ctx.get_json(edgar.SUBMISSIONS_URL % ("%010d" % cik), "news")
        meta = pick_filing(sub, args.form, args.accn or None)
        folder = os.path.join(base, meta["accn"])
        idx_path = os.path.join(folder, "index.json")
        if os.path.exists(idx_path) and not args.refresh:
            index = json.load(open(idx_path, encoding="utf-8"))
        else:
            url = news.filing_url(cik, meta["accn"], meta["doc"])
            body, retrieved = ctx.get(url, "filings")
            lines = html_to_lines(body.decode("utf-8", "replace"))
            if not lines:
                raise FetchError("filing text is empty: %s" % url)
            index = write_all(folder, url, meta, retrieved, lines, split_sections(lines), wanted)
            if args.grep:
                print("wrote %s" % folder, file=sys.stderr)
    if args.grep:
        for hit in grep(folder, index, args.grep):
            print(json.dumps(hit, ensure_ascii=False))
        return index
    out = manifest(index, folder)
    common.emit(out, args.out)
    return out


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
