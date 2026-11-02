# Pillar 1 — Business quality and moat (20 points, 6 items)

**1.1 Returns above the cost of capital.** Test: ROIC ≥ `r_base` in at least four of the last five
fiscal years, computed both with and without goodwill and intangibles; score 1 when either series
passes and name which. Inputs `metrics.roic`, `metrics.valuation.params.r_base`. Source: Mauboussin and
Callahan 2013 and 2014 (UNVERIFIED page-level, PDFs unreadable); "both ways" from Mauboussin 2016
interview. Why: value is created only when returns exceed the cost of the capital employed; four of
five years separates a franchise from a cycle peak. Not this: a single trough year in a cyclical, or
ROIC depressed only by a recent acquisition's goodwill when the ex-goodwill series passes.

**1.2 Incremental returns.** Test: ROIIC over five years (ΔNOPAT ÷ Δinvested capital) > `r_base`.
Inputs `metrics.roiic_5y`. Source: this standard's formulation; the concept of competitive advantage
period from Mauboussin (UNVERIFIED). Why: a company that reinvests at high incremental returns compounds;
one that cannot should return the cash instead. Not this: a shrinking capital base with rising NOPAT
(negative denominator → `n/a`, note it).

**1.3 Gross profitability.** Test: (revenue − COGS) ÷ total assets ≥ 0.33. Inputs
`metrics.gross_profitability`. Source: Novy-Marx (2013), JFE 108(1), for the factor; the 0.33 cutoff is
this standard's choice (the paper ranks, it does not cut). Why: gross profitability predicts returns
about as well as book-to-market and is hard to manipulate. Not this: banks, insurers, REITs (`n/a`).

**1.4 Defended margins.** Test: gross margin in the latest year ≥ gross margin five years earlier
minus 2 percentage points. Inputs `metrics.gross_margin_5y_change`. Source: this standard. Why: a
moat shows up as pricing power; margins that erode under competition are the first visible crack.
Not this: a documented mix shift the 10-K names (hardware → services), cited by the analyst.

**1.5 Moat source with evidence.** Test: the dossier's Business and moat section cites at least one
passage (10-K Item 1 or 7, IR document) that evidences a Morningstar moat source — intangible assets,
switching costs, network effect, cost advantage, efficient scale — with a URL. Source: Morningstar
equity research methodology (2017 PDF, see research notes). Why: a moat name without a filing passage
is the analyst's feeling. Not this: a sentence from a blog or a post; a generic "strong brand"
without the passage.

**1.6 Durable demand.** Test: revenue five-year CAGR > 0 and no two consecutive annual revenue
declines in the last ten years. Inputs `metrics.revenue_cagr_5y`,
`metrics.revenue_declines_consecutive_10y`. Source: this standard. Why: a decade horizon needs a
business whose demand does not fall two years running. Not this: a divestiture year the 10-K names.
