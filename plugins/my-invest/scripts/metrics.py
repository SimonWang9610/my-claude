#!/usr/bin/env python3
"""metrics.py <facts.json> [--out PATH] [--mos 0.30] [--erp X]

Derives every `metrics.*` object of facts.json (skills/data/references/facts-schema.md) from
`fundamentals.annual`, `price`, `macro` and `sector_class`, per skills/score/rules/*.md and
skills/score/references/valuation.md. A pure function of the input file; stdlib only.

Conventions the cards leave open (each also stated in the object's `note` where it applies):
- Years are matched by `fy` (t-1 = fy0-1, t-5 = fy0-5), not by list position; a gap yields null.
- Debt fields (`st_debt`, `lt_debt`) null -> 0 (concept absent = no debt), noted.
- Shares and EPS are split-adjusted to today's basis: a split dated after a year's `period_end`
  multiplies that year's shares (divides its EPS) by the ratio.
- EBIT = `operating_income`, else `pretax_income + interest_expense`.
- Owner earnings per year = net_income + da - min(capex, da) (estimate); CF_0 averages the
  available years among the last three.
Ratios are rounded to 4 decimals, dollar amounts to 2. Missing inputs give null plus `reason`.
Exit 1 with {"error": ...} only when the input cannot be read.
"""
import argparse
import datetime
import json
import math
import sys

ERP_DEFAULT = 4.20          # Damodaran implied ERP, % (valuation.md source [3])
ERP_DEFAULT_DATE = "2026-10-01"
NA_SECTORS = ("financial", "reit", "utility")
TAX_DEFAULT, TAX_CAP = 0.21, 0.35
G_LO, G_HI = -0.20, 0.40
HORIZONS = (1.0, 2.0, 5.0, 10.0)
HORIZON_METHOD = ("V_h = V_0 (1+r)^h - sum_{t<=floor(h)} CF_t (1+r)^(h-t) - frac(h) x CF_{floor(h)+1}: "
                  "fractional compounding, the partial year's flow pro-rated and received at h")


def hkey(h):
    return "%.10g" % h


def parse_horizons(text):
    """'1,3,7.5' -> (1.0, 3.0, 7.5); each in (0, 10], duplicates dropped, order kept."""
    out = []
    for tok in str(text).split(","):
        tok = tok.strip()
        if not tok:
            continue
        h = float(tok)
        if not 0 < h <= 10 or not math.isfinite(h):
            raise ValueError("horizon %r outside (0, 10] years" % tok)
        if h not in out:
            out.append(h)
    if not out:
        raise ValueError("no horizons given")
    return tuple(out)
BENEISH = {"const": -4.84, "DSRI": 0.920, "GMI": 0.528, "AQI": 0.404, "SGI": 0.892,
           "DEPI": 0.115, "SGAI": -0.172, "TATA": 4.679, "LVGI": -0.327}


# ---------- helpers ----------

def num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)) and math.isfinite(v):
        return float(v)
    return None


def r4(x):
    return None if x is None else round(x, 4)


def r2(x):
    return None if x is None else round(x, 2)


def div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def null_obj(reason, inputs, **fields):
    out = dict(fields)
    out["inputs"] = inputs
    out["reason"] = reason
    return out


class Years:
    """fundamentals.annual indexed by fiscal year; k = years back from the latest."""

    def __init__(self, annual, splits, shares_history=None):
        self.hist = {}
        for h in shares_history if isinstance(shares_history, list) else []:
            if isinstance(h, dict) and isinstance(h.get("fy"), int):
                self.hist.setdefault(h["fy"], h)
        self.idx = {}
        rows = []
        for i, r in enumerate(annual if isinstance(annual, list) else []):
            if isinstance(r, dict) and isinstance(r.get("fy"), int) and r["fy"] not in self.idx:
                self.idx[r["fy"]] = i
                rows.append(r)
        rows.sort(key=lambda r: r["fy"], reverse=True)
        self.rows = rows
        self.by_fy = {r["fy"]: r for r in rows}
        self.fy0 = rows[0]["fy"] if rows else None
        self.splits = []
        for s in splits if isinstance(splits, list) else []:
            if isinstance(s, dict) and isinstance(s.get("date"), str) and num(s.get("ratio")):
                self.splits.append((s["date"], num(s["ratio"])))

    def truncate(self, fy_then):
        """The same history as seen at fiscal year fy_then (rows with fy <= fy_then)."""
        t = Years.__new__(Years)
        t.hist, t.idx, t.splits = self.hist, self.idx, self.splits
        t.rows = [r for r in self.rows if r["fy"] <= fy_then]
        t.by_fy = {r["fy"]: r for r in t.rows}
        t.fy0 = t.rows[0]["fy"] if t.rows else None
        return t

    def row(self, k):
        return None if self.fy0 is None else self.by_fy.get(self.fy0 - k)

    def v(self, k, field):
        r = self.row(k)
        return num(r.get(field)) if r else None

    def fy(self, k):
        return None if self.fy0 is None else self.fy0 - k

    def ref(self, ks, field=None):
        ids = sorted(self.idx[self.fy0 - k] for k in ks if self.row(k) is not None)
        if not ids:
            return "fundamentals.annual[]"
        span = str(ids[0]) if ids[0] == ids[-1] else "%d..%d" % (ids[0], ids[-1])
        return "fundamentals.annual[%s]%s" % (span, "." + field if field else "")

    def split_factor(self, k, r=None):
        r = r or self.row(k)
        end = r.get("period_end") if r else None
        if not isinstance(end, str):
            end = "%d-12-31" % self.fy(k)
        f = 1.0
        for date, ratio in self.splits:
            if date > end:
                f *= ratio
        return f

    def shares(self, k):
        s = self.v(k, "shares_diluted")
        return None if s is None else s * self.split_factor(k)

    def shares_or_history(self, k):
        """(split-adjusted shares, source path) from annual, else fundamentals.shares_history."""
        s = self.shares(k)
        if s is not None:
            return s, self.ref([k], "shares_diluted")
        h = self.hist.get(self.fy(k)) if self.fy0 is not None else None
        hs = num(h.get("shares_diluted")) if h else None
        if hs is None:
            return None, None
        return hs * self.split_factor(k, h), "fundamentals.shares_history[fy=%d].shares_diluted" % self.fy(k)

    def eps(self, k):
        e = self.v(k, "eps_diluted")
        return None if e is None else e / self.split_factor(k)

    def debt(self, k, field, notes):
        d = self.v(k, field)
        if d is None and self.row(k) is not None:
            notes.add("%s null in FY%d treated as 0" % (field, self.fy(k)))
            return 0.0
        return d

    def ebit(self, k):
        oi = self.v(k, "operating_income")
        if oi is not None:
            return oi
        p, i = self.v(k, "pretax_income"), self.v(k, "interest_expense")
        return None if p is None or i is None else p + i

    def gm_cogs(self, k):
        """(revenue - cogs) / revenue, falling back to gross_profit when cogs is null."""
        rev, cogs = self.v(k, "revenue"), self.v(k, "cogs")
        gp = rev - cogs if rev is not None and cogs is not None else self.v(k, "gross_profit")
        return gp, div(gp, rev)

    def oe(self, k):
        ni, da, capex = self.v(k, "net_income"), self.v(k, "da"), self.v(k, "capex")
        if ni is None or da is None or capex is None:
            return None
        return ni + da - min(capex, da)

    def fcf(self, k):
        ocf, capex = self.v(k, "ocf"), self.v(k, "capex")
        return None if ocf is None or capex is None else ocf - capex


def with_notes(obj, notes):
    if notes:
        prev = obj.get("note")
        obj["note"] = "; ".join(([prev] if prev else []) + sorted(notes))
    return obj


def market_cap(price, notes):
    mc = num(price.get("market_cap"))
    if mc is None:
        last, so = num(price.get("last")), num(price.get("shares_out"))
        if last is not None and so is not None:
            notes.add("market_cap null: price.last x price.shares_out")
            mc = last * so
    return mc


# ---------- pillar inputs ----------

