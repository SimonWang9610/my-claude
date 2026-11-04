#!/usr/bin/env python3
"""fred.py [--series A,B,C] [--years N] - macro series from FRED (primary) into `macro_series` and `macro`.

Usage: python3 fred.py [--series DGS10,CPIAUCSL] [--years 5] [--md] --project P
Without --series the DEFAULT_SERIES table runs, capped at config depth.macro_series. Without config
fred_api_key the public fredgraph CSV is read; with a key the FRED JSON API (the key is redacted in `sources`).
--md: per series the latest value, the value a year earlier and the change.
"""
import csv
import datetime as dt
import io
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import db  # noqa: E402

SCRIPT = "fred.py"
CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=%s"
API_URL = "https://api.stlouisfed.org/fred/series/observations?%s"

# series -> (title, units, frequency); the order is the priority when depth.macro_series caps the run
DEFAULT_SERIES = [
    ("DGS10", "10-Year Treasury constant maturity yield", "percent", "daily"),
    ("DGS2", "2-Year Treasury constant maturity yield", "percent", "daily"),
    ("T10Y2Y", "10-year minus 2-year Treasury spread", "percent", "daily"),
    ("FEDFUNDS", "Effective federal funds rate", "percent", "monthly"),
    ("CPIAUCSL", "CPI, all items, urban consumers (seasonally adjusted)", "index 1982-84=100", "monthly"),
    ("UNRATE", "Unemployment rate", "percent", "monthly"),
    ("GDPC1", "Real gross domestic product", "billions of chained 2017 dollars", "quarterly"),
    ("VIXCLS", "CBOE volatility index (VIX)", "index", "daily"),
]
META = {s: (t, u, f) for s, t, u, f in DEFAULT_SERIES}


# --- parsing ------------------------------------------------------------------------------------
def parse_csv(text):
    """fredgraph CSV -> [(YYYY-MM-DD, value)]; '.' (missing) rows are dropped."""
    out = []
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 2 or row[0] in ("observation_date", "DATE") or not row[0][:4].isdigit():
            continue
        v = row[1].strip()
        if v in (".", ""):
            continue
        try:
            out.append((row[0].strip(), float(v)))
        except ValueError:
            continue
    return out


def parse_json(data):
    """FRED API observations -> [(YYYY-MM-DD, value)]; '.' rows are dropped."""
    out = []
    for o in data.get("observations", []):
        v = str(o.get("value", ".")).strip()
        if v == "." or not o.get("date"):
            continue
        try:
            out.append((o["date"], float(v)))
        except ValueError:
            continue
    return out


def series_url(series, key):
    if key:
        return API_URL % urllib.parse.urlencode({"series_id": series, "api_key": key, "file_type": "json"})
    return CSV_URL % series


def fetch(series, key):
    """(url, observations) for one series from the API when a key exists, else the CSV endpoint."""
    url = series_url(series, key)
    if key:
        return url, parse_json(common.get_json(url))
    return url, parse_csv(common.get_text(url))


# --- storing ------------------------------------------------------------------------------------
def store(conn, series, url, observations, years, today=None):
    """Upsert the sources, macro_series and macro rows for one series; returns (source_id, rows kept)."""
    today = today or dt.date.today()
    cutoff = (today - dt.timedelta(days=365 * years)).isoformat()
    title, units, freq = META.get(series, (None, None, None))
    sid = db.source(conn, url, "primary", "FRED %s" % series)
    db.upsert(conn, "macro_series", [{"series": series, "title": title, "units": units, "frequency": freq,
                                      "source_id": sid, "updated_at": common.iso()}])
    rows = [{"series": series, "date": d, "value": v} for d, v in observations if d >= cutoff]
    db.upsert(conn, "macro", rows)
    return sid, len(rows)


def summary(conn, series_list):
    """Per series: latest value and date, the value a year earlier, and the change."""
    recs = []
    for s in series_list:
        latest = db.one(conn, "SELECT date, value FROM macro WHERE series = ? ORDER BY date DESC LIMIT 1", (s,))
        if not latest:
            recs.append({"series": s, "latest_date": None, "latest": None, "year_ago": None, "change": None, "units": META.get(s, ("", "", ""))[1]})
            continue
        ago = (dt.date.fromisoformat(latest["date"]) - dt.timedelta(days=365)).isoformat()
        prev = db.one(conn, "SELECT date, value FROM macro WHERE series = ? AND date <= ? ORDER BY date DESC LIMIT 1", (s, ago))
        change = latest["value"] - prev["value"] if prev else None
        recs.append({"series": s, "latest_date": latest["date"], "latest": latest["value"],
                     "year_ago": prev["value"] if prev else None, "change": change,
                     "change_pct": (change / prev["value"] * 100) if prev and prev["value"] else None,
                     "units": META.get(s, ("", "", ""))[1]})
    return recs


# --- CLI ----------------------------------------------------------------------------------------
def run(argv=None):
    p = common.parser(SCRIPT, "FRED macro series")
    p.add_argument("--series", default="", help="comma-separated FRED ids (default: the built-in table, capped by depth.macro_series)")
    p.add_argument("--years", type=int, default=5, help="keep observations within N years (default 5)")
    a = p.parse_args(argv)
    project = common.resolve_project(a.project)
    cfg = common.load_config(project)
    key = cfg.get("fred_api_key") or ""
    if a.series:
        wanted = [s.strip().upper() for s in a.series.split(",") if s.strip()]
    else:
        wanted = [s for s, _, _, _ in DEFAULT_SERIES][: common.depth(cfg, "macro_series")]
    conn = db.connect(project)

    stored, failed = {}, {}
    for s in wanted:
        try:
            url, obs = fetch(s, key)
            sid, n = store(conn, s, url, obs, a.years)
            stored[s] = {"rows": n, "source_id": sid, "latest": obs[-1][0] if obs else None}
        except common.FetchError as e:
            failed[s] = str(e)
    out = {"ok": True, "script": SCRIPT, "years": a.years, "endpoint": "api" if key else "csv", "series": stored}
    if failed:
        out["failed"] = failed
    if not stored:
        return common.fail(SCRIPT, "no series stored", failed=failed)
    md = None
    if a.md:
        md = db.md_table(summary(conn, list(stored)), ["series", "latest_date", "latest", "year_ago", "change", "change_pct", "units"])
    return common.emit(out, md)


if __name__ == "__main__":
    sys.exit(common.run_main(SCRIPT, run))
