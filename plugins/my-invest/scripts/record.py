#!/usr/bin/env python3
"""record.py - the analysis history: open a run, compute confidence, record calls, score them later, finalise the
report with every figure linked to its source.

  record.py open --question Q --intent I --subjects A,B [--plan @steps.json]   -> run id
  record.py confidence RUN_ID SUBJECT [--action buy]      -> the three parts and the total, from views/valuations/calls
  record.py calls RUN_ID --json ROWS                      -> store the recommendations (fills prices, due date)
  record.py score                                         -> settle calls past due against SPY from the prices table
  record.py record [--action buy] [--ticker T]            -> the track record table
  record.py lint --file DRAFT.md                          -> citation and section check only
  record.py report RUN_ID --file DRAFT.md [--slug S]      -> lint, link [S<id>] markers, append Sources, render the
                                                             page data/reports/<date>-<slug>.html (with a price chart
                                                             per ticker from the prices table), close the run
  record.py fail RUN_ID --notes "..."                     -> close a run that produced no answer
Markers: `[S12]` (or `[S3, S7]`) cites sources.id 12. Every line with a figure needs one; the lint refuses the rest.
The chat answer stays Markdown; the saved report is the HTML page, self-contained, dark-mode aware, phone width.
"""
import html as html_mod
import datetime as dt
import json
import os
import re
import sys

import common
import db

SCRIPT = "record.py"
REPORTS_DIR = "reports"
MARKER = re.compile(r"\[S(\d+(?:\s*,\s*S?\d+)*)\](?!\()")
DIGIT = re.compile(r"\d")
REQUIRED_SECTIONS = ["What to do", "Why", "Supporting analysis", "The case against", "Track record", "Not verified"]
REQUIRED_DIMENSIONS = {  # per intent: the views a conclusion must rest on (evidence coverage denominator)
    "stock": ["fundamentals", "valuation", "statistics", "macro", "industry", "sentiment"],
    "holdings": ["fundamentals", "valuation", "statistics", "macro"],
    "sector": ["industry", "macro", "sentiment"],
    "macro": ["macro", "sentiment"],
    "mix": ["fundamentals", "valuation", "statistics", "macro", "industry", "sentiment"],
    "digest": ["statistics", "macro", "sentiment"],
}
BUY_SIDE = ("buy", "add", "hold")
SELL_SIDE = ("trim", "sell", "avoid", "wait")
STANCE_SIGN = {"for": 1, "against": -1, "neutral": 0}
GRADE_WEIGHT = {"primary": 1.0, "derived": 0.75, "secondary": 0.5}
BANDS = ((80, "strong evidence"), (65, "solid"), (45, "mixed"), (0, "thin"))
DISCLAIMER = ("> This is research, not licensed financial advice. Every figure above links to the source it was taken "
              "from or to the script run that computed it; the judgments are the analyst's.")


def band(total):
    for floor, word in BANDS:
        if total >= floor:
            return word
    return "thin"


def side(action):
    return "buy" if action in BUY_SIDE else "sell"


# --- runs ---------------------------------------------------------------------------------------
def open_run(conn, question, intent, subjects, plan=None):
    if intent not in db.INTENTS:
        raise ValueError("intent must be one of %s" % (db.INTENTS,))
    return db.insert(conn, "runs", {"asked_at": common.iso(), "question": question, "intent": intent,
                                    "subjects": [s.strip().upper() if ":" not in s else s.strip() for s in subjects],
                                    "plan": plan, "status": "open"})


def run_row(conn, run_id):
    r = db.one(conn, "SELECT * FROM runs WHERE id = ?", (run_id,))
    if not r:
        raise ValueError("no run %s" % run_id)
    return r


