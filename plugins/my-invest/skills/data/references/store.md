# Data folder — one folder per stock, grown by questions

Everything lives under `<project>/data/` (`<project>` = the folder Claude Code runs in, `${CLAUDE_PROJECT_DIR}`,
passed as `--project`; `"store_dir"` in `config.json` or `MY_INVEST_STORE` overrides the whole folder).
The plugin writes nothing anywhere else.

```
<project>/data/
  config.json                 the one settings file (sec_user_agent required; margin_of_safety, store_dir, fred_api_key, finnhub_api_key, python)
  .gitignore                  generated: .cache/ .venv/ config.json
  .cache/                     raw downloads
  .venv/                      the yfinance environment the plugin creates on first use
  market/                     SPY.json, <SECTOR_ETF>.json price series shared by all stocks
  find/                       <date>-<slug>-chain.md, <date>-<slug>.md/.html   (industry chain maps and screens)
  digests/                    <date>-daily|weekly.md/.html
  stocks/<TICKER>/
    INDEX.md                  generated each run: name, sector, chain position, latest decision, folder map, history table, open questions
    facts/
      facts.json              fundamentals, prices, macro, market, options, momentum, derived metrics
      series.json             ten-year daily prices
      scorecard.json          gates, items, pillars, score, zones, action matrix, confidence, short-term lens
      holdings.json           positions from the current question; deleted by the advisor after the answer
      holdings_tables.json    outcomes and tax tables for that question; deleted with it
      peers.json              the comparison table against up to four peers (compare.py)
      last_run.json           incremental state
    filings/<accn>/           the 10-K split into items, auditor's report, notes (immutable)
    research/
      research.md             cumulative cited research, dated entries, ids S100+
      evidence.json           verdicts for the four evidence-required items
      industry.md             the stock's industry chain position and related stocks, cited
    history/
      log.md                  one line per question: date, question, lens, tier, score, stance, confidence, price, zones, what changed
      <date>-<HHMM>.md        the narrative written for that question (why, strengths, weaknesses, thesis, answer)
    reports/
      dossier.md              the full report for the latest question
      <date>-<HHMM>.md        dated snapshot of each dossier
      <date>-<HHMM>.html      the answer as a web page: tables, chart panels, full dossier
    charts/<date>.html        the five panels alone
```

## Refresh rules

| Data | Rule |
|---|---|
| prices, options, market, momentum, macro | every run (prices only when the cached date is older than the last trading day) |
| fundamentals | only when the submissions feed shows a 10-K or 10-Q newer than the one used |
| filings_recent | three years back, merged and deduplicated |
| filing extracts | immutable; a new 10-K gets a new folder |
| research.md, evidence.json | the researcher appends dated entries since the last run; verdicts re-judged only on a new 10-K |
| industry.md | written when absent or older than 90 days, or when the question asks about the industry or peers |
| INDEX.md, log.md, reports, charts | every run |

## Source id ranges

Scripts use `S1`–`S99`: `S1`–`S59` fetched sources in `facts.json`, `S60` the metrics derived row, `S61` the
score derived row, `S62` the history row, `S80`–`S89` the peer comparison rows, `S90`–`S99` the holdings tax
sources (fixed, so saved narratives keep resolving). The researcher uses `S100` upward, cumulative across
runs. `report.py` merges both ranges into the dossier's Evidence log; the lint's `--facts` option resolves
the ids of the sibling `facts.json`, `scorecard.json`, `holdings_tables.json` and `research.md`.

## Incremental run

1. `facts.py <T>` refreshes per the table and prints `changed: […]`, `reused: […]`, `news_since`.
2. The researcher gets the stock folder, `news_since`, the `changed` list, the first free id
   (`store.py next-id <T>`), whether `evidence.json` must be (re)judged and whether `industry.md` is due,
   and adds only new or changed evidence.
3. `score.py` and `report.py` run on the whole folder; `log.md` records what moved since the last line and
   `INDEX.md` is regenerated.
