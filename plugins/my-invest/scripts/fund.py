#!/usr/bin/env python3
"""fund.py TICKER [--years 10] [--store DIR] - profile, holdings and price trend of an ETF or mutual fund via yfinance.

facts.py covers SEC registrants only; a fund (QQQ, VGT, SQQQ, a Canadian-listed YTSL.NE) has no companyfacts, so this
script writes <store>/stocks/<TICKER>/facts/fund.json from Yahoo (secondary): `kind` with its reason, the index
tracked, expense ratio, assets, yield, top holdings, sector and asset-class weights, portfolio P/E, and a `price` block
(returns on adjusted closes over 21/126/252 trading days, 5y/10y CAGR as prices.py, MA50/MA200 and realized volatility
on closes as momentum.py, trend by rule ST1). SPY over the same windows comes from <store>/market/SPY.json when present
(never fetched here). series.json beside fund.json has prices.py --series' shape so chart.py can draw it.
Every unavailable field is null and named in `missing` with its reason; nothing is estimated.
A company ticker (quoteType EQUITY) is refused: use facts.py.
Yahoo's fund profile is cached one trading day under <store>/.cache/prices/; history shares prices.py's cache.
Sources: S1 prices, S2 fund profile, S7 SPY (the id market.py gives it).
"""
import datetime as dt
import json
import os
import re

import common
import momentum
import prices
from common import FetchError

SCRIPT = "fund.py"
PRICE_ID, PROFILE_ID, SPY_ID = "S1", "S2", "S7"
HOLDINGS_URL = "https://finance.yahoo.com/quote/%s/holdings/"
FUND_TYPES = ("ETF", "MUTUALFUND")
WINDOWS = (("return_1m", 21), ("return_6m", 126), ("return_12m", 252))
TREND_RULE = ("ST1: above the 200-day average and the 50-day above the 200-day -> up; below both -> down; else none")
INFO_KEYS = ("longName", "shortName", "quoteType", "category", "fundFamily", "fundInceptionDate", "totalAssets",
             "yield", "navPrice", "currency")
ASSET_KEYS = {"cashPosition": "cash", "stockPosition": "stock", "bondPosition": "bond",
              "preferredPosition": "preferred", "convertiblePosition": "convertible", "otherPosition": "other"}
FLAGS = {"leveraged": "leveraged or inverse: resets daily, not built for holding (fund's own prospectus governs)",
         "covered-call": "covered-call: gives up upside for income"}
FLAGS["inverse"] = FLAGS["leveraged"]

# --- kind rules. Short-maturity bond funds say "Short-Term" / "Ultra-Short" without being inverse or leveraged, so
#     those phrases are blanked from the name before the markers are searched ("UltraShort", one word, stays).
_BOND_TERM = re.compile(r"ultra[- ]short|short[- ](?:term|duration|maturity)", re.I)
_LEVERAGED = re.compile(r"\bultra|\b[23]x\b|leveraged", re.I)
_INVERSE = re.compile(r"short\b|\binverse\b|\bbear\b", re.I)
_COVERED = re.compile(r"covered call|yield ?shares|yieldmax|option income|premium income|enhanced income", re.I)
_BOND_CAT = re.compile(r"bond|government|muni|bank loan|fixed income", re.I)
_SECTORS = ("Technology", "Health", "Financial", "Energy", "Utilities", "Real Estate", "Communications", "Consumer",
            "Industrials", "Natural Resources", "Precious Metals", "Materials")
_INTL = ("Foreign", "Emerging", "International", "Global", "Ex North America", "World")
_STYLE = re.compile(r"\b(?:large|mid|small)(?:-cap)?\s+(?:blend|growth|value)\b|total (?:stock )?market", re.I)
_ACTIVE = re.compile(r"actively[- ]managed|active management", re.I)
_INDEX = re.compile(r"\bthe\s+((?:(?!\bthe\b)(?:[^.;,()]|(?<=\b[A-Z])\.))+?\b(?:Index|Indices))\b")
_GENERIC_INDEX = ("index", "underlying index", "indices")


def _num(x):
    return prices._num(x)


