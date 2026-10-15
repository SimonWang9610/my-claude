---
name: evidence
description: >-
  Defines the provenance rule every my-invest output obeys: source classes, the [S<n>] marker and
  evidence-log format, the no-evidence protocol, freshness limits, how quotes and posts are handled, the
  disclaimer line, and the lint that checks all of it. Use when writing or checking any my-invest dossier,
  research file, digest or table; preloaded into the researcher agent, not invoked by the user.
user-invocable: false
---

# evidence

No number from memory. A figure, date, quote or claim about a company appears in an output only with
a marker `[S<n>]` that resolves in that output's Evidence log. Anything else is written `no evidence`.

## Source classes (log column `class`)

- **primary** — an SEC filing or XBRL fact (`sec.gov`, `data.sec.gov`), a company investor-relations
  page, an exchange notice, a Treasury or FRED series.
- **derived** — a value a plugin script computed from cited inputs; the `what` column names the script
  and the input markers: `Piotroski F, metrics.py from S3 S4`.
- **secondary** — prices and estimates from Yahoo via yfinance, news outlets, analyst notes, aggregators.
- **social** — Reddit, X, Xueqiu, Substack and similar posts.

For the same fact a primary beats a secondary; cite the primary. A secondary figure in a scorecard
input is allowed only where no primary exists (prices, consensus) and is marked `secondary` in the row.

## Marker and log

Every sentence or table cell that carries a figure ends with `[S<n>]`. One marker may cover several
figures from the same source and period. The Evidence log closes every dossier, digest and discovery
table:

```
| S | class | what | url | as-of | retrieved |
| S1 | primary | FY2025 10-K, revenue and operating cash flow | https://www.sec.gov/Archives/edgar/data/.../...htm | FY2025 | 2026-10-14 |
```

`as-of` is the period or date the fact describes; `retrieved` is the fetch date. The URL must open to
the fact itself: a filing, an API call, an article. A homepage or a search page is not a source. A
`derived` row's url column holds `file://<path to the facts.json it was computed into>`.

**Ids.** Scripts use `S1`–`S99`, regenerated each run: `S1`–`S59` the fetched sources in `facts.json`,
`S60` the metrics derived row, `S61` the score derived row, `S62` the history row, `S80`–`S89` the peer
comparison rows, `S90`–`S99` the holdings script's tax sources. The researcher's `research.md` uses `S100` upward, cumulative across runs, so an old citation
still resolves; it ends with `## Open questions` and its own `## Evidence log`. `report.py` merges both
ranges into the dossier.

**Display, not arithmetic.** Converting units (dollars to millions, a ratio to a percent) and rounding
for display are allowed when the unit is stated in the header or beside the figure. Summing, averaging,
differencing or any other arithmetic on fetched figures is not; a value the dossier needs but no script
provides is `no evidence` and an open question for the data layer.

## No-evidence protocol

- Missing input → the cell reads `no evidence`, the item scores 0, and the gap is listed under
  **Open questions**. Never interpolate, never recall a figure, never average "typical" values.
- An unavoidable estimate (maintenance capex) is labelled `estimate` with its method and input
  markers: `estimate: 5-yr average D&A [S7]`. Estimates never feed a gate.
- Two sources disagree → cite both, say which one the output uses and why, in one clause.

## Freshness

Prices at most one trading day old; fundamentals from the latest filed period, flagged when the
submissions feed shows a newer filing; macro at most seven days old. A stale figure stays cited and
gains `(stale, as-of <date>)` after its marker.

## Posts and news

Cite URL, author handle or outlet, and date. Quote at most 15 words, and only text you read verbatim
(a local filing extract, a page's own text); a fetch that returns a summary yields a paraphrase,
written without quotation marks. Opinion is attributed ("the poster argues…"), never adopted as fact.
A search result is not evidence; only a fetched page is.

## Disclaimer

The last line of every dossier, digest and discovery table, verbatim:

> Model-backed research for the owner's own study, not investment advice. Every figure is as cited
> and may be wrong or stale.

## Mechanical check

Before handing any output back:

```
"${CLAUDE_PLUGIN_ROOT}/scripts/run.sh" "${CLAUDE_PLUGIN_DATA}" lint.py [--part] <file>
```

`--part` for `research.md`, `narrative.md` or a script's Markdown output (no disclaimer expected), with
`--facts <facts.json>` so the ids of the sibling `facts.json`, `scorecard.json`, `holdings_tables.json` and
`research.md` resolve; without them for a dossier, digest or find table.
`report.py` runs the full check itself and fails on a violation. It fails on a figure line without a resolving marker, a marker without a log row, a log row
without a URL, or a missing disclaimer. A failing lint is a defect in the output, not a reason to drop
the figure.
