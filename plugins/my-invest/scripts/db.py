#!/usr/bin/env python3
"""db.py - the one database: <project>/data/invest.db, created and migrated on first use by any script.

Holds the two kinds of data that gain from history: fetched series (prices, fundamentals, macro, estimates,
fund weights, news) and analysis history (runs, views, valuations, stats, calls). Holdings are never stored.
Text (reports) lives in files. Every numeric row points at a `sources` row with the URL it came from.

CLI (JSON out unless --md):
  db.py init                       create or migrate; prints the path and version
  db.py tables                     every table with its row count and purpose
  db.py describe TABLE             columns with types and meanings
  db.py query "SELECT ..." [--md]  read-only query (writes are refused)
  db.py write TABLE --json ROWS    upsert rows (a JSON list, or @file.json); keys = the primary key
  db.py exec "UPDATE ..."          one write statement; prints rows changed
  db.py source URL --grade G [--title T]   register a source (a page the analyst read) and print its id
  db.py schema --md                the schema reference (skills/data/references/schema.md is this output)
Python: connect(project) -> sqlite3.Connection; source(); upsert(); insert(); rows(); one().
"""
import datetime as dt
import json
import os
import sqlite3
import sys

import common

SCRIPT = "db.py"
DB_NAME = "invest.db"
SCHEMA_VERSION = 1

INTENTS = ("stock", "holdings", "sector", "macro", "mix", "digest")
DIMENSIONS = ("fundamentals", "valuation", "statistics", "macro", "industry", "sentiment")
METHODS = ("dcf", "reverse_dcf", "pe_range", "pe_peers")
STANCES = ("for", "against", "neutral")
TIERS = ("conservative", "moderate", "aggressive")
ACTIONS = ("buy", "add", "hold", "trim", "sell", "wait", "avoid")
GRADES = ("primary", "secondary", "derived")
SCENARIOS = ("low", "base", "high")
OUTCOMES = ("open", "right", "wrong", "void")

