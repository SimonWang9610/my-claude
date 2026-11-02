# Short-term lens — weeks to months, labelled, never a gate override

Applies when the question's horizon is under a year or ambiguous. `momentum.py` computes the inputs,
`score.py` assembles the block. The output states the base rates, because the primary evidence for
short-horizon predictability is modest, cross-sectional and regime-dependent. Verification status per
source: research/2026-10-14-pins.md ("Short-term lens").

**ST1 Trend state (description, not an edge).** Test: price above the 200-day average and the 50-day
above the 200-day → `trend up`; below both → `trend down`; else `no trend`. Inputs `momentum.ma50`,
`ma200`. Source: moving-average rules go back to Brock, Lakonishok and LeBaron (1992), Journal of Finance
47(5) [UNVERIFIED primary]; Sullivan, Timmermann and White (1999), Journal of Finance 54(5), discussion
paper text VERIFIED: after adjusting for data snooping, "scant evidence that technical trading rules were
of any economic value during the period 1987-1996". Why kept: the state describes where the price sits
relative to its own history, which the holdings answer needs. Not this: a crossover inside a 1% band
(`no trend`); any claim that the state predicts returns.

**ST2 Time-series momentum.** Test: 12-month return skipping the latest month (`return_12m_skip_1m`) > 0
→ positive. Source: Moskowitz, Ooi and Pedersen (2012), Journal of Financial Economics 104(2), VERIFIED:
"the past 12-month excess return of each instrument is a positive predictor of its future return", with
"strong return continuation for the first year and weaker reversals for the next 4 years"; results are for
58 futures contracts, not single stocks. Cross-sectional stock evidence: George and Hwang (2004) replicate
the 6-month winner-minus-loser spread at 0.48% per month (t = 2.35), January-heavy, VERIFIED. Caveat
line in the output: "single-stock, after-cost evidence is weaker than these portfolio results". Not this:
a 1-month return (reverses; the sources skip it).

**ST3 Nearness to the 52-week high.** Test: `pct_from_52w_high` within 5% → `near high`. Source: George
and Hwang (2004), Journal of Finance 59(5), VERIFIED: "Nearness to the 52-week high dominates and improves
upon the forecasting power of past returns"; 0.45% per month winner-minus-loser, no long-run reversal.
Caveat: a cross-sectional spread, equal-weighted, sample to 2001. Not this: a new high reached on a
takeover announcement (event, not momentum).

**ST4 Momentum-crash regime.** Test: SPY cumulative 24-month return < 0 and `realized_vol_30d` >
1.5 × `realized_vol_1y` → `crash regime`. Source: Daniel and Moskowitz, NBER WP 20439 (2014; JFE 2016),
VERIFIED draft: momentum crashes "occur in 'panic' states - following market declines and when market
volatility is high - and are contemporaneous with market rebounds". Why: in this regime ST2 and ST3
have historically reversed violently; the output says so and lowers the short-term stance to `no trend`.
Not this: a single-stock drawdown while the market is calm.

**ST5 Volatility regime.** Test: `realized_vol_30d` versus `realized_vol_1y` → `calm` (< 0.8×), `normal`,
`stressed` (> 1.5×). Source: this standard's bands. Why: sizing and trigger distances scale with
volatility.

**ST6 Implied move.** Test: `options.implied_move_pct` = ATM implied volatility × √(calendar days / 365) to
the expiry after the horizon end; reported as a one-standard-deviation dollar range. Source: the formula
is market convention (SECONDARY; day count fixed at 365 and labelled); Carr and Wu, "Variance Risk
Premia" (2004 draft; RFS 2009), VERIFIED draft: implied variance exceeds realized on average ("the mean
(log) variance risk premia are negative for all of the stock indexes and for most of the individual
stocks"), so the implied range is upper-biased. Data secondary (Yahoo).

**ST7 Events inside the horizon.** Test: next earnings date, any 8-K Item 2.02 or 8.01 in the window, the
next 10-K. Source: Bernard and Thomas (1989), Journal of Accounting Research 27 [UNVERIFIED]: post-
earnings-announcement drift of about 60 days in the direction of the surprise. Caveat: the surprise is
unknown in advance; the lens lists dates, never a direction.

**ST8 Relative strength.** Test: 6-month return minus SPY's and minus the sector ETF's
(`rel_strength_spy_6m`, `rel_strength_sector_6m`). Source: the cross-sectional momentum literature above
(George and Hwang 2004, VERIFIED, for the spread magnitude). Caveat: inputs are secondary (Yahoo).

## Short-term stance

`trend up` when ST1 is `trend up` and ST2 positive and ST4 is not `crash regime`; `trend down` when ST1 is
`trend down` and ST2 negative; otherwise `no trend`. The block ends with the base-rate line: "Short-horizon
signals describe the recent past. The verified sources report portfolio spreads of about half a percent
per month, January-heavy, with violent reversals after market declines. A failed gate overrides this
lens." With holdings: `trend down` and price above the sell zone → the long-horizon `trim or sell`
stands; `trend up` and price above the sell zone → the lens suggests a trailing trigger at the 50-day
average rather than an immediate sale, labelled as the lens's suggestion, not the standard's.
