# The six dimensions: what each answers, from what, and what earns a stance

| Dimension | Answers | Data, grade, script | Look at | Horizon |
|---|---|---|---|---|
| fundamentals | Is the business getting better or worse, and can it carry its debt? | SEC XBRL facts, primary, `sec.py` (`fundamentals_annual`, `fundamentals_quarterly`) | revenue and operating-income growth over 3 and 5 years; operating margin trend; free cash flow (operating cash flow minus capex) and its conversion from net income; net debt vs operating cash flow; diluted share count trend; buybacks and dividends vs free cash flow | 1 to 5 years |
| valuation | What is a share worth under three sets of assumptions, what growth does the price already assume, and what does the market pay for these earnings against the past and the peers? | fundamentals, prices, macro (DGS10), stats (beta), derived, `dcf.py` | DCF value per share low, base, high and the Monte Carlo p10 to p90; the sensitivity grid; the implied growth from the reverse DCF against the history; trailing P/E against the stock's own five-year range and the peers' median; price to free cash flow; EV to operating income | 3 to 5 years |
| statistics | How has the price behaved, and where do the levels sit? | prices, secondary, `stats.py` | CAGR and total return 1, 3, 5 years vs SPY; volatility; max drawdown; beta; trend (close vs 200-day, 50- vs 200-day); distance from the 52-week high; the 3-month one-standard-deviation range; next earnings date | 3 to 12 months |
| macro | Do rates, inflation, growth and policy help or hurt this name or sector now? | FRED, primary, `fred.py`; policy, trade and geopolitics from cited pages, secondary | 10-year yield level and 1-year change (the discount rate's anchor); 10y-2y spread; CPI trend; Fed funds; unemployment; GDP; VIX; the policy items that touch the sector (tariffs, subsidies, sanctions, regulation) | 6 to 24 months |
| industry | Is the industry growing, consolidating, regulated or being displaced, and how are the peers priced? | cited pages, secondary; peers' fundamentals via `sec.py` | growth of the end market; share shifts; pricing power; capex cycle; regulation; up to `depth.peers` peers on growth, margin and valuation | 1 to 5 years |
| sentiment | Are news, posts and surveys leaning for or against, and is that already in the price? | news rows (lean set by the analyst), analysts' targets, VIX, secondary, `news.py`, `yahoo.py estimates` | the mean lean of the last `depth.news` items and what drove it; analysts' mean target vs price and how many analysts; recommendation mean; whether the price already moved on the news | 1 to 6 months |

## What earns a stance

- **for**: the figures point to a higher price over the dimension's horizon (growth and margins rising,
  value above price, trend up, rates falling for a long-duration name, industry expanding, lean positive
  and not yet priced in).
- **against**: the mirror image, or a deal-breaker in sight.
- **neutral**: mixed figures, or a reading that depends on one thing the analyst cannot verify.
- **strength**: 3 when the figures are large, consistent across windows and primary; 2 when clear but from
  one window or one secondary source; 1 when small, noisy or secondary only.

## What a view is not

Not a price target, not advice, not a repeat of another dimension. The valuation view does not restate growth
(that is fundamentals); sentiment does not restate the trend (that is statistics). Each view cites only
the sources it rests on, so the evidence part of confidence measures real coverage.