def piotroski(Y):
    keys = ["roa", "cfo", "d_roa", "accrual", "d_lever", "d_liquid", "eq_offer", "d_margin", "d_turn"]
    inputs = [Y.ref([0, 1, 2]), "price.splits"]
    if Y.row(0) is None or Y.row(1) is None:
        return null_obj("needs two consecutive fiscal years", inputs, fy=Y.fy0, score=None,
                        signals={k: None for k in keys})
    notes = set()
    ta0, ta1, ta2 = Y.v(0, "total_assets"), Y.v(1, "total_assets"), Y.v(2, "total_assets")
    roa0, roa1 = div(Y.v(0, "net_income"), ta1), div(Y.v(1, "net_income"), ta2)
    cfo0 = div(Y.v(0, "ocf"), ta1)

    def avg(a, b):
        return None if a is None or b is None else (a + b) / 2

    lev0 = div(Y.debt(0, "lt_debt", notes), avg(ta0, ta1))
    lev1 = div(Y.debt(1, "lt_debt", notes), avg(ta1, ta2))
    cr0 = div(Y.v(0, "current_assets"), Y.v(0, "current_liabilities"))
    cr1 = div(Y.v(1, "current_assets"), Y.v(1, "current_liabilities"))

    def gm(k):
        gp = Y.v(k, "gross_profit")
        if gp is None and Y.v(k, "revenue") is not None and Y.v(k, "cogs") is not None:
            gp = Y.v(k, "revenue") - Y.v(k, "cogs")
        return div(gp, Y.v(k, "revenue"))

    turn0, turn1 = div(Y.v(0, "revenue"), ta1), div(Y.v(1, "revenue"), ta2)

    def bit(cond_inputs, test):
        return None if any(x is None for x in cond_inputs) else int(test())

    eq = Y.v(0, "equity_issued")
    if eq is not None:
        eq_offer = int(eq <= 0)
    else:
        s0, s1 = Y.shares(0), Y.shares(1)
        eq_offer = None if s0 is None or s1 is None else int(s0 <= s1)
        notes.add("eq_offer fallback: equity_issued null, 1 when split-adjusted diluted shares did not rise")
    gm0, gm1 = gm(0), gm(1)
    s = {
        "roa": bit([roa0], lambda: roa0 > 0),
        "cfo": bit([cfo0], lambda: cfo0 > 0),
        "d_roa": bit([roa0, roa1], lambda: roa0 > roa1),
        "accrual": bit([cfo0, roa0], lambda: cfo0 > roa0),
        "d_lever": bit([lev0, lev1], lambda: lev0 < lev1),
        "d_liquid": bit([cr0, cr1], lambda: cr0 > cr1),
        "eq_offer": eq_offer,
        "d_margin": bit([gm0, gm1], lambda: gm0 > gm1),
        "d_turn": bit([turn0, turn1], lambda: turn0 > turn1),
    }
    missing = [k for k in keys if s[k] is None]
    out = {"fy": Y.fy0, "score": None if missing else sum(s.values()), "signals": s, "inputs": inputs,
           "note": "scaling per Piotroski (2000) pp.7-9: ROA, CFO, accrual, turnover by beginning-of-year "
                   "total assets; leverage by average total assets"}
    if missing:
        out["reason"] = "signals not computable: %s" % ", ".join(missing)
    return with_notes(out, notes)


def altman(Y, sector, price):
    notes = set()
    inputs = [Y.ref([0]), "price.market_cap", "sector_class"]
    if sector in NA_SECTORS:
        return null_obj("model n/a for sector_class %s" % sector, inputs, model=None, value=None, zone=None)
    if sector not in ("manufacturer", "non-manufacturer"):
        return null_obj("unknown sector_class %r" % sector, inputs, model=None, value=None, zone=None)
    ta, ca, cl = Y.v(0, "total_assets"), Y.v(0, "current_assets"), Y.v(0, "current_liabilities")
    re_, ebit, tl = Y.v(0, "retained_earnings"), Y.ebit(0), Y.v(0, "total_liabilities")
    x1 = div(None if ca is None or cl is None else ca - cl, ta)
    x2, x3 = div(re_, ta), div(ebit, ta)
    if sector == "manufacturer":
        model, x4 = "Z", div(market_cap(price, notes), tl)
        x5 = div(Y.v(0, "revenue"), ta)
        xs = {"X1": x1, "X2": x2, "X3": x3, "X4": x4, "X5": x5}
        coef, cuts = {"X1": 1.2, "X2": 1.4, "X3": 3.3, "X4": 0.6, "X5": 1.0}, (1.81, 2.99)
    else:
        model, x4 = "Z''", div(Y.v(0, "equity"), tl)
        xs = {"X1": x1, "X2": x2, "X3": x3, "X4": x4}
        coef, cuts = {"X1": 6.56, "X2": 3.26, "X3": 6.72, "X4": 1.05}, (1.10, 2.60)
    comps = {k: r4(v) for k, v in xs.items()}
    missing = [k for k, v in xs.items() if v is None]
    if missing:
        return with_notes(null_obj("inputs missing for %s" % ", ".join(missing), inputs, model=model,
                                   value=None, zone=None, components=comps), notes)
    value = r4(sum(coef[k] * xs[k] for k in xs))
    zone = "distress" if value < cuts[0] else "grey" if value < cuts[1] else "safe"
    return with_notes({"model": model, "value": value, "zone": zone, "components": comps,
                       "fy": Y.fy0, "inputs": inputs}, notes)


def beneish(Y, sector):
    notes = set()
    inputs = [Y.ref([0, 1])]
    variables = {k: None for k in ("DSRI", "GMI", "AQI", "SGI", "DEPI", "SGAI", "LVGI", "TATA")}
    note = "UNVERIFIED coefficients and cutoff (secondary sources; pillar-5 5.2)"
    if sector in NA_SECTORS:
        return null_obj("model n/a for sector_class %s" % sector, inputs, m=None, flag=None,
                        variables=variables, note=note)
    if Y.row(0) is None or Y.row(1) is None:
        return null_obj("needs two consecutive fiscal years", inputs, m=None, flag=None,
                        variables=variables, note=note)
    v = Y.v
    rev0, rev1 = v(0, "revenue"), v(1, "revenue")

    def safe(f):
        try:
            return f()
        except (TypeError, ZeroDivisionError):
            return None

    def aq(k):
        return 1 - (v(k, "current_assets") + v(k, "ppe_net")) / v(k, "total_assets")

    def dep(k):
        return v(k, "da") / (v(k, "da") + v(k, "ppe_net"))

    def lev(k):
        return (v(k, "current_liabilities") + Y.debt(k, "lt_debt", notes)) / v(k, "total_assets")

    gm0, gm1 = Y.gm_cogs(0)[1], Y.gm_cogs(1)[1]
    variables = {
        "DSRI": safe(lambda: (v(0, "receivables") / rev0) / (v(1, "receivables") / rev1)),
        "GMI": safe(lambda: gm1 / gm0),
        "AQI": safe(lambda: aq(0) / aq(1)),
        "SGI": safe(lambda: rev0 / rev1),
        "DEPI": safe(lambda: dep(1) / dep(0)),
        "SGAI": safe(lambda: (v(0, "sga") / rev0) / (v(1, "sga") / rev1)),
        "LVGI": safe(lambda: lev(0) / lev(1)),
        "TATA": safe(lambda: (v(0, "net_income") - v(0, "ocf")) / v(0, "total_assets")),
    }
    missing = [k for k, x in variables.items() if x is None]
    out = {"fy": Y.fy0, "variables": {k: r4(x) for k, x in variables.items()}, "inputs": inputs, "note": note}
    if missing:
        out.update(m=None, flag=None, reason="variables not computable: %s" % ", ".join(missing))
    else:
        m = BENEISH["const"] + sum(BENEISH[k] * x for k, x in variables.items())
        out.update(m=r4(m), flag=r4(m) > -1.78)
    return with_notes(out, notes)


def accrual_ratio(Y):
    notes = set()
    inputs = [Y.ref([0, 1])]
    method = "Sloan 1996 balance-sheet accruals / average total assets"
    f = ("current_assets", "cash", "current_liabilities", "total_assets")
    vals = {(k, x): Y.v(k, x) for k in (0, 1) for x in f}
    da = Y.v(0, "da")
    if Y.row(1) is None or da is None or any(x is None for x in vals.values()):
        return null_obj("needs current_assets, cash, current_liabilities, total_assets for two years and da",
                        inputs, value=None, method=method)
    d = {x: vals[(0, x)] - vals[(1, x)] for x in f}
    dstd = Y.debt(0, "st_debt", notes) - Y.debt(1, "st_debt", notes)
    tp0, tp1 = Y.v(0, "taxes_payable"), Y.v(1, "taxes_payable")
    if tp0 is None or tp1 is None:
        dtp = 0.0
        notes.add("taxes_payable null: change in taxes payable treated as 0")
    else:
        dtp = tp0 - tp1
    acc = (d["current_assets"] - d["cash"]) - (d["current_liabilities"] - dstd - dtp) - da
    avg_ta = (vals[(0, "total_assets")] + vals[(1, "total_assets")]) / 2
    return with_notes({"fy": Y.fy0, "value": r4(div(acc, avg_ta)), "accruals": r2(acc), "method": method,
                       "inputs": inputs}, notes)


