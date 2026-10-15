#!/usr/bin/env python3
"""score.py <TICKER | stock folder> [--mos 0.30] [--lens long|short|both] [--mode full|screen] [--holding]

Applies the score skill (skills/score/SKILL.md, rules/*.md, references/*.md) to one stock folder:
reads facts/facts.json, research/evidence.json (optional) and facts/holdings.json (optional), writes facts/scorecard.json per
scorecard-schema.md and prints a one-line JSON summary. Arithmetic only; stdlib only.

Conventions the cards leave open:
- as_of = facts.retrieved date (deterministic for a given facts.json).
- A gate whose input is missing is `no evidence` (counted in coverage, never a fail).
- `--mos` different from metrics.valuation.params.mos rebases the buy zone: base value today x (1 - mos).
- Boundaries: price <= buy zone is `buy zone` (matches 4.1's <=); price > sell zone is `sell zone`.
- S<d> (metrics.py) and S<s> (score.py) take the next free ids after facts.json.sources unless a
  derived metrics.py row already exists there; both rows are written into scorecard.sources.
Ratios round to 4 decimals, dollars to 2.
"""
import datetime as dt
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import EnvelopeParser, add_common_args, locate, run_main  # noqa: E402

NA_SECTORS = ("financial", "reit", "utility")
EVIDENCE_ITEMS = ("G4", "1.5", "5.4", "5.5")
UNVERIFIED = ("2.2", "4.5", "5.2")  # threshold items flagged UNVERIFIED in the cards (scorecard-template column)
HORIZONS = ("1", "2", "5", "10")   # default only: the horizons present in metrics.valuation.by_horizon win


def horizon_years(h):
    try:
        y = float(h)
    except (TypeError, ValueError):
        return None
    return y if y > 0 else None


def horizon_label(y):
    """Plain words: 0.25 -> "3 months", 1 -> "1 year", 3 -> "3 years", 2.5 -> "2.5 years"."""
    if y < 1:
        m = round(y * 12)
        return "%d month%s" % (m, "" if m == 1 else "s") if abs(m - y * 12) < 1e-6 else "%g years" % y
    return "%g year%s" % (y, "" if y == 1 else "s")
PILLARS = {"1": ("1.1", "1.2", "1.3", "1.4", "1.5", "1.6"), "2": ("2.1", "2.2", "2.3", "2.4", "2.5"),
           "3": ("3.1", "3.2", "3.3", "3.4", "3.5"), "4": ("4.1", "4.2", "4.3", "4.4", "4.5"),
           "5": ("5.1", "5.2", "5.3", "5.4", "5.5")}
GATE_NAMES = {
    "G1": "Bankruptcy or receivership (8-K Item 1.03, 3 yrs)",
    "G2": "Restatement (8-K Item 4.02, 3 yrs)",
    "G3": "Altman distress zone (manufacturer, Z < 1.81)",
    "G4": "Going-concern paragraph (latest 10-K)",
    "G5": "Negative owner earnings (full capex, 3 of 5 yrs)",
    "G6": "Serial dilution (3 rising yrs and > 10%)",
}
TESTS = {
    "1.1": "ROIC >= r_base in >= 4 of last 5 fiscal years, with or without goodwill",
    "1.2": "ROIIC 5y > r_base", "1.3": "gross profitability >= 0.33",
    "1.4": "gross margin change over 5y >= -2 pp", "1.5": "10-K passage evidences a moat source",
    "1.6": "revenue 5y CAGR > 0 and no two consecutive annual declines in 10y",
    "2.1": "Piotroski F >= 8", "2.2": "Z >= 2.99 (manufacturer) or Z'' >= 2.60 (non-manufacturer)",
    "2.3": "current ratio >= 2", "2.4": "long-term debt <= net current assets",
    "2.5": "no loss year in the last 10", "3.1": "market value created per dollar retained >= 1.0 (5y)",
    "3.2": "split-adjusted diluted shares today <= five years ago", "3.3": "shareholder yield > 0",
    "3.4": "no goodwill impairment in 5y", "3.5": "insider open-market purchase in 12 months",
    "4.1": "price <= buy zone", "4.2": "price <= bull fair value today",
    "4.3": "implied growth at price <= base g", "4.4": "owner-earnings yield >= 10-year Treasury",
    "4.5": "price <= Graham number", "5.1": "Sloan accrual ratio <= 0.05",
    "5.2": "Beneish M <= -1.78", "5.3": "net debt / owner earnings <= 3",
    "5.4": "no material weakness in 10-K Item 9A", "5.5": "no customer >= 10% of revenue",
    "G1": "no 8-K Item 1.03 in 3 years", "G2": "no 8-K Item 4.02 in 3 years", "G3": "Altman Z >= 1.81",
    "G4": "no going-concern paragraph", "G5": "owner earnings (full capex) negative in < 3 of 5 years",
    "G6": "not (shares rose in each of last 3 years and > 10%)",
}
FROM = {  # where a missing or failing input would come from (open questions)
    "evidence": "the researcher citing the latest 10-K (%s) in evidence.json",
    "fund": "the next 10-K via edgar.py",
    "price": "no data gap; changes only with price or refreshed fundamentals",
}
ST_SOURCES = {  # lens-short-term.md, one line each ([U] = pending primary-text verification)
    "ST1": "Brock, Lakonishok and LeBaron (1992) [U]; weaker after 1986 per Sullivan, Timmermann and White (1999) [U]",
    "ST2": "Jegadeesh and Titman (1993) [U]; crash risk after declines per Daniel and Moskowitz (2016) [U]",
    "ST3": "George and Hwang (2004) [U]; a cross-sectional effect, not a single-stock forecast",
    "ST4": "this standard's bands: calm below 0.8x, stressed above 1.5x of 1-year volatility",
    "ST5": "options arithmetic; implied exceeds realized on average per Carr and Wu (2009) [U]; secondary data",
    "ST6": "post-earnings drift per Bernard and Thomas (1989) [U]; the lens lists dates, not a direction",
    "ST7": "Jegadeesh and Titman (1993) [U], relative returns; secondary data",
}
WHERE = {"G4": "auditor's report", "1.5": "Item 1 or 7", "5.4": "Item 9A", "5.5": "segment note or a stated grep"}


def r4(x):
    return None if x is None else round(x, 4)


def r2(x):
    return None if x is None else round(x, 2)


def num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def g(obj, *path):
    for p in path:
        if isinstance(obj, dict):
            obj = obj.get(p)
        elif isinstance(obj, list) and isinstance(p, int) and -len(obj) <= p < len(obj):
            obj = obj[p]
        else:
            return None
    return obj


def round_half_up(x):
    return int(math.floor(x + 0.5))


def money(x):
    return "n/a" if x is None else ("-$%s" % format(-x, ",.2f") if x < 0 else "$%s" % format(x, ",.2f"))


def pct(x, nd=2):
    return "n/a" if x is None else ("%." + str(nd) + "f%%") % (x * 100)


def add_year(d):
    try:
        return d.replace(year=d.year + 1)
    except ValueError:  # 29 Feb
        return d.replace(year=d.year + 1, day=28)


def day(s):
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except (TypeError, ValueError):
        return None


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None


