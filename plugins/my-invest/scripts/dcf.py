#!/usr/bin/env python3
"""dcf.py - a three-scenario discounted cash flow for one ticker from its SEC annual facts, into `valuations`.

Usage: dcf.py TICKER [--run-id N] [--growth lo,base,hi] [--margin lo,base,hi] [--discount lo,base,hi]
                     [--terminal g] [--years 5] [--sims 2000] [--seed 7] [--project P] [--md]
Rates are percent (--growth 5,10,15 means 5%, 10%, 15%).

Inputs come from fundamentals_annual (up to the latest five fiscal years), the 10-year Treasury yield from
`macro` (DGS10) and the 3-year beta from `stats`. Every assumption a flag does not set is derived from the
history, clamped to a sane range, and recorded in `inputs` with whether it was overridden, so the agent can
read and argue with it. Free cash flow = revenue x margin x (1 - tax) + depreciation - capex, both grown with
revenue from their latest ratios; reinvestment is 0. Terminal value is Gordon growth on the last forecast
year; the forecast never exceeds config max_horizon_years. A Monte Carlo on the base case gives p10/p50/p90.
With it come the cross-checks: a sensitivity grid of the base value, the reverse DCF (the growth today's price
assumes), and the trailing P/E against the stock's own five-year range and the stored peers, plus P/FCF and
EV/EBIT; the implied values are stored as `reverse_dcf`, `pe_range` and `pe_peers` rows beside the DCF rows.
"""
import json
import random
import sys

import calc
import common
import db

SCRIPT = "dcf.py"
REVENUE = ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet")
OPINC = ("OperatingIncomeLoss",)
TAX = ("IncomeTaxExpenseBenefit",)
INTEREST = ("InterestExpense",)
DEPREC = ("DepreciationDepletionAndAmortization",)
CAPEX = ("PaymentsToAcquirePropertyPlantAndEquipment",)
SHARES = ("WeightedAverageNumberOfDilutedSharesOutstanding", "EntityCommonStockSharesOutstanding")
EPS = ("EarningsPerShareDiluted",)
OCF = ("NetCashProvidedByUsedInOperatingActivities",)
REVERSE_RANGE = (-0.5, 1.0)  # growth a year the reverse DCF searches between
PE_YEARS = 5
CASH = ("CashAndCashEquivalentsAtCarryingValue",)
CASH_ST = ("MarketableSecuritiesCurrent", "ShortTermInvestments")
DEBT_LT = ("LongTermDebt", "LongTermDebtNoncurrent")
DEBT_ST = ("LongTermDebtCurrent", "DebtCurrent")
DEFAULT_TAX = 0.21
GROWTH_RANGE = (-0.05, 0.25)
GROWTH_FLOOR, GROWTH_CAP = -0.10, 0.30
DISCOUNT_FLOOR = 0.06
TERMINAL_DEFAULT = 0.025
TERMINAL_GAP = 0.01


# --- facts ------------------------------------------------------------------------------------
def facts(conn, ticker):
    """{concept: {period_end: value}} from fundamentals_annual, money in USD and counts in shares."""
    out = {}
    for r in db.rows(conn, "SELECT concept, unit, period_end, value FROM fundamentals_annual WHERE ticker = ? "
                           "AND unit IN ('USD', 'shares', 'USD/shares') ORDER BY period_end", (ticker,)):
        out.setdefault(r["concept"], {})[r["period_end"]] = r["value"]
    return out


def first(fx, concepts):
    for c in concepts:
        if fx.get(c):
            return c, fx[c]
    return None, {}


def series(fx, concepts, years):
    """Values of the first concept found, aligned to the fiscal year ends; None where a year is missing."""
    name, by_end = first(fx, concepts)
    return name, [by_end.get(y) for y in years]


def latest(fx, concepts, years):
    """The latest fiscal-year-end value of the first concept that has one on or before the last year end."""
    for c in concepts:
        by_end = fx.get(c) or {}
        ends = [e for e in by_end if e <= years[-1]] or sorted(by_end)
        if ends:
            e = max(ends)
            return c, e, by_end[e]
    return None, None, None


