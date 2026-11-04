# my-invest

A financial advisor for a beginner in US stocks and funds, built as a Claude Code plugin. You ask in plain
words; it answers with what to do first, as three options you can choose between, then the analysis that
backs it, with every figure linked to where it came from.

## How you use it

- **One stock**: "how about Apple over the next three years?" → the verdict, three option tables
  (conservative, moderate, aggressive) with the columns your question needs, why, the analysis by
  dimension, the case against, the track record, what could not be verified.
- **Your holdings**: "review my positions, the CSV is in holdings/" → one table of positions with the action,
  level, account to sell from first and confidence for each, then the options per position that changes.
  The CSV is read for the run and never stored.
- **A sector or the market**: "is now a good time for semiconductors?" → the names surfaced with an option
  for each.
- **Follow-ups**: "how many shares should I trim, and at what price?" → sizing frames and named levels from
  your own positions.
- **The digest** (`/my-invest:digest`): before you dive in, what needs attention today across your
  holdings: earnings reported or due, big moves, news that changes a view, the macro line, calls that
  settled.

The chat shows Markdown; the same report is saved as an HTML page under `data/reports/` with a price chart.

## What is behind an answer

Six dimensions, each ending in a one-line view with a stance and a strength: SEC fundamentals (primary),
a three-scenario DCF with a Monte Carlo band, price statistics, macro and politics (FRED plus cited pages),
industry, sentiment (news read by the analyst, analysts' targets). Five deal-breakers checked first. The
three options are defined by the risk taken, not by the action. Every conclusion carries a confidence score
out of 100 with three auditable parts: evidence (coverage and source grade), agreement (do the views point
the same way), record (how calls of this kind turned out, scored against SPY when they come due). The
standard is written to be read: `skills/standard/`.

## What is on disk

- `data/invest.db`: one SQLite database, created on first use. Fetched series (prices, fundamentals, macro,
  estimates, fund weights, news) and the analysis history (runs, views, valuations, stats, calls). Schema:
  `skills/data/references/schema.md`.
- `data/reports/*.html`: one page per question.
- `data/config.json`: created with defaults; set `sec_user_agent` to "AppName you@example.com" (the SEC
  requires it). Optional `fred_api_key`.
- Never stored: your holdings.

## Scripts

Nine, one purpose each: `db.py` (the database), `sec.py`, `yahoo.py`, `fred.py`, `news.py` (fetch),
`stats.py`, `dcf.py`, `holdings.py` (arithmetic), `record.py` (runs, confidence, calls, scoring, the
report page). Agents judge; scripts never do. Details: `skills/data/references/scripts.md`.
Tests: `cd scripts && python3 -m unittest discover -s tests -q`.

## Install and update

`/plugin install my-invest --marketplace SimonWang9610/my-claude`. To update from the `my-claude` marketplace: `claude plugin marketplace update my-claude`, then
`claude plugin update my-invest@my-claude`, then restart. `yahoo.py` needs `yfinance`; `run.sh` creates
`data/.venv` with it on first use (Python 3.10 or newer on PATH).

## Limits

US-listed stocks and funds only. Prices, profiles and news are secondary sources and marked so. Tax and
options are out of scope except the account-order rule for Canadian registered accounts. The record part
of confidence is neutral until calls have come due. This is research, not licensed advice.