# --- confidence ---------------------------------------------------------------------------------
def evidence_part(conn, run_id, subject, intent):
    """0-35: 70% coverage of the required dimensions by a view, 30% the source grade of what the views cite."""
    need = REQUIRED_DIMENSIONS.get(intent, REQUIRED_DIMENSIONS["stock"])
    views = db.rows(conn, "SELECT dimension, evidence FROM views WHERE run_id = ? AND subject = ?", (run_id, subject))
    have = {v["dimension"] for v in views}
    coverage = len(have & set(need)) / float(len(need))
    ids = set()
    for v in views:
        try:
            ids |= {int(i) for i in json.loads(v["evidence"] or "[]")}
        except (ValueError, TypeError):
            pass
    grade = 0.0
    if ids:
        rows = db.rows(conn, "SELECT grade FROM sources WHERE id IN (%s)" % ",".join("?" * len(ids)), tuple(ids))
        grade = sum(GRADE_WEIGHT.get(r["grade"], 0.5) for r in rows) / float(len(ids))
    score = round(35 * (0.7 * coverage + 0.3 * grade))
    missing = sorted(set(need) - have)
    reason = "%d of %d dimensions have a view%s; source grade %.2f" % (
        len(have & set(need)), len(need), (", missing " + ", ".join(missing)) if missing else "", grade)
    return score, reason


def agreement_part(conn, run_id, subject):
    """0-35: how far the views point the same way (|weighted stance|), discounted when the DCF scenarios are wide."""
    views = db.rows(conn, "SELECT stance, strength FROM views WHERE run_id = ? AND subject = ?", (run_id, subject))
    if not views:
        return 0, "no views recorded"
    wsum = float(sum(v["strength"] for v in views))
    s = sum(STANCE_SIGN[v["stance"]] * v["strength"] for v in views) / wsum
    vals = {r["scenario"]: r["value_per_share"] for r in db.rows(
        conn, "SELECT scenario, value_per_share FROM valuations WHERE run_id = ? AND ticker = ? AND method = 'dcf'", (run_id, subject))}
    factor, spread_note = 1.0, "no DCF in this run"
    if {"low", "base", "high"} <= set(vals) and vals["base"]:
        spread = (vals["high"] - vals["low"]) / abs(vals["base"])
        factor = 1.0 if spread <= 0.5 else max(0.6, 1.0 - 0.4 * (spread - 0.5))
        spread_note = "DCF high-low spread %.0f%% of base" % (100 * spread)
    score = round(35 * abs(s) * factor)
    lean = "for" if s > 0 else "against" if s < 0 else "split"
    return score, "weighted stance %.2f (%s) over %d views; %s" % (s, lean, len(views), spread_note)


def record_part(conn, action=None, ticker=None):
    """0-30 from settled calls of the same side: 30 * (right + 2.5) / (n + 5), i.e. 15 with no record yet."""
    sql, params = "SELECT action, outcome FROM calls WHERE outcome IN ('right','wrong')", []
    if action:
        sql += " AND action IN (%s)" % ",".join("?" * len(BUY_SIDE if side(action) == "buy" else SELL_SIDE))
        params += list(BUY_SIDE if side(action) == "buy" else SELL_SIDE)
    if ticker:
        sql += " AND ticker = ?"
        params.append(ticker.upper())
    rows = db.rows(conn, sql, tuple(params))
    right = sum(1 for r in rows if r["outcome"] == "right")
    n = len(rows)
    score = round(30 * (right + 2.5) / (n + 5.0))
    what = ("%s-side calls" % side(action)) if action else "all calls"
    reason = "%d of %d settled %s came true" % (right, n, what) if n else "no settled %s yet (neutral prior)" % what
    return score, reason


def confidence(conn, run_id, subject, action=None):
    run = run_row(conn, run_id)
    e, er = evidence_part(conn, run_id, subject, run["intent"])
    a, ar = agreement_part(conn, run_id, subject)
    r, rr = record_part(conn, action, subject if ":" not in subject else None)
    total = e + a + r
    return {"total": total, "band": band(total),
            "parts": {"evidence": {"score": e, "max": 35, "reason": er},
                      "agreement": {"score": a, "max": 35, "reason": ar},
                      "record": {"score": r, "max": 30, "reason": rr}}}


def confidence_line(c):
    p = c["parts"]
    return "Confidence %d/100 (%s): evidence %d/35, %s; agreement %d/35, %s; record %d/30, %s." % (
        c["total"], c["band"], p["evidence"]["score"], p["evidence"]["reason"], p["agreement"]["score"],
        p["agreement"]["reason"], p["record"]["score"], p["record"]["reason"])


# --- calls --------------------------------------------------------------------------------------
def add_months(d, months):
    y, m = d.year, d.month + months
    y, m = y + (m - 1) // 12, (m - 1) % 12 + 1
    day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return d.replace(year=y, month=m, day=day)