def triple(flag, name):
    if not flag:
        return None
    try:
        v = [float(x) / 100.0 for x in flag.split(",")]
    except ValueError:
        raise common.FetchError("--%s wants three percents lo,base,hi, got %r" % (name, flag))
    if len(v) != 3 or not (v[0] <= v[1] <= v[2]):
        raise common.FetchError("--%s wants lo <= base <= hi, got %r" % (name, flag))
    return v


def gather(conn, ticker, cfg, a):
    """Build the inputs dict (every assumption, its origin) or raise FetchError naming what is missing."""
    fx = facts(conn, ticker)
    rev_name, rev_by_end = first(fx, REVENUE)
    if not rev_by_end:
        raise common.FetchError("no annual revenue (%s) for %s; run sec.py %s" % ("/".join(REVENUE), ticker, ticker))
    years = sorted(rev_by_end)[-5:]
    revenue = [rev_by_end[y] for y in years]
    op_name, opinc = series(fx, OPINC, years)
    if opinc[-1] is None:
        raise common.FetchError("no OperatingIncomeLoss for %s in %s; run sec.py %s" % (ticker, years[-1], ticker))
    sh_name, sh_end, shares = latest(fx, SHARES, years)
    if not shares:
        raise common.FetchError("no diluted shares (%s) for %s; run sec.py %s" % ("/".join(SHARES), ticker, ticker))

    assumed, overridden = [], []
    inputs = {"ticker": ticker, "fiscal_years": years, "revenue": revenue, "revenue_concept": rev_name,
              "operating_income": opinc, "shares": shares, "shares_concept": sh_name, "shares_asof": sh_end}

    # tax rate from the latest year
    _, tax_s = series(fx, TAX, years)
    _, int_s = series(fx, INTEREST, years)
    pretax = opinc[-1] - (int_s[-1] or 0)
    if tax_s[-1] is not None and pretax > 0:
        inputs["tax_rate"] = calc.clamp(tax_s[-1] / pretax, 0.0, 0.35)
        inputs["tax_rate_from"] = "IncomeTaxExpenseBenefit / (OperatingIncomeLoss - InterestExpense), %s" % years[-1]
    else:
        inputs["tax_rate"] = DEFAULT_TAX
        inputs["tax_rate_from"] = "default"
        assumed.append("tax_rate 21% (no IncomeTaxExpenseBenefit or pre-tax income <= 0)")

    # depreciation and capex as ratios to the latest revenue
    for key, concepts in (("depreciation", DEPREC), ("capex", CAPEX)):
        _, s = series(fx, concepts, years)
        v = s[-1]
        if v is None:
            v = 0.0
            assumed.append("%s 0 (no %s)" % (key, concepts[0]))
        inputs[key] = v
        inputs[key + "_ratio"] = v / revenue[-1] if revenue[-1] else 0.0
    inputs["reinvestment"] = 0.0
    inputs["reinvestment_note"] = "reinvestment beyond capex is 0; depreciation and capex grow with revenue"

    # cash and debt at the latest year end
    _, _, cash = latest(fx, CASH, years)
    _, _, st = latest(fx, CASH_ST, years)
    if cash is None:
        assumed.append("cash 0 (no CashAndCashEquivalentsAtCarryingValue)")
    inputs["cash"] = (cash or 0.0) + (st or 0.0)
    _, _, lt = latest(fx, DEBT_LT, years)
    _, _, cur = latest(fx, DEBT_ST, years)
    if lt is None and cur is None:
        assumed.append("debt 0 (no LongTermDebt/LongTermDebtNoncurrent/DebtCurrent)")
    inputs["debt"] = (lt or 0.0) + (cur or 0.0)

    # growth
    g = triple(a.growth, "growth")
    if g:
        overridden.append("growth")
    else:
        hist = calc.cagr(revenue[0], revenue[-1], len(revenue) - 1) if len(revenue) > 1 else None
        if hist is None:
            base = 0.0
            assumed.append("growth base 0% (one year of revenue, no CAGR)")
        else:
            base = calc.clamp(hist, *GROWTH_RANGE)
        inputs["revenue_cagr_history"] = hist
        g = [max(base - 0.05, GROWTH_FLOOR), base, min(base + 0.05, GROWTH_CAP)]
    inputs["growth"] = {"low": g[0], "base": g[1], "high": g[2]}

    # margin
    m = triple(a.margin, "margin")
    margins = [o / r for o, r in zip(opinc, revenue) if o is not None and r]
    inputs["operating_margin_history"] = margins
    if m:
        overridden.append("margin")
    else:
        m = [min(margins), calc.mean(margins[-3:]), max(margins)]
    inputs["margin"] = {"low": m[0], "base": m[1], "high": m[2]}

    # discount rate: CAPM
    d = triple(a.discount, "discount")
    if d:
        overridden.append("discount")
        inputs["discount_from"] = "flag"
    else:
        rf = db.one(conn, "SELECT date, value FROM macro WHERE series = 'DGS10' ORDER BY date DESC LIMIT 1")
        if not rf:
            raise common.FetchError("no DGS10 in macro for the risk-free rate; run fred.py")
        b = db.one(conn, "SELECT asof, value FROM stats WHERE ticker = ? AND metric = 'beta' AND window = '3y' "
                         "ORDER BY asof DESC LIMIT 1", (ticker,))
        beta = b["value"] if b else 1.0
        if not b:
            assumed.append("beta 1.0 (no beta 3y in stats; run stats.py %s)" % ticker)
        erp = float(cfg.get("equity_risk_premium", common.DEFAULT_CONFIG["equity_risk_premium"])) / 100.0
        base = max(rf["value"] / 100.0 + beta * erp, DISCOUNT_FLOOR)
        d = [max(base - 0.015, DISCOUNT_FLOOR), base, max(base + 0.015, DISCOUNT_FLOOR)]
        inputs["discount_from"] = {"risk_free": rf["value"] / 100.0, "risk_free_date": rf["date"], "beta": beta,
                                   "beta_from": "stats beta 3y as of %s" % b["asof"] if b else "default 1.0",
                                   "equity_risk_premium": erp}
    inputs["discount"] = {"low": d[0], "base": d[1], "high": d[2]}

    # terminal growth, years
    tg = float(a.terminal) / 100.0 if a.terminal is not None else TERMINAL_DEFAULT
    if a.terminal is not None:
        overridden.append("terminal")
    inputs["terminal_requested"] = tg
    inputs["terminal_rule"] = "at least 1 point below the scenario's discount rate"
    cap = int(cfg.get("max_horizon_years", common.DEFAULT_CONFIG["max_horizon_years"]))
    inputs["years"] = max(1, min(a.years, cap))
    if a.years > cap:
        assumed.append("years capped at %d (config max_horizon_years)" % cap)
    inputs["overridden"] = overridden
    inputs["assumed"] = assumed
    return inputs


