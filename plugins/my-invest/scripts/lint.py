#!/usr/bin/env python3
"""lint.py FILE... [--explain]

The evidence skill's mechanical check for Markdown dossiers, digests and discovery tables:
  log-row            each Evidence log row has an id S<n> and a url starting with http
  no-log             the file has no Evidence log table (header `| S | class | what | url |`)
  unresolved-marker  every [S<n>] in the body resolves to a log row
  uncited-figure     every figure line outside the log and fenced code carries a marker
  scorecard-unanchored  a Scorecard section shows score fractions but carries no marker at all
  disclaimer         the verbatim disclaimer is present
Prints `path:line: <rule> — <excerpt>` per violation and a summary; exit 1 on any violation.
Stdlib only.
"""
import argparse
import re
import sys

DISCLAIMER = ("Model-backed research for the owner's own study, not investment advice. "
              "Every figure is as cited and may be wrong or stale.")

LOG_HEADER = re.compile(r"^\s*\|\s*S\s*\|\s*class\s*\|\s*what\s*\|\s*url\s*\|", re.I)
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s")
SCORECARD = re.compile(r"^\s{0,3}(#{1,6})\s+Scorecard\b", re.I)
MARKER = re.compile(r"\[(S\d+(?:\s*[,;]\s*S\d+)*)\]")
SCORE_WORDS = re.compile(r"\b(Points|Score|Confidence)\b", re.I)
FRACTION = re.compile(r"(?<![\d.])\d{1,3}(?:\.\d+)?\s*/\s*(?:20|100)\b")

# Stripped before anything else: never figures.
PRE_STRIP = [
    ("url", re.compile(r"https?://\S+")),
    ("link target", re.compile(r"\]\([^)]*\)")),
    ("inline code", re.compile(r"`[^`]*`")),
    ("marker", MARKER),
]
# Always figures, checked after PRE_STRIP.
STRONG = [
    ("currency", re.compile(r"(?:US)?\$\s?\d")),
    ("percentage", re.compile(r"\d\s?%")),
    ("multiple", re.compile(r"(?<![\w.])\d+(?:\.\d+)?x\b")),
]
# Stripped before the generic number test.
EXCLUDE = [
    ("date YYYY-MM-DD", re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),
    ("fiscal-year token", re.compile(r"\bFY\s?'?\d{2,4}\b", re.I)),
    ("form name", re.compile(r"\b(?:10-K|10-Q|8-K|6-K|11-K|20-F|40-F|S-[134]|F-1|DEF\s?14A|SC\s?13[DG]|13[DFG])"
                             r"(?:/A)?(?![\w-])|\bForms?\s+\d+\b", re.I)),
    ("item id", re.compile(r"\bItems?\s+\d+[A-Z]?(?:\.\d+)?(?:\s*(?:,|/|&|and|or)\s*\d+[A-Z]?(?:\.\d+)?)*", re.I)),
    ("gate / decision id", re.compile(r"\b(?:G\d+|D-\d+)\b")),
    ("card id at line, cell or list start, or after item/card",
     re.compile(r"(?:(?<=^)|(?<=\|)|(?<=[-*+] )|(?<=\bitem )|(?<=\bitems )|(?<=\bcard ))\s*[1-5]\.[1-6](?![\d.%x])",
                re.I)),
    ("ordered-list number", re.compile(r"^\s*\d+[.)]\s")),
    ("year YYYY", re.compile(r"\b(?:19|20)\d{2}\b")),
]
NUMBER = re.compile(r"\d+\.\d+|\d{2,}")

EXPLAIN = """Figure rules (lint.py --explain)
A line is checked only outside fenced code, outside the Evidence log table, and when it is not a
heading or a table separator row. On the line:
1. Removed first, never figures: URLs, Markdown link targets, inline code spans, [S<n>] markers.
2. Always a figure: currency ($12, US$ 3), percentage (4%, 4.2 %), multiple (12.3x).
3. Removed next: dates YYYY-MM-DD; FY tokens (FY2025, FY25); form names (10-K, 10-Q, 8-K, 20-F,
   DEF 14A, Form 4, ...); item ids (Item 1.03, Items 1.03 and 4.02, Item 9A); gate and decision ids
   (G1, D-8); card ids 1.1-5.6 at line, cell or list start or after "item"/"card"; ordered-list
   numbers; years 1900-2099; score fractions n/20 and n/100 when the line is inside a Scorecard
   section or carries a marker or the word Points, Score or Confidence.
4. Then a figure is any number with a decimal point or with two or more digits.
A figure line needs at least one [S<n>] marker (lists like [S1, S3] count). A Scorecard section
whose fractions were exempted must carry at least one marker somewhere in the section."""


def is_figure_line(text, exempt_fractions):
    for _, rx in PRE_STRIP:
        text = rx.sub(" ", text)
    if any(rx.search(text) for _, rx in STRONG):
        return True
    if exempt_fractions:
        text = FRACTION.sub(" ", text)
    for _, rx in EXCLUDE:
        text = rx.sub(" ", text)
    return bool(NUMBER.search(text))


def cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def lint_text(path, text, part=False, extra_ids=None):
    lines = text.splitlines()
    out = []

    def v(n, rule, line):
        excerpt = line.strip()
        out.append("%s:%d: %s — %s" % (path, n, rule, excerpt[:100] + ("…" if len(excerpt) > 100 else "")))

    # Pass 1: classify lines, build the log.
    kinds, ids = [], set()
    in_fence = in_log = False
    for n, line in enumerate(lines, 1):
        if FENCE.match(line):
            in_fence = not in_fence
            kinds.append("fence")
            continue
        if in_fence:
            kinds.append("fence")
            continue
        if LOG_HEADER.match(line):
            in_log = True
            kinds.append("log")
            continue
        if in_log and line.strip().startswith("|"):
            kinds.append("log")
            if TABLE_SEP.match(line):
                continue
            c = cells(line)
            sid = c[0] if c else ""
            url = c[3] if len(c) > 3 else ""
            if not re.fullmatch(r"S\d+", sid):
                v(n, "log-row", line + "  (id must be S<n>)")
            elif not (url.startswith("http") or (len(c) > 1 and c[1].strip() == "derived" and url.startswith("file://"))):
                v(n, "log-row", line + "  (url must start with http, or file:// for a derived row)")
            else:
                ids.add(sid)
            continue
        in_log = False
        kinds.append("body")
    if extra_ids:
        ids.update(extra_ids)
    if "log" not in kinds and not extra_ids:
        v(1, "no-log", "no Evidence log table with header | S | class | what | url |")

    # Pass 2: markers, figure lines, Scorecard sections.
    sc_level = sc_line = None
    sc_marker = sc_fraction = False

    def close_scorecard():
        if sc_line is not None and sc_fraction and not sc_marker:
            v(sc_line, "scorecard-unanchored", lines[sc_line - 1])

    for n, (line, kind) in enumerate(zip(lines, kinds), 1):
        if kind != "body":
            continue
        h = HEADING.match(line)
        if h:
            level = len(h.group(1))
            if sc_level is not None and level <= sc_level:
                close_scorecard()
                sc_level, sc_line = None, None
            if SCORECARD.match(line):
                sc_level, sc_line, sc_marker, sc_fraction = level, n, False, False
        markers = [m.strip() for g in MARKER.findall(line) for m in re.split(r"[,;]", g)]
        for m in markers:
            if m not in ids:
                v(n, "unresolved-marker", "[%s] in: %s" % (m, line.strip()))
        if sc_level is not None:
            sc_marker = sc_marker or bool(markers)
            sc_fraction = sc_fraction or bool(FRACTION.search(line))
        if h or TABLE_SEP.match(line) or not line.strip():
            continue
        exempt = sc_level is not None or bool(markers) or bool(SCORE_WORDS.search(line))
        if not markers and is_figure_line(line, exempt):
            v(n, "uncited-figure", line)
    close_scorecard()

    flat = " ".join(re.sub(r"^\s*>\s?", "", l) for l in lines).replace("’", "'")
    if not part and DISCLAIMER not in re.sub(r"\s+", " ", flat):
        v(len(lines) or 1, "disclaimer", "verbatim disclaimer line missing")
    return out


def facts_ids(facts_path):
    """Source ids a part may cite: facts/facts.json, its sibling scorecard.json and holdings_tables.json, and the
    Evidence log rows of ../research/research.md."""
    import json as _json
    import os as _os
    ids = set()
    folder = _os.path.dirname(_os.path.abspath(facts_path))   # <stock>/facts
    for fp in (facts_path, _os.path.join(folder, "scorecard.json"), _os.path.join(folder, "holdings_tables.json"), _os.path.join(folder, "peers.json")):
        try:
            with open(fp, encoding="utf-8") as fh:
                ids.update((_json.load(fh).get("sources") or {}).keys())
        except (OSError, ValueError):
            pass
    try:
        with open(_os.path.join(folder, "..", "research", "research.md"), encoding="utf-8") as fh:
            ids.update(re.findall(r"^\|\s*(S\d+)\s*\|", fh.read(), re.M))
    except OSError:
        pass
    return ids


def main(argv=None):
    ap = argparse.ArgumentParser(description="Evidence lint for my-invest Markdown outputs")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--explain", action="store_true", help="print the figure rules and exit")
    ap.add_argument("--part", action="store_true", help="a dossier part: skip the disclaimer check")
    ap.add_argument("--facts", help="facts/facts.json whose source ids (and the sibling scorecard.json, holdings_tables.json and ../research/research.md) resolve markers in a part")
    for flag in ("--data", "--project", "--store"):
        ap.add_argument(flag, help="ignored; present so run.sh can pass it")
    a = ap.parse_args(argv)
    if a.explain:
        print(EXPLAIN)
        return 0
    if not a.files:
        ap.error("at least one FILE is required")
    total = []
    extra = facts_ids(a.facts) if a.facts else set()
    for path in a.files:
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError) as e:
            total.append("%s:0: io — %s" % (path, e))
            continue
        total.extend(lint_text(path, text, part=a.part, extra_ids=extra))
    for line in total:
        print(line)
    if total:
        print("lint: %d violation(s) in %d file(s)" % (len(total), len(a.files)))
        return 1
    print("lint: OK, %d file(s) checked" % len(a.files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
