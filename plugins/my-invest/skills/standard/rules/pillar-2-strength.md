# Pillar 2 — Financial strength (20 points, 5 items)

**2.1 Piotroski F-score high.** Test: F_SCORE ≥ 8 for the latest fiscal year (its nine signals use the
latest two years of statements plus the prior year's beginning assets). Inputs `metrics.piotroski`. Source: Piotroski (2000), JAR 38 Supplement, pp. 7–12 (VERIFIED): ROA, CFO,
accrual and asset turnover scaled by beginning-of-year total assets; leverage by average total assets;
F_ACCRUAL = 1 when CFO > ROA; EQ_OFFER = 1 when no common equity was issued; high group = 8 or 9.
Why: nine binary signals from two years of statements; the author's high group outperformed the low
group within value stocks. Not this: a 7 (report the number; it is not "high" in the source); a firm
with no prior-year data (`n/a`, not 0).

**2.2 Altman solvency.** Test: manufacturers — original Z ≥ 2.99 (UNVERIFIED cutoff; 1.81 is the
verified distress bound used by gate G3); non-manufacturers — Z'' ≥ 2.60 (coefficients VERIFIED from
Altman 2000: 6.56 WC/TA + 3.26 RE/TA + 6.72 EBIT/TA + 1.05 BVE/TL, no constant; the 2.60 zone is
UNVERIFIED). Inputs `metrics.altman`. `n/a` for financials, REITs, utilities. Why: the discriminant
scores summarise liquidity, cumulative profitability, earning power and leverage in one number.
Not this: adding the +3.25 emerging-market constant to a US company's Z''.

**2.3 Current ratio.** Test: current assets ÷ current liabilities ≥ 2. Inputs `fundamentals.annual[0]`.
Source: Graham, The Intelligent Investor (1973) ch. 14 (UNVERIFIED wording; value consistent across
secondaries). Why: Graham's defensive floor against a liquidity squeeze. Not this: a subscription
business with large deferred revenue in current liabilities and negative working capital by design —
score 0 but note it as a model limitation in open questions.

**2.4 Debt covered by working capital.** Test: long-term debt ≤ net current assets (current assets −
current liabilities). Inputs `fundamentals.annual[0]`. Source: Graham (1973) ch. 14 (UNVERIFIED
wording). Why: debt that working capital can retire cannot force a distressed refinancing. Not this:
`n/a` when long-term debt is zero and net current assets are negative (nothing to cover).

**2.5 Ten years without a loss.** Test: no fiscal year with negative net income in the last ten.
Inputs `metrics.earnings_history.loss_years_10y`, `years_available`. Source: Graham (1973) ch. 14
(UNVERIFIED wording). `n/a` when fewer than ten years are available; say how many. Why: earnings
stability through at least one cycle is the cheapest durability test. Not this: a loss caused solely
by a non-cash goodwill impairment while owner earnings stayed positive — still 0, but say so.