# Each table: purpose, columns [(name, type/constraint, meaning)], primary key, extra SQL (indexes).
# This list IS the schema; `schema --md` renders it and CREATE statements are built from it, so the
# reference and the database can never disagree.
TABLES = [
    ("sources", "Where every number came from: one row per URL, with its grade and the last fetch time.",
     [("id", "INTEGER PRIMARY KEY", "row id, referenced by every data row as source_id"),
      ("url", "TEXT NOT NULL UNIQUE", "the raw source, keys redacted; the link the report shows"),
      ("grade", "TEXT NOT NULL CHECK (grade IN ('primary','secondary','derived'))",
       "primary = the issuer's or the government's own data (SEC, FRED); secondary = a vendor (Yahoo, a news "
       "feed); derived = computed by a script from rows that have their own sources"),
      ("title", "TEXT", "what the link is, in a few words"),
      ("fetched_at", "TEXT NOT NULL", "ISO UTC of the last fetch")],
     None, []),
    ("securities", "One row per ticker: what it is, its SEC id, sector and industry.",
     [("ticker", "TEXT PRIMARY KEY", "US ticker, upper case"),
      ("name", "TEXT", "company or fund name"),
      ("cik", "TEXT", "SEC Central Index Key, 10 digits, NULL for a fund with none"),
      ("kind", "TEXT CHECK (kind IN ('stock','fund'))", "stock or fund (ETF)"),
      ("exchange", "TEXT", "listing exchange"),
      ("sector", "TEXT", "Yahoo sector"),
      ("industry", "TEXT", "Yahoo industry"),
      ("currency", "TEXT", "quote currency, USD for everything this plugin covers"),
      ("source_id", "INTEGER REFERENCES sources(id)", "profile source"),
      ("updated_at", "TEXT NOT NULL", "ISO UTC")],
     None, []),
    ("prices", "Daily prices, one row per ticker and trading day.",
     [("ticker", "TEXT NOT NULL", ""), ("date", "TEXT NOT NULL", "YYYY-MM-DD"),
      ("open", "REAL", ""), ("high", "REAL", ""), ("low", "REAL", ""),
      ("close", "REAL NOT NULL", "unadjusted close"),
      ("adj_close", "REAL", "close adjusted for splits and dividends; use for returns"),
      ("volume", "INTEGER", ""),
      ("source_id", "INTEGER NOT NULL REFERENCES sources(id)", "")],
     "PRIMARY KEY (ticker, date)", []),
    ("fundamentals", "SEC XBRL facts in long form: one row per concept, unit and period, the latest filing wins.",
     [("ticker", "TEXT NOT NULL", ""),
      ("concept", "TEXT NOT NULL", "XBRL concept without namespace, e.g. Revenues, NetIncomeLoss"),
      ("unit", "TEXT NOT NULL", "USD, shares, USD/shares, pure"),
      ("period_start", "TEXT NOT NULL DEFAULT ''", "YYYY-MM-DD for a duration fact, '' for an instant (balance sheet)"),
      ("period_end", "TEXT NOT NULL", "YYYY-MM-DD"),
      ("days", "INTEGER", "duration in days; ~365 annual, ~91 quarterly, NULL for an instant"),
      ("fy", "INTEGER", "fiscal year of the filing that reported it"),
      ("fp", "TEXT", "FY, Q1, Q2, Q3"),
      ("form", "TEXT", "10-K, 10-Q, 20-F, ..."),
      ("filed", "TEXT", "filing date; of all filings reporting this period, the latest is kept (restatements win)"),
      ("accession", "TEXT", "accession number of that filing"),
      ("frame", "TEXT", "SEC calendar frame such as CY2023 or CY2023Q4I when the SEC assigned one"),
      ("value", "REAL NOT NULL", ""),
      ("source_id", "INTEGER NOT NULL REFERENCES sources(id)", "the companyfacts API call")],
     "PRIMARY KEY (ticker, concept, unit, period_end, period_start)",
     ["CREATE INDEX IF NOT EXISTS ix_fund_concept ON fundamentals (ticker, concept, days, period_end)"]),
    ("macro_series", "The macro series followed, one row each.",
     [("series", "TEXT PRIMARY KEY", "FRED id, e.g. DGS10, CPIAUCSL, FEDFUNDS, UNRATE, T10Y2Y"),
      ("title", "TEXT", ""), ("units", "TEXT", "percent, index, thousands of persons, ..."),
      ("frequency", "TEXT", "daily, weekly, monthly, quarterly"),
      ("source_id", "INTEGER REFERENCES sources(id)", ""),
      ("updated_at", "TEXT NOT NULL", "")],
     None, []),
    ("macro", "Observations of the macro series.",
     [("series", "TEXT NOT NULL REFERENCES macro_series(series)", ""),
      ("date", "TEXT NOT NULL", ""), ("value", "REAL NOT NULL", "")],
     "PRIMARY KEY (series, date)", []),
    ("estimates", "Analysts' consensus as of a date: price targets, recommendation, next earnings date (secondary).",
     [("ticker", "TEXT NOT NULL", ""), ("asof", "TEXT NOT NULL", "YYYY-MM-DD of the fetch"),
      ("target_mean", "REAL", ""), ("target_median", "REAL", ""), ("target_high", "REAL", ""),
      ("target_low", "REAL", ""), ("analysts", "INTEGER", "number of analysts behind the targets"),
      ("recommendation", "TEXT", "buy, hold, sell as Yahoo words it"),
      ("recommendation_mean", "REAL", "1 strong buy .. 5 sell"),
      ("next_earnings", "TEXT", "YYYY-MM-DD when known"),
      ("source_id", "INTEGER NOT NULL REFERENCES sources(id)", "")],
     "PRIMARY KEY (ticker, asof)", []),
    ("funds", "What a fund is: category, what it tracks, its yearly cost.",
     [("ticker", "TEXT PRIMARY KEY REFERENCES securities(ticker)", ""),
      ("category", "TEXT", "Yahoo category, e.g. Large Growth, Trading--Leveraged Equity"),
      ("tracks", "TEXT", "the index or strategy named in the summary"),
      ("expense_ratio", "REAL", "yearly cost as a fraction, 0.002 = 0.20%"),
      ("net_assets", "REAL", "USD"), ("inception", "TEXT", "YYYY-MM-DD"),
      ("summary", "TEXT", "the fund's own description, trimmed"),
      ("asof", "TEXT NOT NULL", ""), ("source_id", "INTEGER NOT NULL REFERENCES sources(id)", "")],
     None, []),
    ("fund_weights", "A fund's top holdings and sector weights as of a date.",
     [("fund", "TEXT NOT NULL", ""),
      ("kind", "TEXT NOT NULL CHECK (kind IN ('holding','sector'))", "holding = a constituent, sector = a sector bucket"),
      ("key", "TEXT NOT NULL", "constituent ticker or sector name"),
      ("name", "TEXT", "constituent name"),
      ("weight", "REAL NOT NULL", "fraction of the fund, 0.08 = 8%"),
      ("asof", "TEXT NOT NULL", ""), ("source_id", "INTEGER NOT NULL REFERENCES sources(id)", "")],
     "PRIMARY KEY (fund, kind, key, asof)", []),
    ("news", "News items per subject; the analyst records the lean after reading.",
     [("id", "INTEGER PRIMARY KEY", ""),
      ("subject", "TEXT NOT NULL", "a ticker, 'sector:<name>' or 'market'"),
      ("published", "TEXT", "ISO UTC"), ("source", "TEXT", "publisher"),
      ("url", "TEXT NOT NULL UNIQUE", ""), ("title", "TEXT NOT NULL", ""),
      ("summary", "TEXT", "one line, as the feed gave it"),
      ("lean", "REAL CHECK (lean BETWEEN -1 AND 1)", "-1 against .. +1 for the subject; NULL until read"),
      ("lean_by", "TEXT", "who set the lean: 'analyst' with the run id, never a script"),
      ("lean_note", "TEXT", "why, in a few words"),
      ("source_id", "INTEGER REFERENCES sources(id)", "the feed the item came from"),
      ("fetched_at", "TEXT NOT NULL", "")],
     None, ["CREATE INDEX IF NOT EXISTS ix_news_subject ON news (subject, published)"]),
    ("runs", "One row per question asked: how it was read, the plan, where the report went.",
     [("id", "INTEGER PRIMARY KEY", ""), ("asked_at", "TEXT NOT NULL", ""),
      ("question", "TEXT NOT NULL", "verbatim"),
      ("intent", "TEXT NOT NULL CHECK (intent IN ('stock','holdings','sector','macro','mix','digest'))", "the advisor's reading; digest for the daily digest"),
      ("subjects", "TEXT NOT NULL", "JSON list of tickers or sector names"),
      ("plan", "TEXT", "JSON list of steps, each a script call or a cited research step"),
      ("status", "TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','answered','failed'))", ""),
      ("report_path", "TEXT", "data/reports/<date>-<slug>.md once written"),
      ("notes", "TEXT", "what went wrong or was skipped")],
     None, []),
    ("views", "One dimension's reading of one subject in one run: the unit the verdict is composed from.",
     [("id", "INTEGER PRIMARY KEY", ""),
      ("run_id", "INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE", ""),
      ("subject", "TEXT NOT NULL", "ticker or sector"),
      ("dimension", "TEXT NOT NULL CHECK (dimension IN ('fundamentals','valuation','statistics','macro','industry','sentiment'))", ""),
      ("stance", "TEXT NOT NULL CHECK (stance IN ('for','against','neutral'))", "for the subject, against it, or neither"),
      ("strength", "INTEGER NOT NULL CHECK (strength BETWEEN 1 AND 3)", "1 weak, 2 clear, 3 strong"),
      ("horizon", "TEXT", "months or 'structural'"),
      ("sentence", "TEXT NOT NULL", "the reading in one sentence, with its figures"),
      ("evidence", "TEXT NOT NULL", "JSON list of source ids the sentence rests on"),
      ("created_at", "TEXT NOT NULL", "")],
     None, ["CREATE INDEX IF NOT EXISTS ix_views_subject ON views (subject, dimension, created_at)"]),
    ("stats", "Price statistics computed by stats.py as of a date.",
     [("ticker", "TEXT NOT NULL", ""), ("asof", "TEXT NOT NULL", "last price date used"),
      ("metric", "TEXT NOT NULL", "e.g. cagr, volatility, max_drawdown, beta, ma50, ma200, high_52w, low_52w"),
      ("window", "TEXT NOT NULL", "1y, 3y, 5y or 'spot'"),
      ("value", "REAL NOT NULL", ""),
      ("source_id", "INTEGER NOT NULL REFERENCES sources(id)", "derived; the prices rows are the inputs")],
     "PRIMARY KEY (ticker, asof, metric, window)", []),
    ("valuations", "Value estimates: the DCF's three scenarios, the reverse DCF, and the P/E cross-checks; inputs kept with each.",
     [("id", "INTEGER PRIMARY KEY", ""),
      ("run_id", "INTEGER REFERENCES runs(id) ON DELETE SET NULL", ""),
      ("ticker", "TEXT NOT NULL", ""), ("asof", "TEXT NOT NULL", ""),
      ("method", "TEXT NOT NULL DEFAULT 'dcf' CHECK (method IN ('dcf','reverse_dcf','pe_range','pe_peers'))",
       "dcf = a scenario; reverse_dcf = the growth the price implies (value = price); pe_range = EPS x the stock's own "
       "median P/E; pe_peers = EPS x the peers' median P/E"),
      ("scenario", "TEXT CHECK (scenario IN ('low','base','high'))", "low, base or high for a dcf row; NULL otherwise"),
      ("inputs", "TEXT NOT NULL", "JSON: every assumption and its origin; for the P/E rows the multiples themselves"),
      ("value_per_share", "REAL NOT NULL", ""),
      ("price", "REAL", "price on asof"),
      ("upside", "REAL", "value / price - 1"),
      ("p10", "REAL", "Monte Carlo 10th percentile of value per share"),
      ("p50", "REAL", "median"), ("p90", "REAL", "90th percentile"),
      ("source_id", "INTEGER NOT NULL REFERENCES sources(id)", "derived"),
      ("created_at", "TEXT NOT NULL", "")],
     None, ["CREATE INDEX IF NOT EXISTS ix_val_ticker ON valuations (ticker, asof)"]),
    ("calls", "Every recommendation made, with its confidence, and later what actually happened.",
     [("id", "INTEGER PRIMARY KEY", ""),
      ("run_id", "INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE", ""),
      ("ticker", "TEXT NOT NULL", ""),
      ("tier", "TEXT NOT NULL CHECK (tier IN ('conservative','moderate','aggressive'))", ""),
      ("action", "TEXT NOT NULL CHECK (action IN ('buy','add','hold','trim','sell','wait','avoid'))", ""),
      ("limit_price", "REAL", "the price the action is tied to, when there is one"),
      ("size", "TEXT", "shares, a weight, or words"),
      ("horizon_months", "INTEGER NOT NULL", ""),
      ("expected_return", "REAL", "fraction over the horizon, when stated"),
      ("confidence", "INTEGER NOT NULL CHECK (confidence BETWEEN 0 AND 100)", ""),
      ("confidence_parts", "TEXT NOT NULL", "JSON {evidence, agreement, record} with the reason for each"),
      ("believe", "TEXT", "what you have to believe for this tier"),
      ("evidence", "TEXT NOT NULL", "JSON list of source ids"),
      ("price_at_call", "REAL", ""), ("spy_at_call", "REAL", ""),
      ("made_at", "TEXT NOT NULL", "YYYY-MM-DD"), ("due_at", "TEXT NOT NULL", "made_at + horizon"),
      ("realised_at", "TEXT", "date the outcome was scored"),
      ("realised_price", "REAL", ""), ("spy_realised", "REAL", ""),
      ("outcome", "TEXT NOT NULL DEFAULT 'open' CHECK (outcome IN ('open','right','wrong','void'))",
       "right = the price moved the way the action implied by due_at, wrong = it did not, void = unscorable")],
     None, ["CREATE INDEX IF NOT EXISTS ix_calls_ticker ON calls (ticker, made_at)"]),
]

