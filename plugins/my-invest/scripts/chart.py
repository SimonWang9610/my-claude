#!/usr/bin/env python3
"""chart.py TICKER [--store DIR] [--project DIR] [--out PATH] [--data DIR]

Reads <STORE>/stocks/<TICKER>/facts/facts.json and series.json and writes one self-contained HTML page of four
inline-SVG trend panels, plus a fifth when facts/holdings_tables.json exists (no scripts,
no external assets), to <STORE>/stocks/<TICKER>/charts/<YYYY-MM-DD>.html
or --out. Prints {"path", "sources": [{"id","url"}], "as_of": {"prices","fundamentals"}}.
The page adds no number: per-year owner earnings, FCF, cash returned and split-adjusted shares are
read from metrics.py's series; an absent series renders "no evidence".
"""
import datetime
import html
import json
import math
import os
import re

import common
import mdhtml

SCRIPT = "chart.py"
DISCLAIMER = ("Model-backed research for the owner's own study, not investment advice. "
              "Every figure is as cited and may be wrong or stale.")
MAX_POINTS = 1000
W, L, R, T, B = 480, 50, 64, 14, 26          # viewBox width and plot margins
OE_LABEL = "owner earnings (maintenance capex estimated)"


# --- number helpers -----------------------------------------------------------------------------
def num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def compact(v, prefix=""):
    a, s, x = abs(v), "", abs(v)
    for d, u in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if a >= d:
            x, s = a / d, u
            break
    txt = ("%.0f" % x) if x >= 100 else ("%.1f" % x).rstrip("0").rstrip(".")
    return ("-" if v < 0 else "") + prefix + txt + s


def money(v):
    return compact(v, "$") if abs(v) >= 1e4 else "$%.2f" % v if v >= 0 else "-$%.2f" % -v


def money_tick(v):
    return compact(v, "$") if abs(v) >= 1e4 else "$%g" % v


def pct(v):
    return ("%.1f%%" % (v * 100))


def nice_step(raw):
    e = 10 ** math.floor(math.log10(raw))
    f = raw / e
    return (1 if f <= 1 else 2 if f <= 2 else 2.5 if f <= 2.5 else 5 if f <= 5 else 10) * e


def nice_ticks(lo, hi, n=5):
    if hi <= lo:
        lo, hi = (lo - 1, hi + 1) if lo == 0 else (lo - abs(lo) * 0.1, hi + abs(hi) * 0.1)
    step = nice_step((hi - lo) / (n - 1))
    start, end = math.floor(lo / step) * step, math.ceil(hi / step) * step
    ticks, t = [], start
    while t <= end + step / 2:
        ticks.append(round(t, 10))
        t += step
    return ticks, (start, end)


def log_ticks(lo, hi):
    for ms in ((1, 2, 5), (1, 3), (1,)):
        out = [m * 10 ** k for k in range(math.floor(math.log10(lo)), math.ceil(math.log10(hi)) + 1)
               for m in ms if lo <= m * 10 ** k <= hi]
        if len(out) <= 7:
            return out
    return out