# --- the arithmetic -----------------------------------------------------------------------------
def terminal_for(tg, discount):
    return min(tg, discount - TERMINAL_GAP)


def value_per_share(inp, growth, margin, discount, terminal):
    rev, pv, fcf = inp["revenue"][-1], 0.0, 0.0
    for t in range(1, inp["years"] + 1):
        rev *= 1 + growth
        fcf = rev * margin * (1 - inp["tax_rate"]) + rev * inp["depreciation_ratio"] - rev * inp["capex_ratio"] \
            - inp["reinvestment"]
        pv += fcf / (1 + discount) ** t
    tv = fcf * (1 + terminal) / (discount - terminal)
    pv_tv = tv / (1 + discount) ** inp["years"]
    equity = pv + pv_tv - inp["debt"] + inp["cash"]
    return equity / inp["shares"], {"pv_fcf": pv, "pv_terminal": pv_tv, "equity": equity}


def scenarios(inp):
    g, m, d, tg = inp["growth"], inp["margin"], inp["discount"], inp["terminal_requested"]
    plan = {"low": (g["low"], m["low"], d["high"]), "base": (g["base"], m["base"], d["base"]),
            "high": (g["high"], m["high"], d["low"])}
    out = []
    for name in db.SCENARIOS:
        gr, mg, dr = plan[name]
        term = terminal_for(tg, dr)
        v, parts = value_per_share(inp, gr, mg, dr, term)
        row = {"scenario": name, "growth": gr, "margin": mg, "discount": dr, "terminal": term, "value_per_share": v}
        row.update(parts)
        out.append(row)
    return out


