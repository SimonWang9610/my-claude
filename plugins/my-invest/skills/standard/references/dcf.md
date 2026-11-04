# Valuation: the DCF, its sensitivity, the reverse DCF, the P/E cross-checks, and the options

`dcf.py TICKER [--run-id N] [--growth lo,base,hi] [--margin lo,base,hi] [--discount lo,base,hi] [--terminal g] [--years 5]`

## Defaults the script derives (every one recorded in `valuations.inputs`)

- **Revenue growth** base = the revenue CAGR over the stored fiscal years, clamped to −5%..25%; low = base − 5
  points (floor −10%); high = base + 5 points (cap 30%).
- **Operating margin** base = 3-year average; low = the worst year; high = the best year.
- **Discount rate** = cost of equity by CAPM: 10-year Treasury yield (FRED DGS10) + beta (stats 3y, else 1.0)
  × equity risk premium (`config.equity_risk_premium`, 4.2% unless edited); low/high ±1.5 points; floor 6%.
- **Terminal growth** 2.5%, always at least 1 point under the discount rate.
- **Forecast years** 5, the horizon cap. Depreciation and capex follow revenue at their latest ratios;
  reinvestment is zero; tax rate from the filings, clamped 0..35%, 21% when missing.

## What the analyst may override, and the duty that comes with it

Any default, when a filing, a guide, or the industry view justifies it: write the override and its reason
in the DCF view's sentence ("growth 12% rather than the 9% history because the data-centre backlog in the
10-K is 2x last year's [S4]"). An override without a cited reason is not allowed. Never override to reach
a price.

## Sanity checks before a DCF view is written

- Free cash flow negative in the base year → DCF not applicable; view neutral, strength 1, say why.
- Terminal value above 80% of the total → say the value rests on the far future.
- Monte Carlo p10..p90 wider than the price itself → the view is at most strength 1.
- Diluted shares or revenue missing → no DCF, named under Not verified.

## Scenarios onto options

Conservative acts at the **low** value (buy at or below it; sell above it when trimming). Moderate at the
**base**. Aggressive up to the **high**. The upside column in the "What to do" tables is the scenario value
against today's price, with the Monte Carlo band quoted once.

## Seeing the sensitivity instead of trusting one number

The same script prints a grid of the base value for growth five points lower and higher and the discount
rate one and a half points lower and higher. Quote the grid's corners when the view says the value is
fragile. The Monte Carlo band is the same idea with the inputs drawn at random inside their ranges.

## The reverse DCF

`dcf.py` solves for the revenue growth that makes the base-case value equal today's price (margin, discount
and terminal at their base). Read it against the history: "the price assumes 14% a year for five years;
the company grew 5% a year over the last five [S..]". When no growth under 100% a year reaches the price,
the line says so.

## The P/E cross-checks

- **Trailing P/E** = price ÷ the last four quarters' diluted EPS from the filings (annual EPS when the
  quarters are missing). Not applicable when EPS is zero or negative; the script says so with the reason.
- **Its own range**: the trailing P/E at each quarter end over five years, as min, median and max. A P/E
  near the top of its own range with a DCF below price is "against", strength 3; a P/E near its own low
  with a DCF below price is "neutral", and the view says the two methods disagree and why.
- **Peers**: the median trailing P/E of the stocks stored in the same industry (needs `sec.py` and
  `yahoo.py` on the peers first); fewer than two peers → not applicable.
- **Also printed**: price to free cash flow and enterprise value to operating income, from the latest year.
- The implied values (EPS × median own P/E, EPS × peers' median) are stored as `pe_range` and `pe_peers`
  rows beside the DCF rows, so the answer can show "worth x by its own history, y by its peers, z by the DCF".

Multiples say what the market pays for these earnings; the DCF says what the earnings are worth if the
assumptions hold. Neither is the answer alone, and a fund has neither.