VIEWS = {
    "latest_prices": ("The last close per ticker.",
                      "SELECT p.ticker, p.date, p.close, p.adj_close FROM prices p "
                      "JOIN (SELECT ticker, MAX(date) d FROM prices GROUP BY ticker) m "
                      "ON m.ticker = p.ticker AND m.d = p.date"),
    "fundamentals_annual": ("Annual duration facts (350-380 days) and the instants (balance sheet) dated at a fiscal year end; "
                            "an instant is annual when an annual duration of the same ticker ends on its date, whatever "
                            "filing last reported it.",
                            "SELECT f.* FROM fundamentals f WHERE (f.days BETWEEN 350 AND 380) OR (f.period_start = '' AND EXISTS "
                            "(SELECT 1 FROM fundamentals a WHERE a.ticker = f.ticker AND a.period_end = f.period_end "
                            "AND a.days BETWEEN 350 AND 380))"),
    "fundamentals_quarterly": ("Quarterly duration facts (80-100 days) and the instants dated at a quarter end that is not a "
                               "fiscal year end.",
                               "SELECT f.* FROM fundamentals f WHERE (f.days BETWEEN 80 AND 100) OR (f.period_start = '' AND EXISTS "
                               "(SELECT 1 FROM fundamentals q WHERE q.ticker = f.ticker AND q.period_end = f.period_end "
                               "AND q.days BETWEEN 80 AND 100) AND NOT EXISTS (SELECT 1 FROM fundamentals a WHERE a.ticker = f.ticker "
                               "AND a.period_end = f.period_end AND a.days BETWEEN 350 AND 380))"),
    "track_record": ("Scored calls per tier and action: how many were right.",
                     "SELECT tier, action, COUNT(*) n, SUM(outcome = 'right') right_n, SUM(outcome = 'wrong') wrong_n, "
                     "SUM(outcome = 'open') open_n FROM calls GROUP BY tier, action"),
}