def _frame(df):
    """DataFrame -> {column: {index: value}}; {} for anything that is not frame-like."""
    try:
        return df.to_dict()
    except Exception:  # noqa: BLE001
        return {}


def _own_column(d):
    """The fund's own column of a funds_data frame (the other one is "Category Average")."""
    return next((d[c] for c in d if c != "Category Average"), {})


def tracks_from(description):
    """The index a description names ("Nasdaq-100 Index"), stripped of ® / ™; None when it names none."""
    for m in _INDEX.finditer(description or ""):
        name = re.sub(r"[®™]", "", m.group(1)).strip()
        if name.lower() not in _GENERIC_INDEX and len(name) <= 90:
            return name
    return None


def classify(name, category, description, tracks, asset_classes, sector_weights):
    """(kind, reason). Precedence: leveraged/inverse, covered-call, bond, dividend, sector, international, index, other."""
    name, category, description = name or "", category or "", description or ""
    plain = _BOND_TERM.sub(" ", name)
    lev = [m.group(0) for m in _LEVERAGED.finditer(plain)]
    inv = [m.group(0) for m in _INVERSE.finditer(plain)]
    cat_lev, cat_inv = "leveraged" in category.lower(), "inverse" in category.lower()
    if lev or inv or cat_lev or cat_inv:
        words = ("leveraged " if lev or cat_lev else "") + ("inverse" if inv or cat_inv else "")
        why = []
        if lev or inv:
            why.append("name contains %s" % ", ".join(repr(w) for w in lev + inv))
        if cat_lev or cat_inv:
            why.append("category %r" % category)
        return ("inverse" if inv or cat_inv else "leveraged"), "%s -> %s" % ("; ".join(why), words.strip())
    m = _COVERED.search(name)
    if m:
        return "covered-call", "name contains %r -> covered-call" % m.group(0)
    if "derivative income" in category.lower():
        return "covered-call", "category %r -> covered-call" % category
    if _BOND_CAT.search(category):
        return "bond", "category %r names bonds" % category
    bond = (asset_classes or {}).get("bond")
    if bond is not None and bond >= 0.6:
        return "bond", "asset class bond %.2f >= 0.6" % bond
    if "dividend" in name.lower() or "dividend" in category.lower():
        return "dividend", "%s contains 'Dividend'" % ("name" if "dividend" in name.lower() else "category")
    for s in _SECTORS:
        if s.lower() in category.lower():
            return "sector", "category %r names a sector" % category
    for sec, w in sorted((sector_weights or {}).items(), key=lambda kv: -(kv[1] or 0)):
        if w is not None and w >= 0.8:
            return "sector", "sector weight %s %.2f >= 0.8" % (sec, w)
    for word in _INTL:
        if word.lower() in category.lower():
            return "international", "category %r contains %r" % (category, word)
    if tracks:
        return "index", "tracks %r" % tracks
    if _ACTIVE.search(description):
        return "other", "description says %r and names no index" % _ACTIVE.search(description).group(0)
    if _STYLE.search(category):
        return "index", "category %r is a style-box category and the description names no active management" % category
    return "other", "no kind rule matched (category %r; description names no index)" % (category or None)


