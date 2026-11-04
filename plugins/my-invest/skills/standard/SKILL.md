---
name: standard
description: >-
  The analysis standard behind every my-invest answer, written so a beginner can read and apply it: six
  dimensions (fundamentals, DCF, statistics, macro and politics, industry, sentiment) that each end in a
  one-line view; five deal-breakers; the three options (conservative, moderate, aggressive) defined by the
  risk taken; a confidence score out of 100 with three auditable parts; how every call is later scored
  against the index; the citation, dated-horizon and no-verdict rules. Use when forming, checking or
  explaining a verdict about a US stock, fund, sector or portfolio; preloaded by the analyst agent.
user-invocable: false
---

# standard

A verdict is composed in the open from six one-line views, one per dimension, and offered as three options
that differ by the risk taken. Nothing is weighted in secret; every figure links to its source; every
judgment is labelled as the analyst's. Horizons are counted from the price date, named as a month and
year, and never exceed five years.

## 1. The six dimensions and the view record

Each dimension answers one question from a named data grade and ends in a **view**: `stance` for, against
or neutral; `strength` 1 weak, 2 clear, 3 strong; `horizon`; one `sentence` with its figures and markers;
the `evidence` ids. The contract per dimension, the metrics to look at and what earns each stance:
[dimensions.md](references/dimensions.md). A dimension with no data gets no view, and the gap is named
under **Not verified**; it is never filled with a guess.

## 2. Deal-breakers

Checked first, from the filings and the fund profile. Any one of them makes the answer "stay away, or sell
what you hold" with the item cited, and no tiers are offered:

1. Going-concern doubt or a delisting notice in the latest filing.
2. A restatement, an auditor change with disagreement, or a material-weakness finding in the last two years.
3. Debt the business cannot carry: net debt above four years of operating cash flow with cash flow falling.
4. Serial dilution: diluted shares up more than a quarter over three years without matching revenue growth.
5. For a fund: leveraged or inverse (daily-reset) products are not for holding beyond days; say so.

## 3. Valuation: the DCF and its cross-checks

Three DCF scenarios (low, base, high) from the fundamentals with a Monte Carlo band and a sensitivity grid,
the reverse DCF (the growth today's price already assumes), and the P/E cross-checks (trailing P/E against
the stock's own five-year range and the peers' median), all computed by `dcf.py`; the analyst chooses the
assumptions and must write why in the valuation view. Defaults, overrides, sanity checks, how the two
methods are read together and how the scenarios map onto the tiers: [dcf.md](references/dcf.md).

## 4. The three options, defined by risk taken

**Conservative** takes the least risk of loss: it leans only on computed and primary evidence, acts at the
DCF low value, sizes small, and needs the fewest things to be true. **Moderate** acts at the base value with
the views that agree. **Aggressive** accepts the sentiment, trend and industry readings, acts up to the high
value, sizes larger, and names what has to go right. On a sell question the same rule holds: conservative
protects capital first (sells more, sooner, at the nearest level), aggressive holds out for higher levels.
So "conservative" always means less risk, never less action. Each option states: the action, the limit
price or trigger, the size, what you have to believe, one sentence of reasoning, its confidence and its
evidence. When the question names one level, only that option is given.

## 5. Confidence, out of 100

Every conclusion (the headline and each option) carries a score with three parts: **evidence** 35 (coverage
of the dimensions the question needs, and the grade of the sources cited), **agreement** 35 (how far the
views point the same way, discounted when the DCF scenarios are wide), **record** 30 (how settled calls of
the same side turned out). `record.py confidence` computes it from the tables; the formula, the bands and
the wording: [confidence.md](references/confidence.md).

## 6. Calls and how they are scored

Each option is stored as a call with its price and the index level that day. When the horizon has passed,
`record.py score` settles it: a buy-side call (buy, add, hold) was right if the stock beat SPY over the
horizon; a sell-side call (trim, sell, wait, avoid) was right if the stock lagged SPY. The track record is
shown in every answer and feeds the record part of confidence. No call is edited after the fact.

## 7. Rules that never bend

- US-listed stocks and funds only; fundamentals from SEC filings (primary), prices and profiles from Yahoo
  (secondary), macro from FRED (primary), news and research pages (secondary), script output (derived).
- Every figure carries a marker `[S<id>]` to a `sources` row; `record.py` refuses a report without them.
- No default hold: when a dimension the question needs is missing or a script fails, the answer says
  **no verdict** for that part, names the gap and what would close it.
- Numbers come from scripts or source rows; the analyst never does arithmetic in prose.
- Tax and options are out of scope. The one tax rule kept: sell from RRSP first, then TFSA, then a taxable
  account, because a sale in a registered account is not taxed while half of a taxable gain is.