def store_calls(conn, run_id, rows, today=None):
    run_row(conn, run_id)
    today = today or common.today()
    spy = db.latest_price(conn, "SPY")
    out = []
    for r in rows:
        r = dict(r)
        r["run_id"] = run_id
        r["ticker"] = r["ticker"].upper()
        for k in ("tier", "action", "horizon_months", "confidence", "confidence_parts", "evidence"):
            if k not in r:
                raise ValueError("call lacks %s" % k)
        price = db.latest_price(conn, r["ticker"])
        r.setdefault("price_at_call", round(price["close"], 4) if price else None)
        r.setdefault("spy_at_call", round(spy["close"], 4) if spy else None)
        r.setdefault("made_at", today)
        r.setdefault("due_at", add_months(dt.date.fromisoformat(r["made_at"]), int(r["horizon_months"])).isoformat())
        r["id"] = db.insert(conn, "calls", r)
        out.append(r)
    return out


def price_on_or_after(conn, ticker, date):
    return db.one(conn, "SELECT date, close FROM prices WHERE ticker = ? AND date >= ? ORDER BY date LIMIT 1", (ticker, date))


def score_calls(conn, today=None):
    """Settle every open call whose due date has passed: buy-side is right when the stock beat SPY, sell-side when it lagged."""
    today = today or common.today()
    due = db.rows(conn, "SELECT * FROM calls WHERE outcome = 'open' AND due_at <= ?", (today,))
    settled, waiting = [], []
    for c in due:
        if c["price_at_call"] is None or c["spy_at_call"] is None:
            conn.execute("UPDATE calls SET outcome = 'void', realised_at = ? WHERE id = ?", (today, c["id"]))
            settled.append({"id": c["id"], "ticker": c["ticker"], "outcome": "void", "why": "no price at the call"})
            continue
        p, s = price_on_or_after(conn, c["ticker"], c["due_at"]), price_on_or_after(conn, "SPY", c["due_at"])
        if not p or not s:
            waiting.append({"id": c["id"], "ticker": c["ticker"], "due_at": c["due_at"],
                            "need": "yahoo.py prices %s" % ("SPY" if p else c["ticker"])})
            continue
        ret, spy_ret = p["close"] / c["price_at_call"] - 1, s["close"] / c["spy_at_call"] - 1
        beat = ret > spy_ret
        outcome = "right" if (beat if side(c["action"]) == "buy" else not beat) else "wrong"
        conn.execute("UPDATE calls SET outcome = ?, realised_at = ?, realised_price = ?, spy_realised = ? WHERE id = ?",
                     (outcome, p["date"], p["close"], s["close"], c["id"]))
        settled.append({"id": c["id"], "ticker": c["ticker"], "action": c["action"], "outcome": outcome,
                        "return": round(ret, 4), "spy_return": round(spy_ret, 4)})
    return settled, waiting


def track_record(conn, action=None, ticker=None):
    sql, params = ("SELECT ticker, tier, action, made_at, due_at, price_at_call, realised_price, spy_at_call, spy_realised, "
                   "confidence, outcome FROM calls WHERE 1 = 1"), []
    if action:
        sql += " AND action = ?"
        params.append(action)
    if ticker:
        sql += " AND ticker = ?"
        params.append(ticker.upper())
    rows = db.rows(conn, sql + " ORDER BY made_at DESC", tuple(params))
    for r in rows:
        if r["realised_price"] and r["price_at_call"]:
            r["return"] = round(r["realised_price"] / r["price_at_call"] - 1, 4)
            r["spy_return"] = round(r["spy_realised"] / r["spy_at_call"] - 1, 4) if r["spy_realised"] and r["spy_at_call"] else None
    summary = db.rows(conn, "SELECT * FROM track_record")
    return rows, summary


# --- report -------------------------------------------------------------------------------------
def marker_ids(line):
    ids = []
    for m in MARKER.finditer(line):
        ids += [int(x) for x in re.findall(r"\d+", m.group(1))]
    return ids