# --- yfinance --------------------------------------------------------------------------------
def load_profile(ticker):
    """Ticker.info fund fields + funds_data as plain Python (JSON-safe, cacheable). `failed` names what Yahoo lacked."""
    try:
        import yfinance as yf
    except ImportError:
        raise FetchError(
            "yfinance is not installed or Python is older than 3.10 (yfinance 1.x needs Python 3.10+): "
            'install Python 3.10+ and re-run, or set "python" in <project>/data/config.json')
    t = yf.Ticker(ticker)
    out = {"version": getattr(yf, "__version__", "unknown"), "failed": {}, "info": {}}
    try:
        raw = (t.get_info() if hasattr(t, "get_info") else t.info) or {}
        out["info"] = {k: (raw.get(k) if isinstance(raw.get(k), str) else _num(raw.get(k))) for k in INFO_KEYS}
    except Exception as e:  # noqa: BLE001 - yfinance raises assorted errors
        out["failed"]["info"] = str(e)
    try:
        fd = t.funds_data
    except Exception as e:  # noqa: BLE001
        fd, out["failed"]["funds_data"] = None, str(e)

    def grab(name, conv, default=None):
        try:
            v = conv(getattr(fd, name))
            return default if v in (None, {}, [], "") else v
        except Exception as e:  # noqa: BLE001 - a non-fund raises here; empty data comes back as None/NaN
            out["failed"][name] = str(e)
            return default

    out["quote_type"] = out["info"].get("quoteType") or grab("quote_type", lambda f: f())
    out["description"] = grab("description", lambda s: str(s).strip())
    ov = grab("fund_overview", dict) or {}
    out["overview"] = {"category": ov.get("categoryName"), "family": ov.get("family"), "legal_type": ov.get("legalType")}
    out["expense_ratio"] = grab("fund_operations", lambda df: _num(_own_column(_frame(df)).get("Annual Report Expense Ratio")))
    out["equity_pe"] = grab("equity_holdings", lambda df: _num(_own_column(_frame(df)).get("Price/Earnings")))

    def holdings(df):
        d = _frame(df)
        names, pct = d.get("Name", {}), d.get("Holding Percent", {})
        return [{"symbol": s, "name": names.get(s), "weight": _num(pct.get(s))} for s in pct]
    out["top_holdings"] = grab("top_holdings", holdings)
    out["sector_weights"] = grab("sector_weightings", lambda d: {k: _num(v) for k, v in dict(d).items() if _num(v) is not None})
    out["asset_classes"] = grab("asset_classes", lambda d: {ASSET_KEYS.get(k, k): _num(v) for k, v in dict(d).items()
                                                            if _num(v) is not None})
    return out


def get_profile(ctx, ticker, loader=load_profile):
    """Cached profile -> (payload, retrieved_iso); same one-trading-day rule as prices."""
    cache = ctx.cache("prices")
    key = "fund|%s" % ticker
    hit = cache.get(key, ctx.refresh)
    if hit:
        return json.loads(hit[0].decode("utf-8")), hit[1]
    payload = loader(ticker)
    return payload, cache.put(key, json.dumps(payload).encode("utf-8"))


# --- pure computation ------------------------------------------------------------------------
def _date(epoch):
    try:
        return dt.datetime.fromtimestamp(float(epoch), dt.timezone.utc).date().isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def _pairs(dates, closes, adj, end=None):
    """(date, close, adjusted close) triples with a close, up to `end`; adj falls back to close."""
    out = []
    for d, c, a in zip(dates, closes, adj):
        if c is None or (end and d > end):
            continue
        out.append((d, c, a if a is not None else c))
    return out


def windows(triples, miss, prefix):
    """Trading-day window returns on adjusted closes plus 5y/10y CAGR (prices.summarize); nulls named in `miss`."""
    adj = [a for _, _, a in triples]
    out = {}
    for name, n in WINDOWS:
        out[name] = momentum.rnd(momentum.window_return(adj, n))
        if out[name] is None:
            miss.append({"field": prefix + name, "reason": "needs %d closes, have %d" % (n + 1, len(adj))})
    p, _ = prices.summarize([{"date": d, "close": c, "adj_close": a} for d, c, a in triples], {}, ())
    for name in ("return_5y_cagr", "return_10y_cagr"):
        out[name] = momentum.rnd(p[name])
        if p[name] is None:
            why = next((m for m in p["missing"] if m.startswith(name)), name + ": history too short")
            miss.append({"field": prefix + name, "reason": why.split(": ", 1)[1]})
    return out