def by_design_na(reason):
    r = (reason or "").lower()
    return "denominator <= 0" in r or r.startswith("n/a") or "model n/a" in r


# ---------------------------------------------------------------------------------------------
class Scorer:
    def __init__(self, facts, evidence, holdings, mos=None, lens="long", mode="full", holding=False,
                 facts_path="facts.json", out_path="scorecard.json", request=None):
        self.req = request if isinstance(request, dict) else {}
        self.f, self.ev, self.h = facts, evidence, holdings
        self.mode, self.lens = mode, lens
        self.m = facts.get("metrics") or {}
        self.val = self.m.get("valuation") or {}
        self.sector = facts.get("sector_class")
        self.price = num(g(facts, "price", "last"))
        self.as_of = (facts.get("retrieved") or g(facts, "price", "date") or dt.date.today().isoformat())[:10]
        self.r = num(g(self.val, "params", "r_base"))
        positions = g(holdings, "positions") if isinstance(holdings, dict) else None
        self.holding = bool(holding or positions)
        self.P = g(facts, "price", "src") or "S3"
        self.F = g(facts, "fundamentals", "annual", 0, "src") or "S1"
        self.M = g(facts, "macro", "src") or "S4"
        self._ids(facts_path, out_path)
        self.mos = mos
        self.notes = []

    DERIVED_ID, SCORE_ID = "S60", "S61"   # fixed: S60-S69 are derived rows, so narratives survive new facts sources

    def _ids(self, facts_path, out_path):
        inputs = sorted({v for v in self._srcs(self.f.get("fundamentals")) + self._srcs(self.f.get("price"))
                         + self._srcs(self.f.get("macro"))}, key=lambda s: int(s[1:]))
        self.D, self.S = self.DERIVED_ID, self.SCORE_ID
        self.sources = {self.D: {"class": "derived", "what": "metrics.py scorecard inputs and valuation per "
                                 "valuation.md from %s" % " ".join(inputs),
                                 "url": "file://" + os.path.abspath(facts_path), "as_of": self.as_of,
                                 "retrieved": self.as_of}}
        self.out_path = out_path

    def _srcs(self, obj):
        out = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("src", "erp_src") and isinstance(v, str):
                    out.append(v)
                else:
                    out.extend(self._srcs(v))
        elif isinstance(obj, list):
            for v in obj:
                out.extend(self._srcs(v))
        return out

    # -- record builders --
    def item(self, iid, score, status, value=None, markers=(), note=""):
        ev = iid in EVIDENCE_ITEMS
        return {"score": score, "status": status, "value": value, "test": TESTS[iid],
                "markers": list(dict.fromkeys(markers)), "unverified": iid in UNVERIFIED,
                "evidence_required": ev, "note": note}

    def scored(self, iid, ok, value, markers, note):
        return self.item(iid, 1 if ok else 0, "scored", value, markers, note)

    def na(self, iid, note, markers=()):
        return self.item(iid, None, "n/a", None, markers, note)

    def noev(self, iid, note, markers=()):
        return self.item(iid, 0, "no evidence", None, markers, note)

    def from_metric(self, iid, obj, test, note_fn, markers=None):
        """Generic metric item: null by design -> n/a, null otherwise -> no evidence."""
        markers = markers or [self.D]
        v = num(g(obj, "value"))
        if v is None:
            reason = g(obj, "reason") or "input missing from facts.json"
            return (self.na if by_design_na(reason) else self.noev)(iid, reason, markers)
        return self.scored(iid, test(v), v, markers, note_fn(v))

    def evidence(self, iid):
        e = g(self.ev, iid) if isinstance(self.ev, dict) else None
        if not isinstance(e, dict):
            if self.mode == "screen":
                return self.item(iid, None, "pending", None, [], "evidence item pending (screen mode)")
            return self.noev(iid, "no verdict in evidence.json")
        mk = [e["marker"]] if e.get("marker") else []
        quote = ('"%s"' % e["quote"]) if e.get("quote") else ""
        where = e.get("where") or ""
        verdict = e.get("verdict")
        if verdict in ("pass", "fail"):
            extra = ""
            if iid == "1.5" and e.get("moat_sources"):
                extra = "moat sources: %s; " % ", ".join(e["moat_sources"])
            if iid == "5.5" and e.get("method"):
                extra = "method %s; " % e["method"]
            return self.scored(iid, verdict == "pass", verdict, mk,
                               ("%s%s %s" % (extra, where, quote)).strip())
        return self.noev(iid, ("researcher verdict no evidence (%s) %s" % (where, quote)).strip(), mk)

    # -- gates --
    def gates(self):
        out = {}
        fil = self.f.get("filings_recent")
        asof = day(self.as_of)
        for gid, code in (("G1", "1.03"), ("G2", "4.02")):
            if not isinstance(fil, list):
                out[gid] = self.gate("no evidence", None, [], "filings_recent missing from facts.json")
                continue
            start = asof - dt.timedelta(days=1095) if asof else None
            window = [x for x in fil if day(x.get("filed")) and (start is None or day(x["filed"]) >= start)]
            hits = [x for x in window if str(x.get("form", "")).startswith("8-K")
                    and code in [i.strip() for i in str(x.get("items", "")).split(",")]]
            mk = list(dict.fromkeys(x.get("src") for x in fil if x.get("src"))) or ["S2"]
            dates = sorted(str(x["filed"])[:10] for x in fil if day(x.get("filed")))
            cover = "filings index covers %s to %s" % (dates[0], dates[-1]) if dates else "filings index is empty"
            win = self.f.get("filings_window")  # facts.py: whether the submissions feed reached three years back
            short = (not win.get("complete")) if isinstance(win, dict) else (
                not dates or (start is not None and day(dates[0]) > start))
            tail = "; coverage shorter than three years" if short else ""
            if hits:
                out[gid] = self.gate("fail", len(hits), mk, "%s; Item %s on %s%s" % (cover, code, ", ".join(
                    "%s %s" % (h["filed"], h.get("url", "")) for h in hits), tail))
            else:
                out[gid] = self.gate("pass", 0, mk, "%s; no Item %s found%s" % (cover, code, tail))
            out[gid]["coverage_short"] = short
        alt = self.m.get("altman") or {}
        if self.sector != "manufacturer":
            out["G3"] = self.gate("n/a", None, [], "Altman gate applies to manufacturers only "
                                  "(sector_class %s)" % self.sector)
        elif num(alt.get("value")) is None or alt.get("model") != "Z":
            out["G3"] = self.gate("no evidence", None, [self.D], alt.get("reason") or "metrics.altman missing")
        else:
            z = alt["value"]
            out["G3"] = self.gate("fail" if z < 1.81 else "pass", z, [self.D],
                                  "Z %.4f, zone %s, FY%s" % (z, alt.get("zone"), alt.get("fy")))
        e = self.evidence("G4")
        res = {"scored": "pass" if e["score"] == 1 else "fail"}.get(e["status"], e["status"])
        out["G4"] = self.gate(res, e["value"], e["markers"], e["note"])
        gi = self.m.get("gate_inputs") or {}
        if self.sector in NA_SECTORS:
            out["G5"] = self.gate("n/a", None, [], "owner-earnings model n/a for sector_class %s" % self.sector)
        elif num(gi.get("owner_earnings_negative_years_5y_full_capex")) is None:
            out["G5"] = self.gate("no evidence", None, [self.D], "gate_inputs missing")
        else:
            n, k = gi["owner_earnings_negative_years_5y_full_capex"], gi.get("owner_earnings_years_checked_5y")
            out["G5"] = self.gate("fail" if n >= 3 else "pass", n, [self.D],
                                  "%d of %s years negative on full-capex owner earnings" % (n, k))
        dil = self.m.get("dilution_5y") or {}
        rising, v = num(dil.get("rising_years_last3")), num(dil.get("value"))
        if rising is None:
            out["G6"] = self.gate("no evidence", None, [self.D], dil.get("reason") or "dilution_5y missing")
        else:
            fail = rising >= 3 and v is not None and v > 0.10
            out["G6"] = self.gate("fail" if fail else "pass", v, [self.D],
                                  "split-adjusted diluted shares rose in %d of last 3 years; 5-yr change %s"
                                  % (rising, pct(v, 1)))
        return out

    def gate(self, result, value, markers, note):
        return {"result": result, "value": value, "test": "", "markers": list(dict.fromkeys(markers)),
                "note": note}

    # -- pillar items --
    def items(self):
        m, D, P, F = self.m, self.D, self.P, self.F
        r = self.r
        it = {}
        # Pillar 1
        roic = [x for x in (m.get("roic") or []) if isinstance(x, dict)][:5]
        if r is None or not roic:
            it["1.1"] = self.noev("1.1", "metrics.roic or r_base missing", [D])
        else:
            w = sum(1 for x in roic if num(x.get("value")) is not None and x["value"] >= r)
            wo = sum(1 for x in roic if num(x.get("value_ex_goodwill")) is not None and x["value_ex_goodwill"] >= r)
            have = sum(1 for x in roic if num(x.get("value")) is not None)
            best = "with goodwill" if w >= wo else "ex goodwill"
            note = "ROIC >= %.4f in %d of %d years (%s); latest %s" % (r, max(w, wo), len(roic), best,
                                                                      roic[0].get("value"))
            if max(w, wo) >= 4:
                it["1.1"] = self.scored("1.1", True, roic[0].get("value"), [D], note)
            elif have < 5 and max(w, wo) + (5 - have) >= 4:
                it["1.1"] = self.noev("1.1", "ROIC available for %d of 5 years" % have, [D])
            else:
                it["1.1"] = self.scored("1.1", False, roic[0].get("value"), [D], note)
        ro = m.get("roiic_5y") or {}
        if num(ro.get("value")) is None and by_design_na(ro.get("reason")):
            dic = ro.get("delta_invested_capital")
            note = ("invested capital fell %s USD millions over 5 yrs, denominator <= 0" % format(-dic / 1e6, ",.0f")
                    if num(dic) is not None and dic < 0 else ro.get("reason"))
            it["1.2"] = self.na("1.2", note, [D])
        else:
            it["1.2"] = self.from_metric("1.2", ro, lambda v: r is not None and v > r,
                                         lambda v: "ROIIC 5y %.4f vs r_base %.4f" % (v, r or 0))
        if self.sector in ("financial", "reit"):
            it["1.3"] = self.na("1.3", "gross profitability n/a for sector_class %s" % self.sector)
        else:
            it["1.3"] = self.from_metric("1.3", m.get("gross_profitability"), lambda v: v >= 0.33,
                                         lambda v: "gross profitability %.4f" % v)
        it["1.4"] = self.from_metric("1.4", m.get("gross_margin_5y_change"), lambda v: v >= -2,
                                     lambda v: "gross margin change %.4f pp over 5 yrs" % v)
        it["1.5"] = self.evidence("1.5")
        cagr, dec = num(g(m, "revenue_cagr_5y", "value")), num(g(m, "revenue_declines_consecutive_10y", "value"))
        if cagr is None or dec is None:
            it["1.6"] = self.noev("1.6", g(m, "revenue_cagr_5y", "reason") or
                                  g(m, "revenue_declines_consecutive_10y", "reason") or "revenue series missing", [D])
        else:
            it["1.6"] = self.scored("1.6", cagr > 0 and dec < 2, cagr, [D],
                                    "revenue 5y CAGR %.4f; longest run of declines %d yr" % (cagr, dec))
        # Pillar 2
        pio = m.get("piotroski") or {}
        if num(pio.get("score")) is None and len(g(self.f, "fundamentals", "annual") or []) < 2:
            it["2.1"] = self.na("2.1", "no prior-year statements", [D])
        else:
            it["2.1"] = self.from_metric("2.1", {"value": pio.get("score"), "reason": pio.get("reason")},
                                         lambda v: v >= 8, lambda v: "F-score %d of 9" % v)
        alt = m.get("altman") or {}
        if self.sector in NA_SECTORS:
            it["2.2"] = self.na("2.2", "Altman n/a for sector_class %s" % self.sector)
        else:
            cut = 2.99 if alt.get("model") == "Z" or self.sector == "manufacturer" else 2.60
            name = "Z" if cut == 2.99 else "Z''"
            it["2.2"] = self.from_metric("2.2", alt, lambda v: v >= cut,
                                         lambda v: "%s %.4f vs %.2f" % (name, v, cut))
        gi = m.get("gate_inputs") or {}
        it["2.3"] = self.from_metric("2.3", {"value": gi.get("current_ratio")}, lambda v: v >= 2,
                                     lambda v: "current ratio %.4f" % v)
        nca, ltd = num(gi.get("net_current_assets")), g(self.f, "fundamentals", "annual", 0, "lt_debt")
        ltd = 0 if ltd is None and nca is not None else num(ltd)
        if nca is None:
            it["2.4"] = self.noev("2.4", "net current assets missing", [D])
        elif ltd == 0 and nca < 0:
            it["2.4"] = self.na("2.4", "no long-term debt and negative net current assets", [F, D])
        else:
            it["2.4"] = self.scored("2.4", ltd <= nca, ltd, [F, D],
                                    "long-term debt %s USD millions vs net current assets %s USD millions"
                                    % (format(ltd / 1e6, ",.0f"), format(nca / 1e6, ",.0f")))
        loss, yrs = num(gi.get("loss_years_10y")), num(gi.get("years_available_10y"))
        if loss is None or yrs is None:
            it["2.5"] = self.noev("2.5", "earnings history missing", [D])
        elif yrs < 10:
            it["2.5"] = self.na("2.5", "%d of 10 years available" % yrs, [D])
        else:
            it["2.5"] = self.scored("2.5", loss == 0, loss, [D], "%d loss years in %d" % (loss, yrs))
        # Pillar 3
        it["3.1"] = self.from_metric("3.1", m.get("retained_earnings_test"), lambda v: v >= 1.0,
                                     lambda v: "%.4f of market value per dollar retained" % v, [P, D])
        it["3.2"] = self.from_metric("3.2", m.get("dilution_5y"), lambda v: v <= 0,
                                     lambda v: "split-adjusted diluted shares 5-yr change %s" % pct(v, 1))
        it["3.3"] = self.from_metric("3.3", m.get("shareholder_yield"), lambda v: v > 0,
                                     lambda v: "shareholder yield %.4f" % v, [P, D])
        gw = m.get("goodwill_impairment_5y") or {}
        if num(gw.get("value")) is None:
            it["3.4"] = self.noev("3.4", "goodwill_impairment null in every year checked (%s yrs)"
                                  % gw.get("years_checked") if gw else "goodwill_impairment_5y missing", [F, D])
        else:
            it["3.4"] = self.scored("3.4", gw["value"] == 0, gw["value"], [F, D],
                                    "%d impairment years in %s" % (gw["value"], gw.get("years_checked")))
        ins = self.f.get("insiders")
        if ins is None:
            it["3.5"] = self.na("3.5", "insiders null by design")
        else:
            buys = [x for x in ins if isinstance(x, dict) and x.get("code") == "P"] if isinstance(ins, list) else []
            it["3.5"] = self.scored("3.5", bool(buys), len(buys), [x.get("src") for x in buys if x.get("src")],
                                    "%d open-market purchases" % len(buys))
        # Pillar 4
        price = self.price
        val_na = self.sector in NA_SECTORS
        buy, bull = self.zones["buy_below"], self.zones["bull_today"]
        if val_na:
            for k in ("4.1", "4.2", "4.3", "4.4"):
                it[k] = self.na(k, "owner-earnings model n/a for sector_class %s" % self.sector)
        else:
            if price is None or buy is None:
                it["4.1"] = self.noev("4.1", "price or buy zone missing", [P, D])
            else:
                it["4.1"] = self.scored("4.1", price <= buy, price, [P, D],
                                        "price %s vs buy zone %s" % (money(price), money(buy)))
            if bull is None:
                it["4.2"] = self.na("4.2", "bull value null: %s" % (self.val.get("reason") or "owner earnings <= 0"),
                                    [D])
            elif price is None:
                it["4.2"] = self.noev("4.2", "price missing", [P])
            else:
                it["4.2"] = self.scored("4.2", price <= bull, price, [P, D],
                                        "price %s vs bull value %s" % (money(price), money(bull)))
            ig, bg = num(self.val.get("implied_growth_at_price")), num(g(self.val, "scenarios", "base", "g"))
            if ig is None or bg is None:
                it["4.3"] = self.noev("4.3", self.val.get("reason") or "implied growth or base g missing", [D])
            else:
                it["4.3"] = self.scored("4.3", ig <= bg, ig, [D], "implied growth %s vs base %s" % (pct(ig), pct(bg)))
            oy, ty = num(g(m, "owner_earnings", "yield")), num(g(self.f, "macro", "dgs10"))
            if oy is None or ty is None:
                it["4.4"] = self.noev("4.4", "owner-earnings yield or 10-yr Treasury missing", [self.M, D])
            else:
                it["4.4"] = self.scored("4.4", oy >= ty / 100.0, oy, [self.M, D],
                                        "owner-earnings yield %s (estimate: maintenance capex = min(capex, da)) "
                                        "vs 10-yr Treasury %s" % (pct(oy), pct(ty / 100.0)))
        gn = m.get("graham_number") or {}
        if num(gn.get("value")) is None:
            it["4.5"] = (self.na if by_design_na(gn.get("reason")) else self.noev)(
                "4.5", gn.get("reason") or "graham_number missing", [D])
        elif price is None:
            it["4.5"] = self.noev("4.5", "price missing", [P])
        else:
            it["4.5"] = self.scored("4.5", price <= gn["value"], gn["value"], [P, D],
                                    "price %s vs Graham number %s; book value per share %s" % (
                                        money(price), money(gn["value"]), money(gn.get("bvps"))))
        # Pillar 5
        if self.sector == "financial":
            it["5.1"] = self.na("5.1", "accruals n/a for banks and insurers")
        else:
            it["5.1"] = self.from_metric("5.1", m.get("accrual_ratio"), lambda v: v <= 0.05,
                                         lambda v: "accrual ratio %.4f" % v)
        if self.sector in NA_SECTORS:
            it["5.2"] = self.na("5.2", "Beneish n/a for sector_class %s" % self.sector)
        else:
            it["5.2"] = self.from_metric("5.2", {"value": g(m, "beneish", "m"), "reason": g(m, "beneish", "reason")},
                                         lambda v: v <= -1.78, lambda v: "M %.4f vs -1.78" % v)
        nd = m.get("net_debt_to_owner_earnings") or {}
        if self.sector in NA_SECTORS:
            it["5.3"] = self.na("5.3", "structural leverage, sector_class %s" % self.sector)
        elif num(nd.get("net_debt")) is not None and nd["net_debt"] <= 0:
            it["5.3"] = self.scored("5.3", True, nd["net_debt"], [D], "net cash %s USD millions"
                                    % format(-nd["net_debt"] / 1e6, ",.0f"))
        else:
            it["5.3"] = self.from_metric("5.3", nd, lambda v: v <= 3, lambda v: "net debt / owner earnings %.4f" % v)
        it["5.4"] = self.evidence("5.4")
        it["5.5"] = self.evidence("5.5")
        return it

    # -- valuation, zones --
    def compute_zones(self):
        v = self.val
        ft = v.get("fair_value_today") or {}
        buy = num(v.get("buy_zone_below"))
        pmos = num(g(v, "params", "mos"))
        if self.mos is not None and pmos is not None and abs(self.mos - pmos) > 1e-9 and num(ft.get("base")) is not None:
            buy = r2(ft["base"] * (1 - self.mos))
        self.zones = {"buy_below": buy, "sell_above": num(v.get("sell_zone_above")), "base_today": num(ft.get("base")),
                      "bear_today": num(ft.get("bear")), "bull_today": num(ft.get("bull"))}

    def band(self):
        z, p = self.zones, self.price
        if p is None or z["buy_below"] is None or z["sell_above"] is None or z["base_today"] is None:
            return None
        if p <= z["buy_below"]:
            return "below buy zone"
        if p <= z["base_today"]:
            return "buy zone to base value"
        if p <= z["sell_above"]:
            return "base value to sell zone"
        return "above sell zone"

    # -- main --
    def run(self):
        self.compute_zones()
        gates = self.gates()
        for gid, x in gates.items():
            x["test"] = TESTS[gid]
        items = self.items()
        pillars, total = {}, 0.0
        for p, ids in PILLARS.items():
            app = [i for i in ids if items[i]["status"] in ("scored", "no evidence")]
            earned = sum(items[i]["score"] or 0 for i in app)
            pts = 20.0 * earned / len(app) if app else 0.0
            total += pts
            pillars[p] = {"points": r2(pts), "earned": earned, "applicable": len(app),
                          "zero_items": [i for i in app if items[i]["score"] == 0],
                          "na_items": [i for i in ids if items[i]["status"] == "n/a"],
                          "pending_items": [i for i in ids if items[i]["status"] == "pending"],
                          "unverified_items": [i for i in ids if items[i]["unverified"] and i not in
                                               [j for j in ids if items[j]["status"] in ("n/a", "pending")]]}
        score = round_half_up(total)
        failed = [k for k, x in gates.items() if x["result"] == "fail"]
        tier = "pass" if failed or score < 45 else ("track closely" if score >= 70 else "research deeper")
        band = self.band()
        if failed:
            stance = "avoid"
        elif band is None:
            stance = "n/a"
        else:
            stance = {"below buy zone": "buy zone", "above sell zone": "sell zone"}.get(band, "hold")
        # confidence
        gate_app = [x for x in gates.values() if x["result"] not in ("n/a", "pending")]
        item_app = [x for x in items.values() if x["status"] in ("scored", "no evidence")]
        covered = sum(1 for x in gate_app if x["result"] in ("pass", "fail")) + \
            sum(1 for x in item_app if x["status"] == "scored")
        applicable = len(gate_app) + len(item_app)
        coverage = covered / applicable if applicable else 0.0
        agreement = num(self.val.get("agreement"))
        fresh = num(g(self.m, "freshness", "value"))
        out_look = self.outlook()
        spread = out_look.get("spread") if out_look else None
        if spread is not None:   # outlook.md §1: the bear-to-bull spread of the longest horizon is the uncertainty
            spread_term = min(1.0, max(0.0, 1 - spread / 0.20))
            weights = {"coverage": 0.4, "agreement": 0.2, "outlook_spread": 0.2, "freshness": 0.2}
            conf = round_half_up(100 * (0.4 * coverage + 0.2 * (agreement or 0) + 0.2 * spread_term + 0.2 * (fresh or 0)))
        else:
            spread_term, weights = None, {"coverage": 0.5, "agreement": 0.3, "freshness": 0.2}
            conf = round_half_up(100 * (0.5 * coverage + 0.3 * (agreement or 0) + 0.2 * (fresh or 0)))
        bh = g(self.val, "by_horizon")
        self.horizons = sorted((h for h in bh if horizon_years(h)), key=horizon_years) \
            if isinstance(bh, dict) and bh else list(HORIZONS)
        fv = {h: dict((g(self.val, "by_horizon", h) or {})) for h in self.horizons}
        cagr = {h: {s: self.cagr(fv[h].get(s), horizon_years(h)) for s in ("bear", "base", "bull")}
                for h in self.horizons}
        out = {
            "ticker": self.f.get("ticker"), "as_of": self.as_of, "mode": self.mode, "lens": self.lens,
            "sector_class": self.sector, "price": r2(self.price), "price_src": self.P,
            "derived_src": self.D, "score_src": self.S,
            "gates": gates, "items": items, "pillars": pillars,
            "score": score, "tier": tier, "stance": stance, "gates_failed": failed,
            "zones": {k: r2(v) for k, v in self.zones.items()},
            "margin_of_safety": self.mos if self.mos is not None else num(g(self.val, "params", "mos")),
            "fair_value": fv, "implied_cagr": cagr, "required_return": self.r,
            "confidence": {"value": conf, "coverage": r4(coverage), "covered": covered, "applicable": applicable,
                           "agreement": agreement, "freshness": fresh, "outlook_spread": spread,
                           "outlook_spread_term": r4(spread_term) if spread_term is not None else None,
                           "weights": weights},
            "outlook": out_look,
            "action": self.action(failed, band, fv, cagr),
        }
        st, why = self.short_term(failed, band)
        out["short_term"] = st
        out["action"]["options"] = self.options_ops(failed, band, out["action"], st)
        out["action"]["recommendation"] = self.recommendation(failed, out_look, out["action"])
        if st is None:
            out["short_term_reason"] = why
        out["open_questions"] = self.open_questions(gates, items, fresh)
        mk = sorted({m for x in list(gates.values()) + list(items.values()) for m in x["markers"]} | {self.D},
                    key=lambda s: int(s[1:]))
        self.sources[self.S] = {"class": "derived", "what": "score.py gates, items, action matrix and confidence "
                                "from %s" % " ".join(mk), "url": "file://" + os.path.abspath(self.out_path),
                                "as_of": self.as_of, "retrieved": self.as_of}
        out["sources"] = self.sources
        if self.notes:
            out["notes"] = self.notes
        return out

    def cagr(self, v, h):
        if num(v) is None or not self.price or v <= 0:
            return None
        return r4((v / self.price) ** (1.0 / h) - 1)

    def action(self, failed, band, fv, cagr):
        cells = {"below buy zone": ("accumulate", "add"), "buy zone to base value": ("wait for the buy zone", "hold"),
                 "base value to sell zone": ("avoid at this price", "hold, do not add"),
                 "above sell zone": ("avoid", "trim or sell")}
        if failed:
            nh, hd = "avoid", "exit"
        elif band is None:
            nh = hd = "n/a"
        else:
            nh, hd = cells[band]
        rows = []
        for h in self.horizons:
            base = cagr[h]["base"]
            verdict = None
            if base is not None and self.r is not None:
                verdict = ("attractive" if base >= self.r + 0.02 - 1e-12 else
                           "fair" if base >= self.r - 0.02 - 1e-12 else "unattractive")
            y = horizon_years(h)
            rows.append({"horizon": int(y) if y == int(y) else y, "label": horizon_label(y), "bear": fv[h].get("bear"), "base": fv[h].get("base"),
                         "bull": fv[h].get("bull"), "cagr": cagr[h], "verdict": verdict})
        z = self.zones
        trig = [{"name": "buy zone below", "price": r2(z["buy_below"])}, {"name": "base value", "price": r2(z["base_today"])},
                {"name": "sell zone above", "price": r2(z["sell_above"])}]
        times = []
        filed = day(g(self.f, "fundamentals", "annual", 0, "filed"))
        if filed:
            times.append({"name": "next 10-K", "date": add_year(filed).isoformat(), "basis": "last 10-K filed %s + 1 year"
                          % filed.isoformat(), "recheck": ["G1", "G2", "G4"], "markers": [self.F]})
        ne = g(self.f, "options", "next_earnings_date")
        if ne:
            times.append({"name": "next earnings", "date": str(ne)[:10], "basis": "options.next_earnings_date (secondary)",
                          "recheck": ["G1", "G2"], "markers": [g(self.f, "options", "src") or self.P]})
        he = g(self.h, "horizon_end")
        if he:
            times.append({"name": "holding period end", "date": str(he)[:10], "basis": "the question",
                          "recheck": ["G1", "G2", "G4"], "markers": []})
        act = {"holding": self.holding, "band": band,
               "cells": {"not_holding": nh, "holding": hd}, "cell": hd if self.holding else nh,
               "rows": rows, "price_triggers": trig, "time_triggers": times, "required_return": self.r}
        pos = g(self.h, "positions")
        if isinstance(pos, list) and pos:
            act["holdings"] = []
            for p in pos:
                sh, cost = num(p.get("shares")), num(p.get("avg_cost"))
                row = {"account": p.get("account"), "shares": sh, "avg_cost": cost, "value": None, "gain": None}
                if sh is not None and self.price is not None:
                    row["value"] = r2(sh * self.price)
                    if cost is not None:
                        row["gain"] = r2(sh * (self.price - cost))
                if band == "above sell zone" and not failed:
                    row["sell_line"] = "trim or sell: the model's value is realised"
                elif cost is not None and self.price is not None and self.price < cost:
                    row["sell_line"] = "price below cost: loss stated, stance applies unchanged"
                act["holdings"].append(row)
        return act

    # -- options operations (skills/score/rules/options-playbook.md) --
    LARGE_GAIN = 0.20   # this script's reading of "a large gain": price at least 20% above the average cost

    def options_ops(self, failed, band, act, st):
        """O1-O4 entries whose playbook condition holds, each on a contract from facts.options.contracts;
        otherwise one "not now" entry saying why. Educational shapes, not advice."""
        opt = self.f.get("options") if isinstance(self.f.get("options"), dict) else {}
        src = opt.get("src") or self.P
        marks = [src, self.S]
        price, z = self.price, self.zones
        pos = g(self.h, "positions") if isinstance(self.h, dict) else None
        pos = pos if isinstance(pos, list) else []
        shares = sum(num(p.get("shares")) or 0 for p in pos)
        cost = sum((num(p.get("shares")) or 0) * (num(p.get("avg_cost")) or 0) for p in pos)
        avg = cost / shares if shares and cost else None
        own100 = shares >= 100
        cells = act.get("cells") or {}
        hcell, ncell = cells.get("holding"), cells.get("not_holding")
        trend_down = bool(st) and st.get("stance") == "trend down"

        def not_now(reason):
            return [{"op": "not now", "fits_because": reason, "contract": None, "pay_or_receive": None,
                     "best_case": None, "worst_case": None, "markers": marks}]

        contracts = [c for c in (opt.get("contracts") or []) if isinstance(c, dict) and num(c.get("strike"))
                     and num(c.get("mid")) is not None and c.get("type") in ("call", "put")]
        if not opt.get("contracts"):
            return not_now("no contracts available")
        if not price:
            return not_now("no current price")

        def pick(kind, anchor, target, at_or_below=None):
            pool = [c for c in contracts if c["type"] == kind]
            if at_or_below is not None:
                pool = [c for c in pool if c["strike"] <= at_or_below + 1e-9]
            hit = [c for c in pool if c.get("anchor") == anchor]
            pool = hit or pool
            return min(pool, key=lambda c: (abs(c["strike"] - target), -c["strike"])) if pool and target else None

        def entry(op, fits, c, side, best, worst):
            mid, days = c["mid"], num(c.get("days"))
            ann = mid / price * 365 / days if days else None
            return {"op": op, "fits_because": fits,
                    "contract": {k: c.get(k) for k in ("type", "strike", "expiry", "days", "mid", "oi", "iv")},
                    "pay_or_receive": "%s ≈ %s/sh (%s of the price%s)" % (
                        side, money(mid), pct(mid / price, 1), ", %s a year" % pct(ann, 1) if ann is not None else ""),
                    "best_case": best, "worst_case": worst, "markers": marks}

        ops, missing = [], []
        large_gain = avg is not None and price >= avg * (1 + self.LARGE_GAIN)
        o1 = own100 and not failed and hcell in ("hold, do not add", "trim or sell")
        o2 = own100 and (failed or (large_gain and (hcell == "trim or sell" or trend_down)))
        o3 = not failed and not pos and ncell in ("wait for the buy zone", "avoid at this price")
        o4 = not failed and band == "below buy zone"
        if o1:
            sell = z.get("sell_above")
            above = sell is not None and sell >= price
            c = pick("call", "sell_zone" if above else "up_10", sell if above else price * 1.10)
            if c:
                k, m = c["strike"], c["mid"]
                ops.append(entry("O1 Covered call — get paid to agree to sell at %s" % money(k),
                                 "you hold %d shares and the model says %s" % (shares, hcell), c, "receive",
                                 "shares sold at %s plus the %s/sh premium" % (money(k), money(m)),
                                 "you miss gains above %s; a fall still hurts, softened by %s/sh" % (money(k), money(m))))
            else:
                missing.append("O1")
        if o2:
            c = pick("put", "down_10", price * 0.90)
            if c:
                k, m = c["strike"], c["mid"]
                why = ("a deal-breaker check failed and you hold %d shares" % shares if failed else
                       "you hold %d shares with a gain of %s and the model says %s" % (
                           shares, pct(price / avg - 1, 0), "trim or sell" if hcell == "trim or sell" else "the trend is down"))
                ops.append(entry("O2 Protective put — insurance below %s" % money(k), why, c, "pay",
                                 "if the price falls far below %s, the put pays the difference" % money(k),
                                 "the price stays above %s and the %s/sh premium (%s of the position) is lost"
                                 % (money(k), money(m), pct(m / price, 1))))
            else:
                missing.append("O2")
        if o3:
            buy = z.get("buy_below")
            c = pick("put", "buy_zone", buy, at_or_below=buy) if buy else None
            if c:
                k, m = c["strike"], c["mid"]
                ops.append(entry("O3 Cash-secured put — get paid to wait for %s" % money(k),
                                 "you hold none and the model says %s; a strike sits at or below the buy zone %s"
                                 % (ncell, money(buy)), c, "receive",
                                 "the price stays above %s and you keep %s/sh" % (money(k), money(m)),
                                 "the price falls far below %s and you must buy 100 shares at %s (%s net of the premium)"
                                 % (money(k), money(k), money(k - m))))
            else:
                missing.append("O3")
        if o4:
            c = pick("call", "price", price)
            if c:
                k, m = c["strike"], c["mid"]
                ops.append(entry("O4 Long call — a small bet on a rise, loss capped at %s/sh" % money(m),
                                 "the price is in the buy zone and no deal-breaker check failed", c, "pay",
                                 "the price rises well above %s (strike plus premium)" % money(k + m),
                                 "the price stays below %s and the whole %s/sh is lost" % (money(k), money(m))))
            else:
                missing.append("O4")
        if ops:
            return ops
        if missing:
            return not_now("%s would fit, but the chain has no matching contract" % ", ".join(missing))
        if failed:
            return not_now("a deal-breaker check failed and you hold fewer than 100 shares, so there is no operation "
                           "here except staying away")
        if pos and not own100:
            return not_now("you hold %d shares; each contract covers 100, so the covered call and the protective put "
                           "do not fit" % shares)
        if pos:
            return not_now("you hold shares and the model says %s, so there is no operation here except holding" % hcell)
        return not_now("the price is %s and you hold none, so there is no operation here except waiting"
                       % (band or "not valued"))

    def trend(self):
        """ST1 trend state from price, 50- and 200-day averages: up / down / none (None without inputs)."""
        mo = self.f.get("momentum") if isinstance(self.f.get("momentum"), dict) else {}
        price, ma50, ma200 = self.price, num(mo.get("ma50")), num(mo.get("ma200"))
        if None in (price, ma50, ma200) or not ma200:
            return None
        if abs(price / ma200 - 1) < 0.01 or abs(ma50 / ma200 - 1) < 0.01:
            return "none"
        if price > ma200 and ma50 > ma200:
            return "up"
        if price < ma200 and ma50 < ma200:
            return "down"
        return "none"

    # -- outlook and recommendation (skills/score/rules/outlook.md §1, §5) --
    def outlook(self):
        """metrics.outlook with a verdict per horizon (base expected return vs r_base ± 2 pp), or None."""
        o = self.m.get("outlook")
        if not isinstance(o, dict) or not isinstance(o.get("horizons"), dict) or not o["horizons"]:
            return None
        r = num(g(o, "params", "r_base")) or self.r
        hz = {}
        for h, x in o["horizons"].items():
            if not horizon_years(h) or not isinstance(x, dict):
                continue
            base = num(g(x, "base", "cagr"))
            verdict = x.get("verdict")
            if verdict is None and base is not None and r is not None:
                verdict = self.verdict3(base, r)
            hz[h] = dict(x, verdict=verdict, label=horizon_label(horizon_years(h)))
        if not hz:
            return None
        long_ = [h for h in hz if horizon_years(h) >= 1]
        longest = max(long_, key=horizon_years) if long_ else None
        out = {"horizons": dict(sorted(hz.items(), key=lambda kv: horizon_years(kv[0]))), "longest": longest,
               "reference": self.reference_horizon(hz, longest),
               "required_return": r, "params": o.get("params"), "months": o.get("months"),
               "method_note": o.get("method_note"), "markers": [self.D]}
        if longest:
            b, u = num(g(hz[longest], "bear", "cagr")), num(g(hz[longest], "bull", "cagr"))
            out["spread"] = r4(u - b) if None not in (b, u) else None
        return out

    def reference_horizon(self, hz, longest):
        """The horizon the answer leads with: the user's longest stated horizon of a year or more when the
        question named one (request.json horizon_source "question"); otherwise 5 years; else the longest."""
        if self.req.get("horizon_source") == "question":
            asked = [h for h in hz if horizon_years(h) >= 1 and any(
                abs(horizon_years(h) - float(y)) < 1e-9 for y in self.req.get("horizons_years") or []
                if isinstance(y, (int, float)))]
            if asked:
                return max(asked, key=horizon_years)
        five = [h for h in hz if horizon_years(h) == 5]
        return five[0] if five else longest

    @staticmethod
    def verdict3(base, r):
        return "attractive" if base >= r + 0.02 - 1e-12 else "fair" if base >= r - 0.02 - 1e-12 else "expensive"

    REC = {  # outlook.md §5: (holding, return band, trend) -> recommendation; "*" = any trend
        (True, "above", "*"): "hold; add on pullbacks to the 50-day average",
        (True, "within", "up"): "hold; re-check at the next event",
        (True, "within", "none"): "hold; re-check at the next event",
        (True, "within", "down"): "hold, consider trimming to target weight",
        (True, "below", "up"): "trim into strength; trailing trigger at the 50-day average",
        (True, "below", "down"): "trim or sell",
        (True, "below", "none"): "trim or sell",
        (False, "above", "up"): "accumulate (staged entries)",
        (False, "above", "none"): "accumulate (staged entries)",
        (False, "above", "down"): "wait for the trend to turn; first entry at the 200-day average",
        (False, "within", "*"): "buy only on pullbacks: 50-day average, or 10% below today",
        (False, "below", "*"): "wait; the strict value and the pullback levels are the entry map",
    }

    def recommendation(self, failed, out_look, act):
        mo = self.f.get("momentum") if isinstance(self.f.get("momentum"), dict) else {}
        cons = self.f.get("consensus") if isinstance(self.f.get("consensus"), dict) else {}
        levels = {"ma50": r2(num(mo.get("ma50"))), "ma200": r2(num(mo.get("ma200"))),
                  "pullback_10pct": r2(self.price * 0.9) if self.price else None,
                  "strict_value": r2(self.zones.get("base_today")),
                  "consensus_mean": r2(num(g(cons, "targets", "mean"))) if cons.get("available") else None}
        trend = self.trend()
        marks = [self.D, self.S] + ([mo.get("src")] if mo.get("src") else []) + \
            ([cons["src"]] if cons.get("available") and cons.get("src") else [])
        rec = {"levels": levels, "trend": trend, "markers": [m for m in dict.fromkeys(marks) if m]}
        if failed:
            rec.update(holding="exit", not_holding="avoid", basis="gate", band=None,
                       note="failed gate(s) %s override every other input" % ", ".join(failed))
        elif out_look and out_look.get("reference"):
            h = out_look["reference"]
            er, r = num(g(out_look, "horizons", h, "base", "cagr")), out_look.get("required_return")
            if er is None or r is None:
                rec.update(basis="strict value", holding=act["cells"]["holding"], not_holding=act["cells"]["not_holding"],
                           note="outlook base return or required return missing; the strict value cells are shown")
            else:
                band = "above" if er >= r + 0.02 - 1e-12 else "within" if er >= r - 0.02 - 1e-12 else "below"
                t = trend or "none"
                cell = lambda held: self.REC.get((held, band, t)) or self.REC[(held, band, "*")]  # noqa: E731
                rec.update(basis="outlook", horizon=h, label=horizon_label(horizon_years(h)), expected_return=er,
                           required_return=r, band=band, holding=cell(True), not_holding=cell(False))
                if trend is None:
                    rec["note"] = "trend inputs missing (momentum); read as no trend"
        else:
            rec.update(basis="strict value", holding=act["cells"]["holding"], not_holding=act["cells"]["not_holding"],
                       note="metrics.outlook absent (or no horizon of a year or more); the strict value cells are shown")
        rec["cell"] = rec["holding"] if self.holding else rec["not_holding"]
        return rec

    def short_term(self, failed, band):
        if self.lens not in ("short", "both"):
            return None, "lens long"
        mo = self.f.get("momentum")
        if not isinstance(mo, dict):
            return None, "facts.momentum absent"
        mk = [mo.get("src") or self.S]
        mkt, opt = self.f.get("market") or {}, self.f.get("options")
        price = self.price
        ma50, ma200 = num(mo.get("ma50")), num(mo.get("ma200"))
        st = {}
        if None in (price, ma50, ma200):
            st["ST1"] = {"result": "no evidence", "value": None, "markers": mk}
        else:
            res = "trend " + self.trend() if self.trend() != "none" else "no trend"
            st["ST1"] = {"result": res, "value": {"price": r2(price), "ma50": r2(ma50), "ma200": r2(ma200)},
                         "markers": [self.P] + mk}
        r12, r6 = num(mo.get("return_12m_skip_1m")), num(mo.get("return_6m"))
        mom = "no evidence" if None in (r12, r6) else (
            "positive" if r12 > 0 and r6 > 0 else "negative" if r12 < 0 and r6 < 0 else "mixed")
        spy = mkt.get("spy") if isinstance(mkt, dict) else None
        st["ST2"] = {"result": mom, "value": {"return_12m_skip_1m": r4(r12), "return_6m": r4(r6),
                                              "spy_return_12m": r4(num(g(spy, "return_12m"))),
                                              "realized_vol_1y": r4(num(mo.get("realized_vol_1y")))},
                     "markers": mk + ([spy["src"]] if isinstance(spy, dict) and spy.get("src") else [])}
        d52 = num(mo.get("pct_from_52w_high"))
        st["ST3"] = {"result": "no evidence" if d52 is None else ("near high" if abs(d52) <= 0.05 else "not near high"),
                     "value": r4(d52), "markers": mk}
        v30, v1 = num(mo.get("realized_vol_30d")), num(mo.get("realized_vol_1y"))
        if v30 is None or not v1:
            st["ST4"] = {"result": "no evidence", "value": None, "markers": mk}
        else:
            ratio = v30 / v1
            st["ST4"] = {"result": "calm" if ratio < 0.8 else "stressed" if ratio > 1.5 else "normal",
                         "value": {"realized_vol_30d": r4(v30), "realized_vol_1y": r4(v1), "ratio": r4(ratio)},
                         "markers": mk}
        if isinstance(opt, dict) and num(opt.get("implied_move_pct")) is not None:
            amt = num(opt.get("implied_move_abs"))
            st["ST5"] = {"result": "implied move %s to %s" % (pct(opt["implied_move_pct"]), opt.get("expiry_used")),
                         "value": {"implied_move_pct": r4(opt["implied_move_pct"]), "implied_move_abs": r2(amt),
                                   "low": r2(price - amt) if amt is not None and price else None,
                                   "high": r2(price + amt) if amt is not None and price else None,
                                   "expiry": opt.get("expiry_used")},
                         "markers": [opt.get("src") or self.P]}
        else:
            st["ST5"] = {"result": "no evidence", "value": None, "markers": [],
                         "note": g(opt, "reason") or "options chain unavailable"}
        events = []
        if isinstance(opt, dict) and opt.get("next_earnings_date"):
            events.append({"event": "next earnings", "date": str(opt["next_earnings_date"])[:10],
                           "markers": [opt.get("src") or self.P]})
        asof = day(self.as_of)
        for x in self.f.get("filings_recent") or []:
            items = [i.strip() for i in str(x.get("items", "")).split(",")]
            fd = day(x.get("filed"))
            if str(x.get("form", "")).startswith("8-K") and ({"2.02", "8.01"} & set(items)) and fd and asof \
                    and (asof - fd).days <= 90:
                events.append({"event": "8-K Items %s" % x.get("items"), "date": fd.isoformat(),
                               "markers": [x.get("src") or "S2"]})
        filed = day(g(self.f, "fundamentals", "annual", 0, "filed"))
        if filed:
            events.append({"event": "next 10-K", "date": add_year(filed).isoformat(), "markers": [self.F]})
        st["ST6"] = {"result": "%d events" % len(events), "value": events, "markers": []}
        rs, rsec = num(mo.get("rel_strength_spy_6m")), num(mo.get("rel_strength_sector_6m"))
        st["ST7"] = {"result": "no evidence" if rs is None else ("outperforming SPY" if rs > 0 else "lagging SPY"),
                     "value": {"rel_strength_spy_6m": r4(rs), "rel_strength_sector_6m": r4(rsec)}, "markers": mk}
        for k, x in st.items():
            x["source"] = ST_SOURCES[k]
        trend = st["ST1"]["result"]
        stance = ("trend up" if trend == "trend up" and mom == "positive" else
                  "trend down" if trend == "trend down" and mom == "negative" else "no trend")
        block = {"items": st, "stance": stance,
                 "caveat": "Short-horizon signals describe the recent past; the sources above report modest average "
                           "edges with large drawdowns in stressed regimes. A failed gate overrides this lens."}
        if failed:
            block["gate_override"] = "failed gate %s: stance avoid stands" % ", ".join(failed)
        if self.holding and band == "above sell zone":
            if stance == "trend down":
                block["holding_note"] = "trend down and price above the sell zone: the long-horizon trim or sell stands"
            elif stance == "trend up":
                block["holding_note"] = ("trend up and price above the sell zone: the lens suggests a trailing trigger "
                                         "at the 50-day average %s rather than an immediate sale (the lens's "
                                         "suggestion)" % money(ma50))
        return block, None

    def open_questions(self, gates, items, fresh):
        out = []
        for gid, x in gates.items():
            if x["result"] == "no evidence":
                src = FROM["evidence"] % WHERE["G4"] if gid == "G4" else "facts.py (%s inputs)" % gid
                out.append({"id": gid, "text": "%s no evidence: %s; would come from %s" % (gid, x["note"], src),
                            "markers": x["markers"]})
            elif x.get("coverage_short"):
                out.append({"id": gid, "text": "%s; would come from a longer "
                            "submissions history (facts.py filings_recent)" % x["note"], "markers": x["markers"]})
        for iid in sorted(items, key=lambda s: tuple(int(p) for p in s.split("."))):
            x = items[iid]
            if x["status"] == "no evidence":
                src = FROM["evidence"] % WHERE[iid] if x["evidence_required"] else FROM["fund"]
                out.append({"id": iid, "text": "no evidence: %s; would come from %s" % (x["note"], src),
                            "markers": x["markers"]})
            elif x["status"] == "scored" and x["score"] == 0:
                tail = FROM["price"] if iid.startswith("4.") else "no data gap; changes with %s" % FROM["fund"]
                if iid == "4.5":
                    tail += "; asset-light firms fail by construction per card 4.5, formula not widened"
                if iid == "2.3":
                    tail += "; deferred revenue in current liabilities can make this a model limitation"
                out.append({"id": iid, "text": "%s (%s); %s" % (x["note"], x["test"], tail), "markers": x["markers"]})
        if fresh is not None and fresh < 1:
            fr = self.m.get("freshness") or {}
            out.append({"id": "freshness", "text": "freshness %s: price age %s trading days, newer 10-K %s; refreshes "
                        "with facts.py" % (fresh, fr.get("price_age_trading_days"), fr.get("newer_10k_exists")),
                        "markers": [self.D]})
        return out



