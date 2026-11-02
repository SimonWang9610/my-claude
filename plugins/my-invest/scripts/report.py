#!/usr/bin/env python3
"""report.py <TICKER | stock folder> --question "<text>" --lens long|short|both [--narrative PATH] [--chat] [--html]
    [--no-lint]

Renders reports/dossier.md per skills/advisor/references/answer.md from facts/facts.json,
facts/scorecard.json, the narrative (--narrative, default the newest history/<date>-<HHMM>.md other than log.md),
research/research.md and research/industry.md (optional), facts/holdings.json and facts/holdings_tables.json
(optional); writes reports/<date>-<HHMM>.md, appends one line to history/log.md, regenerates INDEX.md at the stock
root, lints the dossier and the index (lint.lint_text) and exits 1 printing the violations unless --no-lint.
With --chat it also prints the beginner chat answer (report-template.md: short answer, price map, plain-words
sections, then `---` and `## Details` with seven technical sections) as Markdown. With --html it writes reports/<date>-<HHMM>.html: the chat answer, the chart panels (chart.build_panels,
inline SVG) and the full dossier, via mdhtml.render. Stdlib only.

Conventions the template leaves open:
- The question is rendered as inline code (verbatim user text, never a cited figure).
- Every rendered line that carries a figure gets the markers of its inputs; lines whose figure is a
  score.py decision without its own input marker cite the score row S<s>.
- History lines cite a derived row S<h> (url file://.../history/log.md) in the dossier; log.md itself
  holds no markers. The snapshot and the history line are written only when lint passes (or --no-lint).
"""
import datetime
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import EnvelopeParser, add_common_args, locate, run_main, stamp, today  # noqa: E402
from lint import DISCLAIMER, facts_ids, lint_text  # noqa: E402
from score import TESTS, horizon_label  # noqa: E402

PILLAR_NAMES = {"1": "Business quality and moat", "2": "Financial strength", "3": "Management and capital allocation",
                "4": "Valuation and margin of safety", "5": "Risks and red flags"}
GATE_NAMES = {
    "G1": "Bankruptcy or receivership (8-K Item 1.03, 3 yrs)", "G2": "Restatement (8-K Item 4.02, 3 yrs)",
    "G3": "Altman distress zone (manufacturer, Z < 1.81)", "G4": "Going-concern paragraph (latest 10-K)",
    "G5": "Negative owner earnings (full capex, 3 of 5 yrs)", "G6": "Serial dilution (3 rising yrs and > 10%)",
}
ST_NAMES = {"ST1": "Trend state", "ST2": "Momentum", "ST3": "Distance from the 52-week high",
            "ST4": "Volatility regime", "ST5": "Implied move", "ST6": "Events inside the horizon",
            "ST7": "Relative strength"}
RESEARCH = ("Business and moat", "Management", "Market trend", "Risk evidence", "News and posts")
SEP = " · "
NEWS_SLOT, PEERS_SLOT, INDUSTRY_SLOT = "News, what it means", "Compared with peers", "Industry"
PILLAR_PLAIN = {"1": "quality", "2": "strength", "3": "capital use", "4": "price", "5": "risk"}
ACCOUNTS = {"NONREG": "Non-registered", "TFSA": "TFSA", "RRSP": "RRSP", "FHSA": "FHSA", "RRIF": "RRIF"}
# (term, trigger regex, plain gloss): printed under "Words used here" only when the trigger appears above it
GLOSS = (
    ("fair value", r"\bfair\b", "what the model thinks one share is worth today, from the cash the business makes"),
    ("buy zone / sell zone", r"\b(?:buy|sell) zone", "cheap enough to buy / expensive enough to sell, by the model's own rule"),
    ("confidence", r"\bconfiden", "how much of the evidence the model could check and how closely its scenarios agree, "
                                   "out of 100"),
    ("confidence band", r"/100 \((?:strong evidence|solid|mixed|thin)\)",
     "the word after the confidence score: strong evidence (80 or more), solid (65 to 79), mixed (45 to 64), thin "
     "(below 45)"),
    ("deal-breaker check", r"deal-breaker", "a pass/fail test (bankruptcy, restatement, going concern, distress, "
                                            "losses, dilution); one failure means stay away"),
    ("owner earnings", r"owner earnings|cash the business really makes",
     "the cash the business really makes: profit plus non-cash charges minus the spending needed to keep it running "
     "(estimated)"),
    ("implied CAGR", r"implied CAGR|yearly return the price implies",
     "the yearly return you would earn if the price moved to the model's value"),
    ("quality / strength / capital use / price / risk", r"\bpillar|\bquality\b|capital use",
     "the five parts of the score, 20 points each"),
    ("trend", r"\btrend|rising lately|falling lately|no clear direction", "whether the price has been rising or "
                                                                          "falling lately, from its moving averages"),
    ("strict value", r"strict value", "the price a cautious value investor would pay today, from the cash the business "
                                      "makes"),
    ("consensus target", r"consensus", "the average price analysts expect a year from now (secondary data)"),
    ("pullback", r"pullback", "a dip back to a recent average price"),
    ("50-day / 200-day average", r"\b(?:50|200)-day average", "the average closing price over the last 50 / 200 "
                                                               "trading days"),
    ("one standard deviation", r"standard deviation", "about two times in three the price ends inside this range, if "
                                                      "the options market is right"),
    ("multiple (P/E)", r"\bP/E\b|\bmultiple\b", "the price divided by one year's earnings per share"),
    ("expected yearly return", r"a year expected|expected yearly return",
     "earnings growth plus the change in the multiple plus cash returned, per year, in the base scenario"),
    ("call", r"\bcalls?\b", "a contract that gives its buyer the right to buy 100 shares at the strike until expiry"),
    ("put", r"\bputs?\b", "a contract that gives its buyer the right to sell 100 shares at the strike until expiry"),
    ("premium", r"\bpremium", "the price of an option, paid by its buyer to its seller"),
    ("strike", r"\bstrike", "the share price written into the option"),
    ("expiry", r"\bexpir", "the last day the option exists"),
    ("covered", r"\bcovered\b", "the call's seller already owns the shares the call may take"),
    ("assignment", r"\bassign|called away", "the buyer uses the option and the seller must deliver or buy the shares"),
    ("time decay", r"time decay", "an option loses value each day as expiry nears, all else equal"),
    ("breakeven", r"breakeven|strike plus premium", "the share price at which the option trade neither gains nor loses"),
)
OPTION_TERMS = {"call", "put", "premium", "strike", "expiry", "covered", "assignment", "time decay", "breakeven"}
INLINE = (  # (term, gloss injected on first mention, guard): skipped when the guard already appears in the line
    (r"\bowner earnings\b(?! \()", "owner earnings (the cash the business really makes)", r"cash the business really makes"),
    (r"\bimplied CAGR\b(?! \()", "implied CAGR (the yearly return the price implies)", r"yearly return the price implies"),
    (r"\bROIC\b(?! \()", "ROIC (return on the money invested in the business)", r"return on the money invested"),
    (r"\bmargin of safety\b(?! \()", "margin of safety (the discount to fair value the model asks for)",
     r"discount to fair value"),
    (r"\bbull value\b(?! \()", "bull value (the model's optimistic value)", r"optimistic value"),
    (r"\bbear value\b(?! \()", "bear value (the model's cautious value)", r"cautious value"),
    (r"\bbase value\b(?! \()", "base value (the model's fair value)", r"the model's fair value"),
    (r"\b(G[1-6])\b", r"deal-breaker check \1", r"deal-breaker"),
)


# ---------- formatting ----------
def money(x):
    if x is None:
        return "n/a"
    return ("-$%s" if x < 0 else "$%s") % format(abs(x), ",.2f")


def pct(x, nd=2):
    if x is None:
        return "n/a"
    s = ("%." + str(nd) + "f") % (x * 100)
    return (s.rstrip("0").rstrip(".") if "." in s else s) + "%"


def mil(x, nd=0):
    return "n/a" if x is None else format(x / 1e6, ",.%df" % nd)


def qty(x):
    return "n/a" if x is None else "%g" % x


def ratio(x):
    return "n/a" if x is None else "%.4f" % x


def mk(ids):
    ids = [i for i in dict.fromkeys(ids) if i]
    return " [%s]" % ", ".join(ids) if ids else ""


def esc(s):
    return str(s).replace("|", "/").replace("\n", " ")


def g(obj, *path):
    for p in path:
        if isinstance(obj, dict):
            obj = obj.get(p)
        elif isinstance(obj, list) and isinstance(p, int) and -len(obj) <= p < len(obj):
            obj = obj[p]
        else:
            return None
    return obj


def num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def ratio1(x):
    return "n/a" if x is None else "%.1f" % x


def spct(x):
    """Signed percent, one decimal: +4.2% / -0.3%."""
    return "n/a" if x is None else "%+.1f%%" % (x * 100)


def unmoney(s):
    """'$1,234.50' / '-$3.00' -> float; None when the text is not a money cell."""
    m = re.fullmatch(r"(-?)\$([\d,]+(?:\.\d+)?)", (s or "").strip())
    return None if not m else float(m.group(2).replace(",", "")) * (-1 if m.group(1) else 1)


def weekdays_between(a, b):
    """Weekdays after ISO date a up to and including b (holidays ignored); None when a date is missing."""
    try:
        da, db = datetime.date.fromisoformat(str(a)[:10]), datetime.date.fromisoformat(str(b)[:10])
    except (TypeError, ValueError):
        return None
    return sum(1 for i in range(1, (db - da).days + 1) if (da + datetime.timedelta(days=i)).weekday() < 5)


def band_word(v):
    """Confidence band: >= 80 strong evidence, 65-79 solid, 45-64 mixed, below 45 thin."""
    if num(v) is None:
        return None
    return "strong evidence" if v >= 80 else "solid" if v >= 65 else "mixed" if v >= 45 else "thin"


def plain(line):
    """Gloss standard terms inline (first mention each) and name pillars in plain words."""
    for rx, rep, guard in INLINE:
        if not re.search(guard, line, re.I):
            line = re.sub(rx, rep, line, count=1)
    return re.sub(r"\b[Pp]illar ([1-5])\b(?! \()", lambda m: "%s (%s)" % (m.group(0), PILLAR_PLAIN[m.group(1)]), line,
                  count=1)


def usd0(x):
    return "n/a" if x is None else ("-$%s" if x < 0 else "$%s") % format(abs(round(x)), ",")


def signed0(x):
    return "n/a" if x is None else ("+" if x >= 0 else "-") + "$" + format(abs(round(x)), ",")


PEER_LABELS = {"sales_growth_5y": "Sales growth (5 yr/yr)",
               "operating_margin": "Profit kept per $1 of sales (operating margin)",
               "roic": "Return on the money invested (ROIC)", "cash_yield": "Cash the business makes, as % of price",
               "debt_years": "Debt vs that cash (years to repay)", "return_12m": "Price change, 12 months",
               "stance": "Model stance"}


def peer_fmt(key, v):
    """Peer table cell: percent for ratios of return/margin/growth/yield, x for multiples, compact $ for sizes."""
    if v is None:
        return "no evidence"
    if not isinstance(v, (int, float)):
        return esc(v)
    k = key.lower()
    if "years" in k:
        return "%.1f years" % v
    if any(w in k for w in ("margin", "roic", "growth", "yield", "return", "cagr", "pct", "ratio_pct")):
        return pct(v, 1)
    if any(w in k for w in ("pe", "ev_", "multiple", "_x", "ratio")):
        return "%.1fx" % v
    if abs(v) >= 1e6:
        for d, u in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
            if abs(v) >= d:
                return "%s$%.1f%s" % ("-" if v < 0 else "", abs(v) / d, u)
    return format(v, ",.2f")


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return None


def read_json(path):
    t = read(path)
    return None if t is None else json.loads(t)


def sid_num(s):
    return int(s[1:]) if re.fullmatch(r"S\d+", s or "") else 10 ** 9


# ---------- parsing ----------
def parse_sections(text, level=2):
    """{heading: [lines]} for `## heading` blocks; text before the first heading is dropped."""
    out, cur = {}, None
    rx = re.compile(r"^%s\s+(.*?)\s*$" % ("#" * level))
    for line in (text or "").splitlines():
        m = rx.match(line)
        if m and not line.startswith("#" * (level + 1)):
            cur = m.group(1)
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return {k: trim(v) for k, v in out.items()}