def price_block(rows, currency, miss):
    triples = _pairs([r["date"] for r in rows], [r.get("close") for r in rows], [r.get("adj_close") for r in rows])
    if not triples:
        raise FetchError("no usable price rows")
    closes = [c for _, c, _ in triples]
    p, _ = prices.summarize(rows, {}, ())
    out = {"last": p["last"], "date": p["date"], "currency": currency, "high_52w": p["high_52w"], "low_52w": p["low_52w"],
           "ma50": momentum.rnd(momentum.sma(closes, 50)), "ma200": momentum.rnd(momentum.sma(closes, 200))}
    out.update(windows(triples, miss, "price."))
    out["realized_vol_30d"] = momentum.rnd(momentum.realized_vol(closes, 30))
    out["realized_vol_1y"] = momentum.rnd(momentum.realized_vol(closes, momentum.TRADING_DAYS))
    for f, need in (("ma50", 50), ("ma200", 200), ("realized_vol_30d", 31), ("realized_vol_1y", 253)):
        if out[f] is None:
            miss.append({"field": "price." + f, "reason": "needs %d closes, have %d" % (need, len(closes))})
    if currency is None:
        miss.append({"field": "price.currency", "reason": "currency not in Yahoo info"})
    last, ma50, ma200 = closes[-1], out["ma50"], out["ma200"]
    if ma200 is None or ma50 is None:
        out["trend"] = None
        miss.append({"field": "price.trend", "reason": "needs the 50- and 200-day averages"})
    elif last > ma200 and ma50 > ma200:
        out["trend"] = "up"
    elif last < ma200 and ma50 < ma200:
        out["trend"] = "down"
    else:
        out["trend"] = "none"
    out["trend_rule"] = TREND_RULE
    return out


def spy_block(series, end_date, miss):
    """SPY windows ending at the fund's price date from a series.json-shaped dict; None (with reason) when unusable."""
    if not series:
        miss.append({"field": "spy", "reason": "no market/SPY.json in the store (market.py writes it)"})
        return None
    triples = _pairs(series.get("dates") or [], series.get("close") or [], series.get("adj_close") or [], end_date)
    if not triples:
        miss.append({"field": "spy", "reason": "market/SPY.json has no closes on or before %s" % end_date})
        return None
    out = windows(triples, miss, "spy.")
    out.update({"as_of": triples[-1][0], "basis": "market/SPY.json adj_close", "src": SPY_ID})
    return out


def assemble(ticker, raw, rows, spy, now, retrieved):
    """Pure: profile payload + price rows + SPY series -> fund.json dict. `retrieved` = {profile, prices, spy} iso."""
    info, miss = raw.get("info") or {}, []

    def need(field, value, reason):
        if value is None:
            miss.append({"field": field, "reason": reason})
        return value
    name = info.get("longName") or info.get("shortName")
    category = info.get("category") or (raw.get("overview") or {}).get("category")
    tracks = tracks_from(raw.get("description"))
    kind, why = classify(name, category, raw.get("description"), tracks, raw.get("asset_classes"), raw.get("sector_weights"))
    price = price_block(rows, info.get("currency"), miss)
    holdings = raw.get("top_holdings") or None
    weights = [h["weight"] for h in holdings or [] if h.get("weight") is not None]
    flags = [FLAGS[kind]] if kind in FLAGS else []
    top_w = round(sum(weights), 6) if weights else None
    if top_w is not None and top_w >= 0.5:
        flags.append("concentrated: top %d holdings are %d%% of the fund" % (len(weights), round(top_w * 100)))
    failed = raw.get("failed") or {}

    def lack(attr, what):
        return "%s: %s" % (attr, failed[attr]) if attr in failed else "Yahoo lists no %s" % what
    out = {
        "ticker": ticker, "quote_type": need("quote_type", raw.get("quote_type"), "Yahoo reports no quoteType"),
        "name": need("name", name, "Yahoo info has no longName"), "as_of": price["date"], "retrieved": common.iso(now),
        "kind": kind, "kind_reason": why,
        "category": need("category", category, "Yahoo lists no category"),
        "family": need("family", info.get("fundFamily") or (raw.get("overview") or {}).get("family"), "Yahoo lists no fund family"),
        "tracks": need("tracks", tracks, "description names no index" if raw.get("description") else lack("description", "description")),
        "expense_ratio": need("expense_ratio", raw.get("expense_ratio"), lack("fund_operations", "expense ratio")),
        "total_assets": need("total_assets", info.get("totalAssets"), "totalAssets not in Yahoo info"),
        "inception": need("inception", _date(info.get("fundInceptionDate")), "fundInceptionDate not in Yahoo info"),
        "distribution_yield": need("distribution_yield", info.get("yield"), "yield not in Yahoo info"),
        "top_holdings": need("top_holdings", holdings, lack("top_holdings", "holdings")),
        "top_holdings_weight": need("top_holdings_weight", top_w, "no holding weights"),
        "sector_weights": need("sector_weights", raw.get("sector_weights") or None, lack("sector_weightings", "sector weights")),
        "asset_classes": need("asset_classes", raw.get("asset_classes") or None, lack("asset_classes", "asset classes")),
        "equity_pe": need("equity_pe", raw.get("equity_pe"), lack("equity_holdings", "portfolio price/earnings")),
        "price": price, "spy": spy_block(spy, price["date"], miss), "flags": flags,
    }
    price["src"] = PRICE_ID
    prov = common.Provenance()
    prov.add("secondary", "%s daily prices, averages, returns, volatility (Yahoo via yfinance %s)" % (ticker, raw.get("version")),
             prices.QUOTE_URL % ticker, price["date"], retrieved["prices"], sid=PRICE_ID)
    prov.add("secondary", "%s fund profile: index, expense ratio, holdings, sector weights, yields (Yahoo via yfinance funds_data)"
             % ticker, HOLDINGS_URL % ticker, now.strftime("%Y-%m-%d"), retrieved["profile"], sid=PROFILE_ID)
    if out["spy"]:
        prov.add("secondary", "SPY adjusted closes for the same windows (market/SPY.json)", prices.QUOTE_URL % "SPY",
                 out["spy"]["as_of"], retrieved.get("spy") or "", sid=SPY_ID)
    out["sources"] = prov.ordered()
    out["missing"] = miss
    return out