def monte_carlo(inp, sims, seed):
    g, m, d, tg = inp["growth"], inp["margin"], inp["discount"], inp["terminal_requested"]
    rng = random.Random(seed)
    vals = []
    for _ in range(sims):
        gr = calc.clamp(rng.gauss(g["base"], (g["high"] - g["low"]) / 4.0), g["low"], g["high"])
        mg = calc.clamp(rng.gauss(m["base"], (m["high"] - m["low"]) / 4.0), m["low"], m["high"])
        dr = calc.clamp(rng.gauss(d["base"], 0.0075), d["low"], d["high"])
        vals.append(value_per_share(inp, gr, mg, dr, terminal_for(tg, dr))[0])
    return {"p10": calc.percentile(vals, 10), "p50": calc.percentile(vals, 50), "p90": calc.percentile(vals, 90),
            "sims": sims, "seed": seed}



# --- what the price assumes, and what the market pays: reverse DCF, sensitivity, P/E -------------------
def reverse_dcf(inp, price):
    """The base-case revenue growth at which the DCF value equals the price (margin, discount, terminal at base).
    Returns (growth, note); growth is None when no rate inside REVERSE_RANGE reaches the price."""
    if not price:
        return None, "no price"
    m, d = inp["margin"]["base"], inp["discount"]["base"]
    term = terminal_for(inp["terminal_requested"], d)
    f = lambda g: value_per_share(inp, g, m, d, term)[0] - price
    lo, hi = REVERSE_RANGE
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        side = "below" if fhi < 0 else "above"
        return None, "no growth between %d%% and %d%% a year reaches the price (the value stays %s it)" % (lo * 100, hi * 100, side)
    for _ in range(80):
        mid = (lo + hi) / 2.0
        fm = f(mid)
        if (fm < 0) == (flo < 0):
            lo, flo = mid, fm
        else:
            hi = mid
    g = (lo + hi) / 2.0
    hist = inp.get("revenue_cagr_history")
    note = "the price assumes %s revenue growth a year for %d years" % (calc.pct(g), inp["years"])
    if hist is not None:
        note += "; the last %d years grew %s a year" % (len(inp["revenue"]) - 1, calc.pct(hist))
    return g, note


def sensitivity(inp):
    """Base value for growth -5/0/+5 points and discount -1.5/0/+1.5 points: [{discount, values: {growth: value}}]."""
    g, m, d, tg = inp["growth"]["base"], inp["margin"]["base"], inp["discount"]["base"], inp["terminal_requested"]
    growths = [g - 0.05, g, g + 0.05]
    grid = []
    for dr in (d - 0.015, d, d + 0.015):
        dr = max(dr, DISCOUNT_FLOOR)
        term = terminal_for(tg, dr)
        grid.append({"discount": dr, "values": {"%.4f" % gr: value_per_share(inp, gr, m, dr, term)[0] for gr in growths}})
    return {"growths": growths, "rows": grid}


def price_near(conn, ticker, date, days=10):
    return db.one(conn, "SELECT date, close FROM prices WHERE ticker = ? AND date BETWEEN ? AND date(?, ?) "
                        "ORDER BY date LIMIT 1", (ticker, date, date, "+%d days" % days))


def trailing_eps(conn, ticker, fx):
    """Diluted EPS of the last fiscal year, adjusted by the quarters reported since (10-Qs) against the same quarters a
    year earlier. Returns (eps, note, annual {fy_end: eps})."""
    annual = fx.get("EarningsPerShareDiluted") or {}
    if not annual:
        return None, "no EarningsPerShareDiluted in the filings", {}
    fy_end = max(annual)
    eps = annual[fy_end]
    q = db.rows(conn, "SELECT period_end, value FROM fundamentals_quarterly WHERE ticker = ? AND concept = 'EarningsPerShareDiluted' "
                      "AND unit = 'USD/shares' AND period_start != '' ORDER BY period_end", (ticker,))
    since = [r for r in q if r["period_end"] > fy_end]
    if not since:
        return eps, "fiscal year to %s, no quarter reported since" % fy_end, annual
    prev_end = max([e for e in annual if e < fy_end] or [""])
    prior = [r for r in q if prev_end < r["period_end"] <= fy_end][: len(since)]
    if len(prior) < len(since):
        return eps, "fiscal year to %s; %d quarter(s) since could not be matched to the prior year" % (fy_end, len(since)), annual
    ttm = eps + sum(r["value"] for r in since) - sum(r["value"] for r in prior)
    return ttm, "fiscal year to %s plus %d quarter(s) since, minus the same quarters a year earlier" % (fy_end, len(since)), annual