def roic_series(Y):
    """Per-year ROIC; returns (output list, raw {k: (nopat, ic)})."""
    out, raw = [], {}
    for r in Y.rows:
        k = Y.fy0 - r["fy"]
        notes = set()
        e = {"fy": r["fy"], "inputs": [Y.ref([k])]}
        oi, pre, tax = Y.v(k, "operating_income"), Y.v(k, "pretax_income"), Y.v(k, "income_tax")
        if pre is None or pre <= 0 or tax is None:
            t = TAX_DEFAULT
            notes.add("tax rate default 0.21 (pretax_income <= 0 or tax missing)")
        else:
            t = clamp(tax / pre, 0.0, TAX_CAP)
        eq, cash = Y.v(k, "equity"), Y.v(k, "cash")
        nopat = None if oi is None else oi * (1 - t)
        ic = None
        if eq is not None and cash is not None:
            ic = eq + Y.debt(k, "st_debt", notes) + Y.debt(k, "lt_debt", notes) - cash
        gw = Y.v(k, "goodwill_intangibles")
        if gw is None:
            notes.add("goodwill_intangibles null treated as 0")
            gw = 0.0
        ic_ex = None if ic is None else ic - gw
        e.update(tax_rate=r4(t), nopat=r2(nopat), invested_capital=r2(ic),
                 value=r4(div(nopat, ic)) if ic is not None and ic > 0 else None,
                 invested_capital_ex_goodwill=r2(ic_ex),
                 value_ex_goodwill=r4(div(nopat, ic_ex)) if ic_ex is not None and ic_ex > 0 else None)
        if e["value"] is None:
            e["reason"] = "operating_income, equity or cash missing, or invested capital <= 0"
        raw[k] = (nopat, ic)
        out.append(with_notes(e, notes))
    return out, raw


def roiic_5y(Y, raw):
    inputs = ["metrics.roic[fy=%s,%s]" % (Y.fy(0), Y.fy(5))]
    a, b = raw.get(0, (None, None)), raw.get(5, (None, None))
    if None in a or None in b:
        return null_obj("needs NOPAT and invested capital in FY0 and FY0-5", inputs, value=None)
    den = a[1] - b[1]
    if den <= 0:
        return null_obj("invested capital did not grow over five years (denominator <= 0)", inputs,
                        value=None, delta_nopat=r2(a[0] - b[0]), delta_invested_capital=r2(den))
    return {"value": r4((a[0] - b[0]) / den), "delta_nopat": r2(a[0] - b[0]),
            "delta_invested_capital": r2(den), "inputs": inputs}


def growth_items(Y):
    res = {}
    gp0, ta0 = Y.gm_cogs(0)[0], Y.v(0, "total_assets")
    gpv = div(gp0, ta0)
    res["gross_profitability"] = {"value": r4(gpv), "inputs": [Y.ref([0])]} if gpv is not None else \
        null_obj("revenue, cogs or total_assets missing", [Y.ref([0])], value=None)
    gm0, gm5 = Y.gm_cogs(0)[1], Y.gm_cogs(5)[1]
    res["gross_margin_5y_change"] = (
        {"value": r4((gm0 - gm5) * 100), "unit": "percentage points", "inputs": [Y.ref([0, 5])]}
        if gm0 is not None and gm5 is not None else
        null_obj("gross margin missing in FY0 or FY0-5", [Y.ref([0, 5])], value=None))
    rev0, rev5 = Y.v(0, "revenue"), Y.v(5, "revenue")
    if rev0 is not None and rev5 is not None and rev5 > 0 and rev0 >= 0:
        res["revenue_cagr_5y"] = {"value": r4((rev0 / rev5) ** 0.2 - 1), "inputs": [Y.ref([0, 5])]}
    else:
        res["revenue_cagr_5y"] = null_obj("revenue missing or non-positive in FY0 or FY0-5", [Y.ref([0, 5])],
                                          value=None)
    run = best = pairs = 0
    for k in range(9):
        a, b = Y.v(k, "revenue"), Y.v(k + 1, "revenue")
        if a is None or b is None:
            run = 0
            continue
        pairs += 1
        run = run + 1 if a < b else 0
        best = max(best, run)
    res["revenue_declines_consecutive_10y"] = {"value": best, "pairs_compared": pairs,
                                               "meaning": "longest run of consecutive annual declines",
                                               "inputs": [Y.ref(range(10), "revenue")]}
    window = range(10)
    ni = [Y.v(k, "net_income") for k in window if Y.v(k, "net_income") is not None]
    eps = [Y.eps(k) for k in window if Y.eps(k) is not None]
    eh = {"loss_years_10y": sum(1 for x in ni if x < 0), "years_available": len(ni),
          "eps_growth_10y": None, "inputs": [Y.ref(window), "price.splits"]}
    if len(eps) >= 6:
        end, start, eh["eps_growth_method"] = mean(eps[:3]), mean(eps[-3:]), "3-year averages at both ends"
    elif len(eps) >= 2:
        end, start, eh["eps_growth_method"] = eps[0], eps[-1], "single years (fewer than 6 EPS years)"
    else:
        end = start = None
    if start is not None and start > 0:
        eh["eps_growth_10y"] = r4(end / start - 1)
    else:
        eh["reason"] = "eps_growth_10y needs >= 2 EPS years and a positive starting EPS"
    res["earnings_history"] = eh
    return res


def cash_items(Y, price):
    res = {}
    notes = set()
    mc = market_cap(price, notes)
    oe0, da, capex = Y.oe(0), Y.v(0, "da"), Y.v(0, "capex")
    inp = [Y.ref([0]), "price.market_cap"]
    if oe0 is None:
        res["owner_earnings"] = null_obj("net_income, da or capex missing", inp, fy=Y.fy0, value=None,
                                         maintenance_capex=None,
                                         maintenance_capex_method="estimate: min(capex, da)", **{"yield": None})
    else:
        res["owner_earnings"] = {"fy": Y.fy0, "value": r2(oe0), "maintenance_capex": r2(min(capex, da)),
                                 "maintenance_capex_method": "estimate: min(capex, da)",
                                 "yield": r4(div(oe0, mc)), "inputs": inp}
    f0 = Y.fcf(0)
    res["fcf"] = {"fy": Y.fy0, "value": r2(f0), "yield": r4(div(f0, mc)), "inputs": inp} if f0 is not None \
        else null_obj("ocf or capex missing", inp, fy=Y.fy0, value=None, **{"yield": None})

    sy_notes = set()

    def comp(field):
        x = Y.v(0, field)
        if x is None:
            sy_notes.add("%s null treated as 0" % field)
            return 0.0
        return x

    if Y.row(0) is None or not mc:
        res["shareholder_yield"] = null_obj("latest year or market cap missing", inp, value=None)
    else:
        dv, bb = comp("dividends_paid"), comp("buybacks")
        dp = comp("debt_repaid") - comp("debt_issued")
        res["shareholder_yield"] = with_notes(
            {"value": r4((dv + bb + dp) / mc), "dividend_yield": r4(dv / mc), "buyback_yield": r4(bb / mc),
             "debt_paydown_yield": r4(dp / mc), "inputs": inp}, sy_notes)

    s0, s5 = Y.shares(0), Y.shares(5)
    rising = [int(Y.shares(k) > Y.shares(k + 1)) for k in range(3)
              if Y.shares(k) is not None and Y.shares(k + 1) is not None]
    dil = {"value": r4(s0 / s5 - 1) if s0 is not None and s5 else None, "split_adjusted": True,
           "rising_years_last3": sum(rising), "pairs_compared_last3": len(rising),
           "inputs": [Y.ref(range(6), "shares_diluted"), "price.splits"]}
    if dil["value"] is None:
        dil["reason"] = "shares_diluted missing in FY0 or FY0-5"
    res["dilution_5y"] = dil

    ret_inp = [Y.ref(range(5)), "price.market_cap", "price.market_cap_5y_ago"]
    ret_notes = set()
    mc5 = num(price.get("market_cap_5y_ago"))
    if mc5 is None:
        close5 = num(price.get("close_5y_ago"))
        sh5, sh_src = Y.shares_or_history(5)
        if close5 is not None and sh5 is not None:
            mc5 = close5 * sh5
            ret_inp = [Y.ref(range(5)), "price.market_cap", "price.close_5y_ago", sh_src, "price.splits"]
            ret_notes.add("market_cap_5y_ago derived: price.close_5y_ago x split-adjusted shares_diluted FY%d"
                          % Y.fy(5))
    den = 0.0
    for k in range(5):
        ni = Y.v(k, "net_income")
        if ni is None:
            den = None
            break
        dv = Y.v(k, "dividends_paid")
        if dv is None:
            ret_notes.add("dividends_paid null treated as 0")
            dv = 0.0
        den += ni - dv
    if den is None or mc is None or mc5 is None:
        res["retained_earnings_test"] = null_obj("net_income for five years, market cap, or market cap five years "
                                                 "ago (market_cap_5y_ago, or close_5y_ago x shares FY0-5) missing",
                                                 ret_inp,
                                                 value=None, window_years=5)
    elif den <= 0:
        res["retained_earnings_test"] = null_obj("nothing retained over five years (denominator <= 0)", ret_inp,
                                                 value=None, window_years=5, retained=r2(den))
    else:
        res["retained_earnings_test"] = {"value": r4((mc - mc5) / den), "window_years": 5,
                                         "retained": r2(den), "market_cap_change": r2(mc - mc5),
                                         "inputs": ret_inp}
    with_notes(res["retained_earnings_test"], ret_notes)

    gi = [Y.v(k, "goodwill_impairment") for k in range(5) if Y.row(k) is not None]
    gi_inp = [Y.ref(range(5), "goodwill_impairment")]
    n_null = sum(1 for x in gi if x is None)
    if n_null == len(gi):
        res["goodwill_impairment_5y"] = null_obj("goodwill_impairment null in every year checked", gi_inp,
                                                 value=None, years_checked=len(gi))
    else:
        res["goodwill_impairment_5y"] = {"value": sum(1 for x in gi if x is not None and x > 0),
                                         "years_checked": len(gi), "inputs": gi_inp}
        if n_null:
            res["goodwill_impairment_5y"]["note"] = "%d of %d years null, counted as no impairment" % (
                n_null, len(gi))

    g_inp = [Y.ref(range(3)), "price.splits"]
    eps3 = [Y.eps(k) for k in range(3)]
    eps_avg = mean(eps3) if all(e is not None for e in eps3) else None
    bvps = div(Y.v(0, "equity"), Y.shares(0))
    gn = {"value": None, "eps_3y_avg": r2(eps_avg), "bvps": r2(bvps), "inputs": g_inp}
    if eps_avg is None or bvps is None:
        gn["reason"] = "eps_diluted for three years, equity or shares_diluted missing"
    elif eps_avg <= 0 or bvps <= 0:
        gn["reason"] = "n/a: three-year average EPS or book value per share <= 0"
    else:
        gn["value"] = r2(math.sqrt(22.5 * eps_avg * bvps))
    res["graham_number"] = gn

    gb_notes = set()
    ebit, cash = Y.ebit(0), Y.v(0, "cash")
    ev = None
    if mc is not None and cash is not None and Y.row(0) is not None:
        ev = mc + Y.debt(0, "st_debt", gb_notes) + Y.debt(0, "lt_debt", gb_notes) - cash
    ey = {"value": r4(div(ebit, ev)) if ev and ev > 0 else None, "ebit": r2(ebit), "ev": r2(ev),
          "inputs": [Y.ref([0]), "price.market_cap"]}
    if ey["value"] is None:
        ey["reason"] = "EBIT, market cap or cash missing, or EV <= 0"
    res["earnings_yield"] = with_notes(ey, gb_notes)
    ppe, ca, cl = Y.v(0, "ppe_net"), Y.v(0, "current_assets"), Y.v(0, "current_liabilities")
    cap = None if ppe is None or ca is None or cl is None else ppe + ca - cl
    roc = {"value": r4(div(ebit, cap)) if cap and cap > 0 else None, "capital": r2(cap), "inputs": [Y.ref([0])]}
    if roc["value"] is None:
        roc["reason"] = "EBIT, ppe_net or working capital missing, or capital <= 0"
    res["return_on_capital"] = roc

    nd_notes = set()
    nd = None
    if cash is not None and Y.row(0) is not None:
        nd = Y.debt(0, "st_debt", nd_notes) + Y.debt(0, "lt_debt", nd_notes) - cash
    ndo = {"value": None, "net_debt": r2(nd), "owner_earnings": r2(oe0), "inputs": [Y.ref([0])]}
    if nd is None or oe0 is None:
        ndo["reason"] = "cash or owner earnings missing"
    elif oe0 <= 0:
        ndo["reason"] = "n/a: owner earnings <= 0"
    else:
        ndo["value"] = r4(nd / oe0)
    res["net_debt_to_owner_earnings"] = with_notes(ndo, nd_notes)
    return res


