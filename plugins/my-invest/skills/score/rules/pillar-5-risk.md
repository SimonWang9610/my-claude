# Pillar 5 — Risks and red flags (20 points, 5 items)

**5.1 Accruals.** Test: Sloan accrual ratio ≤ 0.05 of average total assets. Inputs
`metrics.accrual_ratio` (method: (ΔCA − ΔCash) − (ΔCL − ΔSTD − ΔTaxes payable) − D&A, ÷ average total
assets). Source: Sloan (1996), TAR 71(3), pp. 293–294 (VERIFIED definition and scaling); the 0.05 cut is
this standard's (Sloan ranks into deciles). Why: earnings built from accruals rather than cash
revert; Sloan's highest-accrual decile underperformed. Not this: banks and insurers (`n/a`, excluded
in the source for data reasons).

**5.2 Beneish manipulation index.** Test: M-score ≤ −1.78 using the eight-variable model with
coefficients −4.84, 0.920 DSRI, 0.528 GMI, 0.404 AQI, 0.892 SGI, 0.115 DEPI, −0.172 SGAI, 4.679 TATA,
−0.327 LVGI. UNVERIFIED: coefficients and the −1.78 cutoff come from secondary sources only (the 1999
FAJ text is paywalled; some secondaries use −2.22). Inputs `metrics.beneish`. Source: Beneish (1999),
FAJ 55(5), DOI 10.2469/faj.v55.n5.2296. `n/a` for financials, REITs and utilities. Why: the index flags the statement
patterns that preceded discovered manipulations. Not this: a high SGI alone from honest fast growth —
the whole index decides, and this item is never a gate.

**5.3 Leverage against cash earnings.** Test: net debt (short + long-term debt − cash) ÷ owner
earnings ≤ 3. Inputs `metrics.net_debt_to_owner_earnings`. Source: this standard. `n/a` when owner
earnings ≤ 0 (gate G5 territory) or net debt ≤ 0 (score 1). Why: three years of owner earnings to
clear the debt keeps a downturn from becoming a refinancing event. Not this: a utility or REIT whose
model carries structural leverage (`n/a` by sector class).

**5.4 Internal control.** Test: the latest 10-K Item 9A reports no material weakness. Evidence-required:
the researcher cites the 10-K URL and quotes ≤15 words. Source: the filing (primary). Why: a material
weakness means the numbers every other item uses were produced by a control system management itself
calls deficient. Not this: a disclosed remediation completed within the year (score 1, note it).

**5.5 Customer concentration.** Test: no single customer accounts for 10% or more of revenue per the
latest 10-K. Evidence-required: the researcher cites the disclosure, or the 10-K's statement that no
customer exceeds 10%, or — because Regulation S-K Item 101(c) and ASC 280-10-50-42 require the
disclosure whenever a customer reaches 10% of revenue — the researcher's grep of the full filing
extract finding no such disclosure (cite the filing and state the grep). Source: the filing (primary);
https://www.ecfr.gov/current/title-17/section-229.101. Why: a decade thesis cannot rest on one
buyer's purchasing decision. Not this: a receivables concentration note (that is credit exposure, not
revenue; report it under risks); a government-agency customer in a defence contractor — still 0.