# --- schema -------------------------------------------------------------------------------------
def create_sql(name, cols, pk, extra):
    body = ",\n  ".join("%s %s" % (c, t) for c, t, _ in cols)
    if pk:
        body += ",\n  " + pk
    return ["CREATE TABLE IF NOT EXISTS %s (\n  %s\n)" % (name, body)] + list(extra)


def schema_statements():
    out = ["CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL, applied_at TEXT NOT NULL)"]
    for name, _, cols, pk, extra in TABLES:
        out += create_sql(name, cols, pk, extra)
    for name, (_, sql) in VIEWS.items():
        out.append("CREATE VIEW IF NOT EXISTS %s AS %s" % (name, sql))
    return out


MIGRATIONS = {  # version -> statements applied when upgrading to it (1 is the initial schema)
    1: schema_statements,
}


def db_path(project):
    return os.path.join(common.data_dir(project), DB_NAME)


def connect(project=None, path=None):
    """Open (creating and migrating when needed) the project's database. Foreign keys on, WAL, dict-like rows."""
    if not path:
        project = common.resolve_project(project or "")
        common.load_config(project)  # first run: data/, .gitignore and config.json with defaults appear
        path = db_path(project)
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
    migrate(conn)
    return conn


def current_version(conn):
    has = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'").fetchone()
    if not has:
        return 0
    v = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0]
    return v or 0