def pe_history(conn, ticker, annual, years=PE_YEARS):
    """Trailing P/E at each fiscal year end with a price nearby, over the last `years` fiscal years."""
    pts = []
    for end in sorted(annual)[-years:]:
        if annual[end] and annual[end] > 0:
            p = price_near(conn, ticker, end)
            if p:
                pts.append({"date": p["date"], "pe": p["close"] / annual[end]})
    return pts


def peers_pe(conn, ticker):
    """Trailing P/E (latest annual EPS, latest price) of the stored stocks in the same industry."""
    me = db.one(conn, "SELECT industry FROM securities WHERE ticker = ?", (ticker,))
    if not me or not me["industry"]:
        return [], None, "industry unknown; run yahoo.py profile %s" % ticker
    peers = db.rows(conn, "SELECT ticker FROM securities WHERE industry = ? AND ticker != ? AND kind = 'stock'", (me["industry"], ticker))
    out = []
    for p in peers:
        eps = db.one(conn, "SELECT value FROM fundamentals_annual WHERE ticker = ? AND concept = 'EarningsPerShareDiluted' "
                           "AND unit = 'USD/shares' ORDER BY period_end DESC LIMIT 1", (p["ticker"],))
        lp = db.latest_price(conn, p["ticker"])
        if eps and eps["value"] > 0 and lp:
            out.append({"ticker": p["ticker"], "pe": lp["close"] / eps["value"]})
    if len(out) < 2:
        return out, None, "fewer than two peers in %s with filings and prices stored (run sec.py and yahoo.py on them)" % me["industry"]
    return out, calc.percentile([o["pe"] for o in out], 50), "%d peers in %s" % (len(out), me["industry"])


def cross_checks(conn, ticker, inp, fx, price):
    """P/E now and against its own range and the peers, price to free cash flow, EV to operating income."""
    out = {"not_applicable": []}
    eps, note, annual = trailing_eps(conn, ticker, fx)
    out["eps_ttm"], out["eps_note"] = eps, note
    if eps is None or eps <= 0:
        out["not_applicable"].append("P/E: %s" % ("earnings are zero or negative" if eps is not None else note))
        out["pe"] = None
    else:
        out["pe"] = price / eps if price else None
        pts = pe_history(conn, ticker, annual)
        if out["pe"] is not None:
            pts.append({"date": "now", "pe": out["pe"]})
        pes = [p["pe"] for p in pts]
        out["pe_range"] = ({"min": min(pes), "median": calc.percentile(pes, 50), "max": max(pes), "n": len(pes), "points": pts}
                           if len(pes) >= 2 else None)
        if out["pe_range"] is None:
            out["not_applicable"].append("P/E range: fewer than two fiscal year ends with a price stored")
        peers, med, pnote = peers_pe(conn, ticker)
        out["peers"] = {"list": peers, "median": med, "note": pnote}
        if med is None:
            out["not_applicable"].append("peers' P/E: " + pnote)
        out["value_at_median_pe"] = eps * out["pe_range"]["median"] if out["pe_range"] else None
        out["value_at_peers_pe"] = eps * med if med else None
    mcap = price * inp["shares"] if price else None
    _, _, ocf = latest(fx, OCF, inp["fiscal_years"])
    fcf = (ocf - inp["capex"]) if ocf is not None else None
    out["free_cash_flow"] = fcf
    out["p_fcf"] = mcap / fcf if (mcap and fcf and fcf > 0) else None
    if out["p_fcf"] is None:
        out["not_applicable"].append("P/FCF: " + ("no operating cash flow in the filings" if ocf is None else
                                                 "free cash flow is zero or negative" if fcf is not None and fcf <= 0 else "no price"))
    ebit = inp["operating_income"][-1]
    out["ev_ebit"] = (mcap + inp["debt"] - inp["cash"]) / ebit if (mcap and ebit and ebit > 0) else None
    if out["ev_ebit"] is None:
        out["not_applicable"].append("EV/EBIT: " + ("operating income is zero or negative" if mcap else "no price"))
    return out


