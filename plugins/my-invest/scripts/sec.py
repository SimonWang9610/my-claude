#!/usr/bin/env python3
"""sec.py TICKER [--years N] - primary-source fundamentals: the SEC companyfacts API into `fundamentals`.

Usage: python3 sec.py AAPL [--years 5] [--md] --project P
Resolves the CIK from the SEC ticker file, fetches every XBRL fact the company ever filed, keeps the concepts
listed in CONCEPTS for periods ending within --years (plus everything in the latest filing) and stores them in
long form; of the filings that report the same period, the latest filed wins (restatements win).
--md prints the latest annual value per concept (from the fundamentals_annual view).
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import db  # noqa: E402

SCRIPT = "sec.py"
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK%s.json"
NOT_REGISTRANT = "%s is not an SEC registrant (a fund?); use yahoo.py profile"

# (taxonomy, concept); stored without the namespace.
CONCEPTS = [("us-gaap", c) for c in (
    "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "CostOfRevenue", "CostOfGoodsAndServicesSold",
    "GrossProfit", "OperatingIncomeLoss", "NetIncomeLoss", "EarningsPerShareDiluted",
    "WeightedAverageNumberOfDilutedSharesOutstanding", "ResearchAndDevelopmentExpense",
    "SellingGeneralAndAdministrativeExpense", "DepreciationDepletionAndAmortization", "InterestExpense",
    "IncomeTaxExpenseBenefit", "NetCashProvidedByUsedInOperatingActivities",
    "PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsForRepurchaseOfCommonStock", "PaymentsOfDividends",
    "PaymentsOfDividendsCommonStock", "Assets", "Liabilities", "StockholdersEquity",
    "CashAndCashEquivalentsAtCarryingValue", "MarketableSecuritiesCurrent", "ShortTermInvestments", "LongTermDebt",
    "LongTermDebtNoncurrent", "LongTermDebtCurrent", "DebtCurrent", "Goodwill", "AccountsReceivableNetCurrent",
    "InventoryNet")] + [("dei", "EntityCommonStockSharesOutstanding")]

_TICKERS = {}  # ticker -> 10-digit CIK, parsed once per process


# --- CIK ----------------------------------------------------------------------------------------
def load_tickers(ua):
    """The SEC ticker file as {TICKER: cik10}; parsed once and kept in memory only."""
    if not _TICKERS:
        data = common.get_json(TICKERS_URL, ua)
        for entry in (data.values() if isinstance(data, dict) else data):
            _TICKERS[str(entry["ticker"]).upper()] = "%010d" % int(entry["cik_str"])
    return _TICKERS


def resolve_cik(conn, ticker, ua):
    """securities.cik when stored, else the SEC ticker file; None when the ticker is not a registrant."""
    row = db.one(conn, "SELECT cik FROM securities WHERE ticker = ?", (ticker,))
    if row and row["cik"]:
        return row["cik"]
    return load_tickers(ua).get(ticker)


# --- facts --------------------------------------------------------------------------------------
def _date(s):
    return dt.date.fromisoformat(s)


def select_facts(data, years, today=None):
    """Flatten companyfacts into fundamentals rows (without ticker/source_id), oldest filing first, so that an
    upsert leaves the latest filed fact for each (concept, unit, period_end, period_start)."""
    today = today or dt.date.today()
    cutoff = (today - dt.timedelta(days=365 * years)).isoformat()
    facts = data.get("facts", {})
    raw = []
    for taxonomy, concept in CONCEPTS:
        units = facts.get(taxonomy, {}).get(concept, {}).get("units", {})
        for unit, items in units.items():
            for f in items:
                if f.get("val") is None or not f.get("end"):
                    continue
                raw.append((concept, unit, f))
    latest_filed = max((f.get("filed") or "" for _, _, f in raw), default="")
    latest_accns = {f.get("accn") for _, _, f in raw if f.get("filed") == latest_filed}
    rows = []
    for concept, unit, f in raw:
        if f["end"] < cutoff and f.get("accn") not in latest_accns:
            continue
        start = f.get("start") or ""
        rows.append({
            "concept": concept, "unit": unit, "period_start": start, "period_end": f["end"],
            "days": (_date(f["end"]) - _date(start)).days if start else None,
            "fy": f.get("fy"), "fp": f.get("fp"), "form": f.get("form"), "filed": f.get("filed"),
            "accession": f.get("accn"), "frame": f.get("frame"), "value": float(f["val"]),
        })
    rows.sort(key=lambda r: (r["filed"] or "", r["accession"] or ""))
    return rows


def store_facts(conn, ticker, data, years, source_id, today=None):
    """Upsert the selected facts for one ticker; returns {concept: rows kept}, the latest (fy, form), missing concepts."""
    rows = select_facts(data, years, today)
    for r in rows:
        r["ticker"] = ticker
        r["source_id"] = source_id
    db.upsert(conn, "fundamentals", rows)
    kept = {}
    for r in rows:
        kept[(r["concept"], r["unit"], r["period_end"], r["period_start"])] = r
    counts = {}
    for (concept, _, _, _) in kept:
        counts[concept] = counts.get(concept, 0) + 1
    latest = max(rows, key=lambda r: r["filed"] or "") if rows else None
    missing = [c for _, c in CONCEPTS if c not in counts]
    return counts, latest, missing


def latest_annual(conn, ticker):
    return db.rows(conn,
                   "SELECT concept, unit, period_end, days, fy, form, filed, value FROM fundamentals_annual f "
                   "WHERE ticker = ? AND period_end = (SELECT MAX(period_end) FROM fundamentals_annual "
                   "WHERE ticker = f.ticker AND concept = f.concept AND unit = f.unit) ORDER BY concept, unit",
                   (ticker,))


# --- CLI ----------------------------------------------------------------------------------------
def run(argv=None):
    p = common.parser(SCRIPT, "SEC companyfacts fundamentals for one ticker")
    p.add_argument("ticker")
    p.add_argument("--years", type=int, default=0, help="keep periods ending within N years (default: config depth.fundamental_years)")
    a = p.parse_args(argv)
    ticker = a.ticker.upper()
    project = common.resolve_project(a.project)
    cfg = common.load_config(project)
    years = a.years or common.depth(cfg, "fundamental_years")
    ua = cfg.get("sec_user_agent") or None
    conn = db.connect(project)

    cik = resolve_cik(conn, ticker, ua)
    if not cik:
        return common.fail(SCRIPT, NOT_REGISTRANT % ticker)
    url = FACTS_URL % cik
    data = common.get_json(url, ua)
    sid = db.source(conn, url, "primary", "SEC companyfacts %s" % ticker)
    counts, latest, missing = store_facts(conn, ticker, data, years, sid)
    db.upsert(conn, "securities", [{"ticker": ticker, "name": data.get("entityName"), "cik": cik, "kind": "stock",
                                    "currency": "USD", "source_id": sid, "updated_at": common.iso()}])
    out = {"ok": True, "script": SCRIPT, "ticker": ticker, "cik": cik, "name": data.get("entityName"),
           "years": years, "rows": sum(counts.values()), "counts": counts,
           "latest_fy": latest["fy"] if latest else None, "latest_form": latest["form"] if latest else None,
           "latest_filed": latest["filed"] if latest else None, "missing": missing, "source_id": sid}
    md = None
    if a.md:
        md = "## %s latest annual values (%s)\n\n" % (ticker, data.get("entityName")) + db.md_table(latest_annual(conn, ticker))
    return common.emit(out, md)


if __name__ == "__main__":
    sys.exit(common.run_main(SCRIPT, run))
