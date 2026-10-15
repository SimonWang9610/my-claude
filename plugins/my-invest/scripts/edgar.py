#!/usr/bin/env python3
"""edgar.py TICKER - SEC EDGAR: ticker -> CIK, submissions, companyfacts -> up to 10 normalized annual rows.

Normalization follows skills/analyze/references/facts-schema.md ("Normalization rules").
Prints one JSON object: ticker, cik, name, sic, sector_class, sources, fundamentals, shares_history.
"""
import datetime as dt
import sys

import common
from common import FetchError

SCRIPT = "edgar.py"
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK%s.json"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK%s.json"
MAX_YEARS = 10

# field -> (kind, unit, alternatives, outflow)
# alternative: "Concept" | ("sum", [c1, c2]) summing the components present | ("all", [c1, c2]) sum, only when every
# component is present (composite fallback, tried after the aggregate concepts) | ("diff", A, [B1, B2]) A minus Bs present.
# First alternative that yields a value for a period wins (per period, so concept changes over time are bridged).
F = "flow"
I = "instant"
FIELDS = [
    ("revenue", F, "USD", ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                           "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet",
                           "SalesRevenueGoodsNet", "RevenuesNetOfInterestExpense"], False),
    ("cogs", F, "USD", ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"], False),
    ("gross_profit", F, "USD", ["GrossProfit"], False),  # fallback revenue - cogs applied after
    ("sga", F, "USD", ["SellingGeneralAndAdministrativeExpense",
                       ("all", ["SellingAndMarketingExpense", "GeneralAndAdministrativeExpense"])], False),
    ("rd", F, "USD", ["ResearchAndDevelopmentExpense",
                      "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"], False),
    ("operating_income", F, "USD", ["OperatingIncomeLoss"], False),
    ("interest_expense", F, "USD", ["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt"], False),
    ("pretax_income", F, "USD", [
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"],
     False),
    ("income_tax", F, "USD", ["IncomeTaxExpenseBenefit"], False),
    ("net_income", F, "USD", ["NetIncomeLoss", "ProfitLoss"], False),
    ("eps_diluted", F, "USD/shares", ["EarningsPerShareDiluted"], False),
    ("shares_diluted", F, "shares", ["WeightedAverageNumberOfDilutedSharesOutstanding"], False),
    ("ocf", F, "USD", ["NetCashProvidedByUsedInOperatingActivities",
                       "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"], False),
    ("capex", F, "USD", ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
                         "PaymentsForCapitalImprovements"], True),
    ("da", F, "USD", ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization",
                      "DepreciationAmortizationAndOther", "DepreciationAmortizationAndAccretionNet",
                      "Depreciation"], False),
    ("dividends_paid", F, "USD", ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"], True),
    ("buybacks", F, "USD", ["PaymentsForRepurchaseOfCommonStock"], True),
    ("debt_issued", F, "USD", ["ProceedsFromIssuanceOfLongTermDebt", "ProceedsFromIssuanceOfDebt",
                               "ProceedsFromIssuanceOfSeniorLongTermDebt",
                               "ProceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet",
                               "ProceedsFromDebtMaturingInMoreThanThreeMonths"], False),
    ("debt_repaid", F, "USD", ["RepaymentsOfLongTermDebt", "RepaymentsOfDebt", "RepaymentsOfSeniorDebt",
                              "RepaymentsOfLongTermDebtAndCapitalSecurities",
                              "RepaymentsOfDebtMaturingInMoreThanThreeMonths"], True),
    ("equity_issued", F, "USD", ["ProceedsFromIssuanceOfCommonStock", "StockIssuedDuringPeriodValueNewIssues"], False),
    ("total_assets", I, "USD", ["Assets"], False),
    ("current_assets", I, "USD", ["AssetsCurrent"], False),
    ("cash", I, "USD", ["CashAndCashEquivalentsAtCarryingValue",
                        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "Cash"], False),
    ("receivables", I, "USD", ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent"], False),
    ("inventory", I, "USD", ["InventoryNet"], False),
    ("ppe_net", I, "USD", ["PropertyPlantAndEquipmentNet"], False),
    ("goodwill_intangibles", I, "USD", ["IntangibleAssetsNetIncludingGoodwill",
                                        ("sum", ["Goodwill", "IntangibleAssetsNetExcludingGoodwill"])], False),
    ("current_liabilities", I, "USD", ["LiabilitiesCurrent"], False),
    ("st_debt", I, "USD", ["DebtCurrent", ("sum", ["ShortTermBorrowings", "CommercialPaper", "LongTermDebtCurrent"])],
     False),
    ("lt_debt", I, "USD", ["LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations",
                           "LongTermNotesPayable", "LongTermDebt"], False),
    ("total_liabilities", I, "USD", [
        "Liabilities",
        ("diff", "LiabilitiesAndStockholdersEquity", ["StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"]),
        ("diff", "LiabilitiesAndStockholdersEquity", ["StockholdersEquity"])], False),
    ("equity", I, "USD", ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
     False),
    ("retained_earnings", I, "USD", ["RetainedEarningsAccumulatedDeficit"], False),
    ("taxes_payable", I, "USD", ["TaxesPayableCurrent", "IncomeTaxesPayableCurrent", "IncomeTaxesPayable",
                                 "AccruedIncomeTaxesCurrent"], False),
    ("goodwill_impairment", F, "USD", ["GoodwillImpairmentLoss", "GoodwillAndIntangibleAssetImpairment",
                                       "ImpairmentOfIntangibleAssetsIncludingGoodwill"], False),
]
ANCHORS = ("Assets", "LiabilitiesAndStockholdersEquity")
# As originally reported: later 10-Ks restate these for splits and metrics.py split-adjusts itself.
EARLIEST_FILED = ("shares_diluted", "eps_diluted")
FULL_YEAR_DAYS = (350, 380)  # covers 52/53-week years


def sector_class(sic):
    """SIC -> sector_class per the schema table."""
    try:
        n = int(sic)
    except (TypeError, ValueError):
        return "non-manufacturer"
    if n == 6798:
        return "reit"
    if 6000 <= n <= 6799:
        return "financial"
    if 4900 <= n <= 4999:
        return "utility"
    if 2000 <= n <= 3999:
        return "manufacturer"
    return "non-manufacturer"


def resolve_cik(ctx, ticker):
    """Ticker -> (cik_int, title, retrieved) via company_tickers.json."""
    data, retrieved = ctx.get_json(TICKERS_URL, "edgar")
    want = {ticker.upper(), ticker.upper().replace(".", "-"), ticker.upper().replace("-", ".")}
    for row in data.values():
        if str(row.get("ticker", "")).upper() in want:
            return int(row["cik_str"]), row.get("title", ""), retrieved
    raise FetchError("ticker %s not found in SEC company_tickers.json (US SEC registrants only)" % ticker)


def _days(f):
    a = dt.date.fromisoformat(f["start"])
    b = dt.date.fromisoformat(f["end"])
    return (b - a).days


def facts_for(usgaap, concept, unit):
    c = usgaap.get(concept)
    return (c or {}).get("units", {}).get(unit, []) if c else []


def pick(facts, end, flow, earliest=False):
    """Latest-`filed` (earliest when `earliest`) 10-K, fp=FY fact for period `end`; flow facts span a full year."""
    best = None
    for f in facts:
        if f.get("form") != "10-K" or f.get("fp") != "FY" or f.get("end") != end:
            continue
        if flow:
            if "start" not in f or not (FULL_YEAR_DAYS[0] <= _days(f) <= FULL_YEAR_DAYS[1]):
                continue
        elif "start" in f:
            continue
        if best is None:
            best = f
            continue
        k, kb = (f.get("filed", ""), f.get("accn", "")), (best.get("filed", ""), best.get("accn", ""))
        if (k < kb) if earliest else (k > kb):
            best = f
    return best


def fiscal_periods(usgaap):
    """{period_end: {fy, filed, accn}} from each 10-K's own balance-sheet date (latest end per accn)."""
    by_accn = {}
    for concept in ANCHORS:
        for f in facts_for(usgaap, concept, "USD"):
            if f.get("form") != "10-K" or f.get("fp") != "FY" or "start" in f:
                continue
            cur = by_accn.get(f["accn"])
            if cur is None or f["end"] > cur["end"]:
                by_accn[f["accn"]] = {"end": f["end"], "fy": f.get("fy"), "filed": f.get("filed", ""), "accn": f["accn"]}
    periods = {}
    for rec in by_accn.values():
        cur = periods.get(rec["end"])
        if cur is None or rec["filed"] > cur["filed"]:
            periods[rec["end"]] = rec
    return periods


def _label(alt):
    if isinstance(alt, str):
        return alt
    if alt[0] in ("sum", "all"):
        return "sum: " + " + ".join(alt[1])
    return "%s-%s" % (alt[1], "-".join(alt[2]))


def _alt_concepts(alt):
    if isinstance(alt, str):
        return [alt]
    return list(alt[1]) if alt[0] in ("sum", "all") else [alt[1]] + list(alt[2])


def resolve_alt(usgaap, alt, unit, end, flow, earliest=False):
    if isinstance(alt, str):
        f = pick(facts_for(usgaap, alt, unit), end, flow, earliest)
        return None if f is None else f["val"]
    if alt[0] in ("sum", "all"):
        vals = [pick(facts_for(usgaap, c, unit), end, flow, earliest) for c in alt[1]]
        vals = [v["val"] for v in vals if v is not None]
        if alt[0] == "all" and len(vals) != len(alt[1]):
            return None
        return sum(vals) if vals else None
    a = pick(facts_for(usgaap, alt[1], unit), end, flow, earliest)
    if a is None:
        return None
    bs = [pick(facts_for(usgaap, c, unit), end, flow, earliest) for c in alt[2]]
    bs = [b["val"] for b in bs if b is not None]
    return a["val"] - sum(bs) if bs else None


def normalize(companyfacts, src="S1", max_years=MAX_YEARS):
    """companyfacts JSON -> (annual rows newest first, concept_map, missing)."""
    usgaap = companyfacts.get("facts", {}).get("us-gaap", {})
    periods = fiscal_periods(usgaap)
    if not periods:
        raise FetchError("no 10-K annual facts in companyfacts (not a US 10-K filer?)")
    ends = sorted(periods, reverse=True)[:max_years]
    used = {name: [] for name, *_ in FIELDS}
    missing = []
    rows = []
    for end in ends:
        p = periods[end]
        row = {"fy": p["fy"], "period_end": end, "form": "10-K", "filed": p["filed"], "accn": p["accn"]}
        for name, kind, unit, alts, outflow in FIELDS:
            flow = kind == F
            val = None
            for alt in alts:
                val = resolve_alt(usgaap, alt, unit, end, flow, name in EARLIEST_FILED)
                if val is not None:
                    if _label(alt) not in used[name]:
                        used[name].append(_label(alt))
                    break
            if val is not None and outflow:
                val = abs(val)
            row[name] = val
        if row["gross_profit"] is None and row["revenue"] is not None and row["cogs"] is not None:
            row["gross_profit"] = row["revenue"] - row["cogs"]
            if "revenue-cogs" not in used["gross_profit"]:
                used["gross_profit"].append("revenue-cogs")
        for name, kind, unit, alts, _ in FIELDS:
            if row[name] is not None:
                continue
            seen = any(facts_for(usgaap, c, unit) for a in alts for c in _alt_concepts(a))
            if name == "gross_profit":
                reason = "GrossProfit absent and revenue/cogs unavailable"
            elif not seen:
                reason = "no us-gaap concept matched"
            elif kind == F:
                reason = "concept present but no full-year FY 10-K fact for this period"
            else:
                reason = "concept present but no FY 10-K instant fact for this period"
            missing.append({"field": name, "fy": row["fy"], "reason": reason})
        row["src"] = src
        rows.append(row)
    concept_map = {}
    for name, kind, unit, alts, _ in FIELDS:
        concept_map[name] = used[name] or [_label(a) for a in alts]
    return rows, concept_map, missing


def latest_periodic(sub):
    """Newest filing date of a 10-K or 10-Q in the submissions feed ("" when none)."""
    r = sub.get("filings", {}).get("recent", {})
    return max([d for d, f in zip(r.get("filingDate", []), r.get("form", [])) if f in ("10-K", "10-Q")] or [""])


def needs_fundamentals(sub, annual_filed, seen=""):
    """True when a 10-K or 10-Q was filed after annual[0].filed and after the last one already acted on."""
    return latest_periodic(sub) > max(annual_filed or "", seen or "")


def reusable(prev):
    """A previous facts.json can stand in for a companyfacts fetch."""
    try:
        return bool(prev["cik"] and prev["fundamentals"]["annual"]
                    and prev["sources"]["S1"]["what"].startswith("companyfacts"))
    except (KeyError, TypeError):
        return False


def reuse(ctx, prev, sub, sub_ret):
    """Same shape as `build`, from a previous facts.json (cached normalization) and a fresh submissions feed."""
    cik10, sub_url = prev["cik"], SUBMISSIONS_URL % prev["cik"]
    prov = common.Provenance()
    s1 = prev["sources"]["S1"]
    prov.add(s1["class"], s1["what"], s1["url"], s1["as_of"], s1["retrieved"], sid="S1")
    recent = sub.get("filings", {}).get("recent", {}).get("filingDate", [])
    prov.add("primary", "submissions: filings index", sub_url, recent[0] if recent else "", sub_ret, sid="S2")
    fund = {k: v for k, v in prev["fundamentals"].items() if k != "shares_history"}
    sic = sub.get("sic", "") or prev.get("sic", "")
    return {"ticker": prev["ticker"], "cik": cik10, "name": sub.get("name") or prev.get("name"), "sic": sic,
            "sector_class": sector_class(sic), "retrieved": common.iso(ctx.now()), "sources": prov.sources,
            "fundamentals": fund, "shares_history": prev["fundamentals"].get("shares_history", [])}


def build(ctx, ticker, sub=None):
    """`sub` = (submissions JSON, retrieved) when the caller already fetched it (facts.py shares one fetch)."""
    ticker = ticker.upper()
    cik, title, _ = resolve_cik(ctx, ticker)
    cik10 = "%010d" % cik
    sub_url, cf_url = SUBMISSIONS_URL % cik10, COMPANYFACTS_URL % cik10
    sub, sub_ret = sub or ctx.get_json(sub_url, "edgar")
    cf, cf_ret = ctx.get_json(cf_url, "edgar")
    rows, concept_map, missing = normalize(cf, "S1")
    prov = common.Provenance()
    first, last = rows[-1]["fy"], rows[0]["fy"]
    prov.add("primary", "companyfacts (XBRL) FY%s-FY%s" % (first, last), cf_url, "FY%s" % last, cf_ret)
    recent = sub.get("filings", {}).get("recent", {}).get("filingDate", [])
    prov.add("primary", "submissions: filings index", sub_url, recent[0] if recent else "", sub_ret)
    sic = sub.get("sic", "") or ""
    return {
        "ticker": ticker, "cik": cik10, "name": sub.get("name") or title, "sic": sic,
        "sector_class": sector_class(sic), "retrieved": common.iso(ctx.now()),
        "sources": prov.sources,
        "fundamentals": {"annual": rows, "concept_map": concept_map, "missing": missing},
        "shares_history": [{"fy": r["fy"], "period_end": r["period_end"], "shares_diluted": r["shares_diluted"],
                            "src": "S1"} for r in rows if r["shares_diluted"] is not None],
    }


def run(argv=None):
    ap = common.base_parser("SEC EDGAR fundamentals for one ticker")
    ap.add_argument("ticker")
    args = ap.parse_args(argv)
    out = build(common.ctx_from(args), args.ticker)
    common.emit(out, args.out)
    return out


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