def migrate(conn):
    v = current_version(conn)
    for target in range(v + 1, SCHEMA_VERSION + 1):
        stmts = MIGRATIONS[target]()
        conn.execute("BEGIN")
        for s in stmts:
            conn.execute(s)
        conn.execute("INSERT INTO schema_version (version, applied_at) VALUES (?, ?)", (target, common.iso()))
        conn.execute("COMMIT")
    return SCHEMA_VERSION


def table_names():
    return [t[0] for t in TABLES]


def columns(name):
    for t in TABLES:
        if t[0] == name:
            return [c for c, _, _ in t[2]]
    raise KeyError("no table %s" % name)


def pk_columns(name):
    for t in TABLES:
        if t[0] == name:
            if t[3]:
                inner = t[3][t[3].index("(") + 1:t[3].rindex(")")]
                return [c.strip() for c in inner.split(",")]
            return [c for c, typ, _ in t[2] if "PRIMARY KEY" in typ]
    raise KeyError("no table %s" % name)


# --- writes -------------------------------------------------------------------------------------
def source(conn, url, grade, title=None, fetched_at=None):
    """Upsert a sources row by URL (keys redacted) and return its id."""
    if grade not in GRADES:
        raise ValueError("grade must be one of %s" % (GRADES,))
    url = common.redact(url)
    conn.execute(
        "INSERT INTO sources (url, grade, title, fetched_at) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(url) DO UPDATE SET grade = excluded.grade, fetched_at = excluded.fetched_at, "
        "title = COALESCE(excluded.title, sources.title)",
        (url, grade, title, fetched_at or common.iso()))
    return conn.execute("SELECT id FROM sources WHERE url = ?", (url,)).fetchone()[0]