def f1(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def esc(s):
    return html.escape(str(s), quote=True)


# --- svg primitives ----------------------------------------------------------------------------
def line_path(pts):
    """pts: [(x, y) | None]; None breaks the line (a gap, never a zero)."""
    out, pen = [], False
    for p in pts:
        if p is None:
            pen = False
            continue
        out.append(("L" if pen else "M") + f1(p[0]) + "," + f1(p[1]))
        pen = True
    return "".join(out)


def bar_path(x, w, y0, y1, r=4.0):
    """Bar from baseline y0 to data end y1; 4px rounded data end, square at the baseline."""
    h = abs(y1 - y0)
    r = min(r, h, w / 2)
    d = -1 if y1 < y0 else 1                     # direction from baseline to data end
    return ("M%s,%sV%sQ%s,%s %s,%sH%sQ%s,%s %s,%sV%sZ" % (
        f1(x), f1(y0), f1(y1 - d * r), f1(x), f1(y1), f1(x + r), f1(y1), f1(x + w - r),
        f1(x + w), f1(y1), f1(x + w), f1(y1 - d * r), f1(y0)))


def hline(x0, x1, y, cls):
    return '<line class="%s" x1="%s" x2="%s" y1="%s" y2="%s"/>' % (cls, f1(x0), f1(x1), f1(y), f1(y))


def text(x, y, s, cls="tk", anchor="start"):
    return '<text class="%s" x="%s" y="%s" text-anchor="%s">%s</text>' % (cls, f1(x), f1(y), anchor, esc(s))


def svg(h, body, label):
    return ('<svg viewBox="0 0 %d %d" role="img" aria-label="%s">%s</svg>' % (W, h, esc(label), "".join(body)))


def y_axis(ticks, ys, x0, x1, fmt):
    out = []
    for t in ticks:
        out.append(hline(x0, x1, ys(t), "gl"))
        out.append(text(x0 - 6, ys(t) + 4, fmt(t), "tk", "end"))
    return out


def dot(x, y, cls, tip):
    return '<circle class="%s" cx="%s" cy="%s" r="4"><title>%s</title></circle>' % (cls, f1(x), f1(y), esc(tip))


# --- context -----------------------------------------------------------------------------------
class Ctx:
    def __init__(self, facts, series):
        self.f, self.s = facts, series
        self.sources = facts.get("sources") or {}
        rows = (facts.get("fundamentals") or {}).get("annual") or []
        self.rows = sorted([r for r in rows if num(r.get("fy")) is not None], key=lambda r: r["fy"])
        self.years = [r["fy"] for r in self.rows]
        self.metrics = facts.get("metrics") or {}
        self.val = self.metrics.get("valuation") or {}
        self.macro = facts.get("macro") or {}
        self.used = set()

    def ids(self, *ids):
        return {i for i in ids if i}

    def footer(self, ids):
        ids = sorted({i for i in ids if i}, key=lambda i: (len(i), i))
        if not ids:
            return '<p class="src">Sources: none</p>'
        parts = ["%s (%s)" % (esc(i), esc((self.sources.get(i) or {}).get("url") or "no url")) for i in ids]
        return '<p class="src">Sources: %s</p>' % " · ".join(parts)

    def valuation_ids(self):
        return self.ids(*[r.get("src") for r in self.rows], (self.f.get("price") or {}).get("src"),
                        self.macro.get("src"), self.macro.get("erp_src"))


def panel(ctx, title, caption, body, ids, legend="", table=""):
    inner = body if body else '<p class="none">no evidence</p>'
    if body:
        ctx.used |= {i for i in ids if i in ctx.sources}
    return ('<section class="panel"><h2>%s</h2><p class="cap">%s</p>%s%s%s%s</section>'
            % (esc(title), caption, legend, inner, table if body else "", ctx.footer(ids if body else set())))


def legend(items):
    """items: [(css var, label, kind)] kind in bar | line | dash."""
    lis = ['<li><span class="key %s" style="--c:var(%s)"></span>%s</li>' % (k, v, esc(lbl)) for v, lbl, k in items]
    return '<ul class="legend">%s</ul>' % "".join(lis)


def table(head, rows):
    th = "".join("<th>%s</th>" % esc(h) for h in head)
    tr = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in r) for r in rows)
    return ('<details><summary>Table</summary><div class="tw"><table><thead><tr>%s</tr></thead>'
            '<tbody>%s</tbody></table></div></details>' % (th, tr))


def cell(v, fmt):
    return "no evidence" if v is None else fmt(v)


# --- panel 1: price on a log scale with today's zones --------------------------------------------
def downsample(dates, vals):
    """Split into contiguous valid runs (gaps stay gaps), stride each run, keep each run's end."""
    runs, cur = [], []
    for d, v in zip(dates, vals):
        if num(v) is not None and v > 0:
            cur.append((d, v))
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    total = sum(len(r) for r in runs)
    stride = max(1, math.ceil(total / MAX_POINTS))
    out = []
    for r in runs:
        keep = r[::stride]
        if keep[-1] is not r[-1]:
            keep.append(r[-1])
        out.append(keep)
    return out


def ordinal(d):
    return datetime.date.fromisoformat(d[:10]).toordinal()


