# Confidence: the formula, the bands, the wording

`record.py confidence RUN_ID SUBJECT [--action A]` computes it from the tables; the analyst never estimates it.

| Part | Max | Computed as | Reason shown |
|---|---|---|---|
| evidence | 35 | 35 × (0.7 × coverage + 0.3 × grade). Coverage = dimensions with a view ÷ dimensions the intent needs (stock 6; holdings 4: fundamentals, valuation, statistics, macro; sector 3: industry, macro, sentiment; macro 2). Grade = mean weight of the sources the views cite: primary 1.0, derived 0.75, secondary 0.5 | "4 of 6 dimensions have a view, missing industry, sentiment; source grade 0.81" |
| agreement | 35 | 35 × |Σ stance × strength ÷ Σ strength| × spread factor. Spread = (DCF high − low) ÷ base; factor 1 up to 50%, falling 0.4 per 100% to a floor of 0.6 | "weighted stance 0.67 (for) over 6 views; DCF high-low spread 90% of base" |
| record | 30 | 30 × (right + 2.5) ÷ (settled + 5) over settled calls of the same side (buy-side: buy, add, hold; sell-side: trim, sell, wait, avoid). No record → 15 | "3 of 5 settled buy-side calls came true" |

Total 0..100. Bands: **80+ strong evidence**, **65–79 solid**, **45–64 mixed**, **below 45 thin**.

## Where it appears

- The headline carries the total and the band for the moderate option.
- Each option's table has a confidence cell with the total and the one part that limits it most
  ("58, mixed: agreement 12/35, statistics and sentiment against").
- The full line goes under **Supporting analysis** once:
  `Confidence 62/100 (mixed): evidence 25/35, ...; agreement 22/35, ...; record 15/30, ...`

## How to read it, for the user

Evidence low → we did not see enough; agreement low → the signs disagree; record low → calls like this
one have not worked before. A high score is not a promise: the record part is the one that catches a
method that sounds good and keeps being wrong.
