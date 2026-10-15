#!/usr/bin/env python3
"""news.py TICKER [--since DAYS] [--fts "phrase"] [--rss] [--forms F1,F2|all] [--items 2.02,5.02]

Recent filings from the SEC submissions feed (primary), optional EDGAR full-text-search hits (primary),
optional Google News RSS (secondary; failures tolerated, reported in `rss_error`).
Default form set: 8-K, 10-K, 10-Q, 6-K, 20-F, 40-F, proxy, registration statements, 13D/G, tender, NT forms
(Forms 3/4/5 and the like are noise unless named in --forms). --items keeps only 8-Ks naming one of the items.
"""
import datetime as dt
import urllib.parse
import xml.etree.ElementTree as ET

import common
import edgar
from common import FetchError

SCRIPT = "news.py"
FTS_URL = "https://efts.sec.gov/LATEST/search-index?"
RSS_URL = "https://news.google.com/rss/search?q=%s&hl=en-US&gl=US&ceid=US:en"
DEFAULT_FORM_PREFIXES = ("8-K", "10-K", "10-Q", "6-K", "20-F", "40-F", "DEF 14A", "DEFA14A", "S-1", "S-3", "S-4",
                         "SC 13", "SCHEDULE 13", "SC TO", "NT 10")


def filing_url(cik_int, accn, doc):
    return "https://www.sec.gov/Archives/edgar/data/%d/%s/%s" % (int(cik_int), accn.replace("-", ""), doc)


def form_wanted(form, forms):
    if forms == "all":
        return True
    if forms:
        return form in forms
    return form.startswith(DEFAULT_FORM_PREFIXES)


def recent_filings(sub, cik_int, since_days, today, forms=None, items=None, src="S2"):
    """Filter submissions `filings.recent` to the window. Returns (list newest first, coverage_start)."""
    r = sub.get("filings", {}).get("recent", {})
    cutoff = (today - dt.timedelta(days=since_days)).isoformat()
    want_items = set(items or [])
    out = []
    n = len(r.get("accessionNumber", []))
    for i in range(n):
        filed, form = r["filingDate"][i], r["form"][i]
        if filed < cutoff or not form_wanted(form, forms):
            continue
        it = r.get("items", [""] * n)[i] or ""
        if want_items and not (form.startswith("8-K") and want_items & {x.strip() for x in it.split(",")}):
            continue
        out.append({"form": form, "filed": filed, "items": it,
                    "url": filing_url(cik_int, r["accessionNumber"][i], r["primaryDocument"][i]), "src": src})
    out.sort(key=lambda x: x["filed"], reverse=True)
    dates = r.get("filingDate", [])
    return out, (min(dates) if dates else None)


def fts_hits(obj, since_cutoff):
    """EDGAR full-text-search JSON -> hit list within the window."""
    hits = []
    for h in obj.get("hits", {}).get("hits", []):
        s = h.get("_source", {})
        accn, _, fname = h.get("_id", "").partition(":")
        ciks = s.get("ciks") or [""]
        if not accn or not fname or s.get("file_date", "") < since_cutoff:
            continue
        hits.append({"form": s.get("form"), "filed": s.get("file_date"), "items": ",".join(s.get("items") or []),
                     "file_type": s.get("file_type"),
                     "url": filing_url(int(ciks[0]), accn, fname) if ciks[0] else None})
    return sorted(hits, key=lambda x: x["filed"], reverse=True)


def parse_rss(body):
    root = ET.fromstring(body)
    out = []
    for it in root.iter("item"):
        src = it.find("source")
        out.append({"title": (it.findtext("title") or "").strip(), "url": (it.findtext("link") or "").strip(),
                    "published": (it.findtext("pubDate") or "").strip(),
                    "outlet": (src.text or "").strip() if src is not None else ""})
    return out


def build(ctx, ticker, since=90, fts="", rss=False, forms=None, items=None, sub=None):
    """`sub` = (submissions JSON, retrieved) when the caller already fetched it (facts.py shares one fetch)."""
    ticker = ticker.upper()
    if sub:
        cik, title = int(sub[0]["cik"]), sub[0].get("name", ticker)
    else:
        cik, title, _ = edgar.resolve_cik(ctx, ticker)
    cik10 = "%010d" % cik
    today = ctx.now().date()
    prov = common.Provenance()
    sub_url = edgar.SUBMISSIONS_URL % cik10
    sub, sub_ret = sub or ctx.get_json(sub_url, "news")
    dates = sub.get("filings", {}).get("recent", {}).get("filingDate", [])
    sid = prov.add("primary", "submissions: filings index", sub_url, dates[0] if dates else "", sub_ret)
    filings, coverage = recent_filings(sub, cik, since, today, forms, items, sid)
    cutoff = (today - dt.timedelta(days=since)).isoformat()
    out = {"ticker": ticker, "cik": cik10, "window": {"since_days": since, "from": cutoff, "to": today.isoformat(),
                                                      "feed_oldest": coverage},
           "sources": prov.sources, "filings": filings}
    if fts:
        q = {"q": '"%s"' % fts, "forms": "8-K", "ciks": cik10, "dateRange": "custom",
             "startdt": cutoff, "enddt": today.isoformat()}
        url = FTS_URL + urllib.parse.urlencode(q)
        obj, ret = ctx.get_json(url, "news")
        out["fts_hits"] = fts_hits(obj, cutoff)
        out["fts_source"] = prov.add("primary", "EDGAR full-text search: %s" % fts, url, today.isoformat(), ret)
    if rss:
        try:
            url = RSS_URL % urllib.parse.quote_plus('"%s" stock' % title)
            body, ret = ctx.get(url, "news")
            out["rss"] = parse_rss(body)
            out["rss_source"] = prov.add("secondary", "Google News RSS: %s" % title, url, today.isoformat(), ret)
        except Exception as e:  # tolerated by design: undocumented, flaky feed
            out["rss"], out["rss_error"] = [], str(e)
    return out


def run(argv=None):
    ap = common.base_parser("Recent filings / news for one ticker")
    ap.add_argument("ticker")
    ap.add_argument("--since", type=int, default=90, help="window in days")
    ap.add_argument("--fts", default="", help="EDGAR full-text phrase (8-K)")
    ap.add_argument("--rss", action="store_true", help="add Google News RSS (secondary)")
    ap.add_argument("--forms", default="", help="comma list of exact forms, or 'all'")
    ap.add_argument("--items", default="", help="8-K item filter, e.g. 2.02,5.02")
    args = ap.parse_args(argv)
    forms = args.forms if args.forms == "all" else [f.strip() for f in args.forms.split(",") if f.strip()]
    items = [i.strip() for i in args.items.split(",") if i.strip()]
    out = build(common.ctx_from(args), args.ticker, args.since, args.fts, args.rss, forms, items)
    common.emit(out, args.out)
    return out


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