def _resolved_mos(a):
    """--mos flag, else the project's configured margin of safety (common.resolve_mos), else None (metrics params)."""
    if a.mos is not None:
        return a.mos
    try:
        from common import resolve_mos, resolve_setting
        if resolve_setting("margin_of_safety", None, getattr(a, "data", ""), project=getattr(a, "project", "")) in (None, ""):
            return None
        return resolve_mos(getattr(a, "data", ""), None, project=getattr(a, "project", ""))
    except Exception:  # noqa: BLE001 - no common.py or no setting: fall back to metrics params
        return None


def main(argv=None):
    ap = EnvelopeParser(description="Score one store folder into scorecard.json")
    ap.add_argument("target", help="ticker or stock folder path")
    ap.add_argument("--mos", type=float, default=None, help="margin of safety (default metrics params.mos)")
    ap.add_argument("--lens", choices=("long", "short", "both"), default=None,
                    help="default: request.json lens, else long")
    ap.add_argument("--mode", choices=("full", "screen"), default="full")
    ap.add_argument("--holding", action="store_true", help="treat the position as held")
    add_common_args(ap)
    a = ap.parse_args(argv)
    st = locate(a.target, a)
    fp = st.facts
    facts = load_json(fp)
    if facts is None:
        raise FileNotFoundError("facts/facts.json not found in %s" % st.root)
    out = a.out or st.scorecard
    req = load_json(os.path.join(st.root, "request.json"))
    req = req if isinstance(req, dict) else {}
    lens = a.lens or (req.get("lens") if req.get("lens") in ("long", "short", "both") else None) or "long"
    holding = a.holding or bool(str(req.get("holdings_text") or "").strip())
    sc = Scorer(facts, load_json(st.evidence), load_json(st.holdings), _resolved_mos(a), lens, a.mode, holding,
                facts_path=fp, out_path=out, request=req).run()
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(sc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps({"scorecard": out, "ticker": sc["ticker"], "score": sc["score"], "tier": sc["tier"],
          "stance": sc["stance"], "confidence": sc["confidence"]["value"], "gates_failed": sc["gates_failed"]}))


if __name__ == "__main__":
    run_main("score.py", main)