def trim(lines):
    while lines and not lines[0].strip():
        lines = lines[1:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines


def parse_research(text):
    """Cumulative research.md: `## <section>` bodies, `### Open questions` lines, `### Evidence log` rows."""
    secs, oq, log, cur, mode = {}, [], [], None, "body"
    for line in (text or "").splitlines():
        h2 = re.match(r"^##\s+(.*?)\s*$", line)
        h3 = re.match(r"^###\s+(.*?)\s*$", line)
        special = (h2 or h3) and (h2 or h3).group(1).lower() in ("open questions", "evidence log")
        if special:  # either heading level ends the body sections
            mode = (h2 or h3).group(1).lower()
            cur = None
            continue
        if h2:
            cur, mode = h2.group(1), "body"
            secs.setdefault(cur, [])
            continue
        if h3 and mode != "body":
            mode = "body"
        if mode == "open questions":
            if line.strip():
                oq.append(line)
        elif mode == "evidence log":
            if re.match(r"^\s*\|\s*S\d+\s*\|", line):
                log.append(line.strip())
        elif cur is not None:
            secs[cur].append(line)
    return {k: trim(v) for k, v in secs.items()}, oq, log


def parse_history(line):
    """A history/log.md line -> {date, question, lens, tier, score, stance, confidence, price, said, expected, zones,
    changed}. Fields are found by name, so lines written before a field existed parse too (the key is then absent)."""
    parts = line.lstrip("- ").split(SEP)
    out = {"date": parts[0].strip() if parts else ""}
    for part in parts[1:]:
        if part.startswith("changed: "):
            out["changed"] = part[len("changed: "):]
        else:
            name, _, val = part.partition(" ")
            out[name] = val
    return out


# ---------- renderer ----------
class Report:
    def __init__(self, stock, question, lens, date, narrative=None, when=None):
        self.st, self.store = stock, stock.root
        self.q, self.lens, self.date = question, lens, date
        self.when = when or datetime.datetime.now(datetime.timezone.utc)
        self.f = read_json(stock.facts)
        self.sc = read_json(stock.scorecard)
        if self.f is None or self.sc is None:
            raise FileNotFoundError("facts/facts.json and facts/scorecard.json are required in %s" % stock.root)
        self.narr_path = narrative or stock.newest_narrative()
        self.narr_text = read(self.narr_path) if self.narr_path else None
        self.narr = parse_sections(self.narr_text) if self.narr_text else None
        self.res, self.res_oq, self.res_log = parse_research(read(stock.research))
        self.ind_text = read(stock.industry)
        self.ind, self.ind_oq, ind_log = parse_research(self.ind_text) if self.ind_text else ({}, [], [])
        self.res_log = self.res_log + ind_log
        self.hold = read_json(stock.holdings)
        req = read_json(os.path.join(stock.root, "request.json"))
        self.req = req if isinstance(req, dict) else {}
        self.what_if = [float(x) for x in (g(self.req, "what_if", "price") or []) if isinstance(x, (int, float))]
        self.wants = self.req.get("wants") if isinstance(self.req.get("wants"), list) else None
        self.tables = read_json(stock.holdings_tables)
        self.m = self.f.get("metrics") or {}
        self.val = self.m.get("valuation") or {}
        self.P = self.sc.get("price_src") or g(self.f, "price", "src") or "S3"
        self.D, self.S = self.sc.get("derived_src"), self.sc.get("score_src")
        self.F = g(self.f, "fundamentals", "annual", 0, "src") or "S1"
        self.sources = dict(self.f.get("sources") or {})
        self.sources.update(self.sc.get("sources") or {})
        self.H = "S62"   # fixed derived row (S60 metrics, S61 score, S62 history)
        self.hist_path = stock.log
        self.hist_line_now = None            # set by history_line(); excluded from "what this advisor said before"
        self.spy = read_json(os.path.join(stock.market_dir, "SPY.json"))
        self.sources[self.H] = {"class": "derived", "what": "report.py run history, one line per analysis",
                                "url": "file://" + os.path.abspath(self.hist_path), "as_of": date, "retrieved": date}
        peers = read_json(os.path.join(stock.facts_dir, "peers.json"))
        if isinstance(peers, dict) and isinstance(peers.get("sources"), dict):
            for k, v in peers["sources"].items():
                if isinstance(v, dict) and v.get("url"):
                    self.sources.setdefault(k, v)
        if isinstance(self.tables, dict) and isinstance(self.tables.get("sources"), dict):
            for k, v in self.tables["sources"].items():
                if isinstance(v, dict) and v.get("url"):
                    self.sources.setdefault(k, v)

    def own(self, ids):
        """markers of an item, or the score row when it has none."""
        return mk(ids or [self.S])

    # -- history --
    def history_line(self):
        sc, z = self.sc, self.sc.get("zones") or {}
        q = "`%s`" % re.sub(r"\s+", " ", self.q.replace("`", "'").replace(SEP, " - ")).strip()
        rec = self.rec()
        fields = [self.date, "question " + q, "lens " + self.lens, "tier " + sc["tier"], "score %s/100" % sc["score"],
                  "stance " + sc["stance"], "confidence %s/100" % sc["confidence"]["value"],
                  "price " + money(sc.get("price")), "said " + (rec.get("cell") or rec.get("stance") or sc["stance"])]
        if rec.get("basis") == "outlook":
            fields.append("expected %s/yr at %s vs %s required" % (pct(rec.get("expected_return"), 1), rec.get("label"),
                                                                   pct(rec.get("required_return"), 1)))
        fields.append("zones buy below %s / sell above %s" % (money(z.get("buy_below")), money(z.get("sell_above"))))
        prev = self.history()[-1:]
        if not prev:
            changed = "first analysis"
        else:
            old, new = parse_history(prev[0]), parse_history(SEP.join(fields))
            diffs = ["%s %s → %s" % (name, old.get(name, ""), new.get(name, "")) for name in ("tier", "score", "stance", "zones")
                     if old.get(name, "") != new.get(name, "")]
            changed = "; ".join(diffs) if diffs else "no change in tier, score, stance or zones"
        self.hist_line_now = "- " + SEP.join(fields + ["changed: " + changed])
        return self.hist_line_now

    def history(self):
        t = read(self.hist_path) or ""
        return [l for l in t.splitlines() if l.startswith("- ")]

    def prior_history(self):
        """log.md lines of earlier runs: the line this run writes is dropped once appended."""
        lines = self.history()
        return lines[:-1] if lines and lines[-1] == self.hist_line_now else lines

    def spy_change(self, a, b):
        """SPY simple return from ISO date a to b (adj_close, else close), None when the series does not cover both."""
        spy = self.spy
        if not isinstance(spy, dict) or not isinstance(spy.get("dates"), list):
            return None
        col = next((spy[k] for k in ("adj_close", "close") if isinstance(spy.get(k), list) and any(num(v) is not None for v in spy[k])), None)
        if col is None:
            return None
        pts = sorted((str(d)[:10], num(v)) for d, v in zip(spy["dates"], col) if isinstance(d, str) and num(v) is not None)

        def at(d):
            prior = [v for dd, v in pts if dd <= str(d)[:10]]
            return prior[-1] if prior else None
        va, vb = at(a), at(b)
        return None if va is None or vb is None or va <= 0 else vb / va - 1

    # -- sections --
    def header(self):
        f = self.f
        return ["# %s (%s) — dossier" % (f.get("name"), f.get("ticker")),
                "Updated %s · CIK %s · %s · last price %s on %s [%s]" % (
                    self.date, f.get("cik"), f.get("sector_class"), money(self.sc.get("price")),
                    g(f, "price", "date"), self.P), ""]

    def verdict(self):
        sc, z = self.sc, self.sc.get("zones") or {}
        return ["**Tier:** %s · **Score:** %s/100 · **Stance:** %s · **Confidence:** %s/100 [%s]" % (
            sc["tier"], sc["score"], sc["stance"], sc["confidence"]["value"], self.S),
            "Price %s [%s] vs buy zone below %s and sell zone above %s (base fair value %s, bear %s, bull %s) [%s]." % (
                money(sc.get("price")), self.P, money(z.get("buy_below")), money(z.get("sell_above")),
                money(z.get("base_today")), money(z.get("bear_today")), money(z.get("bull_today")), self.D),
            "Every value, zone and cell here is the model's output, not a forecast or advice [%s]." % self.S]

    def action_lines(self):
        a = self.sc.get("action") or {}
        cells = a.get("cells") or {}
        out = ["| Position | Model cell | Applies |", "|---|---|---|",
               "| not holding | %s | %s |" % (cells.get("not_holding"), "" if a.get("holding") else "yes"),
               "| holding | %s | %s |" % (cells.get("holding"), "yes" if a.get("holding") else ""), ""]
        if self.sc.get("gates_failed"):
            out.append("Failed gate(s) %s force stance avoid [%s]." % (", ".join(self.sc["gates_failed"]), self.S))
        trig = ", ".join("%s %s" % (t["name"], money(t["price"])) for t in a.get("price_triggers") or [])
        out.append("Price triggers: %s [%s]." % (trig or "none", self.D))
        for t in a.get("time_triggers") or []:
            out.append("- Time trigger: %s %s (%s; re-check %s)%s" % (
                t["name"], t["date"], t["basis"], ", ".join(t.get("recheck") or []), self.own(t.get("markers"))))
        return out

    def outlook(self):
        a = self.sc.get("action") or {}
        out = ["| Horizon | Bear | Base | Bull | Base implied CAGR | Verdict | |", "|---|---|---|---|---|---|---|"]
        for r in a.get("rows") or []:
            out.append("| %s | %s | %s | %s | %s | %s | [%s, %s] |" % (
                r.get("label") or horizon_label(r["horizon"]), money(r["bear"]), money(r["base"]), money(r["bull"]), pct(g(r, "cagr", "base")),
                r.get("verdict") or "n/a", self.D, self.S))
        out += ["", "Implied CAGR = (value at horizon ÷ price)^(1/h) − 1; verdict versus required return %s ± 2 pp "
                "(attractive above, unattractive below) [%s, %s]." % (pct(self.sc.get("required_return")), self.D, self.S)]
        if self.f.get("consensus"):
            out.append("Analyst consensus: present in facts.json but not rendered (no schema yet) [%s]." % self.S)
        return out

    def thesis(self):
        """The narrative Thesis; without one, a mechanical line per horizon the valuation carries."""
        if self.narr is not None and "Thesis" in self.narr:
            return self.narr["Thesis"]
        rows = g(self.sc, "action", "rows") or []
        return ["- **%s** — base value %s against today's %s; the price implies %s a year (%s) [%s, %s, %s]" % (
            r.get("label") or horizon_label(r["horizon"]), money(r.get("base")), money(self.sc.get("price")),
            pct(g(r, "cagr", "base")), r.get("verdict") or "n/a", self.D, self.P, self.S) for r in rows] or \
            self.slot("Thesis")

    def slot(self, name, lines=None):
        if self.narr is None or name not in self.narr:
            return ["- narrative pending: the analyze skill writes the %s slot in history/<date>-<HHMM>.md" % name.lower()]
        return self.narr[name] if lines is None else lines

    def strengths(self):
        it = self.sc.get("items") or {}
        s = [i for i in sorted(it) if i[0] in "13" and it[i]["status"] == "scored" and it[i]["score"] == 1][:4]
        w = ["gate %s failed: %s%s" % (k, x["note"], self.own(x["markers"]))
             for k, x in (self.sc.get("gates") or {}).items() if x["result"] == "fail"]
        w += ["%s %s%s" % (i, it[i]["note"], self.own(it[i]["markers"])) for i in sorted(it)
              if i[0] in "245" and it[i]["status"] == "scored" and it[i]["score"] == 0]
        strengths = ["- %s %s%s" % (i, it[i]["note"], self.own(it[i]["markers"])) for i in s]
        weaknesses = ["- " + x for x in w[:4]]
        narr = self.narr or {}  # a narrative slot replaces the mechanical list (its bullets carry ids and markers)
        if [l for l in narr.get("Strengths", []) if l.strip()]:
            strengths = [l for l in narr["Strengths"] if l.strip()]
        if [l for l in narr.get("Weaknesses", []) if l.strip()]:
            weaknesses = [l for l in narr["Weaknesses"] if l.strip()]
        return strengths or ["- none scored"], weaknesses or ["- none scored"]

    def why(self, limit=None):
        """narrative Why bullets when the slot exists, else one mechanical bullet per pillar."""
        lines = [l for l in (self.narr or {}).get("Why", []) if l.strip()]
        if lines:
            return [l for l in lines if l.startswith("- ")][:limit] if limit else lines
        return ["- Pillar %s %s: %s/20 [%s]" % (p, PILLAR_NAMES[p], "%g" % x["points"], self.S)
                for p, x in sorted(self.sc["pillars"].items())]

    def holdings(self):
        t = self.tables
        if isinstance(t, dict):
            md = None
            try:
                import holdings as hmod  # holdings.py's own renderer, when its shape matches
                md = hmod.render_md(t)
            except Exception:  # noqa: BLE001 - fall back to the minimal renderer below
                md = None
            if md:
                md = re.split(r"^#{2,3}\s+Evidence log", md, flags=re.M)[0]
                return trim([l for l in md.splitlines() if DISCLAIMER not in l.replace("’", "'")])
            return self.holdings_fallback(t)
        rows = g(self.sc, "action", "holdings") or []
        out = ["| Account | Shares | Avg cost | Value at price | Gain at price | Sell line | |", "|---|---|---|---|---|---|---|"]
        for r in rows:
            out.append("| %s | %s | %s | %s | %s | %s | [%s, %s] |" % (
                r.get("account"), qty(r.get("shares")), money(r.get("avg_cost")), money(r.get("value")),
                money(r.get("gain")), r.get("sell_line", ""), self.P, self.S))
        out += ["", "- holdings_tables.json absent: outcome and tax tables pending (holdings.py)"]
        return out

    def holdings_fallback(self, t):
        hid = next((k for k, v in (t.get("sources") or {}).items() if isinstance(v, dict) and v.get("class") == "derived"),
                   None) or self.S
        out = ["| Account | Shares | Avg cost | Point | Price | Value | Gain | |", "|---|---|---|---|---|---|---|---|"]
        for o in t.get("outcomes") or []:
            for p in o.get("price_points") or []:
                out.append("| %s | %s | %s | %s | %s | %s | %s | [%s, %s] |" % (
                    o.get("account"), qty(o.get("shares")), money(o.get("avg_cost")), p.get("label"), money(p.get("price")),
                    money(p.get("value")), money(p.get("gain", p.get("gain_abs"))), self.P, hid))
        for r in t.get("tax") or []:
            cm = r.get("citation_marker") or r.get("src")
            ids = [cm] if cm in self.sources else []
            out.append("- %s: %s; estimate %s%s" % (r.get("account"), r.get("rule", r.get("treatment", "")),
                                                    r.get("estimate", "n/a"), mk(ids + [hid])))
        for d in t.get("dividends") or []:
            src = d.get("src") if isinstance(d.get("src"), list) else [d.get("src")]
            out.append("- %s dividends: %s%s" % (d.get("account"), d.get("treatment", ""),
                                                  mk([x for x in src if x in self.sources] + [hid])))
        return out

    def options(self):
        o = self.f.get("options")
        if not isinstance(o, dict) or o.get("implied_move_pct") is None:
            why = (o or {}).get("reason") if isinstance(o, dict) else None
            return ["- no evidence: %s" % (why or "facts.json has no options object (options.py not run or chain "
                                            "unavailable)")]
        s, price = o.get("src") or self.P, self.sc.get("price")
        amt = o.get("implied_move_abs")
        out = ["| Expiry used | Implied volatility | Implied move | Put/call OI ratio | Max pain | Next earnings | |",
               "|---|---|---|---|---|---|---|",
               "| %s | %s | %s (%s) | %s | %s | %s | [%s] |" % (
                   o.get("expiry_used"), pct(o.get("atm_iv")), pct(o.get("implied_move_pct")), money(amt),
                   ratio(o.get("put_call_oi_ratio")), money(o.get("max_pain")), o.get("next_earnings_date") or "n/a", s), ""]
        if amt is not None and price:
            out.append("Secondary data: the options market prices a move of about ±%s (%s) by %s, a range of %s to %s "
                       "around today's price; implied moves run above realized on average, so read it as an upper-biased "
                       "range [%s, %s]." % (pct(o["implied_move_pct"]), money(amt), o.get("expiry_used"),
                                            money(price - amt), money(price + amt), s, self.P))
        return out

    def short_term(self):
        st = self.sc.get("short_term")
        if not st:
            return None
        rows = ["| Item | Result | Inputs | Source and caveat | |", "|---|---|---|---|---|"]
        for k in sorted(st["items"]):
            x = st["items"][k]
            v = x.get("value")
            if isinstance(v, dict):
                vs = ", ".join("%s %s" % (a, "n/a" if b is None else b) for a, b in v.items())
            elif isinstance(v, list):
                vs = "; ".join("%s %s" % (e["event"], e["date"]) for e in v)
                x = dict(x, markers=[m for e in v for m in e.get("markers", [])])
            else:
                vs = "n/a" if v is None else str(v)
            rows.append("| %s %s | %s | %s | %s |%s |" % (k, ST_NAMES[k], x["result"], esc(vs), esc(x["source"]),
                                                         self.own(x.get("markers"))))
        rows += ["", "**Short-term stance:** %s [%s]." % (st["stance"], self.S), "", st["caveat"]]
        for k in ("gate_override", "holding_note"):
            if st.get(k):
                rows.append("- %s [%s, %s]" % (st[k], self.S, self.D))
        return rows

    def market(self):
        out = []
        mkt = self.f.get("market")
        if isinstance(mkt, dict):
            for key in ("spy", "sector"):
                x = mkt.get(key)
                if isinstance(x, dict):
                    out.append("- %s returns: 1 month %s, 3 months %s, 6 months %s, 12 months %s; above its 200-day "
                               "average: %s%s" % (x.get("etf", "SPY") if key == "sector" else "SPY", pct(x.get("return_1m")),
                                                  pct(x.get("return_3m")), pct(x.get("return_6m")),
                                                  pct(x.get("return_12m")), "yes" if x.get("above_200d") else "no",
                                                  mk([x.get("src")]) or " [%s]" % self.S))
            fx = mkt.get("fx_usdcad")
            if isinstance(fx, dict) and fx.get("rate"):
                out.append("- USD/CAD %.4f on %s%s" % (fx["rate"], fx.get("date"), mk([fx.get("src")])))
        else:
            out.append("- market block: no evidence (facts.json has no market object; market.py not run)")
        mac = self.f.get("macro") or {}
        if mac.get("dgs10") is not None:
            out.append("- 10-year Treasury yield %s%% as of %s [%s]; implied equity risk premium %s%% as of %s [%s]" % (
                mac["dgs10"], mac.get("dgs10_date"), mac.get("src"), mac.get("erp"), mac.get("erp_date"),
                mac.get("erp_src") or mac.get("src")))
        return out

    def facts_section(self):
        f, m, D, F, P = self.f, self.m, self.D, self.F, self.P
        p = f.get("price") or {}
        out = ["52-week range %s to %s; market cap USD %s million; returns YTD %s, 1-year %s, 5-year CAGR %s, "
               "10-year CAGR %s (secondary) [%s]" % (money(p.get("low_52w")), money(p.get("high_52w")),
                                                     mil(p.get("market_cap")), pct(p.get("ytd_return")),
                                                     pct(p.get("return_1y")), pct(p.get("return_5y_cagr")),
                                                     pct(p.get("return_10y_cagr")), P)]
        if p.get("splits"):
            out.append("Splits: %s [%s]" % (", ".join("%s ratio %s" % (s.get("date"), s.get("ratio")) for s in p["splits"]), P))
        out += ["", "### Ten-year table (USD millions; diluted shares in millions, split-adjusted; ROIC as a fraction; "
                "owner earnings are an estimate: maintenance capex = min(capex, da))",
                "| FY | Revenue | Net income | Owner earnings (estimate) | Free cash flow | ROIC | Diluted shares "
                "(split-adjusted) | Cash returned (dividends + buybacks) | Source |",
                "|---|---|---|---|---|---|---|---|---|"]

        def by_fy(key, field="value"):
            return {x.get("fy"): x.get(field) for x in m.get(key) or [] if isinstance(x, dict)}
        oe, fcf, roic = by_fy("owner_earnings_series"), by_fy("fcf_series"), by_fy("roic")
        sh, cr = by_fy("shares_diluted_adjusted"), by_fy("cash_returned", "total")
        for r in g(f, "fundamentals", "annual") or []:
            fy = r.get("fy")
            out.append("| %s | %s | %s | %s | %s | %s | %s | %s | [%s, %s] |" % (
                fy, mil(r.get("revenue")), mil(r.get("net_income")), mil(oe.get(fy)), mil(fcf.get(fy)),
                ratio(roic.get(fy)), mil(sh.get(fy), 3), mil(cr.get(fy)), r.get("src") or F, D))
        a0 = g(f, "fundamentals", "annual", 0) or {}
        miss = [x for x in g(f, "fundamentals", "missing") or [] if x.get("fy") == a0.get("fy")]
        if miss:
            out += ["", "FY%s fields with no evidence: %s [%s]" % (a0.get("fy"), "; ".join(
                "%s (%s)" % (x["field"], x.get("reason", "")) for x in miss), F)]
        out += ["", "### Key derived metrics"]
        pio, alt, ben = m.get("piotroski") or {}, m.get("altman") or {}, m.get("beneish") or {}
        lines = [
            "Piotroski F (FY%s): %s of 9" % (pio.get("fy"), pio.get("score")),
            "Altman %s (FY%s): %s, zone %s" % (alt.get("model"), alt.get("fy"), alt.get("value"), alt.get("zone")),
            "Beneish M (FY%s): %s (UNVERIFIED coefficients and cutoff)" % (ben.get("fy"), ben.get("m")),
            "Accrual ratio: %s" % g(m, "accrual_ratio", "value"),
            "ROIIC 5-year: %s" % (g(m, "roiic_5y", "value") if g(m, "roiic_5y", "value") is not None
                                  else "n/a (%s)" % g(m, "roiic_5y", "reason")),
            "Gross profitability %s; gross margin 5-year change %s percentage points; revenue CAGR 5-year %s" % (
                g(m, "gross_profitability", "value"), g(m, "gross_margin_5y_change", "value"),
                g(m, "revenue_cagr_5y", "value")),
            "Shareholder yield %s; dilution 5-year %s; retained-earnings test %s" % (
                g(m, "shareholder_yield", "value"), g(m, "dilution_5y", "value"), g(m, "retained_earnings_test", "value")),
            "Graham number %s (3-year average EPS %s, book value per share %s)" % (
                money(g(m, "graham_number", "value")), g(m, "graham_number", "eps_3y_avg"), g(m, "graham_number", "bvps")),
            "Owner-earnings yield %s (estimate: maintenance capex = min(capex, da)); free cash flow yield %s; "
            "net debt to owner earnings %s" % (g(m, "owner_earnings", "yield"), g(m, "fcf", "yield"),
                                               g(m, "net_debt_to_owner_earnings", "value")),
            "Goodwill impairments in 5 years: %s" % (g(m, "goodwill_impairment_5y", "value")
                                                     if g(m, "goodwill_impairment_5y", "value") is not None
                                                     else "no evidence (%s)" % g(m, "goodwill_impairment_5y", "reason")),
        ]
        out += ["- %s [%s]" % (l, D) for l in lines]
        gi, fr = m.get("gate_inputs") or {}, m.get("freshness") or {}
        out += ["", "### Gate inputs and freshness",
                "- Owner-earnings negative years in last 5 (full capex): %s of %s [%s]" % (
                    gi.get("owner_earnings_negative_years_5y_full_capex"), gi.get("owner_earnings_years_checked_5y"), D),
                "- Current ratio %s; net current assets USD %s million [%s]" % (
                    gi.get("current_ratio"), mil(gi.get("net_current_assets")), D),
                "- Loss years in 10 years: %s of %s available [%s]" % (gi.get("loss_years_10y"),
                                                                       gi.get("years_available_10y"), D),
                "- Freshness %s; price age %s trading days; newer 10-K exists: %s [%s]" % (
                    fr.get("value"), fr.get("price_age_trading_days"), fr.get("newer_10k_exists"), D)]
        v, pa = self.val, self.val.get("params") or {}
        out += ["", "### Valuation (%s basis, per valuation.md)" % (v.get("cash_flow_basis") or "owner-earnings").replace("_", " "),
                "- Parameters: r_base %s, r_bear %s, terminal g %s, margin of safety %s, CF0 USD %s million over %s "
                "years, owner-earnings CAGR 5-year %s, growth cap %s (%s) [%s]" % (
                    pa.get("r_base"), pa.get("r_bear"), pa.get("terminal_g"), pa.get("mos"), mil(pa.get("cf0")),
                    pa.get("cf0_years"), pa.get("oe_cagr_5y"), pa.get("growth_cap"), pa.get("growth_cap_source"), D)]
        for s in ("bear", "base", "bull"):
            sc = g(v, "scenarios", s) or {}
            out.append("- Scenario %s: growth %s, discount rate %s%s [%s]" % (
                s, sc.get("g"), sc.get("r"), " (%s)" % sc["basis"] if sc.get("basis") else "", D))
        ft = v.get("fair_value_today") or {}
        out.append("- Fair value today per share: bear %s, base %s, bull %s; agreement %s; implied growth at price %s [%s]" % (
            money(ft.get("bear")), money(ft.get("base")), money(ft.get("bull")), v.get("agreement"),
            v.get("implied_growth_at_price"), D))
        return out

    def scorecard(self):
        sc, z, D, S = self.sc, self.sc.get("zones") or {}, self.D, self.S
        out = ["## Scorecard — as of %s" % sc["as_of"], ""] + self.verdict()[:2] + [
            "", "### Gates", "| Gate | Result | Evidence |", "|---|---|---|"]
        for gid in sorted(sc["gates"]):
            x = sc["gates"][gid]
            out.append("| %s %s | %s | %s%s |" % (gid, GATE_NAMES[gid], x["result"], esc(x["note"]), self.own(x["markers"])))
        out += ["", "### Pillars",
                "| Pillar | Points | Scored 0 or no evidence | n/a (reason) | UNVERIFIED threshold items (per card) |",
                "|---|---|---|---|---|"]
        it = sc["items"]
        for p in sorted(sc["pillars"]):
            pl = sc["pillars"][p]
            ids = [i for i in it if i.split(".")[0] == p]
            zero = ["%s %s%s%s" % (i, "no evidence: " if it[i]["status"] == "no evidence" else "", esc(it[i]["note"]),
                                    self.own(it[i]["markers"])) for i in ids if it[i]["status"] in ("scored", "no evidence")
                    and it[i]["score"] == 0]
            na = ["%s: %s%s" % (i, esc(it[i]["note"]), self.own(it[i]["markers"])) for i in ids if it[i]["status"] == "n/a"]
            na += ["%s: pending (screen mode)" % i for i in ids if it[i]["status"] == "pending"]
            unv = ["%s %s, scored %s%s" % (i, esc(it[i]["note"]), it[i]["score"], self.own(it[i]["markers"]))
                   for i in pl.get("unverified_items") or []]
            pts = pl["points"]
            out.append("| %s %s | %s/20 | %s | %s | %s |" % (p, PILLAR_NAMES[p], ("%g" % pts), "; ".join(zero) or "none",
                                                              "; ".join(na), "; ".join(unv)))
        v, pa = self.val, self.val.get("params") or {}
        basis = (v.get("cash_flow_basis") or "owner_earnings").replace("_", "-")
        bear_basis = g(v, "scenarios", "bear", "basis")
        out += ["", "### Fair value by horizon (per share, %s basis%s) [%s]" % (
            basis, "; bear on %s" % bear_basis if bear_basis else "", D),
            "| Horizon | Bear | Base | Bull | |", "|---|---|---|---|---|",
            "| today | %s | %s | %s | [%s] |" % (money(z.get("bear_today")), money(z.get("base_today")),
                                                money(z.get("bull_today")), D)]
        for h in sorted(sc.get("fair_value") or {}, key=lambda k: float(k) if re.fullmatch(r"[\d.]+", k) else 1e9):
            x = sc["fair_value"].get(h) or {}
            label = horizon_label(float(h)) if re.fullmatch(r"\d+(?:\.\d+)?", h) and float(h) > 0 else h
            out.append("| %s | %s | %s | %s | [%s] |" % (label, money(x.get("bear")), money(x.get("base")),
                                                         money(x.get("bull")), D))
        mos = sc.get("margin_of_safety", pa.get("mos"))
        out += ["", "Implied growth at price %s vs base scenario %s [%s]. Parameters: r %s, bear r %s, terminal g %s, "
                "margin of safety %s [%s]." % (pct(v.get("implied_growth_at_price")), pct(g(v, "scenarios", "base", "g")),
                                               D, pct(pa.get("r_base")), pct(pa.get("r_bear")), pct(pa.get("terminal_g")),
                                               pct(mos), D)]
        c = sc["confidence"]
        out += ["", "### Confidence",
                ("%s/100 = 0.4 × coverage %s (%s of %s) + 0.2 × agreement %s + 0.2 × outlook spread term %s (clamp(1 − "
                 "bear-to-bull spread %s ÷ 20 pp), longest horizon) + 0.2 × freshness %s (weights are this standard's "
                 "opinion, outlook.md) [%s, %s]. Tier cutoffs 70 / 45 are this standard's opinion (D-8) [%s]." % (
                     c["value"], c["coverage"], c.get("covered"), c.get("applicable"), c["agreement"],
                     c.get("outlook_spread_term"), pct(c.get("outlook_spread"), 1), c["freshness"], D, S, S))
                if c.get("outlook_spread") is not None else
                "%s/100 = 0.5 × coverage %s (%s of %s) + 0.3 × agreement %s + 0.2 × freshness %s (weights are this "
                "standard's opinion, valuation.md) [%s, %s]. Tier cutoffs 70 / 45 are this standard's opinion (D-8) [%s]." % (
                    c["value"], c["coverage"], c.get("covered"), c.get("applicable"), c["agreement"], c["freshness"], D, S, S)]
        return out  # the scorecard's open questions render once, in the merged ## Open questions

    def research(self, name):
        body = self.res.get(name)
        return body if body else ["- no evidence: research.md has no %s entries yet" % name.lower()]

    def open_questions(self):
        out = ["### From the scorecard"]
        out += ["- %s — %s%s" % (q["id"], esc(q["text"]), self.own(q.get("markers"))) for q in self.sc.get("open_questions") or []] \
            or ["- none"]
        out += ["", "### From facts.json"]
        for key, why in (("options", "options.py"), ("momentum", "momentum.py"), ("market", "market.py")):
            if not isinstance(self.f.get(key), dict):
                out.append("- %s: no evidence; would come from %s" % (key, why))
        for key in ("insiders", "consensus"):
            if self.f.get(key) is None:
                out.append("- %s: null by design in this version" % key)
        a0 = g(self.f, "fundamentals", "annual", 0) or {}
        for x in g(self.f, "fundamentals", "missing") or []:
            if x.get("fy") == a0.get("fy"):
                out.append("- FY%s %s: no evidence (%s); would come from edgar.py [%s]" % (
                    x["fy"], x["field"], x.get("reason", ""), self.F))
        out += ["", "### From research"] + ((self.res_oq + self.ind_oq) or ["- none"])
        return out

    def evidence_log(self):
        rows = {}
        for k, s in self.sources.items():
            rows[k] = "| %s | %s | %s | %s | %s | %s |" % (k, s.get("class"), esc(s.get("what", "")), s.get("url"),
                                                          s.get("as_of", ""), s.get("retrieved", ""))
        for line in self.res_log:
            k = re.match(r"^\|\s*(S\d+)", line).group(1)
            rows.setdefault(k, line)
        return ["| S | class | what | url | as-of | retrieved |", "|---|---|---|---|---|---|"] + \
            [rows[k] for k in sorted(rows, key=sid_num)]

    def industry_body(self):
        """industry.md verbatim minus its Open questions and Evidence log sections (merged elsewhere); the file's
        top title is dropped and `#`/`##` headings become `###` so the section nests under the dossier heading."""
        out, skip = [], False
        for line in (self.ind_text or "").splitlines():
            h = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
            if h and h.group(2).lower() in ("open questions", "evidence log"):
                skip = True
                continue
            if h and len(h.group(1)) <= 2:
                skip = False
                if len(h.group(1)) == 1:
                    continue
                line = "### " + h.group(2)
            elif h:
                skip = False
            if not skip:
                out.append(line)
        return trim(out)

    def industry_table(self):
        """Rows (cells) of the first Markdown table in industry.md, header and separator excluded."""
        rows, seen = [], False
        for line in self.industry_body():
            if line.strip().startswith("|"):
                seen = True
                if re.match(r"^\s*\|?\s*:?-{3,}", line):
                    continue
                rows.append([c.strip() for c in line.strip().strip("|").split("|")])
            elif seen:
                break
        return rows[1:] if len(rows) > 1 else []

    def related_groups(self):
        """Tickers grouped by link from the related-stocks table (a table with Ticker and Link columns)."""
        head, groups = None, {}
        for line in self.industry_body():
            if not line.strip().startswith("|"):
                head = None
                continue
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if re.match(r"^:?-{3,}", c[0]):
                continue
            low = [x.lower() for x in c]
            if head is None:
                head = (low.index("ticker"), low.index("link")) if "ticker" in low and "link" in low else False
                continue
            if head and len(c) > max(head):
                t = re.sub(r"\[S\d+.*?\]|[`*]", "", c[head[0]]).strip()
                link = re.sub(r"\[S\d+.*?\]", "", c[head[1]]).strip().lower()
                if t and link:
                    groups.setdefault(link if link.endswith("s") else link + "s", []).append(t)
        return groups

    def chain_sentence(self):
        """The first prose line of the chain-position part of industry.md (tables, bullets and headings skipped)."""
        lines, in_chain = self.industry_body(), False
        for line in lines:
            h = re.match(r"^#{1,6}\s+(.*)$", line)
            if h:
                in_chain = "chain" in h.group(1).lower() or "position" in h.group(1).lower()
                continue
            if in_chain and line.strip() and not line.strip().startswith(("|", "-", "*", ">")):
                return line.strip()
        return None

    def industry_line(self):
        groups = self.related_groups()
        if groups:
            line = SEP.join("%s %s" % (k, ", ".join(dict.fromkeys(v))) for k, v in groups.items())
            chain = self.chain_sentence()
            return line + (" — " + chain if chain and len(chain) < 200 else "")
        rows = self.industry_table()
        if not rows:
            return "not yet mapped"
        body_ids = re.findall(r"\[S\d+(?:\s*[,;]\s*S\d+)*\]", " ".join(self.industry_body()))
        parts = []
        for r in rows[:4]:
            text = " – ".join(c for c in r[:3] if c)
            row_ids = re.findall(r"\[S\d+(?:\s*[,;]\s*S\d+)*\]", " ".join(r))
            if not re.search(r"\[S\d+", text) and (row_ids or body_ids):
                text += " " + (row_ids or body_ids)[0]
            parts.append(text)
        return "; ".join(parts)

    def industry_chat(self, limit=6):
        lines = [l for l in self.industry_body() if l.strip() and not l.startswith("#")
                 and not re.match(r"^\s*\|?\s*:?-{3,}", l)]
        rows = [l for l in lines if l.strip().startswith(("|", "- "))]
        return (rows or lines)[:limit]

    FOLDER_MAP = (
        ("facts/facts.json", "fundamentals, prices, macro, market, options, momentum, derived metrics"),
        ("facts/series.json", "ten-year daily prices"),
        ("facts/scorecard.json", "gates, items, pillars, score, zones, action matrix, short-term lens"),
        ("facts/holdings.json", "stated positions"),
        ("facts/holdings_tables.json", "outcome and tax tables"),
        ("facts/peers.json", "side-by-side with peers (compare.py)"),
        ("facts/last_run.json", "incremental state"),
        ("filings", "the 10-K split into items, auditor's report, notes"),
        ("research/research.md", "cumulative cited research"),
        ("research/evidence.json", "verdicts for the evidence-required items"),
        ("research/industry.md", "industry chain position and related stocks"),
        ("history/log.md", "one line per question"),
        ("history/*.md", "the narrative written for each question"),
        ("reports/dossier.md", "the full report for the latest question"),
        ("reports/*.md", "dated dossier snapshots"),
        ("reports/*.html", "the answer as a web page"),
        ("charts/*.html", "the five panels alone"),
    )

    def folder_map(self):
        out = []
        for rel, what in self.FOLDER_MAP:
            if "*" in rel:
                skip = ("log.md",) if rel.startswith("history") else ("dossier.md", "dossier.html") if rel.startswith("reports/") else ()
                hits = [h for h in sorted(glob.glob(os.path.join(self.store, rel))) if os.path.basename(h) not in skip]
                path = os.path.relpath(hits[-1], self.store) if hits else None
                label = "%s (newest of %d)" % (rel, len(hits)) if len(hits) > 1 else rel
            else:
                path = rel if os.path.exists(os.path.join(self.store, rel)) else None
                label = rel
            out.append("- [`%s`](%s) — %s" % (label, path, what) if path else "- `%s` — %s (not yet written)" % (label, what))
        return out

    def history_rows(self, lines):
        """History table rows (newest first) from log.md-format lines."""
        rows = ["| Date | Question | Lens | Tier | Score | Stance | Confidence | Price | Said | Zones | Changed | |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for line in reversed(lines):
            p = parse_history(line)
            p["said"] = p.get("said", "") + ("; expected " + p["expected"] if p.get("expected") else "")
            cells = [esc(p.get(k, "")) for k in ("date", "question", "lens", "tier", "score", "stance", "confidence",
                                                 "price", "said", "zones", "changed")]
            rows.append("| %s | [%s] |" % (" | ".join(cells), self.H))
        return rows

    def index_md(self, hist_lines):
        f, sc = self.f, self.sc
        oq = len([q for q in sc.get("open_questions") or []]) + len(
            [l for l in self.res_oq + self.ind_oq if l.strip().startswith("-") and "none" not in l.lower()])
        out = ["# %s (%s) — index" % (f.get("name"), f.get("ticker")),
               "CIK `%s` · sector class %s · sector ETF %s" % (f.get("cik"), f.get("sector_class"), f.get("sector_etf") or "n/a"),
               "", "**Industry:** " + self.industry_line(), "",
               "## Latest decision", "Question: `%s` · lens %s" % (re.sub(r"\s+", " ", self.q.replace("`", "'")), self.lens),
               ""] + self.verdict() + [""] + self.action_lines()
        note = g(self.m, "calibration", "record_summary", "note")
        out += ["Track record: %s [%s]" % (note, self.D)] if note else []
        out += [""] + ["## Folder map"] + self.folder_map() + [""]
        out += ["## History"] + self.history_rows(hist_lines) + [""]
        out += ["Open questions: %d [%s]" % (oq, self.S), "",
                "Updated `%s UTC`" % self.when.strftime("%Y-%m-%d %H:%M"), "",
                "### Evidence log", "| S | class | what | url | as-of | retrieved |", "|---|---|---|---|---|---|",
                "| %s | derived | report.py run history, one line per analysis | %s | %s | %s |" % (
                    self.H, self.sources[self.H]["url"], self.date, self.date), ""]
        return "\n".join(out)

    def dossier(self, hist_line):
        out = self.header()
        out += ["## The short answer", self.headline()[3:] + mk([self.D, self.S]), ""] + self.short_answer() + [
            "", self.price_map(), self.strict_line(), "", "### Model cells and triggers"] + \
            self.verdict() + [""] + self.action_lines() + [""]
        ana = self.analyst_section()
        out += ["## Price outlook"] + (["### What the analyst expects, and why"] + ana + ["", "### Strict value lens"]
                                       if ana else []) + self.outlook() + [""]
        out += ["## Track record"] + self.track_record() + [""]
        out += ["## Answer", "**Question:** `%s` · lens: %s" % (self.q.replace("`", "'"), self.lens), ""] + \
            self.slot("Answer") + [""]
        out += ["## Thesis"] + self.thesis() + [""]
        out += ["## Why"] + self.why() + [""]
        out += ["## The case against"] + self.case_against() + [""]
        out += ["## What the news says"] + (self.news_table() or [
            "- no evidence: no news slot in the narrative and no dated news in research/research.md"]) + [""]
        peers = self.peers_table()
        out += ["## Compared with similar companies"] + (peers + [""] + [
            l for l in (self.narr or {}).get(PEERS_SLOT, []) if l.strip()] if peers else [
            "- no evidence: facts/peers.json not written yet (compare.py)"]) + [""]
        out += ["## How the industry is doing"] + (self.industry_plain() or [
            "- no evidence: no industry slot in the narrative and research/industry.md absent"]) + [""]
        s, w = self.strengths()
        out += ["## Strengths and weaknesses", "### Strengths"] + s + ["", "### Weaknesses"] + w + [""]
        if self.hold is not None:
            out += ["## Holdings"] + self.holdings() + [""]
        out += ["## Options context"] + self.options() + [""]
        st = self.short_term()
        if st:
            out += ["## Short-term lens"] + st + [""]
        for name in ("Business and moat", "Management"):
            out += ["## " + name] + self.research(name) + [""]
        out += ["## Market trend"] + self.research("Market trend") + ["", "Market block:"] + self.market() + [""]
        if self.ind_text and self.industry_body():
            out += ["## Industry and related stocks"] + self.industry_body() + [""]
        out += ["## Facts"] + self.facts_section() + [""]
        out += self.scorecard() + [""]
        for name in ("Risk evidence", "News and posts"):
            out += ["## " + name] + self.research(name) + [""]
        out += ["## What could not be verified"] + self.not_verified() + [""]
        out += ["## Open questions"] + self.open_questions() + [""]
        hist = [l + " [%s]" % self.H for l in reversed(self.history() + [hist_line])]
        out += ["## History"] + hist + [""]
        out += ["## Evidence log"] + self.evidence_log() + ["", "> " + DISCLAIMER, ""]
        return "\n".join(out)

    # -- forward outlook (skills/standard/rules/outlook.md), led by the answer; the strict value is one lens --
    def ol(self):
        o = self.sc.get("outlook")
        return o if isinstance(o, dict) and o.get("horizons") else None

    def rec(self):
        return g(self.sc, "action", "recommendation") or {}

    def ref(self):
        """The horizon the answer leads with (score.py outlook.reference; older scorecards: the longest)."""
        o = self.ol() or {}
        h = o.get("reference") or o.get("longest")
        return h if h in (o.get("horizons") or {}) else None

    def ol_marks(self):
        return [self.D, self.S]

    def cons(self):
        c = self.f.get("consensus")
        return c if isinstance(c, dict) and c.get("available") else None

    def headline(self):
        o = self.ol()
        if not o or not self.ref() or self.sc.get("gates_failed"):
            return self.headline_strict()
        h = o["horizons"][self.ref()]
        word = {"attractive": "attractive on fundamentals", "fair": "fairly priced on fundamentals",
                "expensive": "expensive on fundamentals"}.get(h.get("verdict"), "no verdict on fundamentals")
        trend = {"up": "rising trend", "down": "falling trend", "none": "no clear trend"}.get(self.rec().get("trend"),
                                                                                           "trend unknown")
        b, u, r = g(h, "bear", "cagr"), g(h, "bull", "cagr"), o.get("required_return")
        base = g(h, "base", "cagr")
        rel = ("above" if base >= r + 0.02 else "about" if base >= r - 0.02 else "below") if None not in (base, r) else "versus"
        return "## %s — %s, %s; expect roughly %s to %s a year over the %s, %s the %s the risk demands" % (
            self.f.get("ticker"), word, trend, pct(b, 0), pct(u, 0), self.dated(self.ref(), h.get("label")), rel, pct(r, 1))

    def short_answer(self):
        o, rec = self.ol(), self.rec()
        if not o or not self.ref():
            return self.short_answer_strict()
        sc, h, D, S = self.sc, o["horizons"][self.ref()], self.D, self.S
        rows = ["| Question | Answer |", "|---|---|",
                "| Where is the price likely to go? | %s: %s to %s (base %s), about %s a year expected vs %s required — %s "
                "[%s, %s] |" % (h.get("label"), money(g(h, "bear", "price")), money(g(h, "bull", "price")),
                                money(g(h, "base", "price")), pct(g(h, "base", "cagr"), 1), pct(o.get("required_return"), 1),
                                h.get("verdict") or "n/a", D, S)]
        rows.append("| Next few months? | %s |" % self.months_cell())
        why = ("base %s a year vs %s required, trend %s" % (pct(rec.get("expected_return"), 1),
                                                         pct(rec.get("required_return"), 1), rec.get("trend") or "unknown")
               if rec.get("basis") == "outlook" else rec.get("note") or "")
        held = g(sc, "action", "holding")
        sell = rec.get("holding") or "n/a"
        rows.append("| Should I sell? | %s%s — %s%s |" % (
            "" if held else "No position to sell; a holder's cell: ", sell, why, mk(rec.get("markers") or [S])))
        lv = rec.get("levels") or {}
        entries = SEP.join("%s %s" % (n, money(lv[k])) for k, n in (
            ("ma50", "50-day average"), ("ma200", "200-day average"), ("pullback_10pct", "10% below today"),
            ("strict_value", "strict value")) if lv.get(k) is not None)
        rows.append("| Should I buy? | %s%s%s |" % (rec.get("not_holding") or "n/a",
                                                   " — entry levels: " + entries if entries else "",
                                                   mk(rec.get("markers") or [S])))
        rows.append(self.short_answer_strict()[-1].replace("How confident is the model?", "How confident is the analyst?"))
        return rows

    def months_cell(self):
        m = g(self.ol(), "months") or {}
        rng, parts = m.get("range_1sd") or {}, []
        o = self.f.get("options") if isinstance(self.f.get("options"), dict) else {}
        if rng.get("low") is not None and rng.get("high") is not None:
            parts.append("likely range %s–%s by %s (one standard deviation)" % (money(rng["low"]), money(rng["high"]),
                                                                              rng.get("expiry") or "the horizon"))
        elif o.get("implied_move_abs") is not None and self.sc.get("price"):
            p, a = self.sc["price"], o["implied_move_abs"]
            parts.append("likely range %s–%s by %s (one standard deviation)" % (money(p - a), money(p + a),
                                                                              o.get("expiry_used")))
        else:
            parts.append("no options range available")
        tr = re.sub(r"^trend\s+|^no\s+trend$", lambda x: "" if x.group(0).startswith("trend") else "none",
                    str(m.get("trend") or self.rec().get("trend") or "unknown"))
        parts.append("trend %s" % tr)
        ev = [e for e in (m.get("events") or []) if isinstance(e, dict) and e.get("date")]
        ev = sorted(ev, key=lambda e: e["date"]) or [{"event": t["name"], "date": t["date"]} for t in
                                                     sorted(g(self.sc, "action", "time_triggers") or [],
                                                            key=lambda t: t["date"])]
        if ev:
            parts.append("next event %s (%s)" % (ev[0]["date"], ev[0].get("event")))
        return "; ".join(parts) + mk([self.D, self.S] + ([o.get("src")] if o.get("src") else []))

    def base_then(self):
        b = g(self.m, "calibration", "base_forecast_then")
        return b.get("cagr") if isinstance(b, dict) else b

    def calibration_line(self):
        c = self.m.get("calibration")
        if not isinstance(c, dict) or c.get("ratio_price_to_value") is None:
            return None
        ratio = c["ratio_price_to_value"]
        call = ("%.1f× overvalued" % ratio) if ratio >= 1 else ("%.0f%% undervalued" % ((1 - ratio) * 100))
        s = "in FY%s the strict model called it %s (price %s vs value %s); it returned %s a year since" % (
            c.get("fy_then"), call, money(c.get("price_then")), money(c.get("strict_value_then")),
            pct(c.get("realized_cagr_since"), 1))
        if self.base_then() is not None:
            s += "; the outlook's base case then would have said %s a year (error %s pp)" % (
                pct(self.base_then(), 1), "%+.1f" % c["error_pp"] if c.get("error_pp") is not None else "n/a")
        return s + " [%s]" % self.D

    def price_map(self):
        """Markers ordered by price, left to right; labels kept."""
        o = self.ol()
        if not o or not self.ref():
            return self.price_map_strict()
        lv, h = self.rec().get("levels") or {}, o["horizons"][self.ref()]
        pull = lv.get("ma50") if lv.get("ma50") is not None else lv.get("pullback_10pct")
        c = self.cons()
        pts = [(lv.get("strict_value"), "strict value"), (pull, "pullback"), (self.sc.get("price"), "today"),
               (g(c, "targets", "mean") if c else None, "consensus target"),
               (g(h, "bull", "price"), "bull %s" % h.get("label"))]
        pts = sorted(((v, "%s %s" % (lbl, money(v))) for v, lbl in pts if v is not None), key=lambda x: x[0])
        items = [t for _, t in pts]
        mid = " ── ".join(items[1:-1])
        line = items[0] if len(items) == 1 else "%s ◄── %s ──► %s" % (items[0], mid, items[-1]) if mid else \
            "%s ◄──► %s" % (items[0], items[-1])
        marks = [self.D, self.P] + ([c.get("src")] if c and c.get("src") else [])
        return "`%s`%s" % (line, mk(marks))

    def strict_line(self):
        cal = self.calibration_line()
        return "A strict value investor would pay %s [%s]%s" % (
            money((self.sc.get("zones") or {}).get("base_today")), self.D,
            "; the model's record on this stock: " + cal if cal else "; no calibration on record")

    def analyst_section(self):
        o = self.ol()
        if not o:
            return []
        D, P = self.D, self.P
        out = ["*computed by scripts*", "",
               "| Horizon | Bear | Base | Bull | Expected yearly return (base) | Verdict | |", "|---|---|---|---|---|---|---|"]
        for h, x in o["horizons"].items():
            out.append("| %s | %s | %s | %s | %s | %s | [%s, %s] |" % (
                x.get("label"), money(g(x, "bear", "price")), money(g(x, "base", "price")), money(g(x, "bull", "price")),
                pct(g(x, "base", "cagr"), 1), x.get("verdict") or "n/a", D, self.S))
        c = self.cons()
        if c:
            t = c.get("targets") or {}
            out.append("| Analyst consensus (%s analysts, secondary) | %s | %s | %s | — | — | [%s] |" % (
                t.get("count", "n/a"), money(t.get("low")), money(t.get("mean")), money(t.get("high")), c.get("src") or P))
        else:
            out.append("| Analyst consensus | not available | | | — | — | |")
        pa = o.get("params") or {}
        gi = g(pa, "g", "inputs") or {}
        hist = gi.get("eps_cagr_5y")
        two, one = gi.get("consensus_2y"), gi.get("consensus_next_year")   # the figure the blend used: 2-year first
        nxt, kind = (two, "two-year") if two is not None else (one, "next-year")
        src = " (%s)" % "; ".join(x for x in (
            "the company's 5-year record of %s" % pct(hist, 1) if hist is not None else None,
            "analysts' %s %s estimate" % (pct(nxt, 1), kind) if nxt is not None else None) if x) \
            if hist is not None or nxt is not None else ""
        cmark = [c.get("src")] if c and c.get("src") and nxt is not None else []
        mu = pa.get("multiple") or {}
        basis = {"pe": "P/E", "ps": "price-to-sales"}.get(mu.get("basis"), mu.get("basis") or "multiple")
        out += ["",
                "- Growth assumed: base %s a year%s%s" % (pct(g(pa, "g", "base"), 1), src, mk([D] + cmark)),
                "- Multiple assumed: today's %s %s drifting to the 10-year median %s (range %s–%s) [%s]" % (
                    basis, ratio1(mu.get("current")), ratio1(mu.get("median")), ratio1(mu.get("p25")),
                    ratio1(mu.get("p75")), D),
                "- Cash returned: %s a year in dividends and buybacks [%s]" % (pct(pa.get("shareholder_yield"), 1), D),
                "- The market's own assumption: today's price implies %s growth for ten years [%s]" % (
                    pct(self.val.get("implied_growth_at_price"), 1), D)]
        if o.get("method_note"):
            out.append("- Method: %s [%s]" % (o["method_note"], D))
        return out

    def strict_lens(self):
        z, out = self.sc.get("zones") or {}, self.outlook()
        out += ["", "Buy zone below %s, base fair value %s, sell zone above %s; implied growth at today's price %s "
                "[%s]." % (money(z.get("buy_below")), money(z.get("base_today")), money(z.get("sell_above")),
                           pct(self.val.get("implied_growth_at_price")), self.D)]
        c = self.m.get("calibration")
        if isinstance(c, dict):
            out += ["", "Calibration: FY%s price %s, strict value then %s, ratio %s, realised %s a year since, base "
                    "forecast then %s, error %s pp [%s]." % (
                        c.get("fy_then"), money(c.get("price_then")), money(c.get("strict_value_then")),
                        c.get("ratio_price_to_value"), pct(c.get("realized_cagr_since"), 1),
                        pct(self.base_then(), 1), ratio1(c.get("error_pp")), self.D)]
            if c.get("note"):
                out.append("- %s [%s]" % (c["note"], self.D))
        return out

    # -- beginner chat answer (report-template.md "Chat answer — written for a beginner") --
    def zone_money(self, key):
        return money((self.sc.get("zones") or {}).get(key))

    def headline_strict(self):
        sc, z, p = self.sc, self.sc.get("zones") or {}, self.sc.get("price")
        band = g(sc, "action", "band")
        if sc.get("gates_failed"):
            s = "a deal-breaker check failed, so the model says stay away whatever the price"
        elif band == "above sell zone":
            far = p and z.get("base_today") and p >= 1.5 * z["base_today"]
            s = "the price is %sabove what the model thinks a share is worth" % ("far " if far else "")
        elif band == "base value to sell zone":
            s = "the price is above what the model thinks a share is worth, but not yet in the sell zone"
        elif band == "buy zone to base value":
            s = "the price is below what the model thinks a share is worth, but not yet cheap enough to buy"
        elif band == "below buy zone":
            s = "the price is in the model's buy zone, well below what it thinks a share is worth"
        else:
            s = "the model could not put a fair value on this stock, so it gives no price signal"
        return "## %s — %s" % (self.f.get("ticker"), s)

    def short_answer_strict(self):
        sc, a = self.sc, self.sc.get("action") or {}
        cells, z, P, D, S = a.get("cells") or {}, sc.get("zones") or {}, self.P, self.D, self.S
        failed, band, held = sc.get("gates_failed"), a.get("band"), a.get("holding")
        hc = cells.get("holding")
        if not held:
            sell = "No position to sell"
        elif hc == "exit":
            sell = "Yes — sell: a deal-breaker check failed"
        elif hc == "trim or sell":
            sell = "Yes — trim or sell"
        elif hc in ("hold", "hold, do not add"):
            sell = "Not yet — hold"
        else:
            sell = "No — the model would %s" % hc
        times = a.get("time_triggers") or []
        recheck = " and ".join("%s (%s)" % (t["date"], t["name"]) for t in times if t["name"] in ("next 10-K", "next earnings"))
        tmarks = [m for t in times for m in t.get("markers") or []]
        if held and hc in ("trim or sell", "exit"):
            when = "now"
        elif held:
            when = "when the price crosses %s (the sell zone)" % money(z.get("sell_above"))
        elif failed:
            when = "not while a deal-breaker check fails"
        else:
            when = "when the price falls below %s (the buy zone)" % money(z.get("buy_below"))
        when += "; re-check on %s" % recheck if recheck else ""
        if failed:
            buy = "No — a deal-breaker check failed"
        elif band == "below buy zone":
            buy = "Yes — below %s it is in the buy zone" % money(z.get("buy_below"))
        else:
            buy = "No — wait for %s or below" % money(z.get("buy_below"))
        c = sc.get("confidence") or {}
        wts = c.get("weights") or {"coverage": 0.5, "agreement": 0.3, "freshness": 0.2}
        terms = {"coverage": c.get("coverage"), "agreement": c.get("agreement"), "freshness": c.get("freshness"),
                 "outlook_spread": c.get("outlook_spread_term")}
        short = {k: w * (1 - (terms.get(k) or 0)) for k, w in wts.items()}
        low = max(short, key=short.get)
        lowers = {"coverage": "some checks lack evidence (%s of %s covered)" % (c.get("covered", "n/a"), c.get("applicable", "n/a")),
                  "agreement": "its strict bear and bull values are far apart, so the fair value is uncertain",
                  "outlook_spread": "the bear and bull scenarios are far apart (%s a year between them)"
                                    % pct(c.get("outlook_spread"), 0),
                  "freshness": "the prices or filings it used are not the latest"}[low]
        return ["| Question | Answer |", "|---|---|",
                "| Should I sell? | %s (model stance: %s) [%s] |" % (sell, sc.get("stance"), S),
                "| When? | %s%s |" % (when, mk(([D] if "$" in when else []) + tmarks + [S])),
                "| At what price? | sell zone starts at %s; buy zone ends at %s; today %s [%s, %s] |" % (
                    money(z.get("sell_above")), money(z.get("buy_below")), money(sc.get("price")), D, P),
                "| Should I buy? | %s [%s, %s] |" % (buy, D, S),
                "| How confident is the model? | %s/100%s — what lowers it: %s [%s] |" % (
                    c.get("value"), " (%s)" % band_word(c.get("value")) if band_word(c.get("value")) else "", lowers, S)]

    def price_map_strict(self):
        z = self.sc.get("zones") or {}
        return "`buy zone ◄── %s ──── %s fair ──── %s ──► sell zone      ▲ you are here %s`%s" % (
            money(z.get("buy_below")), money(z.get("base_today")), money(z.get("sell_above")),
            money(self.sc.get("price")), mk([self.D, self.P]))

    def why_plain(self):
        lines = [l for l in (self.narr or {}).get("Why", []) if l.startswith("- ")]
        if lines:
            return [plain(l) for l in lines[:5]]
        return ["- %s (%s): %s/20 [%s]" % (PILLAR_PLAIN[p].capitalize(), PILLAR_NAMES[p].lower(), "%g" % x["points"],
                                          self.S) for p, x in sorted(self.sc["pillars"].items())]

    # -- proof sections: the record, the case against, what is missing (always shown) --
    def track_record(self):
        """The simulated per-year record (metrics.calibration.record) and what this advisor said in earlier runs."""
        D, rec = self.D, g(self.m, "calibration", "record") or []
        out = ["*computed by scripts; simulated with today's method on the data then available*"]
        if rec:
            out += ["", "| Years ago | FY | Price then | Strict value then | Base case said (per year) | What happened "
                    "(per year) | SPY same window (per year) | |", "|---|---|---|---|---|---|---|---|"]
            for e in sorted(rec, key=lambda e: e.get("years_back") or 0):
                out.append("| %s | %s | %s | %s | %s | %s | %s | [%s] |" % (
                    e.get("years_back"), e.get("fy_then"), money(e.get("price_then")), money(e.get("strict_value_then")),
                    pct(e.get("base_forecast_cagr"), 1), pct(e.get("realized_cagr_since"), 1),
                    pct(e.get("spy_cagr_same_window"), 1), D))
            bases = sorted({(e.get("realized_basis") or "").split(" (")[0] for e in rec if e.get("realized_basis")})
            out += ["", "What happened = %s; SPY from market/SPY.json over the same dates [%s]" % (
                " or ".join(bases) or "n/a", D)]
            note = g(self.m, "calibration", "record_summary", "note")
            if note:
                out.append("%s [%s]" % (note, D))
        said = self.said_before()
        if said:
            out += ["", "**What this advisor said before about %s**" % self.f.get("ticker"), ""] + said
        if not rec and not said:
            return ["No past calls yet; the simulated record needs at least three fiscal years of data [%s]." % D]
        return out

    def said_before(self, limit=8):
        """One row per earlier run date (that day's last log line): what was said, price then and now, SPY since."""
        by_date = {}
        for line in self.prior_history():
            p = parse_history(line)
            if p.get("date"):
                by_date[p["date"]] = p
        if not by_date:
            return []
        now, pdate = num(self.sc.get("price")), g(self.f, "price", "date") or self.date
        rows = ["| Date | Said | Price then | Price now (change) | SPY same window | |", "|---|---|---|---|---|---|"]
        for d in sorted(by_date, reverse=True)[:limit]:
            p = by_date[d]
            said = p.get("said") or p.get("stance") or "n/a"
            said += "; expected " + p["expected"] if p.get("expected") else ""
            then = unmoney(p.get("price"))
            chg = spct(now / then - 1) if then and now else "n/a"
            rows.append("| %s | %s | %s | %s (%s) | %s | [%s] |" % (
                d, esc(said), p.get("price") or "n/a", money(now), chg, spct(self.spy_change(d, pdate)), self.H))
        return rows

    def not_verified(self):
        """Inputs the standard asks for that this run did not have: items, gates, null metrics, stale prices, and
        the narrative's own `## Not verified` lines."""
        D, S, out = self.D, self.S, []
        it = self.sc.get("items") or {}
        for i in sorted(it):
            x = it[i]
            if x.get("status") in ("no evidence", "pending"):
                out.append("- Item %s (%s): %s%s [%s]" % (i, x.get("test") or TESTS.get(i, ""), x["status"],
                                                          " — " + esc(x["note"]) if x.get("note") else "", S))
        gates = self.sc.get("gates") or {}
        for gid in sorted(gates):
            x = gates[gid]
            if x.get("result") in ("pending", "no evidence"):
                out.append("- Gate %s (%s): %s%s [%s]" % (gid, GATE_NAMES.get(gid, ""), x["result"],
                                                          " — " + esc(x["note"]) if x.get("note") else "", S))
        nulls = [(k, v) for k, v in self.m.items() if isinstance(v, dict) and v.get("reason") and k != "freshness"
                 and (("value" in v and v["value"] is None) or ("available" in v and v["available"] is None))]
        out += ["- %s: %s [%s]" % (k.replace("_", " "), esc(v["reason"]), D) for k, v in nulls[:8]]
        if len(nulls) > 8:
            out.append("- and %d more metrics without a value this run (see Facts) [%s]" % (len(nulls) - 8, D))
        fr, pdate = self.m.get("freshness") or {}, g(self.f, "price", "date")
        age = max(num(fr.get("price_age_trading_days")) or 0, weekdays_between(pdate, self.date) or 0)
        if age > 1:
            out.append("- Price is stale: the last price is dated %s, %d trading days before this run [%s]" % (pdate, age, D))
        if fr.get("newer_10k_exists"):
            out.append("- A newer 10-K has been filed than the one these figures come from [%s]" % D)
        if fr.get("value") is None and fr.get("reason"):
            out.append("- Freshness could not be judged: %s [%s]" % (esc(fr["reason"]), D))
        out += [l for l in (self.narr or {}).get("Not verified", []) if l.strip()]
        return ["*computed by scripts*", ""] + (out or ["Every input the standard asks for was available this run [%s]." % S])

    def case_against(self):
        lines = [l for l in (self.narr or {}).get("Case against", []) if l.strip()]
        return ["*the analyst's reading of the numbers above*", ""] + (lines or [
            "The analyst's note has no case-against section; ask for a refreshed analysis [%s]." % self.H])

    def news_rows(self):
        """(date, what, meaning) rows: the narrative slot first, else the five newest research news items."""
        body = [l for l in (self.narr or {}).get(NEWS_SLOT, []) if l.strip()]
        rows = []
        for l in body:
            if l.strip().startswith("|"):
                c = [x.strip() for x in l.strip().strip("|").split("|")]
                if re.match(r"^:?-{3,}", c[0]) or c[0].lower() == "date":
                    continue
                rows.append((c + ["", "", ""])[:3])
            elif l.startswith("- "):
                parts = [x.strip() for x in l[2:].split(" — ", 2)]
                rows.append((parts + ["", "—", "—"])[:3] if len(parts) > 1 else ["", parts[0], "—"])
        if rows:
            return rows
        items = []
        for l in self.res.get("News and posts") or []:
            p = [x.strip() for x in l[2:].split(SEP)] if l.startswith("- ") else []
            if len(p) >= 4 and re.match(r"\d{4}-\d{2}-\d{2}", p[1]):
                items.append((p[1][:10], [p[1], "%s: %s" % (p[2], SEP.join(p[3:])), "—"]))
        return [r for _, r in sorted(items, key=lambda x: x[0], reverse=True)[:5]]

    def news_table(self):
        rows = self.news_rows()
        if not rows:
            return []
        return ["| Date | What happened | What it means for this stock |", "|---|---|---|"] + [
            "| %s | %s | %s |" % tuple(esc(c) for c in r) for r in rows]

    def peers(self):
        p = read_json(os.path.join(self.st.facts_dir, "peers.json"))
        return p if isinstance(p, dict) and p.get("rows") else None

    def peers_table(self):
        """compare.py's table: `columns` per ticker ({ticker, src, rows: {key: {value}}}) or rows with `values`."""
        p = self.peers()
        if not p:
            return []
        rows, cols, gone = p["rows"], [], []
        if isinstance(p.get("columns"), list):
            for c in p["columns"]:
                if isinstance(c.get("rows"), dict):
                    cols.append((c.get("ticker"), {k: (v or {}).get("value") if isinstance(v, dict) else v
                                                   for k, v in c["rows"].items()}, c.get("src")))
                else:
                    gone.append("%s (%s)" % (c.get("ticker"), c.get("reason") or c.get("status") or "no data"))
        else:
            tick = [p.get("ticker") or self.f.get("ticker")] + [t for t in p.get("peers") or [] if t != p.get("ticker")]
            cols = [(t, {r.get("key"): (r.get("values") or {}).get(t) for r in rows}, None) for t in tick]
        if not cols:
            return []
        ids = sorted({c[2] for c in cols if c[2]} or set((p.get("sources") or {}).keys()), key=sid_num)
        out = ["| | %s | |" % " | ".join(c[0] for c in cols), "|---|%s---|" % ("---|" * len(cols))]
        for r in rows:
            k = r.get("key", "")
            marks = r.get("markers") or ([r["src"]] if r.get("src") else ids)
            out.append("| %s | %s |%s |" % (esc(PEER_LABELS.get(k, r.get("label") or k)),
                                           " | ".join(peer_fmt(k, c[1].get(k)) for c in cols), mk(marks)))
        if gone:
            out += ["", "Not compared: %s." % "; ".join(gone)]
        return out

    def industry_plain(self):
        lines = [l for l in (self.narr or {}).get(INDUSTRY_SLOT, []) if l.startswith("- ")]
        if lines:
            return [plain(l) for l in lines]
        if not self.ind_text:
            return []
        bullets = [l for l in self.industry_body() if l.startswith("- ")][:4]
        if bullets:
            return bullets
        return ["- %s" % " — ".join(c for c in r if c) for r in self.industry_table()[:4]]

    def your_shares(self):
        t, P = self.tables, self.P
        if self.hold is None:
            return []
        head = ["| Account | Shares | You paid | Worth now | Gain | Tax if sold now | You keep | |",
                "|---|---|---|---|---|---|---|---|"]
        if not isinstance(t, dict):
            rows = [("| %s | %s | %s | %s | %s | pending (holdings.py not run) | — | [%s, %s] |" % (
                ACCOUNTS.get(r.get("account"), r.get("account")), qty(r.get("shares")), money(r.get("avg_cost")),
                usd0(r.get("value")), signed0(r.get("gain")), P, self.S)) for r in g(self.sc, "action", "holdings") or []]
            return head + rows
        hid = next((k for k, v in (t.get("sources") or {}).items() if isinstance(v, dict) and v.get("class") == "derived"),
                   self.S)
        rate = t.get("marginal_rate")
        tax = {x.get("account"): x for x in t.get("tax") or []}

        def point(acct, label):
            return next((p for p in g(tax, acct, "points") or [] if p.get("label") == label), {})

        def tax_cells(acct, label, worth):
            tp = point(acct, label)
            est, keep = tp.get("estimated_tax_cad"), tp.get("after_tax_proceeds_cad")
            if est is None:
                return "no evidence", "no evidence"
            if est == 0:
                return "$0", usd0(worth)
            return ("≈ CAD %s%s" % (format(round(est), ","), " at %s" % pct(rate, 0) if rate is not None else ""),
                    "≈ CAD %s" % format(round(keep), ",") if keep is not None else "no evidence")

        rows, named = [], {}
        wanted = list(self.what_if)
        for o in t.get("outcomes") or []:
            a = o.get("account")
            cur = next((p for p in o.get("price_points") or [] if p.get("label") == "current"), {})
            tx, keep = tax_cells(a, "current", cur.get("value"))
            src = g(tax, a, "src")
            rows.append("| %s | %s | %s | %s | %s | %s | %s |%s |" % (
                ACCOUNTS.get(a, a), qty(o.get("shares")), money(o.get("avg_cost")), usd0(cur.get("value")),
                signed0(cur.get("gain_abs")), tx, keep, mk([P, hid] + ([src] if src in self.sources else []))))
            pts = [p for p in o.get("price_points") or [] if str(p.get("label", "")).startswith("named")]
            have = {p.get("price") for p in pts}
            sh, cost = num(o.get("shares")), num(o.get("cost_total"))
            for w in wanted:                       # a what-if price holdings.py did not evaluate: value and gain only
                if w not in have and sh is not None:
                    pts.append({"label": "what if %s" % money(w), "price": w, "value": sh * w,
                                "gain_abs": sh * w - cost if cost is not None else None})
            for p in pts:
                tx, keep = tax_cells(a, p["label"], p.get("value"))
                if not point(a, p["label"]):
                    tx, keep = "not computed (holdings.py)", "—"
                rows.append("| %s, if it hits %s | %s | %s | %s | %s | %s | %s |%s |" % (
                    ACCOUNTS.get(a, a), money(p.get("price")), qty(o.get("shares")), money(o.get("avg_cost")),
                    usd0(p.get("value")), signed0(p.get("gain_abs")), tx, keep, mk([hid])))
                est = point(a, p["label"]).get("estimated_tax_cad")
                named.setdefault(p.get("price"), []).append("%s %s%s" % (
                    ACCOUNTS.get(a, a), signed0(p.get("gain_abs")),
                    ", tax ≈ CAD %s" % format(round(est), ",") if est else ""))
        at = ["if it hits %s: %s%s" % (money(price), "; ".join(parts), mk([hid])) for price, parts in named.items()]
        return head + rows + ([""] + at if at else [])

    def could_change(self):
        thesis = (self.narr or {}).get("Thesis", [])
        line = next((l for l in thesis if "would break it" in l.lower()), None)
        if line:
            text = re.split(r"\*\*\s*[—:-]\s*|—", line, maxsplit=1)[-1].strip()
            parts = [x.strip().rstrip(".") for x in text.split(";") if x.strip()]
            if parts:
                return ["- %s" % plain(x) for x in parts[:3]]
        a, z = self.sc.get("action") or {}, self.sc.get("zones") or {}
        out = ["- The price falls below %s (buy zone) or the model's value moves: it is recomputed after each filing [%s]"
               % (money(z.get("buy_below")), self.D)]
        rows = [r for r in a.get("rows") or [] if r.get("base") is not None]
        if rows:
            r = rows[-1]
            out.append("- Within %s: the model's base value reaches %s; the price would have to come down to about that "
                       "for the share to look fair [%s, %s]" % (r.get("label") or horizon_label(r["horizon"]),
                                                                money(r["base"]), self.D, self.S))
        out += ["- %s on %s: the model re-checks its deal-breaker tests%s" % (
            t["name"][:1].upper() + t["name"][1:], t["date"], self.own(t.get("markers")))
            for t in (a.get("time_triggers") or [])[:1]]
        return out[:3]

    def if_hits(self):
        """One line per what-if price: which side of the zones it falls on."""
        z, out = self.sc.get("zones") or {}, []
        for p in self.what_if:
            b, s_, base = z.get("buy_below"), z.get("sell_above"), z.get("base_today")
            if None in (b, s_, base):
                where = "the model has no zones to compare it with"
            elif p >= s_:
                where = "in the sell zone (it starts at %s): the model would say trim or sell, and not buy" % money(s_)
            elif p >= base:
                where = "between fair value %s and the sell zone %s: hold, do not add" % (money(base), money(s_))
            elif p >= b:
                where = "below fair value %s but above the buy zone %s: hold, wait to buy" % (money(base), money(b))
            else:
                where = "in the buy zone (below %s): the model would say buy or add" % money(b)
            out.append("- If it hits %s: %s [%s]" % (money(p), where, self.D))
        return out

    def options_plain(self):
        ops = g(self.sc, "action", "options")
        if not ops:
            return ["Not now: options were not evaluated in this scorecard (re-run score.py) [%s]." % self.S]
        rows = [o for o in ops if o.get("op") != "not now" and o.get("contract")]
        if not rows:
            o = ops[0]
            return ["Not now: %s%s." % (o.get("fits_because"), self.own(o.get("markers")))]
        out = ["| Operation | When it fits | Contract | You pay / receive | Best case | Worst case |",
               "|---|---|---|---|---|---|"]
        for o in rows:
            c = o["contract"]
            side = "sell" if str(o.get("pay_or_receive", "")).startswith("receive") else "buy"
            out.append("| %s | %s | %s 1 %s per 100 sh, strike %s, expires %s | %s%s | %s | %s |" % (
                esc(re.sub(r"^O\d\s+", "", o["op"])), esc(o.get("fits_because")), side, c.get("type"),
                money(c.get("strike")), c.get("expiry"), esc(o.get("pay_or_receive")), self.own(o.get("markers")),
                esc(o.get("best_case")), esc(o.get("worst_case"))))
        return out

    def short_view(self):
        st = self.sc.get("short_term")
        if not st:
            return []
        word = {"trend up": "The price has been rising lately (above its 50-day and 200-day averages)",
                "trend down": "The price has been falling lately (below its 50-day and 200-day averages)"}.get(
            st.get("stance"), "The price has shown no clear direction lately")
        o = self.f.get("options") if isinstance(self.f.get("options"), dict) else {}
        bits = [word]
        if o.get("implied_move_abs") is not None:
            bits.append("implied move to %s: ± %s" % (o.get("expiry_used"), money(o["implied_move_abs"])))
        ev = g(st, "items", "ST6", "value")
        if isinstance(ev, list):
            nxt = sorted((e for e in ev if e.get("date", "") >= self.date), key=lambda e: e["date"])
            if nxt:
                bits.append("next event: %s on %s" % (nxt[0]["event"], nxt[0]["date"]))
        return ["- %s%s" % (SEP.join(bits), mk([self.S, self.P] + ([o.get("src")] if o.get("src") else []))),
                "- Caution: short-term signals describe the recent past; they do not override the answer above."]

    def details(self, s, w):
        a = self.sc.get("action") or {}
        hold = ["- %s: %s shares at %s cost, value %s, gain %s at today's price%s [%s, %s]" % (
            r.get("account"), qty(r.get("shares")), money(r.get("avg_cost")), money(r.get("value")), money(r.get("gain")),
            "; " + r["sell_line"] if r.get("sell_line") else "", self.P, self.S) for r in a.get("holdings") or []]
        ind = self.industry_chat() if self.ind_text else []
        oq = ["- %s — %s%s" % (q["id"], esc(q["text"]), self.own(q.get("markers")))
              for q in (self.sc.get("open_questions") or [])[:3]] or ["- none"]
        st = self.short_term()
        return [("1. Strict value lens", self.strict_lens()),
                ("2. Action matrix", self.action_lines() + ([""] + hold if hold else [])),
                ("3. Strengths / weaknesses", ["**Strengths**"] + s + ["", "**Weaknesses**"] + w),
                ("4. Industry and peers", ind or ["- not yet mapped (research/industry.md absent)"]),
                ("5. Options context", self.options() + [""] + self.contracts_considered()),
                ("6. Short-term lens", st or ["- not computed (%s)" % self.sc.get("short_term_reason", "lens long")]),
                ("7. Open questions", oq)]

    def contracts_considered(self):
        cs = [c for c in (g(self.f, "options", "contracts") or []) if isinstance(c, dict)]
        if not cs:
            return ["- contracts considered: none in facts.json"]
        s = g(self.f, "options", "src") or self.P
        out = ["| Anchor | Type | Strike | Expiry | Days | Mid | Open interest | IV | |", "|---|---|---|---|---|---|---|---|---|"]
        out += ["| %s | %s | %s | %s | %s | %s | %s | %s | [%s] |" % (
            c.get("anchor"), c.get("type"), money(c.get("strike")), c.get("expiry"), c.get("days"), money(c.get("mid")),
            c.get("oi"), pct(c.get("iv")), s) for c in cs]
        return out

    def chat(self, paths, page=None, full=False):
        """The beginner answer. Unless `full` (the page), sections request.json `wants` leaves out are dropped."""
        s, w = self.strengths()
        want = (lambda k: True) if full or self.wants is None else (lambda k: k in self.wants)
        sec = [("The short answer", self.short_answer())]
        if want("price") or self.what_if:
            sec.append(("Price map", [self.price_map(), self.strict_line()] +
                        ([""] + self.if_hits() if self.what_if else [])))
        if self.ol() and want("price"):
            sec.append(("What the analyst expects, and why", self.analyst_section()))
        sec.append(("The case against", self.case_against()))
        sec.append(("Why, in plain words", ["*the analyst's reading*", ""] + self.why_plain()))
        sec.append(("Track record", self.track_record()))
        news, peers, ind = self.news_table(), self.peers_table(), self.industry_plain()
        if news and want("news"):
            sec.append(("What the news says", ["*the analyst's reading*", ""] + news))
        if peers and want("peers"):
            slot = [l for l in (self.narr or {}).get(PEERS_SLOT, []) if l.strip()]
            sec.append(("Compared with similar companies", peers + ([""] + slot if slot else [])))
        if ind and want("industry"):
            sec.append(("How the industry is doing", ind))
        mine = self.your_shares()
        if mine and want("holdings"):
            sec.append(("Your shares", mine))
        sec.append(("What could change the answer", self.could_change()))
        sec.append(("What could not be verified", self.not_verified()))
        if want("options"):
            sec.append(("Options, explained with your numbers", self.options_plain() + [
                "- Options can lose the whole premium; selling a call caps your gain; shares can be called away early. "
                "This shows how the pieces work on this stock, not a recommendation."]))
        sv = self.short_view()
        if sv and want("short_term"):
            sec.append(("Short-term view", sv))
        above = "\n".join([self.headline()] + [l for _, b in sec for l in b])
        sec.append(("Words used here", ["- **%s** — %s" % (t, d) for t, rx, d in GLOSS if re.search(rx, above, re.I)]))
        files = [("page", page)] if page else []
        files.append(("dossier", paths[0]))
        charts = sorted(glob.glob(os.path.join(self.store, "charts", "*.html")))
        if charts:
            files.append(("chart", charts[-1]))
        out = [self.headline(), ""]
        for t, b in sec:
            out += ["### " + t] + b + [""]
        out += ["Files: " + SEP.join("[%s](file://%s)" % (n, os.path.abspath(p)) for n, p in files), "",
                "> " + DISCLAIMER, "", "---", "## Details", ""]
        for t, b in self.details(s, w):
            out += ["### " + t] + b + [""]
        return "\n".join(out)

    # ---------- the brief: the short report the user reads (advisor/references/answer.md) ----------
    def price_date(self):
        return g(self.f, "price", "date") or self.sc.get("as_of") or self.date

    def end_month(self, h):
        """Calendar month h years after the price date: 'Nov 2031'."""
        try:
            d = datetime.date.fromisoformat(str(self.price_date())[:10])
        except ValueError:
            return "n/a"
        months = int(round(float(h) * 12))
        y, m = divmod(d.month - 1 + months, 12)
        return datetime.date(d.year + y, m + 1, 1).strftime("%b %Y")

    def dated(self, h, label=None):
        """'5 years from today (to Nov 2031)' so a horizon is never read as a past span."""
        return "%s from today (to %s)" % (label or horizon_label(h), self.end_month(h))

    def source_url(self, sid):
        s = self.sources.get(sid) or {}
        if s.get("url"):
            return s["url"]
        row = next((l for l in self.res_log if re.match(r"^\|\s*%s\s*\|" % sid, l)), None)
        if row:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) > 3 and cells[3]:
                return cells[3]
        return None

    def link(self, sid):
        url = self.source_url(sid)
        return "[%s](%s)" % (sid, url) if url else "[%s]" % sid

    def linkify(self, text):
        """[S3] and [S60, S61] become links to the source row's URL (a filing, an API call, an article, or the
        local file a script computed into), so a reader jumps from a figure to its raw source."""
        return re.sub(r"\[(S\d+(?:,\s*S\d+)*)\](?!\()",
                      lambda m: ", ".join(self.link(x.strip()) for x in m.group(1).split(",")), text)

    def used_ids(self, text):
        return sorted({x for grp in re.findall(r"\[(S\d+(?:,\s*S\d+)*)\](?!\()", text)
                       for x in re.split(r",\s*", grp)}, key=sid_num)

    def sources_lines(self, text):
        """One line per source cited in the text; a derived row (a script's arithmetic) is followed by the raw
        sources named in its `what`, so the reader can jump from a computed figure to the filing or API behind it."""
        out, ids, seen = [], list(self.used_ids(text)), set()
        for sid in ids:
            s = self.sources.get(sid) or {}
            if s.get("class") == "derived":
                ids += [x for x in re.findall(r"\bS\d+\b", str(s.get("what", ""))) if x not in ids]
        for sid in sorted(set(ids), key=sid_num):
            s = self.sources.get(sid) or {}
            what, cls = s.get("what"), s.get("class")
            if not s:
                row = next((l for l in self.res_log if re.match(r"^\|\s*%s\s*\|" % sid, l)), None)
                if row:
                    cells = [c.strip() for c in row.strip().strip("|").split("|")]
                    cls, what = (cells + ["", ""])[1], (cells + ["", "", ""])[2]
            url = self.source_url(sid)
            if cls == "derived":
                out.append("- %s — %s (a script's arithmetic; its inputs are the sources above): %s" % (
                    sid, esc(what or "derived"), "<%s>" % url if url else "no file"))
            else:
                out.append("- %s — %s%s: %s" % (sid, esc(what or "source"), " (%s)" % cls if cls else "",
                                                "<%s>" % url if url else "no URL"))
        return out

    def rec_reason(self):
        rec, r = self.rec(), self.ref()
        if rec.get("basis") != "outlook" or rec.get("expected_return") is None:
            return rec.get("note") or ""
        h = g(self.ol(), "horizons", r) or {}
        return "the expected return of about %s a year over the %s %s the %s the risk demands, and the trend is %s" % (
            pct(rec.get("expected_return"), 1), self.dated(r, h.get("label")),
            {"above": "beats", "within": "is about", "below": "is below"}.get(rec.get("band"), "versus"),
            pct(rec.get("required_return"), 1), rec.get("trend") or "unknown")

    def levels_line(self):
        lv = (self.rec().get("levels") or {})
        names = (("ma50", "50-day average"), ("pullback_10pct", "10% below today"), ("ma200", "200-day average"),
                 ("strict_value", "a strict value investor's price"))
        parts = ["%s (%s)" % (money(lv[k]), n) for k, n in names if lv.get(k) is not None]
        return SEP.join(parts)

    def answer_lines(self):
        """The direct answer: what to do if you hold it, what to do if you want to buy, the limit-order levels."""
        sc, rec, S = self.sc, self.rec(), self.S
        marks = mk(rec.get("markers") or [S])
        if sc.get("gates_failed"):
            return ["- **Stay away, or sell what you hold** — a deal-breaker check failed (%s); nothing else in this "
                    "report softens that%s" % (", ".join(sc["gates_failed"]), mk([S]))]
        if not rec.get("holding") and not rec.get("not_holding"):
            return ["- **No verdict** — %s; this report does not fill the gap with a default hold%s" % (
                esc(rec.get("note") or "the scripts could not compute an expected return"), mk([S]))]
        if rec.get("basis") != "outlook" or rec.get("expected_return") is None:
            z = self.sc.get("zones") or {}
            why = "the outlook could not be computed (%s), so the strict value rule decides: fair value %s, buy below %s, " \
                  "sell above %s" % (esc(rec.get("note") or "inputs missing"), money(z.get("base_today")),
                                     money(z.get("buy_below")), money(z.get("sell_above")))
        else:
            why = self.rec_reason()
        out = ["- **If you hold it:** %s — because %s%s" % (rec.get("holding") or "n/a", why, marks),
               "- **If you want to buy:** %s%s" % (rec.get("not_holding") or "n/a", marks)]
        lv = self.levels_line()
        if lv:
            out.append("- **Limit-order levels the rule points to:** %s%s" % (lv, marks))
        return out + self.if_hits()

    def summary_rows(self):
        """Six to eight rows of the figures the answer rests on, each dated and linked."""
        sc, o, r, D, S, P = self.sc, self.ol(), self.ref(), self.D, self.S, self.P
        rows = ["| | |", "|---|---|", "| Price today (%s) | %s [%s] |" % (self.price_date(), money(sc.get("price")), P)]
        if o and r:
            h = o["horizons"][r]
            rows.append("| Expected by %s (%s) | worst %s · likely %s · best %s — about %s a year in the likely case [%s, %s] |" % (
                self.end_month(r), "%s from today" % h.get("label"), money(g(h, "bear", "price")),
                money(g(h, "base", "price")), money(g(h, "bull", "price")), pct(g(h, "base", "cagr"), 1), D, S))
            rows.append("| Return the risk demands | %s a year (10-year Treasury yield plus an equity risk premium) [%s] |" % (
                pct(o.get("required_return"), 1), D))
        rows.append("| Next few months | %s |" % self.months_cell())
        c = self.cons()
        if c and g(c, "targets", "mean") is not None:
            rows.append("| Analysts' average 12-month target (secondary; only about 38%% of such targets are met) | %s from %s analysts [%s] |" % (
                money(g(c, "targets", "mean")), g(c, "targets", "count") or "n/a", c.get("src") or "S12"))
        rows.append(self.short_answer_strict()[-1].replace("How confident is the model?", "Confidence")
                    .replace("How confident is the analyst?", "Confidence"))
        a = self.sc.get("action") or {}
        hold = a.get("holdings") or []
        if hold:
            worth = sum(num(x.get("value")) or 0 for x in hold)
            gain = sum(num(x.get("gain")) or 0 for x in hold)
            rows.append("| Your shares | worth %s, gain %s (%s) [%s, %s] |" % (
                usd0(worth), signed0(gain), ", ".join(ACCOUNTS.get(x.get("account"), x.get("account")) for x in hold),
                P, S))
        return rows

    def record_lines(self):
        """The track record in two sentences; the per-year table stays in the dossier."""
        out = []
        note = g(self.m, "calibration", "record_summary", "note")
        if note:
            out.append("- %s [%s]" % (note, self.D))
        said = self.said_before(limit=1)
        if len(said) > 2:
            c = [x.strip() for x in said[2].strip().strip("|").split("|")]
            out.append("- Last time (%s) this advisor said %s at %s; now %s, SPY %s over the same days [%s]" % (
                c[0], c[1], c[2], c[3], c[4], self.H))
        return out or ["- No past calls yet; the simulated record needs at least three fiscal years of data [%s]" % self.D]

    def missing_lines(self, limit=3):
        lines = [l for l in self.not_verified() if l.startswith("- ")]
        more = len(lines) - limit
        return lines[:limit] + (["- and %d more, listed in the dossier [%s]" % (more, self.S)] if more > 0 else [])

    def brief(self, paths, page=None, links=False):
        """The short report: answer, summary, why, risks, record, what to watch, not verified, the detail the
        question asked for, sources as links. Everything else lives in the dossier for later questions. With
        `links` (the page) every inline marker is a link too; in the chat the Sources list carries the links."""
        want = (lambda k: True) if self.wants is None else (lambda k: k in self.wants)
        sec = [("Answer", self.answer_lines()),
               ("Summary", ["*computed by scripts; horizons count from today, %s*" % self.price_date(), ""] + self.summary_rows()),
               ("Why", ["*the analyst's reading*", ""] + self.why_plain()[:4]),
               ("Risks: the case against", [l for l in self.case_against()[2:] if l.strip()][:3]),
               ("Track record", self.record_lines()),
               ("What to watch", self.could_change()),
               ("Not verified", self.missing_lines())]
        mine = self.your_shares()
        if mine:
            sec.append(("Your shares", mine))
        news = self.news_table()
        if news and want("news"):
            sec.append(("News, what it means", news[:5]))
        if want("peers"):
            slot = [l for l in (self.narr or {}).get(PEERS_SLOT, []) if l.strip()]
            if slot:
                sec.append(("Compared with similar companies", slot[:2]))
        if want("options"):
            ops = self.options_plain()
            if ops and not ops[0].startswith("Not now"):
                sec.append(("Options on this stock, explained", ops + [
                    "- Options can lose the whole premium; selling a call caps your gain. This shows how the pieces work, "
                    "not a recommendation."]))
        sv = self.short_view()
        if sv and want("short_term"):
            sec.append(("Short-term view", sv))
        body = [self.headline(), "*As of %s. Every horizon below is counted from that date.*" % self.price_date(), ""]
        for t, b in sec:
            body += ["### " + t] + b + [""]
        text = "\n".join(body)
        words = ["- **%s** — %s" % (t, d) for t, rx, d in GLOSS if re.search(rx, text, re.I)
                 and (t not in OPTION_TERMS or "### Options" in text) and t != "quality / strength / capital use / price / risk"]
        if words:
            body += ["### Words used here"] + words + [""]
        body += ["### Sources"] + self.sources_lines(text) + [""]
        files = [("full dossier", paths[0])] + ([("page", page)] if page else [])
        charts = sorted(glob.glob(os.path.join(self.store, "charts", "*.html")))
        if charts:
            files.append(("chart", charts[-1]))
        body += ["Files: " + SEP.join("[%s](file://%s)" % (n, os.path.abspath(p)) for n, p in files), "", "> " + DISCLAIMER]
        return self.linkify("\n".join(body)) if links else "\n".join(body)


# ---------- funds (ETFs): rendered from facts/fund.json, which fund.py writes; no scorecard ----------
FUND_KIND = {"index": "an index fund", "sector": "a sector fund", "bond": "a bond fund", "dividend": "a dividend fund",
             "international": "an international fund", "leveraged": "a leveraged fund", "inverse": "an inverse fund",
             "covered-call": "a covered-call fund", "other": "a fund"}


class FundReport:
    """The brief for a fund. The 'fund rule' is this standard's own reading of trend, cost and concentration; it is
    labelled as such because no model values a fund the way the scorecard values a company."""

    def __init__(self, stock, question, date, when=None):
        self.st, self.store, self.q, self.date = stock, stock.root, question, date
        self.when = when or datetime.datetime.now(datetime.timezone.utc)
        self.f = read_json(os.path.join(stock.facts_dir, "fund.json"))
        if self.f is None:
            raise FileNotFoundError("facts/fund.json is required in %s (run fund.py)" % stock.root)
        self.sources = dict(self.f.get("sources") or {})
        self.H = "S62"
        self.hist_path = stock.log
        self.sources[self.H] = {"class": "derived", "what": "report.py run history, one line per analysis",
                                "url": "file://" + os.path.abspath(self.hist_path), "as_of": date, "retrieved": date}
        self.P = next((k for k, v in self.sources.items() if "price" in str(v.get("what", "")).lower()), "S1")
        self.Q = next((k for k, v in self.sources.items() if "profile" in str(v.get("what", "")).lower()), "S2")
        self.M = next((k for k, v in self.sources.items() if "SPY" in str(v.get("what", ""))), None)
        self.res_log = []
        self.m = {}

    source_url, link, linkify, used_ids, sources_lines = (Report.source_url, Report.link, Report.linkify,
                                                          Report.used_ids, Report.sources_lines)

    def pr(self):
        return self.f.get("price") if isinstance(self.f.get("price"), dict) else {}

    def kind_phrase(self):
        k = self.f.get("kind") or "other"
        what = FUND_KIND.get(k, "a fund")
        tracks = self.f.get("tracks")
        return "%s%s" % (what, " tracking %s" % tracks if tracks else "")

    def rule(self):
        """(holder, buyer) per the fund rule."""
        k, p = self.f.get("kind"), self.pr()
        if k in ("leveraged", "inverse"):
            return ("not built for holding: it resets daily, so over weeks it drifts from its index; the fund's own "
                    "prospectus governs", "do not buy to hold")
        if k == "covered-call":
            return ("hold only if you want income more than growth: it gives up part of the upside",
                    "buy only for income; the underlying stock keeps the upside")
        tr, ma200 = p.get("trend"), p.get("ma200")
        if tr == "up":
            return ("hold; add on a dip toward the 200-day average%s" % (" (%s)" % money(ma200) if ma200 else ""),
                    "buy in stages; the 200-day average%s is the natural limit level" % (" %s" % money(ma200) if ma200 else ""))
        if tr == "down":
            return ("hold off adding until the price is back above its 200-day average%s" % (
                " (%s)" % money(ma200) if ma200 else ""), "wait for the trend to turn")
        return ("hold; no trend signal either way", "buy in stages if you want the exposure")

    def vs_spy(self, key):
        a, b = num(self.pr().get(key)), num(g(self.f, "spy", key))
        if a is None:
            return "n/a"
        return "%s (SPY %s)" % (spct(a) if "cagr" not in key else pct(a, 1) + " a year",
                                (spct(b) if "cagr" not in key else pct(b, 1) + " a year") if b is not None else "n/a")

    def headline(self):
        p = self.pr()
        return "## %s — %s, %s; trend %s; 12 months %s" % (
            self.f.get("ticker"), self.f.get("name") or "fund", self.kind_phrase(), p.get("trend") or "unknown",
            self.vs_spy("return_12m"))

    def summary_rows(self):
        p, P, Q, M = self.pr(), self.P, self.Q, self.M
        rows = ["| | |", "|---|---|",
                "| Price today (%s) | %s %s [%s] |" % (p.get("date") or self.date, money(p.get("last")), p.get("currency") or "", P),
                "| 52-week range | %s to %s [%s] |" % (money(p.get("low_52w")), money(p.get("high_52w")), P),
                "| 1 month / 6 months / 12 months | %s / %s / %s [%s%s] |" % (
                    self.vs_spy("return_1m"), self.vs_spy("return_6m"), self.vs_spy("return_12m"), P, ", %s" % M if M else ""),
                "| 5 years / 10 years, per year | %s / %s [%s%s] |" % (
                    self.vs_spy("return_5y_cagr"), self.vs_spy("return_10y_cagr"), P, ", %s" % M if M else ""),
                "| Trend | %s (%s) [%s] |" % (p.get("trend") or "unknown", esc(p.get("trend_rule") or "ST1"), P)]
        er = self.f.get("expense_ratio")
        rows.append("| Yearly cost (expense ratio) | %s [%s] |" % (pct(er, 2) if er is not None else "no evidence", Q))
        th = [h for h in (self.f.get("top_holdings") or []) if isinstance(h, dict)]
        if th:
            rows.append("| Biggest holdings | %s — top %d = %s of the fund [%s] |" % (
                ", ".join("%s %s" % (h.get("symbol"), pct(h.get("weight"), 1)) for h in th[:5]), min(len(th), 10),
                pct(self.f.get("top_holdings_weight"), 0), Q))
        return rows

    def brief(self, paths, page=None, links=False):
        holder, buyer = self.rule()
        P, Q = self.P, self.Q
        body = [self.headline(), "*As of %s. A fund has no scorecard: the answer follows the fund rule (trend, cost, "
                "concentration), this standard's own reading, not a model of the fund's value.*" % (self.pr().get("date") or self.date), "",
                "### Answer",
                "- **What it is:** %s (%s)%s [%s]" % (self.kind_phrase(), esc(self.f.get("category") or "no category"),
                                                       "; " + esc(self.f.get("kind_reason")) if self.f.get("kind_reason") else "", Q),
                "- **If you hold it:** %s [%s]" % (holder, P),
                "- **If you want to buy:** %s [%s]" % (buyer, P)]
        body += ["- **Watch out:** %s [%s]" % (esc(fl), Q) for fl in (self.f.get("flags") or [])[:2]]
        body += ["", "### Summary", "*computed by scripts*", ""] + self.summary_rows() + [""]
        body += ["### What to watch",
                 "- The price crossing its 200-day average %s changes the trend reading [%s]" % (money(self.pr().get("ma200")), P),
                 "- A change in the fund's biggest holdings or its cost, on the fund's own page [%s]" % Q, ""]
        miss = [m for m in (self.f.get("missing") or []) if isinstance(m, dict)]
        body += ["### Not verified"] + (["- %s: %s [%s]" % (m.get("field"), esc(m.get("reason")), Q) for m in miss[:4]] or
                                       ["- Every field the fund rule asks for was available this run [%s]" % Q]) + [""]
        text = "\n".join(body)
        words = ["- **%s** — %s" % (t, d) for t, rx, d in GLOSS if re.search(rx, text, re.I)]
        if words:
            body += ["### Words used here"] + words + [""]
        body += ["### Sources"] + self.sources_lines(text) + [""]
        files = [("full dossier", paths[0])] + ([("page", page)] if page else [])
        body += ["Files: " + SEP.join("[%s](file://%s)" % (n, os.path.abspath(p)) for n, p in files), "", "> " + DISCLAIMER]
        return self.linkify("\n".join(body)) if links else "\n".join(body)

    def history_line(self):
        p, holder = self.pr(), self.rule()[0]
        q = "`%s`" % re.sub(r"\s+", " ", self.q.replace("`", "'").replace(SEP, " - ")).strip()
        return "- " + SEP.join([self.date, "question " + q, "fund " + (self.f.get("kind") or "other"),
                                "price " + money(p.get("last")), "trend " + str(p.get("trend") or "unknown"),
                                "said " + holder.split(";")[0].split(":")[0]])

    def history(self):
        t = read(self.hist_path) or ""
        return [l for l in t.splitlines() if l.startswith("- ")]

    def evidence_log(self):
        rows = ["| S | class | what | url | as-of | retrieved |", "|---|---|---|---|---|---|"]
        for k in sorted(self.sources, key=sid_num):
            s = self.sources[k]
            rows.append("| %s | %s | %s | %s | %s | %s |" % (k, s.get("class"), esc(s.get("what", "")), s.get("url"),
                                                            s.get("as_of", ""), s.get("retrieved", "")))
        return rows

    def dossier(self, brief_md, hist_line):
        body = ["# %s (%s) — fund dossier" % (self.f.get("name"), self.f.get("ticker")),
                "Updated %s · %s · last price %s on %s [%s]" % (self.date, self.kind_phrase(), money(self.pr().get("last")),
                                                                self.pr().get("date"), self.P), ""]
        keep = brief_md.split("\n### Words used here")[0].split("\n### Sources")[0]
        body += [l for l in keep.splitlines()[1:] if not l.startswith("Files: ") and not l.startswith("> ")]
        th = [h for h in (self.f.get("top_holdings") or []) if isinstance(h, dict)]
        if th:
            body += ["", "## Holdings", "| Holding | Weight | |", "|---|---|---|"] + [
                "| %s %s | %s | [%s] |" % (h.get("symbol"), esc(h.get("name") or ""), pct(h.get("weight"), 2), self.Q) for h in th]
        sw = self.f.get("sector_weights") or {}
        if isinstance(sw, dict) and sw:
            body += ["", "## Sector weights", "| Sector | Weight | |", "|---|---|---|"] + [
                "| %s | %s | [%s] |" % (k, pct(v, 1), self.Q) for k, v in sorted(sw.items(), key=lambda kv: -(num(kv[1]) or 0))]
        body += ["", "## History"] + ["%s [%s]" % (l, self.H) for l in reversed(self.history() + [hist_line])]
        body += ["", "## Evidence log"] + self.evidence_log() + ["", "> " + DISCLAIMER, ""]
        return "\n".join(body)

    def index_md(self, hist_lines):
        p = self.pr()
        out = ["# %s — %s (fund)" % (self.f.get("ticker"), self.f.get("name")),
               "%s · trend %s · price %s on %s [%s]" % (self.kind_phrase(), p.get("trend"), money(p.get("last")), p.get("date"), self.P),
               "", "## Decision", "- If you hold it: %s [%s]" % (self.rule()[0], self.P),
               "- If you want to buy: %s [%s]" % (self.rule()[1], self.P), "",
               "## Folder", "- facts/fund.json — what the fund is, holds and costs; prices and returns vs SPY",
               "- reports/dossier.md — the latest brief with holdings, sector weights, history and the evidence log",
               "- reports/<date>-<HHMM>.md|.html — dated snapshots and pages", "- history/log.md — one line per question", "",
               "## History", "| Date | Question | Trend | Price | Said | |", "|---|---|---|---|---|---|"]
        for l in reversed(hist_lines):
            h = parse_history(l)
            out.append("| %s | %s | %s | %s | %s | [%s] |" % (h.get("date"), esc(h.get("question", "")), h.get("trend", ""),
                                                             h.get("price", ""), esc(h.get("said", "")), self.H))
        out += ["", "Updated %s" % self.when.strftime("%Y-%m-%d %H:%M UTC")]
        return "\n".join(out) + "\n"


def write_html(r, path, brief_md, dossier_md, dossier_html=None):
    """The page: the brief, then the chart panels, then a link to the full dossier (written as its own page)."""
    import chart
    import mdhtml
    ticker = r.f.get("ticker") or os.path.basename(os.path.normpath(r.store))
    series = read_json(r.st.series)
    if not hasattr(r, "sc"):
        panels = ['<p class="none">Charts: none for a fund yet.</p>']
    elif series is None:
        panels = ['<p class="none">Charts: no evidence (facts/series.json missing; run facts.py first).</p>']
    else:
        panels, _ = chart.build_panels(r.f, series, r.tables if isinstance(r.tables, dict) else None)
    md = "# %s\n\n**Question:** `%s`\n\n%s" % (ticker, r.q.replace("`", "'"), brief_md)
    extra = ['<h2 id="charts">Charts</h2>'] + panels
    if dossier_html:
        extra.append('<h2 id="full-dossier">Full detail</h2><p>Everything the scripts and the analyst produced, for '
                     'later questions: <a href="%s">dossier</a> (also <code>reports/dossier.md</code>).</p>' %
                     os.path.basename(dossier_html))
    page = mdhtml.render(md, "%s Analysis" % ticker, extra, css=chart.PANEL_CSS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)
    if dossier_html:
        with open(dossier_html, "w", encoding="utf-8") as fh:
            fh.write(mdhtml.render(dossier_md, "%s dossier" % ticker))


def fund_main(a, st, when, date, name):
    r = FundReport(st, a.question, date, when)
    hist_line = r.history_line()
    os.makedirs(st.reports_dir, exist_ok=True)
    os.makedirs(st.history_dir, exist_ok=True)
    snap = os.path.join(st.reports_dir, name + ".md")
    page = os.path.join(st.reports_dir, name + ".html") if a.html else None
    brief_md = r.brief((st.dossier, snap), page)
    text = r.dossier(brief_md, hist_line)
    with open(st.dossier, "w", encoding="utf-8") as fh:
        fh.write(text)
    violations = [] if a.no_lint else lint_text(st.dossier, text)
    if violations:
        for v in violations:
            print(v)
        print("lint: %d violation(s) in %s; snapshot and history not written" % (len(violations), st.dossier))
        sys.exit(1)
    with open(snap, "w", encoding="utf-8") as fh:
        fh.write(text)
    with open(st.log, "a", encoding="utf-8") as fh:
        fh.write(hist_line + "\n")
    if page:
        write_html(r, page, r.brief((st.dossier, snap), page, links=True), text, os.path.join(st.reports_dir, "dossier.html"))
    index = r.index_md(r.history())
    with open(st.index, "w", encoding="utf-8") as fh:
        fh.write(index)
    if a.chat:
        print(brief_md)
    else:
        out = {"dossier": st.dossier, "snapshot": snap, "history": hist_line, "index": st.index, "fund": True,
               "lint": "skipped" if a.no_lint else "OK"}
        if page:
            out["html"] = os.path.abspath(page)
        print(json.dumps(out))


def main(argv=None):
    ap = EnvelopeParser(description="Render the dossier, the history line, INDEX.md and the chat answer")
    ap.add_argument("target", help="ticker or stock folder path")
    ap.add_argument("--question", required=True)
    ap.add_argument("--lens", choices=("long", "short", "both"), default=None,
                    help="default: request.json lens, else long")
    ap.add_argument("--narrative", default="", help="narrative file (default: newest history/<date>-<HHMM>.md)")
    ap.add_argument("--chat", action="store_true", help="print the brief (the short report) as Markdown")
    ap.add_argument("--html", action="store_true",
                    help="also write reports/<date>-<HHMM>.html (the brief and the charts) and reports/dossier.html")
    ap.add_argument("--no-lint", action="store_true", help="skip the evidence lint")
    add_common_args(ap)
    a = ap.parse_args(argv)
    st = locate(a.target, a)
    when = datetime.datetime.now(datetime.timezone.utc)
    date, name = today(), stamp(when)
    if not os.path.exists(st.scorecard) and os.path.exists(os.path.join(st.facts_dir, "fund.json")):
        return fund_main(a, st, when, date, name)
    req = read_json(os.path.join(st.root, "request.json"))
    req = req if isinstance(req, dict) else {}
    lens = a.lens or (req.get("lens") if req.get("lens") in ("long", "short", "both") else None) or "long"
    r = Report(st, a.question, lens, date, a.narrative or None, when)
    hist_line = r.history_line()
    text = r.dossier(hist_line)
    snap = os.path.join(st.reports_dir, name + ".md")
    os.makedirs(st.reports_dir, exist_ok=True)
    with open(st.dossier, "w", encoding="utf-8") as fh:
        fh.write(text)
    violations = [] if a.no_lint else lint_text(st.dossier, text)
    if violations:
        for v in violations:
            print(v)
        print("lint: %d violation(s) in %s; snapshot and history not written" % (len(violations), st.dossier))
        sys.exit(1)
    with open(snap, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.makedirs(st.history_dir, exist_ok=True)
    with open(st.log, "a", encoding="utf-8") as fh:
        fh.write(hist_line + "\n")
    page = os.path.join(st.reports_dir, name + ".html") if a.html else None
    chat_md = r.brief((st.dossier, snap), page)
    if page:
        write_html(r, page, r.brief((st.dossier, snap), page, links=True), text, os.path.join(st.reports_dir, "dossier.html"))
    index = r.index_md(r.history())        # after the snapshot and the page, so the folder map links this run's files
    with open(st.index, "w", encoding="utf-8") as fh:
        fh.write(index)
    ivio = [] if a.no_lint else lint_text(st.index, index, part=True, extra_ids=facts_ids(st.facts))
    if ivio:
        for v in ivio:
            print(v)
        print("lint: %d violation(s) in %s" % (len(ivio), st.index))
        sys.exit(1)
    if a.chat:
        print(chat_md)
    else:
        out = {"dossier": st.dossier, "snapshot": snap, "history": hist_line, "index": st.index,
               "lint": "skipped" if a.no_lint else "OK"}
        if page:
            out["html"] = os.path.abspath(page)
        print(json.dumps(out))


if __name__ == "__main__":
    run_main("report.py", main)
