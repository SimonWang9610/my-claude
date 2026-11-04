# The nine scripts: purpose, usage, what they write and print

All: `run.sh <script.py> … --project P`; JSON envelope on stdout; `--md` for a table. Grades in brackets.

| Script | Purpose | Usage | Writes | Prints |
|---|---|---|---|---|
| `db.py` | the database: create, inspect, read, write | `init` · `tables` · `describe T` · `query "SQL"` · `write T --json ROWS` · `exec "SQL"` · `source URL --grade G --title T` · `schema --md` | schema; rows you pass | rows, counts, the new source id and marker |
| `sec.py` | fundamentals from SEC XBRL [primary] | `sec.py T [--years 5]` | `fundamentals`, `securities` | concepts stored, latest fiscal year, concepts missing; `--md` latest annual values |
| `yahoo.py` | prices, profile, analysts' estimates, fund weights [secondary] | `yahoo.py prices T` (incremental from the last stored day) · `profile T` · `estimates T` · `all T` | `prices`, `securities`, `funds`, `fund_weights`, `estimates` | rows added, what failed per part |
| `fred.py` | macro series [primary] | `fred.py [--series DGS10,CPIAUCSL] [--years 5]` | `macro_series`, `macro` | latest value, a year earlier, the change |
| `news.py` | news items; the analyst's lean [secondary] | `news.py fetch SUBJECT [--query Q] [--days 30]` · `news.py lean ID VALUE --by "analyst run N" [--note …]` | `news` | items with ids |
| `stats.py` | price statistics and levels [derived] | `stats.py T [--asof D]` | `stats` | metric · window · value (returns 1 day to 5 years, volatility, drawdown, beta, averages, 52-week levels, 3-month range, trend); what was skipped (SPY missing) |
| `dcf.py` | three-scenario DCF with a Monte Carlo band and sensitivity grid, reverse DCF, P/E cross-checks [derived] | `dcf.py T [--run-id N] [--growth lo,base,hi] [--margin …] [--discount …] [--terminal g]` | `valuations` | scenario · inputs · value per share · vs price; the band; the grid; implied growth; P/E now, its range, the peers |
| `holdings.py` | arithmetic over the user's broker CSV, nothing stored | `holdings.py CSV-or-folder [--size T1,T2] [--caps 15,12.5,10] [--total USD]` | nothing | positions, concentration, look-through via `fund_weights`, sizing frames, sell-from order, levels |
| `record.py` | runs, confidence, calls, scoring, lint, the report page | `open` · `confidence RUN SUBJECT [--action A]` · `calls RUN --json ROWS` · `score` · `record` · `lint --file D` · `report RUN --file D` · `fail RUN --notes …` | `runs`, `calls`, `data/reports/*.html` | run id; the confidence parts; settled calls; the track record; lint problems; the report path |

Shared modules, not scripts: `common.py` (project, config, HTTP, envelope) and `calc.py` (pure math and number formats).

## Order in a typical run

`record.py score` (settle what is due) → `yahoo.py all T` → `sec.py T` → `fred.py` → `stats.py T` →
`dcf.py T --run-id N` → `news.py fetch T` → the analyst reads, sets leans, registers research pages with
`db.py source`, writes views → `record.py confidence` → `record.py calls` → `record.py report`.

## Failure shape

A script that cannot do its job exits 1 with `{"ok": false, "script": …, "error": "<what and what to do>"}`;
a partial success (one Yahoo part failed) exits 0 and lists `failed`. The advisor relays the error with the
stage and gives **no verdict** for the part that depended on it.

## Why nine, and why these

Each script owns one kind of result, so a wrong number is traced to one file and one table. Fetchers are
split by source because each source has its own access rules (the SEC's user agent and rate, FRED's key,
Yahoo's library). Arithmetic is split by what it computes (prices → statistics, filings → value, a CSV →
sizing). `record.py` alone touches the analysis history, so the track record cannot be edited by accident.