def series(Y, price_known):
    """Per-fiscal-year series for the dossier's ten-year table, newest first."""
    oe, fcf, cash, shares = [], [], [], []
    for r in Y.rows:
        k, fy = Y.fy0 - r["fy"], r["fy"]
        inp = [Y.ref([k])]
        o, da, capex = Y.oe(k), Y.v(k, "da"), Y.v(k, "capex")
        e = {"fy": fy, "value": r2(o), "maintenance_capex": r2(min(capex, da)) if o is not None else None,
             "method": "estimate: min(capex, da)",
             "value_full_capex": r2(Y.v(k, "net_income") + da - capex) if o is not None else None,
             "inputs": inp}
        if o is None:
            e["reason"] = "net_income, da or capex missing"
        oe.append(e)
        f = Y.fcf(k)
        fcf.append({"fy": fy, "value": r2(f), "inputs": inp} if f is not None else
                   {"fy": fy, "value": None, "inputs": inp, "reason": "ocf or capex missing"})
        notes = set()
        comps = {}
        for field in ("dividends_paid", "buybacks"):
            x = Y.v(k, field)
            if x is None:
                notes.add("%s null treated as 0" % field)
                x = 0.0
            comps[field] = x
        cash.append(with_notes({"fy": fy, "dividends_paid": r2(comps["dividends_paid"]),
                                "buybacks": r2(comps["buybacks"]),
                                "total": r2(comps["dividends_paid"] + comps["buybacks"]), "inputs": inp}, notes))
        sh = Y.shares(k) if price_known else None
        e = {"fy": fy, "value": r2(sh), "inputs": [Y.ref([k], "shares_diluted"), "price.splits"]}
        if sh is None:
            e["reason"] = "shares_diluted missing" if price_known else "price null (fetch failure; see fetch_errors)"
        shares.append(e)
    return {"owner_earnings_series": oe, "fcf_series": fcf, "cash_returned": cash, "shares_diluted_adjusted": shares}


def gate_inputs(Y, m):
    """Counts and ratios for G5 and items 2.3 / 2.4 / 2.5, so the scorer does no arithmetic."""
    notes = set()
    full = [e["value_full_capex"] for e in m["owner_earnings_series"] if Y.fy0 - e["fy"] < 5]
    known = [x for x in full if x is not None]
    ca, cl = Y.v(0, "current_assets"), Y.v(0, "current_liabilities")
    nca = None if ca is None or cl is None else ca - cl
    out = {"owner_earnings_negative_years_5y_full_capex": sum(1 for x in known if x < 0),
           "owner_earnings_years_checked_5y": len(known),
           "current_ratio": r4(div(ca, cl)), "net_current_assets": r2(nca),
           "lt_debt_to_net_current_assets": None,
           "loss_years_10y": m["earnings_history"]["loss_years_10y"],
           "years_available_10y": m["earnings_history"]["years_available"],
           "inputs": [Y.ref(range(5)), Y.ref(range(10), "net_income")]}
    reasons = []
    if len(known) < 5:
        reasons.append("owner earnings (full capex) available for %d of the last 5 years" % len(known))
    if nca is None:
        reasons.append("current_assets or current_liabilities missing")
    elif nca <= 0:
        reasons.append("lt_debt_to_net_current_assets: net current assets <= 0")
    elif Y.row(0) is not None:
        out["lt_debt_to_net_current_assets"] = r4(Y.debt(0, "lt_debt", notes) / nca)
    if reasons:
        out["reason"] = "; ".join(reasons)
    return with_notes(out, notes)


def trading_days_between(a, b):
    """Weekdays after date a up to and including date b (exchange holidays ignored)."""
    n, d = 0, a
    while d < b:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def freshness(Y, facts):
    out = {"value": None, "price_age_trading_days": None, "newer_10k_exists": None,
           "inputs": ["price.date", "retrieved", "filings_recent", Y.ref([0], "filed")],
           "note": "trading days = weekdays from price.date to the date of `retrieved`, holidays ignored; "
                   "only form 10-K counts as a newer filing; 2-5 trading days with no newer 10-K scores 0.5"}
    price = facts.get("price") if isinstance(facts.get("price"), dict) else {}

    def day(x):
        try:
            return datetime.date.fromisoformat(str(x)[:10])
        except ValueError:
            return None

    pdate, asof = day(price.get("date")), day(facts.get("retrieved"))
    filed0 = day((Y.row(0) or {}).get("filed"))
    reasons = []
    if pdate and asof:
        out["price_age_trading_days"] = trading_days_between(pdate, asof)
    else:
        reasons.append("price.date or retrieved missing")
    if filed0 and isinstance(facts.get("filings_recent"), list):
        out["newer_10k_exists"] = any(
            isinstance(f, dict) and f.get("form") == "10-K" and day(f.get("filed")) and day(f.get("filed")) > filed0
            for f in facts["filings_recent"])
    else:
        reasons.append("fundamentals.annual[0].filed or filings_recent missing")
    age, newer = out["price_age_trading_days"], out["newer_10k_exists"]
    if age is not None and age > 5:
        out["value"] = 0.0
    elif age is not None and newer is not None:
        out["value"] = 0.5 if newer or age > 1 else 1.0
    if out["value"] is None:
        out["reason"] = "; ".join(reasons)
    return out


# ---------- valuation (valuation.md) ----------

