# Outlook — where the price is likely to go, by horizon, with the evidence behind each number

The forward view a professional gives: not one intrinsic value, but scenarios whose inputs are stated,
compared with the return the risk demands, and checked against the model's own past errors. `metrics.py`
computes the block (`metrics.outlook`), `score.py` turns it into verdicts and recommendations, the answer
leads with it. The conservative owner-earnings value (valuation.md) stays as one lens, labelled "a strict
value investor's price", never as the headline.

## 1. Expected return decomposition (horizons of a year or more)

For each requested horizon h and scenario s ∈ {bear, base, bull}:

```
price_h = EPS_0 × (1 + g_s)^h × multiple_h,s
expected yearly return_s = (price_h / price_0)^(1/h) − 1 + shareholder yield
```

Sources (pinned in research/2026-10-14-pins.md, "Outlook"): the decomposition is Bogle and Nolan (2015),
"Occam's Razor Redux", Journal of Portfolio Management 42(1): return = "the sum of the current dividend
yield, the expected annual growth in nominal earnings per share" and "the expected change in the
price-to-earnings multiple" (VERIFIED via the CFA Institute digest; the 1991 article is UNVERIFIED).
Multiple mean reversion: Campbell and Shiller (2001), NBER WP 8221, ten-year returns regressed on the
price-smoothed-earnings ratio, R² 40% (in-sample); GMO quarterly letter 2Q 2017: valuations "revert to
around 16 times normalized earnings over 7 years". Pricing versus valuation and the caution on analyst
growth: Damodaran, 2015 blog post and "Growth Rates and Terminal Value" slides (consensus forecasts
"tend to be highly correlated across analysts"). The output's method line names these and says the
accuracy figures are in-sample.

| Input | bear | base | bull | Evidence |
|---|---|---|---|---|
| EPS_0 | diluted EPS, latest fiscal year, split-adjusted | same | same | facts S1 |
| g (earnings growth) | lower of: 5-year EPS CAGR − 3 pp, consensus next-year growth − 3 pp, 0% floor | blend: ½ × 5-year EPS CAGR + ½ × consensus next-2-year growth; capped at 25% | higher of the two + 3 pp, capped at 30% | facts S1 (history), consensus (secondary) |
| multiple_h | the stock's own 10-year P/E 25th percentile (or peer median when lower) | drifts linearly from today's P/E to the 10-year median by year 10 | max(today's P/E, 75th percentile) held for two years, then drifting to the 75th percentile by year 10 — even the bull case mean-reverts over long horizons | metrics.multiples (from S1, S3) |
| shareholder yield | dividends + buybacks ÷ market cap, latest year | same | same | metrics.shareholder_yield |

When EPS is ≤ 0, use price-to-sales with sales growth and the 10-year P/S range; say so. When fewer than
five years of multiples exist, use what exists and lower confidence.

**Verdict per horizon**: base expected return versus the required return `r_base` (Treasury + equity risk
premium): ≥ r + 2 pp → `attractive`; within ±2 pp → `fair`; < r − 2 pp → `expensive`. The spread
bear-to-bull is the uncertainty and feeds confidence.

## 2. The next months (horizons under a year)

Not an earnings model; a probable range: trend state and momentum (lens-short-term.md ST1–ST4), the
options-implied one-standard-deviation range to the expiry after the horizon (ST6), scheduled events
inside the horizon (earnings, 10-K, product events) (ST7), consensus revisions in the last 90 days
(direction of EPS estimate changes, secondary), and the regime flag (ST4). Output: `range_1sd` in dollars
at the horizon, `trend`, `events`, `revisions`, and the base-rate line. Never a point forecast.

## 3. Consensus (secondary, from Yahoo via yfinance)

Mean, median, high and low analyst price targets and their count; EPS estimates for the current and next
fiscal year; revenue growth estimates; recommendation mean; 30-day estimate revisions. Shown as a row
beside the scenarios and used in g; never as the verdict. The row carries its base rate: Bradshaw, Brown
and Huang (2013), Review of Accounting Studies 18(4), found "only 38% of target prices are met" at the
twelve-month horizon and 64% at some point within it (abstract, relayed). Revisions: Chan, Jegadeesh and
Lakonishok (1996), Journal of Finance 51(5): "Security analysts' earnings forecasts also respond
sluggishly to past news". When consensus is unavailable the block says so and the base g uses history alone.

## 4. Calibration — the model's own record on this stock

For the fiscal year five years back: the strict owner-earnings fair value with that year's inputs
(valuation.md method, today's rate and premium) versus the price then, and the realised yearly return
since; and what the expected-return decomposition's base case would have forecast then versus realised.
Output: `calibration` with both errors in plain words ("five years ago the strict model called Apple 2.1×
overvalued; it returned 19.7% a year since"). This line always appears beside the strict value when the
price is above its sell line, so the reader can weigh the model.

## 5. Recommendation logic (score.py `action.recommendation`)

| Situation | Base expected return at the reference horizon (the user's horizon; 5 years when none was stated) | Trend (ST1) | Recommendation |
|---|---|---|---|
| holding | ≥ r + 2 pp | any | hold; add on pullbacks to the 50-day average |
| holding | within ±2 pp | up / none | hold; re-check at the next event |
| holding | within ±2 pp | down | hold, consider trimming to target weight |
| holding | < r − 2 pp | up | trim into strength; trailing trigger at the 50-day average |
| holding | < r − 2 pp | down / none | trim or sell |
| not holding | ≥ r + 2 pp | up / none | accumulate (staged entries) |
| not holding | ≥ r + 2 pp | down | wait for the trend to turn; first entry at the 200-day average |
| not holding | within ±2 pp | any | buy only on pullbacks: 50-day average, or 10% below today |
| not holding | < r − 2 pp | any | wait; the strict value and the pullback levels are the entry map |
| any | gate failed | any | avoid / exit |

Every cell carries the numbers that produced it (expected return, required return, trend, levels) and
the one-line "strict value investor's price" so the reader sees both views.