def upsert(conn, table, rows, keys=None):
    """INSERT ... ON CONFLICT(primary key) DO UPDATE for a list of dicts. Returns the row count written.
    Unknown columns raise; missing non-key columns are left to their defaults (or NULL)."""
    rows = list(rows)
    if not rows:
        return 0
    cols = columns(table)
    keys = keys or pk_columns(table)
    used = [c for c in cols if any(c in r for r in rows)]
    bad = set().union(*(r.keys() for r in rows)) - set(cols)
    if bad:
        raise ValueError("unknown columns for %s: %s" % (table, sorted(bad)))
    missing = [k for k in keys if k not in used]
    if missing == ["id"]:  # autoincrement id tables: plain inserts
        conn.execute("BEGIN")
        try:
            for r in rows:
                insert(conn, table, r)
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        return len(rows)
    if missing:
        raise ValueError("rows for %s lack key columns %s" % (table, missing))
    sets = [c for c in used if c not in keys]
    sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, ", ".join(used), ", ".join("?" * len(used)))
    if sets:
        sql += " ON CONFLICT(%s) DO UPDATE SET %s" % (", ".join(keys), ", ".join("%s = excluded.%s" % (c, c) for c in sets))
    else:
        sql += " ON CONFLICT(%s) DO NOTHING" % ", ".join(keys)
    conn.execute("BEGIN")
    try:
        conn.executemany(sql, [tuple(_json(r.get(c)) for c in used) for r in rows])
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    return len(rows)


def insert(conn, table, row):
    """Plain INSERT of one dict; returns the new row id."""
    cols = columns(table)
    bad = set(row) - set(cols)
    if bad:
        raise ValueError("unknown columns for %s: %s" % (table, sorted(bad)))
    used = [c for c in cols if c in row]
    cur = conn.execute("INSERT INTO %s (%s) VALUES (%s)" % (table, ", ".join(used), ", ".join("?" * len(used))),
                       tuple(_json(row[c]) for c in used))
    return cur.lastrowid


def _json(v):
    return json.dumps(v) if isinstance(v, (list, dict)) else v


# --- reads --------------------------------------------------------------------------------------
def rows(conn, sql, params=()):
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def one(conn, sql, params=()):
    r = conn.execute(sql, params).fetchone()
    return dict(r) if r else None


def latest_price(conn, ticker):
    return one(conn, "SELECT * FROM latest_prices WHERE ticker = ?", (ticker.upper(),))


def read_only(conn):
    """Refuse every statement that is not a read."""
    def auth(action, a, b, c, d):
        ok = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
        return sqlite3.SQLITE_OK if action in ok else sqlite3.SQLITE_DENY
    conn.set_authorizer(auth)


# --- rendering ----------------------------------------------------------------------------------
def md_table(recs, cols=None):
    if not recs:
        return "_no rows_"
    cols = cols or list(recs[0].keys())
    fmt = lambda v: "" if v is None else ("%.4g" % v if isinstance(v, float) else str(v))
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(fmt(r.get(c)) for c in cols) + " |" for r in recs]
    return "\n".join(lines)


def schema_md():
    out = ["# invest.db schema (generated by `db.py schema --md`; version %d)" % SCHEMA_VERSION, "",
           "One SQLite file at `<project>/data/invest.db`, created and migrated by the first script that runs. "
           "Every numeric row carries `source_id` pointing at `sources`, which holds the URL the report links to. "
           "Holdings are never stored; reports are files under `data/reports/`.", ""]
    for name, purpose, cols, pk, _ in TABLES:
        out += ["## %s" % name, "", purpose, ""]
        if pk:
            out += ["Key: `%s`" % pk.replace("PRIMARY KEY ", ""), ""]
        out += ["| column | type | meaning |", "|---|---|---|"]
        out += ["| %s | %s | %s |" % (c, t.split(" CHECK")[0].replace(" REFERENCES", ", refs"), m) for c, t, m in cols]
        out.append("")
    out += ["## Views", ""]
    for name, (purpose, _) in VIEWS.items():
        out.append("- `%s`: %s" % (name, purpose))
    out += ["", "## Enumerations", "",
            "- intents: %s" % ", ".join(INTENTS), "- dimensions: %s" % ", ".join(DIMENSIONS),
            "- stances: %s" % ", ".join(STANCES), "- tiers: %s" % ", ".join(TIERS),
            "- actions: %s" % ", ".join(ACTIONS), "- grades: %s" % ", ".join(GRADES),
            "- scenarios: %s" % ", ".join(SCENARIOS), "- valuation methods: %s" % ", ".join(METHODS),
            "- outcomes: %s" % ", ".join(OUTCOMES), ""]
    return "\n".join(out)


