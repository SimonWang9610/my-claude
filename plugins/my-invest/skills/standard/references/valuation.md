# Valuation model — fair value by horizon, zones, implied growth, confidence

Computed once per `facts.json` by `metrics.py`; the scorer reads, never recomputes. Every parameter
below is published here and stored under `metrics.valuation.params`. Where a choice is this standard's
own, it says so; tune after ten dossiers (DECISIONS D-8, D-12).

## Cash flow basis

Owner earnings per Buffett (1986 letter [1]): reported earnings + depreciation, depletion, amortization
and other non-cash charges − maintenance capital expenditure. Maintenance capex is "a guess" in the
source; the plugin's estimate is `min(capex, da)` and is labelled `estimate` wherever it appears.
Starting flow `CF_0` = mean of the last three fiscal years' owner earnings (this standard's smoothing
choice). Cross-check: free cash flow = operating cash flow − capex; the bear scenario uses the lower of
the two.

## Discount rate

`r_base` = 10-year Treasury yield (FRED DGS10 [2]) + implied equity risk premium (Damodaran, trailing
12-month with adjusted payout [3]; a dated constant in `macro.py` carried as `macro.erp`; `metrics.py`
falls back to its own copy of the constant and records `params.erp_source`; `--erp` overrides).
No beta: the model prices every company at market-average risk and lets the bear scenario carry the
uncertainty (`r_bear = r_base + 2 pp`, this standard's choice). Intrinsic value is "the discounted value
of the cash that can be taken out of a business during its remaining life" (Buffett 1994 [4]).

## Growth scenarios

Explicit years 1–10, then a terminal value. Years 1–5 grow at `g`; years 6–10 fade linearly to the
terminal rate. Terminal growth `g_t = min(2.5%, DGS10)`: stable growth "should not exceed the
riskless rate" (Damodaran [5]); the 2.5% ceiling is this standard's.

| Scenario | g (years 1–5) | r | flow basis |
|---|---|---|---|
| base | `clamp(5-yr owner-earnings CAGR, 0%, 15%)`, further capped at sustainable growth = `ROIIC_5y × reinvestment rate` when ROIIC is available, else at 10% | r_base | owner earnings |
| bear | base ÷ 2 | r_base + 2 pp | min(owner earnings, FCF) |
| bull | min(base + 3 pp, 20%) | r_base | owner earnings |

Reinvestment rate = `1 − (dividends + buybacks) / owner earnings`, clamped to [0, 1].

## Values

- Equity value today `V_0` = Σ PV(CF_t, t = 1..10) + PV(terminal) + net cash (cash − short-term debt −
  long-term debt), per diluted share. The net-cash adjustment is this standard's simplification;
  owner earnings are already after interest.
- Value at horizon h ∈ {1, 2, 5, 10}: `V_h = V_0 × (1 + r)^h − Σ_{t ≤ h} CF_t × (1 + r)^(h − t)`, the value of
  the remaining flows at year h. It is the price path consistent with the scenario, not a forecast of
  the market price.
- Buy zone: price below `V_0(base) × (1 − margin of safety)`; margin of safety from `userConfig`
  (default 30%, this standard's choice; Graham names no single figure). Sell zone: price above
  `V_0(bull)`.
- Implied growth at price: the `g` (same shape) for which the base model's `V_0` equals the last price;
  bisection on [−20%, 40%]. Compared with base `g` in pillar 4.

## Confidence (0–100)

`confidence = round(100 × (0.5 × coverage + 0.3 × agreement + 0.2 × freshness))`

- coverage = scored items with evidence ÷ applicable items (gates and pillars; `n/a` excluded); the
  scorer counts it, since it depends on the scoring.
- agreement = `clamp(1 − (V_0(bull) − V_0(bear)) / V_0(base), 0, 1)` — `metrics.valuation.agreement`.
- freshness = 1 when the price is at most one trading day old and no 10-K newer than the one the
  fundamentals use has been filed; 0.5 when a newer 10-K exists; 0 when the price is older than five
  trading days — `metrics.freshness`. Quarterly reports do not count: the model is annual.

Weights are this standard's opinion and are stated in the Scorecard next to the number.

## Sources

[1] https://www.berkshirehathaway.com/letters/1986.html · [2] https://fred.stlouisfed.org/series/DGS10 ·
[3] https://pages.stern.nyu.edu/~adamodar/New_Home_Page/home.htm (4.20%, as of 2026-10-01 at last check) ·
[4] https://www.berkshirehathaway.com/letters/1994.html ·
[5] https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/stablegrowthrate.htm