def lint(text, known_ids):
    """Return a list of problems: figures without a marker, unknown markers, missing sections."""
    problems, in_code, seen = [], False, set()
    low = text.lower()
    for sec in REQUIRED_SECTIONS:
        if not re.search(r"^#+\s*.*%s" % re.escape(sec.lower()), low, re.M):
            problems.append("missing section: %s" % sec)
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not s or s.startswith("#") or re.match(r"^\|?[\s:|-]+\|?$", s) or s.startswith(">"):
            continue
        ids = marker_ids(s)
        for i in ids:
            seen.add(i)
            if i not in known_ids:
                problems.append("line %d: unknown source S%d" % (n, i))
        bare = MARKER.sub("", s)
        bare = re.sub(r"\(S\d+\)", "", bare)
        if DIGIT.search(bare) and not ids and not s.lower().startswith("*as of"):
            problems.append("line %d: a figure without a source marker: %s" % (n, s[:80]))
    return problems, seen


def link_markers(text, sources):
    def repl(m):
        ids = [int(x) for x in re.findall(r"\d+", m.group(1))]
        return "".join("[S%d](%s)" % (i, sources[i]["url"]) for i in ids if i in sources) or m.group(0)
    return MARKER.sub(repl, text)


def sources_section(ids, sources):
    lines = ["", "## Sources", ""]
    for i in sorted(ids):
        s = sources[i]
        lines.append("- S%d: %s (%s) <%s>, fetched %s" % (i, s["title"] or "source", s["grade"], s["url"], s["fetched_at"][:10]))
    return "\n".join(lines)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "report"


def finalise(conn, project, run_id, draft, slug=None, today=None):
    run = run_row(conn, run_id)
    sources = {r["id"]: r for r in db.rows(conn, "SELECT * FROM sources")}
    problems, used = lint(draft, set(sources))
    if problems:
        return None, problems
    text = link_markers(draft, sources) + "\n" + sources_section(used, sources) + "\n\n" + DISCLAIMER + "\n"
    today = today or common.today()
    subjects = json.loads(run["subjects"] or "[]")
    name = "%s-%s.html" % (today, slug or slugify(run["intent"] + "-" + "-".join(subjects[:3])))
    folder = os.path.join(common.data_dir(project), REPORTS_DIR)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    title = next((l.lstrip("# ").strip() for l in draft.splitlines() if l.startswith("# ")), "my-invest report")
    charts = [c for c in (price_svg(conn, t) for t in subjects if ":" not in t) if c]
    with open(path, "w") as f:
        f.write(page(title, md_to_html(text), charts))
    rel = os.path.relpath(path, project)
    conn.execute("UPDATE runs SET status = 'answered', report_path = ? WHERE id = ?", (rel, run_id))
    return rel, []


# --- HTML page ----------------------------------------------------------------------------------
CSS = """:root{--bg:#fff;--fg:#1b1f23;--mute:#6a737d;--line:#e1e4e8;--acc:#0969da;--up:#1a7f37;--down:#cf222e}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#e6edf3;--mute:#8b949e;--line:#30363d;--acc:#58a6ff;--up:#3fb950;--down:#f85149}}
body{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:16px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif}
main{max-width:860px;margin:0 auto}h1{font-size:1.5em}h2{font-size:1.2em;border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:1.6em}
table{border-collapse:collapse;width:100%;display:block;overflow-x:auto;font-size:.95em}th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:rgba(127,127,127,.08)}a{color:var(--acc)}code{background:rgba(127,127,127,.12);padding:0 4px;border-radius:4px}
blockquote{color:var(--mute);border-left:3px solid var(--line);margin:1em 0;padding:0 12px}svg{width:100%;height:auto;display:block;margin:8px 0}
.chart-note{color:var(--mute);font-size:.85em}"""