def store(conn, ticker, asof, inp, rows_, mc, price, run_id, extra=None):
    sid = db.source(conn, "derived://dcf.py?ticker=%s&asof=%s" % (ticker, asof), "derived",
                    "dcf.py over fundamentals, macro and stats rows of %s" % ticker)
    now = common.iso()
    ids = []
    for r in rows_:
        base = r["scenario"] == "base"
        r["price"] = price
        r["upside"] = r["value_per_share"] / price - 1 if price else None
        ids.append(db.insert(conn, "valuations", {
            "run_id": run_id, "ticker": ticker, "asof": asof, "scenario": r["scenario"], "inputs": inp,
            "value_per_share": r["value_per_share"], "price": price, "upside": r["upside"],
            "p10": mc["p10"] if base else None, "p50": mc["p50"] if base else None, "p90": mc["p90"] if base else None,
            "source_id": sid, "created_at": now, "method": "dcf"}))
    extra = extra or {}
    rv = extra.get("reverse") or {}
    if rv.get("growth") is not None:
        ids.append(db.insert(conn, "valuations", {
            "run_id": run_id, "ticker": ticker, "asof": asof, "method": "reverse_dcf", "scenario": None,
            "inputs": {"implied_growth": rv["growth"], "note": rv["note"], "margin": inp["margin"]["base"],
                       "discount": inp["discount"]["base"], "years": inp["years"], "history_cagr": inp.get("revenue_cagr_history")},
            "value_per_share": price, "price": price, "upside": 0.0, "source_id": sid, "created_at": now}))
    cc = extra.get("cross") or {}
    for method, key in (("pe_range", "value_at_median_pe"), ("pe_peers", "value_at_peers_pe")):
        v = cc.get(key)
        if v:
            ids.append(db.insert(conn, "valuations", {
                "run_id": run_id, "ticker": ticker, "asof": asof, "method": method, "scenario": None,
                "inputs": {k: cc.get(k) for k in ("eps_ttm", "eps_note", "pe", "pe_range", "peers", "p_fcf", "ev_ebit", "free_cash_flow")},
                "value_per_share": v, "price": price, "upside": v / price - 1 if price else None, "source_id": sid, "created_at": now}))
    return ids, sid