def flows(cf0, g, gt):
    out, cf = [], cf0
    for t in range(1, 11):
        gr = g if t <= 5 else g + (gt - g) * (t - 5) / 5.0
        cf *= 1 + gr
        out.append(cf)
    return out


def equity_value(cf0, g, r, gt):
    fl = flows(cf0, g, gt)
    pv = sum(c / (1 + r) ** t for t, c in enumerate(fl, 1))
    tv = fl[-1] * (1 + gt) / (r - gt)
    return pv + tv / (1 + r) ** 10, fl


def rates(macro, erp_arg):
    """(dgs10 %, erp %, erp source): --erp, else macro.erp, else the dated constant."""
    if erp_arg is not None:
        erp, src = erp_arg, "--erp"
    elif num(macro.get("erp")) is not None:
        erp, src = num(macro.get("erp")), "macro.erp"
    else:
        erp, src = ERP_DEFAULT, "metrics.py constant as of %s" % ERP_DEFAULT_DATE
    return num(macro.get("dgs10")), erp, src


def valuation(Y, facts, mos, erp_arg, roiic, horizons=HORIZONS, g_base=None):
    price = facts.get("price") if isinstance(facts.get("price"), dict) else {}
    macro = facts.get("macro") if isinstance(facts.get("macro"), dict) else {}
    sector = facts.get("sector_class")
    inputs = ["metrics.owner_earnings", Y.ref(range(10)), "macro", "price"]
    skeleton = {"params": {"mos": mos, "fade_from_year": 6}, "cash_flow_basis": "owner_earnings",
                "scenarios": {s: {"g": None, "r": None} for s in ("bear", "base", "bull")},
                "fair_value_today": {"bear": None, "base": None, "bull": None},
                "by_horizon": {hkey(h): {"bear": None, "base": None, "bull": None} for h in horizons},
                "buy_zone_below": None, "sell_zone_above": None, "implied_growth_at_price": None}

    def fail(reason):
        out = dict(skeleton)
        out.update(inputs=inputs, reason=reason)
        return out

    if not isinstance(facts.get("macro"), dict):
        return fail("macro null (fetch failure; see fetch_errors)")
    if not isinstance(facts.get("price"), dict):
        return fail("price null (fetch failure; see fetch_errors): splits and price unavailable")
    if sector in NA_SECTORS:
        return fail("owner-earnings model n/a for sector_class %s (score SKILL step 1)" % sector)
    notes = set()
    dgs10, erp, erp_src = rates(macro, erp_arg)
    if dgs10 is None:
        return fail("macro.dgs10 missing")
    oes = [Y.oe(k) for k in range(3) if Y.oe(k) is not None]
    if not oes:
        return fail("owner earnings missing for the last three fiscal years")
    if len(oes) < 3:
        notes.add("CF_0 averages %d year(s), not 3" % len(oes))
    cf0 = mean(oes)
    if cf0 <= 0:
        return fail("CF_0 (mean owner earnings, last three years) <= 0")
    shares = Y.shares(0)
    cash = Y.v(0, "cash")
    if not shares or shares <= 0 or cash is None:
        return fail("shares_diluted or cash missing in the latest year")
    net_cash = cash - Y.debt(0, "st_debt", notes) - Y.debt(0, "lt_debt", notes)

    r_base = dgs10 / 100 + erp / 100
    r_bear = r_base + 0.02
    gt = min(0.025, dgs10 / 100)
    if r_base <= gt:
        return fail("r_base <= terminal growth; Gordon value undefined")
    oe0, oe5 = Y.oe(0), Y.oe(5)
    if oe0 is not None and oe5 is not None and oe0 > 0 and oe5 > 0:
        cagr = (oe0 / oe5) ** 0.2 - 1
    else:
        cagr = None
        notes.add("5-yr owner-earnings CAGR undefined (missing or non-positive endpoint): base g = 0")
    g = clamp(cagr, 0.0, 0.15) if cagr is not None else 0.0
    paid = (Y.v(0, "dividends_paid") or 0.0) + (Y.v(0, "buybacks") or 0.0)
    reinvest = clamp(1 - paid / oe0, 0.0, 1.0) if oe0 is not None and oe0 > 0 else 0.0
    if roiic is not None:
        cap, cap_src = roiic * reinvest, "ROIIC_5y x reinvestment rate"
    else:
        cap, cap_src = 0.10, "default 0.10 (ROIIC_5y unavailable)"
    g = max(0.0, min(g, cap))
    if g_base is not None:
        g = g_base
    g_bull = min(g + 0.03, 0.20)
    g_bear = g / 2
    bear_basis = []
    for k in range(3):
        o, f = Y.oe(k), Y.fcf(k)
        if o is not None:
            bear_basis.append(min(o, f) if f is not None else o)
    cf0_bear = mean(bear_basis)

    def scen(c0, gg, rr):
        v, fl = equity_value(c0, gg, rr, gt)
        v0 = (v + net_cash) / shares
        hz = {}
        for h in horizons:
            n = int(math.floor(h))
            hz[h] = (v0 * (1 + rr) ** h - sum(fl[t - 1] / shares * (1 + rr) ** (h - t) for t in range(1, n + 1))
                     - ((h - n) * fl[n] / shares if h > n else 0.0))
        return v0, hz

    res = {"base": scen(cf0, g, r_base), "bull": scen(cf0, g_bull, r_base)}
    if cf0_bear is not None and cf0_bear > 0:
        res["bear"] = scen(cf0_bear, g_bear, r_bear)
    else:
        res["bear"] = (None, {h: None for h in horizons})
        notes.add("bear CF_0 (min of owner earnings and FCF) <= 0: bear values null")

    last = num(price.get("last"))
    implied, implied_reason = None, None
    if last is None or last <= 0:
        implied_reason = "price.last missing"
    else:
        def f(gg):
            return (equity_value(cf0, gg, r_base, gt)[0] + net_cash) / shares - last
        lo, hi = G_LO, G_HI
        if f(lo) > 0 or f(hi) < 0:
            implied_reason = "price outside the model's range for g in [-0.20, 0.40]"
        else:
            for _ in range(200):
                mid = (lo + hi) / 2
                if f(mid) < 0:
                    lo = mid
                else:
                    hi = mid
            implied = (lo + hi) / 2

    out = {
        "params": {"r_base": r4(r_base), "r_bear": r4(r_bear), "terminal_g": r4(gt), "mos": mos,
                   "fade_from_year": 6, "dgs10": dgs10, "erp": erp, "erp_source": erp_src,
                   "horizons": [hkey(h) for h in horizons], "horizon_method": HORIZON_METHOD,
                   "g_base_source": "what-if" if g_base is not None else "model",
                   "cf0": r2(cf0), "cf0_bear": r2(cf0_bear), "cf0_years": len(oes),
                   "oe_cagr_5y": r4(cagr), "reinvestment_rate": r4(reinvest), "growth_cap": r4(cap),
                   "growth_cap_source": cap_src, "net_cash": r2(net_cash), "shares_diluted": r2(shares)},
        "cash_flow_basis": "owner_earnings",
        "scenarios": {"bear": {"g": r4(g_bear), "r": r4(r_bear), "basis": "min(owner earnings, fcf)"},
                      "base": {"g": r4(g), "r": r4(r_base)}, "bull": {"g": r4(g_bull), "r": r4(r_base)}},
        "fair_value_today": {s: r2(res[s][0]) for s in ("bear", "base", "bull")},
        "by_horizon": {hkey(h): {s: r2(res[s][1][h]) for s in ("bear", "base", "bull")} for h in horizons},
        "buy_zone_below": r2(res["base"][0] * (1 - mos)),
        "sell_zone_above": r2(res["bull"][0]),
        "implied_growth_at_price": r4(implied),
        "agreement": r4(clamp(1 - (res["bull"][0] - res["bear"][0]) / res["base"][0], 0.0, 1.0))
        if res["bear"][0] is not None and res["base"][0] and res["base"][0] > 0 else None,
        "inputs": inputs,
    }
    if implied_reason:
        notes.add("implied_growth_at_price null: " + implied_reason)
    return with_notes(out, notes)


# ---------- multiples, outlook, calibration (rules/outlook.md §1, §2, §4) ----------

RATIOS = ("pe", "pfcf", "ev_ebit", "ps")
REVERSION_YEARS = 10.0      # base multiple reaches the 10-year median at year 10, linearly
MONTHS_DEFAULT_DAYS = 90
METHOD_NOTE = ("Expected yearly return = (EPS_0 x (1+g)^h x multiple_h / price_0)^(1/h) - 1 + shareholder yield "
               "(decomposition per Bogle and Nolan 2015, JPM 42(1); multiple mean reversion per Campbell and Shiller "
               "2001 and GMO 2Q 2017; analyst growth caution per Damodaran). Accuracy figures in the sources are "
               "in-sample.")
CONSENSUS_BASE_RATE = ("Bradshaw, Brown and Huang (2013): 38% of twelve-month analyst targets are met at the horizon, "
                       "64% at some point within it")
