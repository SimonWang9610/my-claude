# Follow-up questions — an action, sized and priced, from the files already on disk

After a brief, the user asks for the next decision: "which price should I sell, and how many shares?",
"how much should I buy first?", "should I move it to the TFSA?". These are answered in the conversation
from the stock folder and one script run, not with a new brief and not with a new analyst. The example
answer the user wants (a trim of Apple and Nvidia) has this shape; keep it.

## Shape

1. **One line on what the question is and what you will run** ("trim mechanics are in the standard: a
   trailing trigger at the 50-day average and trim to target weight; I'll compute the share counts for a
   few target weights from your own positions"). Then run
   `size.py <T> --question "<holdings text>" --total <USD in scope> [--funds QQQ=<value>,VGT=<value>] --md`
   per ticker (funds need `fund.py` first).
2. **The verdict in two or three sentences**: whether the action is consistent with the evidence (the
   recommendation cell, the strict value lens, the trend, concentration once funds are counted), what it
   replaces in the earlier plan ("a trim replaces the add leg"), the tax consequence by account, and the
   one-line disclaimer ("I'm not a licensed advisor; the levels are the model's, the sizing frames are
   arithmetic on your own positions").
3. **How many** — the frames table from `size.py`, one column per ticker: cap at 15%, 12.5%, 10% of the
   portfolio, sell the gain, recover the cost — each as shares to sell, proceeds, shares kept. Mark your
   pick per ticker and say why in one paragraph: outright weight, look-through weight via the funds
   (which fund holds how much of it), and which account to sell from first (the script's order: taxable
   last, RRSP before TFSA) with the reason.
4. **At what price** — per ticker, the plan in halves, each half tied to a level the script printed and
   the rule it comes from: a limit at the 52-week high or the upper edge of the options-implied range
   ("inside the upper part of the implied range to <date>"); a trailing rule at the 50-day average
   ("sell if it closes below $x"); for a stock below its averages, a limit at the 50-day average where a
   bounce first meets resistance, and a floor at the 52-week low where the trend reading flips. Name the
   next earnings date and its implied move when it falls inside the plan. Add the one warning the latest
   news justifies (an after-hours guide, a filing) with its date, and say what the rule does then.
5. **What this changes in the earlier answers** — withdraw any buy plan on a ticker now being trimmed
   (you cannot trim and add the same stock); say what the proceeds cover among the planned buys; confirm
   that the hold verdict on the shares kept is unchanged, with the expected and required returns.

## Rules

- Every number is a script's: `size.py` for shares, proceeds, weights, look-through and levels;
  `holdings.py` when a taxable sale needs the tax line; the scorecard for cells and returns. No
  arithmetic of your own; if a frame the user asks for is not in the script, say so and add it to the
  script, never to the answer.
- Levels come with their rule's name (50-day average, 52-week high, implied range to a date, 52-week low)
  so the user learns what each is; no price target of your own.
- Markers may be left out of a conversational follow-up when every figure comes from a script run in the
  same turn; end with one `Files:` line pointing at `facts/sizing.json` and the stock's page.
- A failed deal-breaker check or an `exit` cell is not sized: the answer is sell, and the frames are not
  shown.
- Holdings read from the question or the broker file stay in the request for this turn; delete
  `facts/sizing.json` with the holdings files when the question stated positions (advisor step 4).
