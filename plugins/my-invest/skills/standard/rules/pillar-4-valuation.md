# Pillar 4 — Valuation and margin of safety (20 points, 5 items)

All fair values come from `metrics.valuation` per [valuation.md](../references/valuation.md).

**4.1 Margin of safety.** Test: last price ≤ base fair value today × (1 − margin of safety). Inputs
`price.last`, `metrics.valuation.buy_zone_below`. Source: Graham, Security Analysis (1934) and The
Intelligent Investor for the principle (UNVERIFIED wording); the default 30% is this standard's. Why:
the gap between price and value is the only protection against being wrong about value. Not this: a
price inside the margin because the bear and base values have collapsed toward it (check 4.2).

**4.2 Not above the bull case.** Test: last price ≤ bull fair value today. Inputs
`metrics.valuation.fair_value_today.bull`. Source: this standard. Why: paying more than the most
optimistic cited scenario leaves no scenario in which the owner wins. Not this: a bull value that is
`null` because owner earnings are negative (then `n/a`; gate G5 handles the rest).

**4.3 Market expects no more than the record.** Test: implied growth at price ≤ base scenario growth.
Inputs `metrics.valuation.implied_growth_at_price`, `scenarios.base.g`. Source: the implied-growth
construction in valuation.md (the name "reverse DCF" is practitioner usage, not Damodaran's). Why: if
the price already assumes faster growth than the business has shown, the owner is paying for a
forecast. Not this: a base `g` capped at 0 for a shrinking firm (then any positive implied growth
fails — correct).

**4.4 Owner earnings beat the bond.** Test: owner-earnings yield (owner earnings ÷ market cap) ≥
10-year Treasury yield. Inputs `metrics.owner_earnings.yield`, `macro.dgs10`. Source: Buffett 1986
for owner earnings (VERIFIED); the Treasury comparison is this standard's. Why: an equity whose cash
yield trails the risk-free rate needs growth to justify itself, and growth is the uncertain part.
Not this: a yield computed from a maintenance-capex estimate — allowed here (labelled), never in a gate.

**4.5 Graham number.** Test: last price ≤ √(22.5 × three-year average EPS × book value per share).
Inputs `metrics.graham_number`. Source: Graham (1973) ch. 14, "the product of the multiplier times the
ratio of price to book value should not exceed 22.5" (UNVERIFIED wording). `n/a` when EPS or book value
per share is ≤ 0. Why: a defensive ceiling that caps paying for both earnings and assets at once.
Not this: asset-light compounders with tiny book value — they fail the test by construction; report
0 and say why in the open questions rather than widening the formula.