MULT_BASIS = ("price = price.close_at[period_end].close (Yahoo closes are split-adjusted to today's basis); EPS and "
              "diluted shares split-adjusted from price.splits; market cap = price x diluted shares; EV = market "
              "cap + st_debt + lt_debt - cash; a ratio is null when its denominator <= 0; current uses price.last "
              "and price.market_cap with the latest fiscal year's figures")


def pctl(xs, q):
    s = sorted(xs)
    if not s:
        return None
    pos = q * (len(s) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def day(x):
    try:
        return datetime.date.fromisoformat(str(x)[:10])
    except ValueError:
        return None


def close_at(price, period_end):
    """(close, adj_close, trading date) at a fiscal period end from price.close_at."""
    ca = price.get("close_at") if isinstance(price, dict) else None
    e = ca.get(period_end) if isinstance(ca, dict) and isinstance(period_end, str) else None
    if not isinstance(e, dict):
        return None, None, None
    return num(e.get("close")), num(e.get("adj_close")), e.get("date")


def ratio_values(Y, k, px, mcap):
    notes = set()
    cash = Y.v(k, "cash")
    ev = None
    if mcap is not None and cash is not None and Y.row(k) is not None:
        ev = mcap + Y.debt(k, "st_debt", notes) + Y.debt(k, "lt_debt", notes) - cash

    def pos(a, b):
        return a / b if a is not None and b is not None and b > 0 else None
    return {"pe": pos(px, Y.eps(k)), "pfcf": pos(mcap, Y.fcf(k)),
            "ev_ebit": pos(ev, Y.v(k, "operating_income")), "ps": pos(mcap, Y.v(k, "revenue"))}


def multiple_history(Y, price):
    """[(fy, period_end, price, raw ratios)] for every fiscal year within ten of the latest."""
    out = []
    for k in range(10):
        r = Y.row(k)
        if r is None:
            continue
        px = close_at(price, r.get("period_end"))[0]
        sh = Y.shares(k)
        mc = px * sh if px is not None and sh is not None else None
        out.append((r["fy"], r.get("period_end"), px, ratio_values(Y, k, px, mc)))
    return out


def ratio_stats(hist, current):
    vals = [v for v in hist if v is not None]
    out = {"current": r4(current), "median_10y": r4(pctl(vals, 0.5)), "p25": r4(pctl(vals, 0.25)),
           "p75": r4(pctl(vals, 0.75)), "low": r4(min(vals)) if vals else None,
           "high": r4(max(vals)) if vals else None, "years_available": len(vals)}
    if not vals:
        out["reason"] = "no fiscal year with a year-end price and a positive denominator"
    return out


def multiples(Y, facts):
    price = facts.get("price")
    inputs = [Y.ref(range(10)), "price.close_at", "price.splits", "price.last", "price.market_cap"]
    if not isinstance(price, dict):
        return null_obj(PRICE_NULL, inputs, years=[], basis_note=MULT_BASIS,
                        **{x: ratio_stats([], None) for x in RATIOS})
    hist = multiple_history(Y, price)
    cur = ratio_values(Y, 0, num(price.get("last")), market_cap(price, set()))
    out = {"years": [dict({"fy": fy, "period_end": pe, "price": r2(px)}, **{x: r4(v[x]) for x in RATIOS})
                     for fy, pe, px, v in hist]}
    for x in RATIOS:
        out[x] = ratio_stats([v[x] for _, _, _, v in hist], cur[x])
    out.update(basis_note=MULT_BASIS, inputs=inputs)
    if not any(px is not None for _, _, px, _ in hist):
        out["reason"] = "price.close_at has no fiscal period-end close"
    return out


def cagr_span(f, max_span=5, min_span=2):
    """(CAGR from f(n) to f(0), n) over the longest span n in [min_span, max_span] with both ends > 0."""
    a = f(0)
    if a is None or a <= 0:
        return None, None
    for n in range(max_span, min_span - 1, -1):
        b = f(n)
        if b is not None and b > 0:
            return (a / b) ** (1.0 / n) - 1, n
    return None, None


def sales_ps(Y, k):
    return div(Y.v(k, "revenue"), Y.shares(k))


def path_multiples(cur, med, p25, p75, h):
    """bear p25 held; base drifts linearly from current to the median over REVERSION_YEARS; bull holds
    max(current, p75) to year 2, then drifts linearly to p75 at year 10 (outlook.md §1)."""
    top = max(cur, p75)
    bull = top if h <= 2 else top + (p75 - top) * min((h - 2) / 8.0, 1.0)
    return {"bear": p25, "base": cur + (med - cur) * min(h / REVERSION_YEARS, 1.0), "bull": bull}


def decomp(x0, g, mult, h, price0, sy):
    """outlook.md §1: price_h and expected yearly return for one scenario."""
    if None in (x0, g, mult, price0) or price0 <= 0:
        return None, None
    ph = x0 * (1 + g) ** h * mult
    if ph <= 0:
        return ph, None
    return ph, (ph / price0) ** (1.0 / h) - 1 + sy


def verdict(cagr, r):
    if cagr is None or r is None:
        return None
    c, rr = r4(cagr), r4(r)
    return "attractive" if c >= rr + 0.02 - 1e-12 else "expensive" if c < rr - 0.02 - 1e-12 else "fair"


def consensus_growth(cons, eps0):
    """(next-year growth, 5-year growth, 2-year growth, method) from facts.consensus; any may be None."""
    if not isinstance(cons, dict) or cons.get("available") is False:
        return None, None, None, None
    gr = cons.get("growth") if isinstance(cons.get("growth"), dict) else {}
    g1, g5 = num(gr.get("next_year")), num(gr.get("next_5y_per_year"))
    eps = cons.get("eps") if isinstance(cons.get("eps"), dict) else {}
    nxt = eps.get("next_fy") if isinstance(eps.get("next_fy"), dict) else {}
    e2 = num(nxt.get("estimate"))
    if e2 is not None and e2 > 0 and eps0 is not None and eps0 > 0:
        return g1, g5, (e2 / eps0) ** 0.5 - 1, "(consensus next-FY EPS / EPS_0)^(1/2) - 1"
    parts = [x for x in (g1, g5) if x is not None]
    if parts:
        return g1, g5, mean(parts), "mean of consensus next-year and 5-year growth"
    return g1, g5, None, None


def scenario_g(hist, cons1, cons2):
    """outlook.md §1 g row. bear also capped at base (the 0% floor can otherwise exceed a negative base)."""
    base_parts = [x for x in (hist, cons2) if x is not None]
    if not base_parts:
        return None
    base = min(mean(base_parts), 0.25)
    bear_c = [x - 0.03 for x in (hist, cons1) if x is not None]
    bear = min(max(0.0, min(bear_c)) if bear_c else 0.0, base)
    bull = min(max(base_parts) + 0.03, 0.30)
    return {"bear": bear, "base": base, "bull": bull}


def trend_state(price, mom):
    p, ma50, ma200 = num(price.get("last")), num(mom.get("ma50")), num(mom.get("ma200"))
    if None in (p, ma50, ma200) or ma200 <= 0:
        return None
    if abs(p / ma200 - 1) < 0.01 or abs(ma50 / ma200 - 1) < 0.01:
        return "no trend"
    if p > ma200 and ma50 > ma200:
        return "trend up"
    if p < ma200 and ma50 < ma200:
        return "trend down"
    return "no trend"


def months(Y, facts, horizons):
    price = facts["price"]
    opt = facts.get("options") if isinstance(facts.get("options"), dict) else {}
    mom = facts.get("momentum") if isinstance(facts.get("momentum"), dict) else {}
    market = facts.get("market") if isinstance(facts.get("market"), dict) else {}
    short = [h for h in horizons if h < 1]
    days = int(round(min(short) * 365)) if short else MONTHS_DEFAULT_DAYS
    last, pdate = num(price.get("last")), day(price.get("date"))
    end = pdate + datetime.timedelta(days=days) if pdate else None
    out = {"horizon_days": days, "inputs": ["price.last", "options", "momentum", "market.spy", "consensus",
                                             "filings_recent"]}
    dte, move, iv = num(opt.get("days_to_expiry")), num(opt.get("implied_move_abs")), num(opt.get("atm_iv"))
    if last is not None and dte is not None and move is not None and days <= dte <= days + 35:
        out["range_1sd"] = {"low": r2(last - move), "high": r2(last + move), "expiry": opt.get("expiry_used"),
                            "method": "options.implied_move to the first listed expiry after the horizon"}
    elif last is not None and iv is not None:
        mv = last * iv * math.sqrt(days / 365.0)
        out["range_1sd"] = {"low": r2(last - mv), "high": r2(last + mv),
                            "expiry": end.isoformat() if end else None,
                            "method": "price.last x options.atm_iv x sqrt(days/365), 365-day count; implied "
                                      "variance exceeds realised on average, so the range is upper-biased"}
    else:
        out["range_1sd"] = {"low": None, "high": None, "expiry": None, "reason": "options.atm_iv or price.last missing"}
    out["trend"] = trend_state(price, mom)
    if out["trend"] is None:
        out["trend_reason"] = "momentum.ma50 / ma200 or price.last missing"
    elif mom.get("as_of"):
        out["trend_as_of"] = mom.get("as_of")
    spy = market.get("spy") if isinstance(market.get("spy"), dict) else {}
    s24, v30, v1y = num(spy.get("return_24m")), num(mom.get("realized_vol_30d")), num(mom.get("realized_vol_1y"))
    out["regime"] = None if None in (s24, v30, v1y) else (
        "crash regime" if s24 < 0 and v30 > 1.5 * v1y else "normal")
    if out["regime"] is None:
        out["regime_reason"] = "market.spy.return_24m or momentum realized volatility missing"
    events = []
    ne = day(opt.get("next_earnings_date"))
    if ne:
        events.append({"event": "earnings", "date": ne.isoformat(), "source": "options.next_earnings_date",
                       "inside_horizon": bool(end and ne <= end)})
    tenk = [day(f.get("filed")) for f in facts.get("filings_recent") or []
            if isinstance(f, dict) and f.get("form") == "10-K" and day(f.get("filed"))]
    last10k = max(tenk) if tenk else day((Y.row(0) or {}).get("filed"))
    if last10k:
        nk = last10k + datetime.timedelta(days=365)
        events.append({"event": "10-K", "date": nk.isoformat(), "source": "estimate: last 10-K filed + 365 days",
                       "inside_horizon": bool(end and nk <= end)})
    out["events"] = events
    cons = facts.get("consensus") if isinstance(facts.get("consensus"), dict) else {}
    rv = cons.get("revisions_90d") if isinstance(cons.get("revisions_90d"), dict) else None
    if rv is None:
        out["revisions"] = {"eps_next_fy_up": None, "eps_next_fy_down": None, "direction": None,
                            "reason": "consensus.revisions_90d unavailable"}
    else:
        up, dn = num(rv.get("eps_next_fy_up")), num(rv.get("eps_next_fy_down"))
        out["revisions"] = {"eps_next_fy_up": up, "eps_next_fy_down": dn,
                            "direction": None if up is None or dn is None else
                            "up" if up > dn else "down" if dn > up else "flat"}
    return out


def outlook(Y, facts, m, erp_arg, horizons):
    price = facts.get("price")
    macro = facts.get("macro") if isinstance(facts.get("macro"), dict) else {}
    inputs = [Y.ref(range(10)), "metrics.multiples", "metrics.shareholder_yield", "macro", "price", "consensus",
              "options", "momentum"]
    long_h = [h for h in horizons if h >= 1]
    empty_h = {hkey(h): {s: {"price": None, "cagr": None} for s in ("bear", "base", "bull")} for h in long_h}
    for v in empty_h.values():
        v["verdict"] = None
    if not isinstance(price, dict):
        return null_obj(PRICE_NULL, inputs, params=None, horizons=empty_h, months=None, method_note=METHOD_NOTE,
                        consensus_base_rate=CONSENSUS_BASE_RATE)
    notes = set()
    dgs10, erp, _ = rates(macro, erp_arg)
    r_base = None if dgs10 is None else dgs10 / 100 + erp / 100
    if r_base is None:
        notes.add("macro.dgs10 missing: verdicts null")
    price0 = num(price.get("last"))
    eps0 = Y.eps(0)
    sy = m["shareholder_yield"]
    dy, by = sy.get("dividend_yield"), sy.get("buyback_yield")
    if dy is None or by is None:
        notes.add("shareholder yield (dividends + buybacks / market cap) unavailable: treated as 0")
    syield = (dy or 0.0) + (by or 0.0)
    mult = m["multiples"]
    cons1, cons5, cons2, cons2_m = consensus_growth(facts.get("consensus"), eps0)
    if eps0 is not None and eps0 > 0:
        basis, x0 = "pe", eps0
        hist, hist_n = cagr_span(Y.eps)
        g_inputs = {"eps_cagr_5y": r4(hist), "eps_cagr_years": hist_n}
    else:
        basis, x0 = "ps", sales_ps(Y, 0)
        hist, hist_n = cagr_span(lambda k: sales_ps(Y, k))
        g_inputs = {"eps_cagr_5y": None, "sales_per_share_cagr_5y": r4(hist), "sales_cagr_years": hist_n}
        cons1 = cons2 = None
        notes.add("EPS_0 <= 0 or missing: price-to-sales basis with sales-per-share growth and the 10-year "
                  "P/S range; consensus EPS growth not used")
    if hist_n is not None and hist_n < 5:
        notes.add("history growth over %d years, not 5" % hist_n)
    g_inputs.update(consensus_next_year=r4(cons1), consensus_5y=r4(cons5), consensus_2y=r4(cons2),
                    consensus_2y_method=cons2_m)
    if cons2 is None and basis == "pe":
        notes.add("consensus unavailable: base g uses history alone")
    gs = scenario_g(hist, cons1, cons2)
    st = mult[basis]
    cur, med, p25, p75 = (num(st.get(x)) for x in ("current", "median_10y", "p25", "p75"))
    if st.get("years_available", 0) < 5:
        notes.add("%d years of %s multiples (fewer than 5): lower confidence" % (st.get("years_available", 0), basis))
    params = {"r_base": r4(r_base), "eps_0": r2(eps0), "price_0": r2(price0), "shareholder_yield": r4(syield),
              "g": dict({s: r4(gs[s]) if gs else None for s in ("bear", "base", "bull")}, inputs=g_inputs),
              "multiple": {"basis": basis, "current": r4(cur), "median": r4(med), "p25": r4(p25), "p75": r4(p75),
                           "high": st.get("high"), "years_available": st.get("years_available", 0),
                           "reversion_years": REVERSION_YEARS,
                           "bear_path": "p25 held (peer median unavailable inside metrics.py)",
                           "base_path": "linear drift from current to the 10-year median, reached at year 10",
                           "bull_path": "max(current, p75) held to year 2, then linear drift to p75 at year 10 "
                                        "(p75 beyond)"}}
    if basis == "ps":
        params["sales_per_share_0"] = r2(x0)
    out = {"params": params, "horizons": empty_h, "method_note": METHOD_NOTE,
           "consensus_base_rate": CONSENSUS_BASE_RATE, "inputs": inputs}
    reasons = []
    if gs is None:
        reasons.append("no growth input (history CAGR and consensus both unavailable)")
    if None in (cur, med, p25, p75):
        reasons.append("%s multiples unavailable (current or 10-year range)" % basis)
    if x0 is None or price0 is None:
        reasons.append("EPS_0 / sales per share or price.last missing")
    if not reasons:
        hz = {}
        for h in long_h:
            mp = path_multiples(cur, med, p25, p75, h)
            e = {}
            for s in ("bear", "base", "bull"):
                ph, c = decomp(x0, gs[s], mp[s], h, price0, syield)
                e[s] = {"price": r2(ph), "cagr": r4(c), "multiple": r4(mp[s])}
            e["verdict"] = verdict(None if e["base"]["cagr"] is None else e["base"]["cagr"], r_base)
            hz[hkey(h)] = e
        out["horizons"] = hz
    else:
        out["reason"] = "; ".join(reasons)
    out["months"] = months(Y, facts, horizons)
    return with_notes(out, notes)


def calibration(Y, facts, m, mos, erp_arg):
    price = facts.get("price")
    inputs = ["fundamentals.annual", "price.close_at", "price.last", "price.splits", "macro"]
    blank = {"fy_then": None, "strict_value_then": None, "price_then": None, "ratio_price_to_value": None,
             "realized_cagr_since": None, "base_forecast_then": None, "error_pp": None}
    if not isinstance(price, dict):
        return null_obj(PRICE_NULL, inputs, **blank)
    ks = [k for k in range(3, 10) if Y.row(k) is not None]
    if not ks:
        return null_obj("fewer than four fiscal years: nothing three or more years back", inputs, **blank)
    k = 5 if Y.row(5) is not None else max(ks)
    fy_then, row_then = Y.fy(k), Y.row(k)
    out = dict(blank, fy_then=fy_then, years_back=k, inputs=[Y.ref(range(k, 10))] + inputs[1:])
    notes = {"strict value uses today's r and terminal g, not the rates of FY%d" % fy_then}
    if k != 5:
        notes.add("fiscal year five years back unavailable: used the oldest year %d back" % k)
    Yt = Y.truncate(fy_then)
    raw_t = roic_series(Yt)[1]
    ro = roiic_5y(Yt, raw_t)
    roiic = None
    if ro.get("value") is not None:
        a, b = raw_t[0], raw_t[5]
        roiic = (a[0] - b[0]) / (a[1] - b[1])
    c, n = cagr_span(Yt.oe)
    g = clamp(c, 0.0, 0.15) if c is not None else 0.0
    oe_t = Yt.oe(0)
    paid = (Yt.v(0, "dividends_paid") or 0.0) + (Yt.v(0, "buybacks") or 0.0)
    reinvest = clamp(1 - paid / oe_t, 0.0, 1.0) if oe_t is not None and oe_t > 0 else 0.0
    g = max(0.0, min(g, roiic * reinvest if roiic is not None else 0.10))
    notes.add("strict growth then: owner-earnings CAGR over %s, clamped [0, 0.15], capped %s" % (
        "%d years" % n if n else "no span (0)", "at ROIIC x reinvestment" if roiic is not None else "at 0.10"))
    val = valuation(Yt, facts, mos, erp_arg, roiic, (1.0,), g_base=g)
    v_then = val["fair_value_today"]["base"]
    px, adj, pdate_then = close_at(price, row_then.get("period_end"))
    last, now = num(price.get("last")), day(price.get("date"))
    then = day(pdate_then) or day(row_then.get("period_end"))
    reasons = []
    if v_then is None:
        reasons.append("strict value then unavailable: %s" % val.get("reason"))
    if px is None:
        reasons.append("price.close_at missing for FY%d period end" % fy_then)
    out.update(strict_value_then=v_then, strict_g_then=r4(g), price_then=r2(px), price_then_date=pdate_then)
    if v_then is not None and v_then > 0 and px is not None:
        out["ratio_price_to_value"] = r4(px / v_then)
    yrs = (now - then).days / 365.25 if now and then else None
    realized = None
    if px is not None and last is not None and yrs and yrs > 0:
        if adj is not None and adj > 0:
            realized = (last / adj) ** (1 / yrs) - 1
            out["realized_basis"] = "total return incl. dividends (price.last vs Yahoo adj_close then)"
        else:
            realized = (last / px) ** (1 / yrs) - 1
            out["realized_basis"] = "price return only (no dividend-adjusted close then)"
        out["realized_cagr_since"] = r4(realized)
        out["years_elapsed"] = r4(yrs)
    else:
        reasons.append("price.last, price.date or the close then missing")
    # §1 base case as of fy_then: history-only g, multiples as of then
    eps_t = Yt.eps(0)
    hist_then = [v for fy, _, _, v in multiple_history(Y, price) if fy <= fy_then]
    if eps_t is not None and eps_t > 0:
        basis, x0 = "pe", eps_t
        gh, gn = cagr_span(Yt.eps)
    else:
        basis, x0 = "ps", sales_ps(Yt, 0)
        gh, gn = cagr_span(lambda j: sales_ps(Yt, j))
    vals = [v[basis] for v in hist_then if v[basis] is not None]
    sh_t = Yt.shares(0)
    mc_t = px * sh_t if px is not None and sh_t else None
    cur_t = ratio_values(Yt, 0, px, mc_t)[basis]
    sy_t = div((Yt.v(0, "dividends_paid") or 0.0) + (Yt.v(0, "buybacks") or 0.0), mc_t) or 0.0
    forecast = None
    if gh is not None and vals and cur_t is not None and yrs and yrs > 0:
        gb = min(gh, 0.25)
        mult = path_multiples(cur_t, pctl(vals, 0.5), pctl(vals, 0.25), pctl(vals, 0.75), yrs)["base"]
        _, forecast = decomp(x0, gb, mult, yrs, px, sy_t)
        out["base_forecast_then"] = {"basis": basis, "g": r4(gb), "g_years": gn, "multiple_then": r4(cur_t),
                                     "median_then": r4(pctl(vals, 0.5)), "years_of_multiples": len(vals),
                                     "shareholder_yield_then": r4(sy_t), "cagr": r4(forecast)}
    else:
        reasons.append("base forecast then needs a history growth rate and multiples as of FY%d" % fy_then)
    if realized is not None and forecast is not None:
        out["error_pp"] = r4((realized - forecast) * 100)
    name = facts.get("ticker") or "the stock"
    words = []
    if out["ratio_price_to_value"] is not None:
        rv = out["ratio_price_to_value"]
        words.append("%d years back (FY%d) the strict model valued %s at $%.2f a share against a price of $%.2f "
                     "(%.2fx the value)" % (k, fy_then, name, v_then, px, rv))
    if realized is not None:
        words.append("it returned %.1f%% a year since (%s)" % (realized * 100, out["realized_basis"].split(" (")[0]))
    if forecast is not None:
        words.append("the base case then forecast %.1f%% a year%s" % (
            forecast * 100, ", an error of %+.1f pp" % out["error_pp"] if out["error_pp"] is not None else ""))
    out["note"] = ("; ".join(words) + ".") if words else None
    if reasons:
        out["reason"] = "; ".join(reasons)
    out["assumptions"] = sorted(notes)
    return out


# ---------- driver ----------

def compute(facts, mos=0.30, erp=None, horizons=HORIZONS, g_base=None):
    fund = facts.get("fundamentals") if isinstance(facts.get("fundamentals"), dict) else {}
    price = facts.get("price") if isinstance(facts.get("price"), dict) else {}
    Y = Years(fund.get("annual"), price.get("splits"), fund.get("shares_history"))
    sector = facts.get("sector_class")
    m = {"piotroski": piotroski(Y), "altman": altman(Y, sector, price), "beneish": beneish(Y, sector),
         "accrual_ratio": accrual_ratio(Y)}
    m["roic"], raw = roic_series(Y)
    m["roiic_5y"] = roiic_5y(Y, raw)
    m.update(growth_items(Y))
    m.update(cash_items(Y, price))
    m.update(series(Y, isinstance(facts.get("price"), dict)))
    m["gate_inputs"] = gate_inputs(Y, m)
    m["freshness"] = freshness(Y, facts)
    raw_roiic = None
    if m["roiic_5y"].get("value") is not None:
        a, b = raw[0], raw[5]
        raw_roiic = (a[0] - b[0]) / (a[1] - b[1])
    m["valuation"] = valuation(Y, facts, mos, erp, raw_roiic, horizons, g_base)
    m["multiples"] = multiples(Y, facts)
    m["outlook"] = outlook(Y, facts, m, erp, horizons)
    m["calibration"] = calibration(Y, facts, m, mos, erp)
    if not isinstance(facts.get("price"), dict):
        blank_price_dependent(m, facts.get("sector_class"))
    return m


PRICE_NULL = "price null (fetch failure; see fetch_errors)"
# metric -> fields that need price (market cap, last price or splits)
PRICE_FIELDS = {
    "owner_earnings": ["yield"], "fcf": ["yield"],
    "shareholder_yield": ["value", "dividend_yield", "buyback_yield", "debt_paydown_yield"],
    "dilution_5y": ["value", "rising_years_last3"], "retained_earnings_test": ["value"],
    "graham_number": ["value", "eps_3y_avg", "bvps"], "earnings_yield": ["value", "ev"],
    "earnings_history": ["eps_growth_10y"],
}


def blank_price_dependent(m, sector):
    """Without price there is no market cap and no split list: null every field that needs them."""
    def blank(obj, fields, why):
        for f in fields:
            obj[f] = None
        obj["reason"] = why if not obj.get("reason") else "%s; %s" % (why, obj["reason"])
    for key, fields in PRICE_FIELDS.items():
        blank(m[key], fields, PRICE_NULL)
    if sector == "manufacturer":
        blank(m["altman"], ["value", "zone"], PRICE_NULL + ": market cap needed for X4")
    p = m["piotroski"]
    if "eq_offer fallback" in (p.get("note") or ""):
        p["signals"]["eq_offer"] = None
        blank(p, ["score"], PRICE_NULL + ": eq_offer fallback needs split-adjusted shares")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Derive metrics.* in facts.json")
    ap.add_argument("facts")
    ap.add_argument("--out")
    ap.add_argument("--mos", type=float, default=0.30)
    ap.add_argument("--erp", type=float, default=None, help="equity risk premium in percent, e.g. 4.2")
    ap.add_argument("--horizons", default="1,2,5,10", help="comma list of years in (0, 10], e.g. 0.25,1,3,7.5")
    ap.add_argument("--g-base", type=float, default=None, help="what-if base growth (decimal, e.g. 0.06)")
    a = ap.parse_args(argv)
    try:
        horizons = parse_horizons(a.horizons)
    except ValueError as e:
        print(json.dumps({"error": "--horizons: %s" % e}))
        return 1
    try:
        with open(a.facts, encoding="utf-8") as fh:
            facts = json.load(fh)
        if not isinstance(facts, dict):
            raise ValueError("top level is not a JSON object")
    except (OSError, ValueError) as e:
        print(json.dumps({"error": "cannot read %s: %s" % (a.facts, e)}))
        return 1
    facts["metrics"] = compute(facts, a.mos, a.erp, horizons, a.g_base)
    out = a.out or a.facts
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=2)
        fh.write("\n")
    print(json.dumps({"ok": True, "out": out, "metrics": sorted(facts["metrics"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