def panel_price(ctx):
    title = "Ten-year price and value zones"
    s = ctx.s
    runs = downsample(s.get("dates") or [], s.get("adj_close") or [])
    pts = [p for r in runs for p in r]
    v = ctx.val
    buy, sell = num(v.get("buy_zone_below")), num(v.get("sell_zone_above"))
    base = num((v.get("fair_value_today") or {}).get("base"))
    psrc = s.get("src")
    if not pts:
        return panel(ctx, title, "Adjusted close on a log scale.", "", set())
    ids = {psrc}
    h = 280
    x0, x1, y0, y1 = L, W - R, T, h - B
    mom = ctx.f.get("momentum") or {}
    mas = [(k, n_, num(mom.get(k))) for k, n_ in (("ma50", "50-day average"), ("ma200", "200-day average"))]
    mas = [(k, n_, m) for k, n_, m in mas if m and m > 0]
    levels = [p[1] for p in pts] + [z for z in (buy, sell, base) if z and z > 0] + [m for _, _, m in mas]
    lo, hi = min(levels) / 1.12, max(levels) * 1.12
    xa, xb = ordinal(pts[0][0]), ordinal(pts[-1][0])
    xs = lambda d: x0 + (ordinal(d) - xa) / max(1, xb - xa) * (x1 - x0)          # noqa: E731
    ys = lambda p: y1 - (math.log(p) - math.log(lo)) / (math.log(hi) - math.log(lo)) * (y1 - y0)  # noqa: E731
    body = y_axis(log_ticks(lo, hi), ys, x0, x1, money_tick)
    left = []
    if buy and buy > 0:
        body.append('<rect class="zb" x="%s" y="%s" width="%s" height="%s"/>'
                    % (x0, f1(ys(buy)), x1 - x0, f1(y1 - ys(buy))))
        left.append((ys(buy) + 14, "buy zone below %s" % money(buy)))
    if sell and sell > 0:
        body.append('<rect class="zs" x="%s" y="%s" width="%s" height="%s"/>' % (x0, y0, x1 - x0, f1(ys(sell) - y0)))
        left.append((y0 + 13, "sell zone above %s" % money(sell)))
    if base and base > 0:
        body.append(hline(x0, x1, ys(base), "ref"))
        left.append((ys(base) - 4, "base fair value today %s" % money(base)))
    prev = None
    for y, lbl in sorted(left):                     # zone labels share the left edge; never stack them
        y = y if prev is None else max(y, prev + 14)
        body.append(text(x0 + 4, y, lbl, "lb"))
        prev = y
    if any(z for z in (buy, sell, base)):
        ids |= ctx.valuation_ids()
    hi_ma = max((m for _, _, m in mas), default=None)
    for k, name, m in mas:                          # today's averages; the higher label rides above its line
        dy = -4 if m == hi_ma else 12
        body.append(hline(x0, x1, ys(m), "ma"))
        body.append(text(x0 + (x1 - x0) * 0.5, ys(m) + dy, "%s %s" % (name, money(m)), "lb"))
    if mas:
        ids |= {i for i in (mom.get("inputs") or []) if isinstance(i, str)}
    ya, yb = int(pts[0][0][:4]), int(pts[-1][0][:4])
    step = max(1, math.ceil((yb - ya) / 5))
    for yr in range(ya + 1, yb + 1, step):
        x = xs("%d-01-01" % yr)
        body.append('<line class="ax" x1="%s" x2="%s" y1="%s" y2="%s"/>' % (f1(x), f1(x), y1, y1 + 4))
        body.append(text(x, h - 8, str(yr), "tk", "middle"))
    body.append(hline(x0, x1, y1, "ax"))
    divs = [d for d in (s.get("dividends") or []) if d.get("date") and num(d.get("amount")) is not None
            and pts[0][0] <= d["date"] <= pts[-1][0]]
    if len(divs) > 60:                                 # sparse: one mark per calendar year
        seen, kept = set(), []
        for d in divs:
            if d["date"][:4] not in seen:
                seen.add(d["date"][:4])
                kept.append(d)
        divs = kept
    for d in divs:
        x = xs(d["date"])
        body.append('<line class="dv" x1="%s" x2="%s" y1="%s" y2="%s"><title>%s dividend $%s</title></line>'
                    % (f1(x), f1(x), y1 - 7, y1, esc(d["date"]), d["amount"]))
    segs = [[(xs(d), ys(p)) for d, p in r] + [None] for r in runs]
    body.append('<path class="ln s1" d="%s"/>' % line_path([p for sg in segs for p in sg]))
    hit = max(1, len(pts) // 120)
    for d, p in pts[::hit]:
        body.append('<circle class="hit" cx="%s" cy="%s" r="5"><title>%s adj. close %s</title></circle>'
                    % (f1(xs(d)), f1(ys(p)), esc(d), money(p)))
    ld, lp = pts[-1]
    body.append(dot(xs(ld), ys(lp), "dt s1", "%s adj. close %s" % (ld, money(lp))))
    body.append(text(x1 + 8, ys(lp) + 4, money(lp), "vl"))
    leg = legend([("--s1", "adjusted close", "line")] + ([("--muted", "dividend paid", "tick")] if divs else [])
                 + ([("--muted", "50/200-day average today", "dot")] if mas else []))
    zones = ("buy zone below %s, sell zone above %s, base fair value %s (metrics.py)"
             % tuple(money(z) if z else "no evidence" for z in (buy, sell, base)))
    cap = "Adjusted close, log scale; last %s on %s [%s]; today's %s." % (money(lp), esc(ld), esc(psrc), zones)
    return panel(ctx, title, cap, svg(h, body, title), ids, leg)


# --- fiscal-year helpers -------------------------------------------------------------------------
def mseries(ctx, key, field="value"):
    """Per-year values from metrics.<key> aligned to ctx.years; None when the series is absent."""
    lst = ctx.metrics.get(key)
    if not isinstance(lst, list):
        return None
    by_fy = {e.get("fy"): e for e in lst if isinstance(e, dict)}
    return [num((by_fy.get(fy) or {}).get(field)) for fy in ctx.years]


def absent(label, vals):
    return label + (" (no evidence)" if vals is None else "")


def x_band(ctx, x0, x1):
    n = max(1, len(ctx.years))
    band = (x1 - x0) / n
    return band, (lambda i: x0 + (i + 0.5) * band)


def year_labels(ctx, xc, y, body):
    step = 1 if len(ctx.years) <= 6 else 2
    for i, fy in enumerate(ctx.years):
        if (len(ctx.years) - 1 - i) % step == 0:
            body.append(text(xc(i), y, "FY%02d" % (fy % 100), "tk", "middle"))


# --- panel 2: revenue, owner earnings, FCF --------------------------------------------------------
def panel_flows(ctx):
    title = "Revenue, owner earnings and free cash flow"
    cap = ("Fiscal-year revenue [%s], owner earnings (maintenance capex estimated) and free cash flow "
           "(metrics.py)." % " ".join(sorted({r.get("src") for r in ctx.rows if r.get("src")})))
    oe, fc = mseries(ctx, "owner_earnings_series"), mseries(ctx, "fcf_series")
    series = [("revenue", "--s1", "revenue", [num(r.get("revenue")) for r in ctx.rows]),
              ("owner_earnings", "--s2", absent(OE_LABEL, oe), oe),
              ("fcf", "--s3", absent("free cash flow", fc), fc)]
    vals = [v if v is not None else [None] * len(ctx.rows) for _, _, _, v in series]
    flat = [v for vs in vals for v in vs if v is not None]
    leg = legend([(c, lbl, "bar") for _, c, lbl, _ in series])
    if not flat:
        return panel(ctx, title, cap, "", set(), leg)
    h = 260
    x0, x1, y0, y1 = L, W - 16, T, h - B
    ticks, (lo, hi) = nice_ticks(min(0, min(flat)), max(0, max(flat)))
    ys = lambda v: y1 - (v - lo) / (hi - lo) * (y1 - y0)    # noqa: E731
    body = y_axis(ticks, ys, x0, x1, lambda t: compact(t, "$"))
    band, xc = x_band(ctx, x0, x1)
    bw = min(24.0, (band * 0.78 - 4) / 3)
    ids = set()
    for i, r in enumerate(ctx.rows):
        left = xc(i) - (3 * bw + 4) / 2
        for k, (key, cvar, lbl, _) in enumerate(series):
            v = vals[k][i]
            if v is None:
                continue
            ids.add(r.get("src"))
            body.append('<path class="bar" data-fy="%d" data-series="%s" style="fill:var(%s)" d="%s">'
                        '<title>FY%d %s %s</title></path>'
                        % (r["fy"], key, cvar, bar_path(left + k * (bw + 2), bw, ys(0), ys(v)), r["fy"], lbl,
                           money(v)))
    body.append(hline(x0, x1, ys(0), "ax"))
    year_labels(ctx, xc, h - 8, body)
    tab = table(["FY", "revenue", "owner earnings (estimate)", "free cash flow"],
                [["FY%d" % r["fy"]] + [cell(vals[k][i], money) for k in range(3)] for i, r in enumerate(ctx.rows)])
    return panel(ctx, title, cap, svg(h, body, title), ids, leg, tab)


# --- panel 3: ROIC against r_base ------------------------------------------------------------------
def panel_roic(ctx):
    title = "ROIC against the discount rate"
    by_fy = {e.get("fy"): e for e in (ctx.metrics.get("roic") or []) if isinstance(e, dict)}
    roic = [num((by_fy.get(fy) or {}).get("value")) for fy in ctx.years]
    exg = [num((by_fy.get(fy) or {}).get("value_ex_goodwill")) for fy in ctx.years]
    differs = any(a is not None and b is not None and abs(a - b) > 1e-9 or (a is None) != (b is None)
                  for a, b in zip(roic, exg))
    rb = num((ctx.val.get("params") or {}).get("r_base"))
    rb_ids = ctx.ids(ctx.macro.get("src"), ctx.macro.get("erp_src"))
    cap = ("Return on invested capital by fiscal year (metrics.py from %s) against the base discount rate "
           "r_base = 10-year Treasury + equity risk premium%s."
           % (" ".join(sorted({r.get("src") for r in ctx.rows if r.get("src")})) or "no evidence",
              (" = %s [%s]" % (pct(rb), " ".join(sorted(rb_ids)))) if rb is not None else ": no evidence"))
    items = [("--s1", "ROIC", "line")] + ([("--s2", "ROIC ex-goodwill", "dash")] if differs else []) + \
            ([("--ink2", "discount rate r_base", "ref")] if rb is not None else [])
    leg = legend(items)
    flat = [v for v in roic + (exg if differs else []) if v is not None]
    if not flat:
        return panel(ctx, title, cap, "", set(), leg)
    h = 240
    x0, x1, y0, y1 = L, W - R, T, h - B
    ticks, (lo, hi) = nice_ticks(min(0, min(flat)), max([0] + flat + ([rb] if rb is not None else [])))
    ys = lambda v: y1 - (v - lo) / (hi - lo) * (y1 - y0)    # noqa: E731
    body = y_axis(ticks, ys, x0, x1, lambda t: "%s%%" % f1(t * 100))
    band, xc = x_band(ctx, x0, x1)
    ids = {r.get("src") for r, v in zip(ctx.rows, roic) if v is not None}
    if rb is not None:
        body.append(hline(x0, x1, ys(rb), "ref"))
        body.append(text(x0 + 4, ys(rb) - 4, "discount rate r_base %s" % pct(rb), "lb"))
        ids |= rb_ids
    body.append(hline(x0, x1, ys(0) if lo < 0 else y1, "ax"))
    for vs, cls, name in ([(exg, "s2 dash", "ROIC ex-goodwill")] if differs else []) + [(roic, "s1", "ROIC")]:
        pts = [(xc(i), ys(v)) if v is not None else None for i, v in enumerate(vs)]
        body.append('<path class="ln %s" d="%s"/>' % (cls, line_path(pts)))
        for i, v in enumerate(vs):
            if v is not None:
                body.append(dot(xc(i), ys(v), "dt " + cls.split()[0], "FY%d %s %s" % (ctx.years[i], name, pct(v))))
    last = max((i for i, v in enumerate(roic) if v is not None), default=None)
    if last is not None:
        body.append(text(xc(last) + 8, ys(roic[last]) + 4, pct(roic[last]), "vl"))
    year_labels(ctx, xc, h - 8, body)
    tab = table(["FY", "ROIC", "ROIC ex-goodwill"],
                [["FY%d" % fy, cell(a, pct), cell(b, pct)] for fy, a, b in zip(ctx.years, roic, exg)])
    return panel(ctx, title, cap, svg(h, body, title), ids, leg, tab)


# --- panel 4: split-adjusted shares and cash returned ----------------------------------------------
def panel_shares(ctx):
    title = "Diluted shares and cash returned"
    shares = mseries(ctx, "shares_diluted_adjusted")
    divs = mseries(ctx, "cash_returned", "dividends_paid")
    bbs = mseries(ctx, "cash_returned", "buybacks")
    price = ctx.f.get("price") or {}
    ssrc = price.get("src") if shares is not None and price.get("splits") else None
    cap = ("Diluted shares by fiscal year, split-adjusted to today's share basis (top), and cash returned as "
           "dividends plus buybacks (bottom), both metrics.py from %s." % " ".join(
               sorted({r.get("src") for r in ctx.rows if r.get("src")} | ({ssrc} if ssrc else set()))))
    leg = legend([("--s1", absent("diluted shares (split-adjusted)", shares), "line"),
                  ("--s2", absent("dividends", divs), "bar"), ("--s3", absent("buybacks", bbs), "bar")])
    shares = shares or [None] * len(ctx.rows)
    divs, bbs = divs or [None] * len(ctx.rows), bbs or [None] * len(ctx.rows)
    has_sh = any(v is not None for v in shares)
    cash = [(d or 0) + (b or 0) if d is not None or b is not None else None for d, b in zip(divs, bbs)]
    has_cash = any(v is not None for v in cash)
    if not has_sh and not has_cash:
        return panel(ctx, title, cap, "", set(), leg)
    h = 330
    x0, x1 = L, W - R
    band, xc = x_band(ctx, x0, x1)
    body, ids = [], set()
    # top plot: shares (its own scale), bottom plot: cash returned (its own scale) - shared x, no dual axis
    ta, tb, ba, bb = T, 128, 172, h - B
    if has_sh:
        sv = [v for v in shares if v is not None]
        ticks, (lo, hi) = nice_ticks(min(sv), max(sv), 4)
        ys = lambda v: tb - (v - lo) / (hi - lo) * (tb - ta)    # noqa: E731
        body += y_axis(ticks, ys, x0, x1, compact)
        body.append('<path class="ln s1" d="%s"/>'
                    % line_path([(xc(i), ys(v)) if v is not None else None for i, v in enumerate(shares)]))
        for i, v in enumerate(shares):
            if v is not None:
                ids.add(ctx.rows[i].get("src"))
                body.append(dot(xc(i), ys(v), "dt s1", "FY%d diluted shares %s" % (ctx.years[i], compact(v))))
        last = max(i for i, v in enumerate(shares) if v is not None)
        body.append(text(xc(last) + 8, ys(shares[last]) + 4, compact(shares[last]), "vl"))
        ids.add(ssrc)
    else:
        body.append(text((x0 + x1) / 2, (ta + tb) / 2, "shares: no evidence", "lb", "middle"))
    body.append(text(x0, ba - 18, "cash returned", "lb"))
    if has_cash:
        ticks, (lo, hi) = nice_ticks(0, max(v for v in cash if v is not None), 4)
        ys = lambda v: bb - (v - lo) / (hi - lo) * (bb - ba)    # noqa: E731
        body += y_axis(ticks, ys, x0, x1, lambda t: compact(t, "$"))
        bw = min(24.0, band * 0.6)
        for i, r in enumerate(ctx.rows):
            segs = [(k, c, v) for k, c, v in (("dividends", "--s2", divs[i]), ("buybacks", "--s3", bbs[i]))
                    if v is not None and v > 0]
            base = ys(0)
            for j, (k, c, v) in enumerate(segs):
                top = base - (ys(0) - ys(v))
                gap = 2 if j else 0
                d = bar_path(xc(i) - bw / 2, bw, base - gap, top, 4 if j == len(segs) - 1 else 0)
                ids.add(r.get("src"))
                body.append('<path class="bar" data-fy="%d" data-series="%s" style="fill:var(%s)" d="%s">'
                            '<title>FY%d %s %s</title></path>' % (r["fy"], k, c, d, r["fy"], k, money(v)))
                base = top
        body.append(hline(x0, x1, bb, "ax"))
    else:
        body.append(text((x0 + x1) / 2, (ba + bb) / 2, "cash returned: no evidence", "lb", "middle"))
    year_labels(ctx, xc, h - 8, body)
    tab = table(["FY", "diluted shares (split-adj.)", "dividends", "buybacks"],
                [["FY%d" % fy, cell(s, compact), cell(d, money), cell(b, money)]
                 for fy, s, d, b in zip(ctx.years, shares, divs, bbs)])
    return panel(ctx, title, cap, svg(h, body, title), ids, leg, tab)


# --- panel 5: holdings outcomes (only when holdings_tables.json exists) -----------------------------
def panel_holdings(ctx, hold):
    title = "Holdings outcomes"
    outs = [o for o in (hold.get("outcomes") or []) if isinstance(o, dict)][:5]   # slots 1-5, fixed order
    labels = []
    for o in outs:
        for p in o.get("price_points") or []:
            if p.get("label") not in [lb for lb, _ in labels]:
                labels.append((p.get("label"), num(p.get("price"))))
    gain = {(o.get("account"), p.get("label")): num(p.get("gain_abs")) for o in outs for p in o.get("price_points") or []}
    pct_ = {(o.get("account"), p.get("label")): num(p.get("gain_pct")) for o in outs for p in o.get("price_points") or []}
    accts = [o.get("account") for o in outs]
    hsrc = sorted(i for i in (hold.get("sources") or {}) if re.fullmatch(r"S9\d", i))
    psrc = (ctx.f.get("price") or {}).get("src")
    cap = ("Gain or loss in USD per account if sold at each price point (holdings.py) [%s]; the current price is "
           "shaded." % " ".join(hsrc + ([psrc] if psrc else [])))
    leg = legend([("--s%d" % (k + 1), str(a), "bar") for k, a in enumerate(accts)])
    flat = [v for v in gain.values() if v is not None]
    if not flat or not labels:
        return panel(ctx, title, cap, "", set(), leg)
    h = 260
    x0, x1, y0, y1 = L + 6, W - 16, T, h - 40
    ticks, (lo, hi) = nice_ticks(min(0, min(flat)), max(0, max(flat)))
    ys = lambda v: y1 - (v - lo) / (hi - lo) * (y1 - y0)    # noqa: E731
    body = y_axis(ticks, ys, x0, x1, lambda t: compact(t, "$"))
    band = (x1 - x0) / len(labels)
    xc = lambda i: x0 + (i + 0.5) * band                     # noqa: E731
    bw = min(24.0, (band * 0.78 - 2 * (len(accts) - 1)) / max(1, len(accts)))
    for i, (lbl, price) in enumerate(labels):
        cur = lbl == "current"
        if cur:
            body.insert(0, '<rect class="cur" x="%s" y="%s" width="%s" height="%s"/>'
                        % (f1(x0 + i * band), y0, f1(band), y1 - y0))
        left = xc(i) - (len(accts) * bw + 2 * (len(accts) - 1)) / 2
        for k, a in enumerate(accts):
            v = gain.get((a, lbl))
            if v is None:
                continue
            gp = pct_.get((a, lbl))
            body.append('<path class="bar" data-label="%s" data-series="%s" style="fill:var(--s%d)" d="%s">'
                        '<title>%s at %s: %s%s</title></path>'
                        % (esc(lbl), esc(a), k + 1, bar_path(left + k * (bw + 2), bw, ys(0), ys(v)), esc(a),
                           esc(lbl), money(v), "" if gp is None else " (%s)" % pct(gp)))
        body.append(text(xc(i), h - 22, lbl, "tk b" if cur else "tk", "middle"))
        body.append(text(xc(i), h - 8, money(price) if price is not None else "no evidence", "tk", "middle"))
    body.append(hline(x0, x1, ys(0), "ax"))
    tab = table(["account"] + [lb for lb, _ in labels],
                [[str(a)] + [cell(gain.get((a, lb)), money) for lb, _ in labels] for a in accts])
    return panel(ctx, title, cap, svg(h, body, title), set(hsrc) | {psrc}, leg, tab)


# --- page --------------------------------------------------------------------------------------------
# panel styles; report.py embeds them with the panels (tokens come from mdhtml)
PANEL_CSS = """.panel h2{font-size:16px;margin:0 0 2px}
.meta,.cap{color:var(--ink2);font-size:13px;margin:0 0 8px}
.panel{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px;margin:0 0 16px}
svg{display:block;width:100%;height:auto;overflow:visible}
svg text{font-family:inherit}
.tk{fill:var(--muted);font-size:11px;font-variant-numeric:tabular-nums}
.lb{fill:var(--ink2);font-size:11px}.vl{fill:var(--ink);font-size:12px;font-weight:600}
.gl{stroke:var(--grid);stroke-width:1}.ax{stroke:var(--axis);stroke-width:1}
.ref{stroke:var(--ink2);stroke-width:1.5;stroke-dasharray:5 4}
.zb{fill:var(--good);opacity:.12}.zs{fill:var(--crit);opacity:.10}
.ln{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.ln.s1{stroke:var(--s1)}.ln.s2{stroke:var(--s2)}.dash{stroke-dasharray:6 4}
.dt{stroke:var(--surface);stroke-width:2}.dt.s1{fill:var(--s1)}.dt.s2{fill:var(--s2)}
.dv{stroke:var(--muted);stroke-width:1}.ma{stroke:var(--muted);stroke-width:1.5;stroke-dasharray:2 3}
.cur{fill:var(--grid);opacity:.6}.tk.b{fill:var(--ink);font-weight:600}.hit{fill:transparent}
.legend{list-style:none;display:flex;flex-wrap:wrap;gap:4px 14px;padding:0;margin:0 0 6px;font-size:12px;color:var(--ink2)}
.key{display:inline-block;width:12px;height:10px;margin-right:5px;vertical-align:-1px}
.key.bar{background:var(--c);border-radius:2px}.key.line{height:2px;vertical-align:3px;background:var(--c)}
.key.dash{height:0;border-top:2px dashed var(--c);vertical-align:3px}
.key.ref{height:0;border-top:1.5px dashed var(--c);vertical-align:3px}
.key.dot{height:0;border-top:2px dotted var(--c);vertical-align:3px}
.key.tick{width:1px;height:8px;background:var(--c);margin:0 8px 0 4px}
.none{color:var(--ink2);font-style:italic;margin:8px 0}
.src{color:var(--ink2);font-size:12px;margin:8px 0 0;overflow-wrap:anywhere}
details{font-size:13px;margin-top:6px}summary{cursor:pointer;color:var(--ink2)}
.panel .tw{overflow-x:auto}.panel table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums;font-size:13px}
.panel th,.panel td{text-align:right;padding:3px 6px;border-bottom:1px solid var(--grid)}
.panel th:first-child,.panel td:first-child{text-align:left}
.disc{color:var(--ink2);font-size:12px;margin:16px 0 8px}
@media (max-width:480px){.tk,.lb{font-size:14px}.vl{font-size:15px}.panel{padding:10px}}
"""
CSS = mdhtml.TOKENS + """*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:680px;margin:0 auto;padding:16px}
h1{font-size:20px;margin:8px 0 2px}
""" + PANEL_CSS


def as_of(ctx):
    prices = (ctx.f.get("price") or {}).get("date") or ((ctx.s.get("dates") or [None])[-1])
    newest = ctx.rows[-1] if ctx.rows else None
    fund = ("FY%d (period end %s)" % (newest["fy"], newest.get("period_end") or "no evidence")) if newest else None
    return prices, fund


def build_panels(facts, series, holdings=None):
    """Panel <section>s (style with PANEL_CSS) and {"sources", "as_of"}; the importable entry for report.py."""
    ctx = Ctx(facts, series)
    if holdings:
        ctx.sources = dict(holdings.get("sources") or {}, **ctx.sources)    # facts ids win on a clash
    panels = [panel_price(ctx), panel_flows(ctx), panel_roic(ctx), panel_shares(ctx)]
    if holdings is not None:
        panels.append(panel_holdings(ctx, holdings))
    prices, fund = as_of(ctx)
    sources = [{"id": i, "url": (ctx.sources.get(i) or {}).get("url")}
               for i in sorted(ctx.used, key=lambda i: (len(i), i))]
    return panels, {"sources": sources, "as_of": {"prices": prices, "fundamentals": fund}}


def render(facts, series, holdings=None):
    panels, manifest = build_panels(facts, series, holdings)
    ticker = facts.get("ticker") or series.get("ticker") or ""
    prices, fund = manifest["as_of"]["prices"], manifest["as_of"]["fundamentals"]
    psrc = (facts.get("price") or {}).get("src") or series.get("src")
    rows = sorted([r for r in ((facts.get("fundamentals") or {}).get("annual") or []) if num(r.get("fy")) is not None],
                  key=lambda r: r["fy"])
    fsrc = rows[-1].get("src") if rows else None
    head = ('<h1>%s · %s</h1><p class="meta">Prices as of %s%s · fundamentals %s%s · generated %s</p>'
            % (esc(ticker), esc(facts.get("name") or "no evidence"), esc(prices or "no evidence"),
               (" [%s]" % esc(psrc)) if psrc and prices else "", esc(fund or "no evidence"),
               (" [%s]" % esc(fsrc)) if fsrc else "", common.today()))
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s Trend Charts</title><style>%s</style></head><body><main>%s%s<p class="disc">%s</p>'
            '</main></body></html>\n' % (esc(ticker), CSS, head, "".join(panels), html.escape(DISCLAIMER, quote=False)))
    return page, manifest


def load_json(path, what):
    if not os.path.exists(path):
        common.fail(SCRIPT, "%s not found at %s; run track first" % (what, path))
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run(argv=None):
    ap = common.EnvelopeParser(prog=SCRIPT, description="Draw trend charts for one ticker as one HTML page")
    ap.add_argument("ticker", help="ticker or stock folder path")
    ap.add_argument("--data", default=os.environ.get("MY_INVEST_DATA", os.path.expanduser("~/.my-invest")),
                    help="data dir (config.json, default store)")
    common.add_store_arg(ap)
    ap.add_argument("--out", default="", help="write the HTML here instead of <ticker>/charts/<date>.html")
    args = ap.parse_args(argv)
    st = common.locate(args.ticker, args)
    facts = load_json(st.facts, "facts.json")
    series = load_json(st.series, "series.json")
    holdings = load_json(st.holdings_tables, "holdings_tables.json") if os.path.exists(st.holdings_tables) else None
    page, manifest = render(facts, series, holdings)
    path = args.out or os.path.join(st.charts_dir, common.today() + ".html")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    out = {"path": os.path.abspath(path)}
    out.update(manifest)
    print(json.dumps(out))
    return out


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