# --- CLI ----------------------------------------------------------------------------------------
def run(argv=None):
    p = common.parser(SCRIPT, "the database: init, tables, describe, query, write, exec, schema")
    p.add_argument("command", choices=["init", "tables", "describe", "query", "write", "exec", "schema", "source"])
    p.add_argument("arg", nargs="?", default="", help="TABLE for describe/write, SQL for query/exec, URL for source")
    p.add_argument("--grade", default="secondary", choices=list(GRADES), help="source: the grade of the URL")
    p.add_argument("--title", default="", help="source: what the link is, in a few words")
    p.add_argument("--json", default="", help="write: rows as a JSON list, or @path to a file holding one")
    p.add_argument("--limit", type=int, default=200, help="query: maximum rows printed")
    a = p.parse_args(argv)
    if a.command == "schema":
        return common.emit({"ok": True, "script": SCRIPT, "tables": table_names(), "version": SCHEMA_VERSION},
                           md=schema_md() if a.md else None)
    project = common.resolve_project(a.project)
    conn = connect(project)
    path = db_path(project)
    if a.command == "init":
        return common.emit({"ok": True, "script": SCRIPT, "path": path, "version": current_version(conn)})
    if a.command == "tables":
        recs = [{"table": t[0], "rows": conn.execute("SELECT COUNT(*) FROM %s" % t[0]).fetchone()[0], "purpose": t[1]}
                for t in TABLES]
        return common.emit({"ok": True, "script": SCRIPT, "path": path, "tables": recs}, md=md_table(recs) if a.md else None)
    if a.command == "describe":
        for name, purpose, cols, pk, _ in TABLES:
            if name == a.arg:
                recs = [{"column": c, "type": t, "meaning": m} for c, t, m in cols]
                return common.emit({"ok": True, "script": SCRIPT, "table": name, "purpose": purpose, "key": pk_columns(name),
                                    "columns": recs}, md=md_table(recs) if a.md else None)
        return common.fail(SCRIPT, "no table %s; tables: %s" % (a.arg, ", ".join(table_names())))
    if a.command == "query":
        read_only(conn)
        try:
            recs = rows(conn, a.arg)[: a.limit]
        except sqlite3.Error as e:
            return common.fail(SCRIPT, "query failed: %s" % e)
        return common.emit({"ok": True, "script": SCRIPT, "rows": recs, "n": len(recs)}, md=md_table(recs) if a.md else None)
    if a.command == "write":
        if a.arg not in table_names():
            return common.fail(SCRIPT, "no table %s" % a.arg)
        raw = a.json
        if raw.startswith("@"):
            with open(raw[1:]) as f:
                raw = f.read()
        try:
            recs = json.loads(raw or "[]")
            if isinstance(recs, dict):
                recs = [recs]
            n = upsert(conn, a.arg, recs)
        except (ValueError, sqlite3.Error) as e:
            return common.fail(SCRIPT, "write failed: %s" % e)
        return common.emit({"ok": True, "script": SCRIPT, "table": a.arg, "written": n})
    if a.command == "source":
        if not a.arg:
            return common.fail(SCRIPT, "source needs a URL")
        sid = source(conn, a.arg, a.grade, a.title or None)
        return common.emit({"ok": True, "script": SCRIPT, "id": sid, "marker": "[S%d]" % sid, "url": common.redact(a.arg)})
    if a.command == "exec":
        try:
            cur = conn.execute(a.arg)
        except sqlite3.Error as e:
            return common.fail(SCRIPT, "exec failed: %s" % e)
        return common.emit({"ok": True, "script": SCRIPT, "changed": cur.rowcount, "last_id": cur.lastrowid})
    return 1


if __name__ == "__main__":
    sys.exit(common.run_main(SCRIPT, run))
