#!/usr/bin/env python3
"""macro.py - 10-year Treasury yield and the equity risk premium constant.

DGS10: FRED series_observations when fred_api_key is set (from <project>/data/config.json), else the Treasury daily par yield curve
TextView table (10 Yr column, newest row). Units are percent (4.21 = 4.21%).

ERP is a HAND-MAINTAINED constant (ERP_DEFAULT / ERP_AS_OF below, Damodaran implied ERP): nothing fetches it.
Refresh it by editing those two constants after each Damodaran update (monthly at most), or override per
run with --erp (percent) and --erp-date YYYY-MM-DD. A stale ERP stays cited with its as_of date.
"""
import html.parser
import json
import re

import common
from common import FetchError

SCRIPT = "macro.py"
ERP_DEFAULT = 4.20
ERP_AS_OF = "2026-10-01"
ERP_URL = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/home.htm"
FRED_API = "https://api.stlouisfed.org/fred/series/observations"
FRED_PUBLIC = "https://fred.stlouisfed.org/series/DGS10"
TREASURY_URL = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView"
                "?type=daily_treasury_yield_curve&field_tdr_date_value=%d")


def parse_fred(obj):
    """Latest non-missing observation -> (value, date)."""
    obs = sorted(obj.get("observations", []), key=lambda o: o.get("date", ""), reverse=True)
    for o in obs:
        try:
            return float(o["value"]), o["date"]
        except (KeyError, ValueError):  # "." marks a missing day
            continue
    raise FetchError("FRED DGS10 returned no non-missing observation")


class _Table(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.headers, self.rows, self._cell, self._row, self._in = [], [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("th", "td"):
            self._in, self._cell = tag, ""
        elif tag == "time" and self._cell is not None:
            self._cell += dict(attrs).get("datetime", "")[:10] + " "  # ISO date beats the m/d/Y text

    def handle_data(self, data):
        if self._cell is not None:
            self._cell += data

    def handle_endtag(self, tag):
        if tag in ("th", "td") and self._cell is not None:
            (self.headers if tag == "th" else self._row).append(self._cell.strip())
            self._cell = None
        elif tag == "tr" and self._row:
            self.rows.append(self._row)
            self._row = None


def parse_treasury(page):
    """Treasury TextView HTML -> (10 Yr value, ISO date) for the newest row with a numeric 10 Yr."""
    t = _Table()
    t.feed(page)
    idx = [i for i, h in enumerate(t.headers) if h.strip().lower() == "10 yr"]
    if not idx:
        raise FetchError("Treasury table has no '10 Yr' column (layout changed?)")
    i = idx[0]
    best = None
    for r in t.rows:
        if len(r) <= i:
            continue
        m = re.match(r"(\d{4}-\d{2}-\d{2})", r[0])
        try:
            v = float(r[i])
        except ValueError:
            continue
        if m and (best is None or m.group(1) > best[1]):
            best = (v, m.group(1))
    if not best:
        raise FetchError("Treasury table has no numeric 10 Yr row")
    return best


def build(ctx, erp=ERP_DEFAULT, erp_date=ERP_AS_OF, env=None):
    prov = common.Provenance()
    key = env.get("FRED_API_KEY", "") if env is not None else ctx.setting("fred_api_key")
    if key:
        url = "%s?series_id=DGS10&api_key=%s&file_type=json&sort_order=desc&limit=20" % (FRED_API, key)
        obj, retrieved = ctx.get_json(url, "macro", key=url.replace(key, "REDACTED"))
        val, date = parse_fred(obj)
        sid = prov.add("primary", "DGS10 (FRED, percent)", FRED_PUBLIC, date, retrieved)
    else:
        year = ctx.now().year
        url = TREASURY_URL % year
        body, retrieved = ctx.get(url, "macro")
        try:
            val, date = parse_treasury(body.decode("utf-8", "replace"))
        except FetchError:
            if ctx.now().month > 1:
                raise
            body, retrieved = ctx.get(TREASURY_URL % (year - 1), "macro")  # early January: new-year table empty
            val, date = parse_treasury(body.decode("utf-8", "replace"))
            url = TREASURY_URL % (year - 1)
        sid = prov.add("primary", "Treasury daily par yield curve, 10 Yr (percent)", url, date, retrieved)
    esid = prov.add("secondary", "implied equity risk premium (Damodaran), hand-maintained constant",
                    ERP_URL, erp_date, common.utcnow().strftime("%Y-%m-%d"))
    macro = {"dgs10": val, "dgs10_date": date, "src": sid, "erp": erp, "erp_date": erp_date, "erp_src": esid,
             "units": "percent"}
    return {"sources": prov.sources, "macro": macro}


def run(argv=None):
    ap = common.base_parser("10y Treasury yield + ERP constant")
    ap.add_argument("--erp", type=float, default=ERP_DEFAULT, help="ERP in percent (default %.2f)" % ERP_DEFAULT)
    ap.add_argument("--erp-date", default="", help="as-of of the --erp override (default today)")
    args = ap.parse_args(argv)
    erp_date = args.erp_date or (ERP_AS_OF if args.erp == ERP_DEFAULT else common.today())
    out = build(common.ctx_from(args), args.erp, erp_date)
    common.emit(out, args.out)
    return out


if __name__ == "__main__":
    common.run_main(SCRIPT, run)
