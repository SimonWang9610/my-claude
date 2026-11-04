---
name: data
description: >-
  The data layer of my-invest: nine scripts, each with one purpose (sec.py fundamentals from the SEC,
  yahoo.py prices, profiles, estimates and fund weights, fred.py macro series, news.py news items and the
  analyst's lean, stats.py price statistics, dcf.py three-scenario valuation, holdings.py arithmetic over
  the user's broker CSV, record.py runs, confidence, calls, scoring and the report page, db.py the database
  itself), the one SQLite database they share with its tables and source rows, the citation markers, and
  what is never stored. Use when fetching, computing, storing or citing anything; preloaded by the analyst agent.
user-invocable: false
---

# data

Scripts fetch, format and compute; agents judge. Everything a script stores goes into one SQLite file,
`<project>/data/invest.db`, created and migrated by the first script that runs (no setup step, no user
action); the only other artifacts are the HTML reports under `data/reports/`. Run convention:
`"${CLAUDE_PLUGIN_ROOT}/scripts/run.sh" <script.py> <args> --project "${CLAUDE_PROJECT_DIR}"`. Every script
prints a JSON envelope (`ok`, `script`, then its result) and most take `--md` for a Markdown table you can
paste. Usage and output of each script: [scripts.md](references/scripts.md). Tables, columns and views:
[schema.md](references/schema.md), generated from `db.py` so it cannot drift.

## Sources and markers

Every stored number points at a `sources` row: the URL it came from, a grade (**primary** SEC or FRED,
**secondary** Yahoo, news or a research page, **derived** a script's arithmetic over sourced rows) and the
fetch time. A figure in an answer carries `[S<id>]` with that row's id; a page the analyst read is
registered with `db.py source URL --grade secondary --title "…"` to get its id. `record.py` turns markers
into links and refuses a report with an uncited figure or an unknown id.

## Reading and writing

Read with `db.py query "SELECT …" --md` (read-only; views `latest_prices`, `fundamentals_annual`,
`fundamentals_quarterly`, `track_record` save joins; arithmetic inside a SELECT, such as this quarter against
a year earlier, counts as a script's and is cited to the rows' sources). The analyst writes its judgments with
`db.py write views --json '[…]'` and `news.py lean ID VALUE --by "analyst run N"`; everything else is
written by the script that computes it. Nothing is edited by hand; a wrong row is replaced by rerunning
the script.

## Never stored

The user's holdings. `holdings.py` reads the broker CSV for the run and prints its arithmetic; no table
holds shares, costs or accounts. The report of that run keeps the answer that was given, nothing else.

## config.json

`<project>/data/config.json`, written with defaults on first run and merged over them afterwards:
`sec_user_agent` (required by the SEC, "AppName you@example.com"), `fred_api_key` (optional),
`python` (optional interpreter), `equity_risk_premium` (percent), `max_horizon_years` (5),
`depth` (`news`, `peers`, `macro_series`, `price_years`, `fundamental_years`).