INLINE = [(re.compile(r"\*\*(.+?)\*\*"), r"<strong>\1</strong>"), (re.compile(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)"), r"<em>\1</em>"),
          (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
          (re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)"), r'<a href="\2">\1</a>')]


def inline(text):
    out = html_mod.escape(text, quote=False)
    for rx, rep in INLINE:
        out = rx.sub(rep, out)
    return out


def md_to_html(md):
    """The Markdown subset the plugin writes: headings, paragraphs, bullets, tables, quotes, fences, inline marks."""
    out, para, in_code, in_list, table = [], [], False, False, []

    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))
            para.clear()

    def flush_table():
        if table:
            head, rows = table[0], [r for r in table[1:] if not re.match(r"^[\s:|-]+$", r)]
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            out.append("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (
                "".join("<th>%s</th>" % inline(c) for c in cells(head)),
                "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in cells(r)) for r in rows)))
            table.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in md.splitlines():
        s = line.rstrip()
        if s.startswith("```"):
            flush_para(); flush_table(); close_list()
            out.append("<pre><code>" if not in_code else "</code></pre>")
            in_code = not in_code
            continue
        if in_code:
            out.append(html_mod.escape(s))
            continue
        if s.strip().startswith("|"):
            flush_para(); close_list()
            table.append(s)
            continue
        flush_table()
        if not s.strip():
            flush_para(); close_list()
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", s)
        if m:
            flush_para(); close_list()
            out.append("<h%d>%s</h%d>" % (len(m.group(1)), inline(m.group(2)), len(m.group(1))))
            continue
        if s.startswith(">"):
            flush_para(); close_list()
            out.append("<blockquote>%s</blockquote>" % inline(s.lstrip("> ")))
            continue
        m = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.*)", s)
        if m:
            flush_para()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>%s</li>" % inline(m.group(1)))
            continue
        para.append(s.strip())
    flush_para(); flush_table(); close_list()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def moving(vals, n):
    out, acc = [], 0.0
    for i, v in enumerate(vals):
        acc += v
        if i >= n:
            acc -= vals[i - n]
        out.append(acc / n if i >= n - 1 else None)
    return out


def price_svg(conn, ticker, years=5, w=860, h=320):
    """Closing prices with the 50- and 200-day averages as an inline SVG; None when fewer than 60 days are stored."""
    rows = db.rows(conn, "SELECT date, close FROM prices WHERE ticker = ? AND date >= date('now', ?) ORDER BY date",
                   (ticker, "-%d years" % years))
    if len(rows) < 60:
        return None
    closes = [r["close"] for r in rows]
    lo, hi = min(closes), max(closes)
    pad_l, pad_r, pad_t, pad_b = 56, 12, 12, 28
    sx = lambda i: pad_l + (w - pad_l - pad_r) * i / float(len(closes) - 1)
    sy = lambda v: pad_t + (h - pad_t - pad_b) * (1 - (v - lo) / ((hi - lo) or 1))
    path = lambda series: " ".join("%.1f,%.1f" % (sx(i), sy(v)) for i, v in enumerate(series) if v is not None)
    ticks = [lo + (hi - lo) * k / 4 for k in range(5)]
    g = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" aria-label="%s closing price">' % (w, h, ticker)]
    for t in ticks:
        g.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--line)" stroke-width="1"/>' % (pad_l, sy(t), w - pad_r, sy(t)))
        g.append('<text x="%d" y="%.1f" font-size="11" fill="var(--mute)" text-anchor="end">%s</text>' % (pad_l - 6, sy(t) + 4, "%.0f" % t))
    for i in (0, len(rows) // 2, len(rows) - 1):
        g.append('<text x="%.1f" y="%d" font-size="11" fill="var(--mute)" text-anchor="middle">%s</text>' % (sx(i), h - 8, rows[i]["date"]))
    g.append('<polyline fill="none" stroke="var(--fg)" stroke-width="1.5" points="%s"/>' % path(closes))
    g.append('<polyline fill="none" stroke="var(--acc)" stroke-width="1.2" points="%s"/>' % path(moving(closes, 50)))
    g.append('<polyline fill="none" stroke="var(--down)" stroke-width="1.2" points="%s"/>' % path(moving(closes, 200)))
    g.append('<text x="%d" y="%d" font-size="11" fill="var(--mute)">close; <tspan fill="var(--acc)">50-day average</tspan>; '
             '<tspan fill="var(--down)">200-day average</tspan></text>' % (pad_l, pad_t))
    g.append("</svg>")
    return "\n".join(g) + '\n<p class="chart-note">%s, last %d trading days stored, %s to %s.</p>' % (
        ticker, len(rows), rows[0]["date"], rows[-1]["date"])


def page(title, body_html, charts):
    parts = [body_html]
    if charts:
        parts.insert(1, "<h2>Price history</h2>\n" + "\n".join(charts))
    first_h2 = body_html.find("<h2>")
    if charts and first_h2 > 0:  # charts right after the headline block, before the first section
        parts = [body_html[:first_h2], "<h2>Price history</h2>\n" + "\n".join(charts), body_html[first_h2:]]
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" "
            "content=\"width=device-width,initial-scale=1\"><title>%s</title><style>%s</style></head>\n<body><main>\n%s\n</main></body></html>\n"
            % (html_mod.escape(title), CSS, "\n".join(parts)))