def build(ctx, ticker, years=10, market_dir=None, loader=None, price_loader=None):
    """Fetch (cached) and assemble; returns (fund dict, series dict). Refuses a non-fund quoteType."""
    ticker = common.safe_ticker(ticker)
    raw, p_ret = get_profile(ctx, ticker, loader or load_profile)
    qt = raw.get("quote_type")
    if qt and qt not in FUND_TYPES:
        raise FetchError("%s is quoteType %s, not a fund: use facts.py for a company" % (ticker, qt))
    if not raw.get("info") and not raw.get("description"):
        raise FetchError("yfinance returned no fund data for %s (%s)" % (
            ticker, "; ".join("%s: %s" % kv for kv in sorted((raw.get("failed") or {}).items())) or "nothing came back"))
    payload, h_ret = prices.get_history(ctx, ticker, years, price_loader or prices.load_yfinance)
    spy = momentum.load_json(os.path.join(market_dir, "SPY.json")) if market_dir else None
    out = assemble(ticker, raw, payload["rows"], spy, ctx.now(),
                   {"profile": p_ret, "prices": h_ret, "spy": (spy or {}).get("retrieved")})
    return out, prices.series_json(ticker, payload["rows"], PRICE_ID, h_ret)


def run(argv=None):
    ap = common.base_parser("ETF / mutual fund profile and price trend via yfinance")
    ap.add_argument("ticker", help="ticker or stock folder path")
    ap.add_argument("--years", type=int, default=10, help="price history years")
    args = ap.parse_args(argv)
    st = common.locate(args.ticker, args)
    ctx = common.ctx_from(args)
    if args.out:
        path, spath = args.out, os.path.splitext(args.out)[0] + ".series.json"
    else:
        common.ensure_store(os.path.dirname(os.path.dirname(st.root)))
        path, spath = os.path.join(st.facts_dir, "fund.json"), st.series
    fund, series = build(ctx, st.ticker, args.years, st.market_dir)
    for p, obj in ((path, fund), (spath, series)):
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.write("\n")
    manifest = {"ok": True, "out": path, "series": spath, "ticker": fund["ticker"], "quote_type": fund["quote_type"],
                "kind": fund["kind"], "as_of": fund["as_of"], "spy": fund["spy"] is not None,
                "missing": [m["field"] for m in fund["missing"]]}
    print(json.dumps(manifest))
    return manifest


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