def md(ticker, asof, inp, rows_, mc, price, extra=None):
    recs = [{"scenario": r["scenario"], "growth": calc.pct(r["growth"]), "margin": calc.pct_plain(r["margin"]),
             "discount": calc.pct_plain(r["discount"]), "terminal": calc.pct_plain(r["terminal"]),
             "value per share": calc.money(r["value_per_share"]),
             "vs price": calc.pct(r["upside"]) if r["upside"] is not None else "no price"} for r in rows_]
    out = ["**%s** DCF as of %s, %d-year forecast, price %s" % (ticker, asof, inp["years"],
                                                                 calc.money(price) if price else "unknown"), "",
           db.md_table(recs), "",
           "Monte Carlo on the base case (%d draws, seed %d): p10 %s · p50 %s · p90 %s per share" % (
               mc["sims"], mc["seed"], calc.money(mc["p10"]), calc.money(mc["p50"]), calc.money(mc["p90"]))]
    extra = extra or {}
    grid = extra.get("sensitivity")
    if grid:
        gs = grid["growths"]
        recs = [dict([("discount \\ growth", calc.pct_plain(r["discount"]))] +
                     [(calc.pct(g), calc.money(r["values"]["%.4f" % g])) for g in gs]) for r in grid["rows"]]
        out += ["", "Base value if growth or the discount rate differ:", "", db.md_table(recs)]
    rv = extra.get("reverse")
    if rv:
        out += ["", "What the price assumes: " + rv["note"] + "."]
    cc = extra.get("cross")
    if cc:
        fmt = lambda v: calc.num(v, 1) if v is not None else "n/a"
        rng = cc.get("pe_range")
        recs = [{"measure": "trailing P/E", "now": fmt(cc.get("pe")),
                 "own 5-year range": "%s / %s / %s (min / median / max, %d points)" % (fmt(rng["min"]), fmt(rng["median"]), fmt(rng["max"]), rng["n"]) if rng else "n/a",
                 "peers": "%s (%s)" % (fmt(cc["peers"]["median"]), cc["peers"]["note"]) if cc.get("peers") else "n/a"},
                {"measure": "price / free cash flow", "now": fmt(cc.get("p_fcf")), "own 5-year range": "", "peers": ""},
                {"measure": "EV / operating income", "now": fmt(cc.get("ev_ebit")), "own 5-year range": "", "peers": ""}]
        out += ["", "What the market pays (trailing EPS %s: %s):" % (calc.money(cc["eps_ttm"]) if cc.get("eps_ttm") is not None else "n/a", cc.get("eps_note", "")),
                "", db.md_table(recs)]
        vals = []
        if cc.get("value_at_median_pe"):
            vals.append("%s at its own median P/E" % calc.money(cc["value_at_median_pe"]))
        if cc.get("value_at_peers_pe"):
            vals.append("%s at the peers' median P/E" % calc.money(cc["value_at_peers_pe"]))
        if vals:
            out.append("Worth " + " · ".join(vals) + " against a price of %s." % (calc.money(price) if price else "unknown"))
        if cc.get("not_applicable"):
            out.append("Not applicable: " + "; ".join(cc["not_applicable"]))
    if inp["assumed"]:
        out += ["", "Assumed: " + "; ".join(inp["assumed"])]
    if inp["overridden"]:
        out += ["", "Overridden by flags: " + ", ".join(inp["overridden"])]
    return "\n".join(out)


def run(argv=None):
    p = common.parser(SCRIPT, "three-scenario DCF for a ticker, written to valuations; rates in percent")
    p.add_argument("ticker")
    p.add_argument("--run-id", type=int, default=None)
    p.add_argument("--growth", default="", help="revenue growth lo,base,hi in percent")
    p.add_argument("--margin", default="", help="operating margin lo,base,hi in percent")
    p.add_argument("--discount", default="", help="discount rate lo,base,hi in percent")
    p.add_argument("--terminal", default=None, help="terminal growth in percent (default 2.5)")
    p.add_argument("--years", type=int, default=5, help="forecast years, capped at config max_horizon_years")
    p.add_argument("--sims", type=int, default=2000)
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args(argv)
    ticker = a.ticker.upper()
    project = common.resolve_project(a.project)
    cfg = common.load_config(project)
    conn = db.connect(project)
    inp = gather(conn, ticker, cfg, a)
    rows_ = scenarios(inp)
    mc = monte_carlo(inp, max(1, a.sims), a.seed)
    lp = db.latest_price(conn, ticker)
    price = lp["close"] if lp else None
    asof = lp["date"] if lp else common.today()
    if not lp:
        inp["assumed"].append("no price in prices; upside left empty (run yahoo.py prices %s)" % ticker)
    g, note = reverse_dcf(inp, price)
    extra = {"reverse": {"growth": g, "note": note}, "sensitivity": sensitivity(inp),
             "cross": cross_checks(conn, ticker, inp, facts(conn, ticker), price)}
    ids, sid = store(conn, ticker, asof, inp, rows_, mc, price, a.run_id, extra)
    out = {"ok": True, "script": SCRIPT, "ticker": ticker, "asof": asof, "price": price, "inputs": inp,
           "scenarios": rows_, "monte_carlo": mc, "reverse_dcf": extra["reverse"], "sensitivity": extra["sensitivity"],
           "cross_checks": extra["cross"], "valuation_ids": ids, "source_id": sid}
    return common.emit(out, md=md(ticker, asof, inp, rows_, mc, price, extra) if a.md else None)


if __name__ == "__main__":
    sys.exit(common.run_main(SCRIPT, run))
