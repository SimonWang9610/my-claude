# Reading the question: intents, subjects, dimensions, and what shapes the tables

| Intent | Signals | Subjects | Dimensions the analyst runs | What shapes the "What to do" columns |
|---|---|---|---|---|
| stock | one or a few tickers or company names; "how about", "outlook", "buy", "sell", "worth" | the tickers | all six | the verb asked: buy → limit price, size, upside to the scenario value; sell → trigger level, how much; "when" → the levels and dates; "worth" → value per scenario vs price, the P/E against its range, the implied growth |
| holdings | "my", "I hold", "portfolio", a CSV path, account names | every ticker in the CSV; funds included | fundamentals, valuation, statistics per position; macro once; industry and sentiment only for positions whose action changes | one row per position: action, limit or trigger, shares or weight to change, account to sell from first, confidence; look-through and concentration beside it |
| sector | an industry, theme or chain; no ticker or many | `sector:<name>`, then the names surfaced | industry, macro, sentiment for the sector; fundamentals and valuation for up to `depth.peers` names | the names surfaced with the option for each: enter now / wait for level / avoid, and why |
| macro | "the market", rates, recession, "is now a good time" | `market` | macro, sentiment; statistics on SPY | what to do with cash or an index position per option |
| mix | two of the above in one question | the union | the union | one combined set of tables, one per option, sectioned by part |

## Rules of reading

- A company name resolves to its ticker through `yahoo.py profile`; when two listings fit, ask once with
  the best guess as default.
- The horizon is the user's when stated; else one and three years, written as "to Nov 2027" and "to Nov
  2029" from the price date. Never beyond five years.
- A named level ("the safe option", "be aggressive") → only that option's table.
- "Which stocks should I buy" with no sector → ask for the area or the holdings; a screen of the whole
  market is not offered.
- The reading line is written before any script runs, so a wrong reading is caught early.
