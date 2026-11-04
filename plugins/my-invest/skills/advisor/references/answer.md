# The answer: Markdown in the chat, the same text as an HTML page on disk

Result first, in this order, for every intent. Sections are fixed; the columns inside the option tables
are not: they are built from the question's own words.

```markdown
I read this as: <intent in plain words>, horizon <dated>, <all three options | the <level> option>.

# <SUBJECT>: <verdict in one sentence, with the dated horizon> — confidence <n>/100 (<band>)
*As of <price date>. Horizons count from that date.*

## What to do
### Conservative
| <columns the question needs> | what you have to believe | confidence | evidence |
### Moderate
...
### Aggressive
...
(one table when a level was named; a failed deal-breaker → one line: stay away or sell, with the item cited)

## Why
- three bullets, each with its figures and markers

## Supporting analysis
One block per dimension in the order valuation, fundamentals, statistics, sentiment, industry, macro: the view
line (stance, strength, horizon) and one table of the figures it rests on, every cell with a marker.
Then the full confidence line.

## The case against
- the strongest reasons the verdict is wrong, each cited

## Track record
The `record.py record --md` summary and the last settled calls on this subject.

## Not verified
- gaps, each with what would close it
```

`record.py report` appends **Sources** (one line per marker with its link) and the disclaimer, turns every
`[S<id>]` into a link, adds a price chart per ticker, and writes the HTML page. The chat shows the
Markdown above; the page is for keeping and for later questions.

## Column examples

- "Should I buy Nvidia?" → action · limit price · size (weight) · upside to the scenario value · believe · confidence · evidence.
- "When should I sell Apple?" → trigger level and its name (50-day average, 52-week high, 3-month range top) · how much · what it changes · believe · confidence · evidence.
- "How many shares should I trim?" → frame (cap 15%, 12.5%, 10%; sell the gain; recover cost) · shares to sell · proceeds · shares kept · from account · confidence.
- "Is now a good time for semiconductors?" → name · what to do · level · why in five words · confidence · evidence.

## Holdings

One table first with a row per position (worth, weight, look-through weight, action, limit or trigger,
account to sell from first, confidence), then three lines: sell / hold / add, with the names. Then the
option tables per position whose action is not hold, then the sections above once for the portfolio
(macro and concentration under Supporting analysis). Funds follow the fund line of the standard's
deal-breakers; a plain index fund's options are about weight, not timing.

## Follow-ups in the conversation

Verdict in two sentences, the frames table from `holdings.py --size`, the plan in halves tied to named
levels, what it changes in the earlier options, one `Files:` line pointing at the page. Markers may be
omitted when every figure comes from a script run in the same turn.

## Words

Plain words; a term from the standard gets a gloss the first time ("the 200-day average, the mean closing
price of the last 200 trading days"). Dates as "Nov 2027", never "5-year". Under about a hundred lines for
one stock.