# --- CLI ----------------------------------------------------------------------------------------
def read_arg(v):
    if v.startswith("@"):
        with open(v[1:]) as f:
            return f.read()
    return v


def run(argv=None):
    p = common.parser(SCRIPT, "runs, confidence, calls, scoring, lint and the final report")
    p.add_argument("command", choices=["open", "confidence", "calls", "score", "record", "lint", "report", "fail"])
    p.add_argument("run_id", nargs="?", type=int, default=None)
    p.add_argument("subject", nargs="?", default="")
    p.add_argument("--question", default="")
    p.add_argument("--intent", default="")
    p.add_argument("--subjects", default="", help="comma-separated tickers or sector:<name>")
    p.add_argument("--plan", default="", help="JSON list of steps, or @file")
    p.add_argument("--json", default="", help="calls: a JSON list of rows, or @file")
    p.add_argument("--action", default="")
    p.add_argument("--ticker", default="")
    p.add_argument("--file", default="", help="lint/report: the Markdown draft")
    p.add_argument("--slug", default="")
    p.add_argument("--notes", default="")
    a = p.parse_args(argv)
    project = common.resolve_project(a.project)
    conn = db.connect(project)
    try:
        if a.command == "open":
            if not (a.question and a.intent and a.subjects):
                return common.fail(SCRIPT, "open needs --question, --intent and --subjects")
            plan = json.loads(read_arg(a.plan)) if a.plan else None
            rid = open_run(conn, a.question, a.intent, a.subjects.split(","), plan)
            return common.emit({"ok": True, "script": SCRIPT, "run_id": rid})
        if a.command == "confidence":
            if a.run_id is None or not a.subject:
                return common.fail(SCRIPT, "confidence needs RUN_ID and SUBJECT")
            c = confidence(conn, a.run_id, a.subject.upper() if ":" not in a.subject else a.subject, a.action or None)
            c.update({"ok": True, "script": SCRIPT, "line": confidence_line(c)})
            return common.emit(c, md=c["line"] if a.md else None)
        if a.command == "calls":
            if a.run_id is None or not a.json:
                return common.fail(SCRIPT, "calls needs RUN_ID and --json")
            rows = json.loads(read_arg(a.json))
            out = store_calls(conn, a.run_id, rows if isinstance(rows, list) else [rows])
            return common.emit({"ok": True, "script": SCRIPT, "stored": len(out), "calls": out})
        if a.command == "score":
            settled, waiting = score_calls(conn)
            return common.emit({"ok": True, "script": SCRIPT, "settled": settled, "waiting": waiting})
        if a.command == "record":
            rows, summary = track_record(conn, a.action or None, a.ticker or None)
            md = db.md_table(summary) + "\n\n" + db.md_table(rows) if a.md else None
            return common.emit({"ok": True, "script": SCRIPT, "summary": summary, "calls": rows}, md=md)
        if a.command in ("lint", "report"):
            if not a.file:
                return common.fail(SCRIPT, "%s needs --file" % a.command)
            with open(a.file) as f:
                draft = f.read()
            if a.command == "lint":
                problems, used = lint(draft, {r["id"] for r in db.rows(conn, "SELECT id FROM sources")})
                return common.emit({"ok": not problems, "script": SCRIPT, "problems": problems, "sources_used": sorted(used)}) if not problems \
                    else common.fail(SCRIPT, "%d problem(s)" % len(problems), problems=problems)
            if a.run_id is None:
                return common.fail(SCRIPT, "report needs RUN_ID")
            rel, problems = finalise(conn, project, a.run_id, draft, a.slug or None)
            if problems:
                return common.fail(SCRIPT, "report refused: %d problem(s)" % len(problems), problems=problems)
            return common.emit({"ok": True, "script": SCRIPT, "report": rel})
        if a.command == "fail":
            if a.run_id is None:
                return common.fail(SCRIPT, "fail needs RUN_ID")
            run_row(conn, a.run_id)
            conn.execute("UPDATE runs SET status = 'failed', notes = ? WHERE id = ?", (a.notes, a.run_id))
            return common.emit({"ok": True, "script": SCRIPT, "run_id": a.run_id, "status": "failed"})
    except (ValueError, KeyError) as e:
        return common.fail(SCRIPT, e)
    return 1


if __name__ == "__main__":
    sys.exit(common.run_main(SCRIPT, run))
