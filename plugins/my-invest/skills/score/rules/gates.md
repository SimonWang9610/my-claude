# Gates — any `fail` forces tier `pass` and stance `avoid`

Each gate is `pass / fail / n/a` with its markers. A gate rests only on a primary-verified source or on
arithmetic; estimates never feed a gate. Items with unverified thresholds live in the pillar cards.

**G1 Bankruptcy or receivership.** Fail when the filings index shows a Form 8-K with Item 1.03 within
the last three years. Inputs `filings_recent` (`news.py --since 1095`). Source: SEC Form 8-K, Item 1.03
"Bankruptcy or Receivership", https://www.sec.gov/files/form8-k.pdf. Why: the equity's claim is being
reorganised; no scorecard arithmetic survives that. Not this: a subsidiary's Chapter 11 disclosed under
Item 8.01 (note it under risks, do not fail the gate).

**G2 Restatement.** Fail on a Form 8-K Item 4.02 within three years. Inputs as G1. Source: SEC Form 8-K,
Item 4.02 "Non-Reliance on Previously Issued Financial Statements". Why: every pillar reads those
statements; the issuer itself says they were wrong. Not this: an immaterial revision disclosed inside a
10-K or 10-Q without an Item 4.02 (pillar 5 risk item instead).

**G3 Altman distress zone (manufacturers only).** Fail when original Z < 1.81 on the latest fiscal year
with current market cap. Inputs `metrics.altman` (model `Z`). Source: Altman (2000) restating Altman
(1968), lower bound 1.81 advocated by the author; coefficients 1.2 WC/TA + 1.4 RE/TA + 3.3 EBIT/TA +
0.6 MVE/TL + 1.0 Sales/TA. `n/a` for non-manufacturers, financials, REITs and utilities (the Z'' zones
are not primary-verified; see pillar 2). Why: the model was built to separate bankrupt from solvent
manufacturers a year ahead. Not this: a low Z driven by a temporary market-cap collapse while EBIT/TA
and WC/TA are healthy — still fail (the author did not carve it out), but say so in the open questions.

**G4 Going-concern paragraph.** Fail when the auditor's report in the latest 10-K contains a
going-concern explanatory paragraph. Evidence-required: the researcher cites the report's URL and
quotes ≤15 words. Source: the filing itself (primary). Why: the auditor doubts the entity survives
twelve months. Not this: the standard "critical audit matters" section, or risk-factor boilerplate
about liquidity.

**G5 Negative owner earnings.** Fail when owner earnings (Buffett 1986 definition, maintenance capex
estimate replaced by full capex for this gate so no estimate feeds it) were negative in three or more
of the last five fiscal years. Inputs `fundamentals.annual[0..4]`. Source:
https://www.berkshirehathaway.com/letters/1986.html. `n/a` for financials. Why: a business that cannot
fund its own maintenance has no cash for owners to discount. Not this: one or two investment-heavy
years in a company with positive cumulative five-year owner earnings.

**G6 Serial dilution.** Fail when split-adjusted diluted shares rose in each of the last three fiscal
years and by more than 10% cumulatively. Inputs `metrics.dilution_5y` (`rising_years_last3`,
`value`), `price.splits`. Source: arithmetic. Why: per-share owner earnings shrink by the dilution
unless the new capital earns above its cost, which three straight years of issuance rarely shows.
Not this: a stock split (adjusted away), a single acquisition year, or share counts rising below 10%
cumulatively from option exercise.
