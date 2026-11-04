---
name: digest
description: >-
  The daily digest for the user's own holdings: reads the broker CSVs under <project>/holdings/, refreshes
  prices, analysts' dates, news and macro for every position through the plugin's scripts, settles the calls
  that came due, and leads with what needs attention today (earnings reported or due this week, a position
  that moved, news that changes a stored view, a macro shift), then one table of the holdings with their
  recent moves and next events, the news that matters with its lean, the macro line and the track record;
  every figure cited, saved as an HTML page. Use when the user asks for the digest, "what's new", "anything I
  should know today", or on /my-invest:digest, with or without a focus such as earnings or one ticker.
argument-hint: [focus, e.g. "earnings" or a ticker]
---

# digest

What the user reads before they dive in: the same scripts, tables, markers and page as the advisor, no new
machinery. The holdings come from `<project>/holdings/*.csv` through `holdings.py` for this run and are
never stored. Know-how: [standard](../standard/SKILL.md), [data](../data/SKILL.md); scripts run as
`"${CLAUDE_PLUGIN_ROOT}/scripts/run.sh" <script.py> … --project "${CLAUDE_PROJECT_DIR}"`.

## 1. Gather

1. `holdings.py "${CLAUDE_PROJECT_DIR}/holdings" --md` → the positions and weights; no folder or no CSV → say
   so and offer to digest the tickers of the last run instead. A focus in the argument narrows the tickers
   or the theme; nothing else changes.
2. `record.py open --question "digest <date> <focus>" --intent digest --subjects <tickers>`; then
   `record.py score` so calls that came due are settled today.
3. Per ticker, in parallel where possible: `yahoo.py prices T` (incremental), `yahoo.py estimates T` (next
   earnings date), `stats.py T` (ret_1d, ret_1w, ret_1m, trend, distance from the 52-week high),
   `news.py fetch T --days <days since the last digest run, at least 2>`. Once: `fred.py`,
   `yahoo.py prices SPY`, `stats.py SPY`.
4. Earnings: a ticker whose `estimates.next_earnings` passed since the last digest, or whose news says it
   reported → `sec.py T` for the new quarter, then `db.py query` on `fundamentals_quarterly` for the latest
   quarter against the same quarter a year earlier (revenue, operating income, diluted EPS): SQL arithmetic
   through `db.py` counts as a script's. Compare with the stored views on that ticker.

## 2. Read

Read the news titles and summaries; set the lean of the items that matter with `news.py lean`. Decide what
needs attention: a position down or up more than its one-standard-deviation three-month range in a week; an
earnings report; a news item whose lean contradicts the stored view; the 10-year yield or VIX moving more
than a point since the last digest; a call that settled. Everything else is a row in the table, not a
bullet.

## 3. Write

```markdown
# Digest for <date>: <n> positions, <k> things need your attention
*As of <price date>. Prices from Yahoo, filings from the SEC, macro from FRED; markers link to each.*

## Needs attention today
- <at most five bullets, each: what happened, the figure with its marker, what it means for the position,
  and the next step: "ask the advisor about T" when it changes a view>

## Your holdings
| ticker | weight | 1 day | 1 week | 1 month | vs 52-week high | trend | next earnings | note |

## Earnings
<one block per report since the last digest: the quarter's revenue, operating income and EPS against a year
earlier, what the market did, and whether the stored view holds>

## News that matters
| when | ticker | source | title (link) | lean | why it matters |

## Macro line
<10-year yield, 10y-2y spread, VIX, Fed funds: level and change since the last digest, one sentence on what it means for the portfolio>

## Track record
<calls settled today and open calls due within a month, from `record.py record --md`>

## Not verified
- <tickers whose fetch failed, with the stage>
```

Keep it under eighty lines; a digest is read in two minutes. Save the draft to the scratchpad, finalise
with `record.py report RUN --file draft.md --slug digest`, paste the Markdown, send or publish the page.
Every figure carries a marker; a digest makes no calls and offers no options; when something needs a
decision it says "ask the advisor", which runs the full analysis.
