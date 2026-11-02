# Action matrix — what the model says to do, at which price, by when

Computed by `score.py`; the skill adds no number. Every cell is a model output and the answer says so once.

## Long-horizon rows (one per horizon h ∈ {1, 2, 5, 10})

| Column | Rule |
|---|---|
| bear / base / bull value at h | `metrics.valuation.by_horizon[h]` |
| implied CAGR at h per scenario | `(V_h / price)^(1/h) − 1` |
| verdict | base CAGR ≥ `r_base` + 2 pp → `attractive`; within ±2 pp of `r_base` → `fair`; below → `unattractive` |

## Stance cell (today's price versus zones; any failed gate → `avoid / exit`)

| Price today | Not holding | Holding |
|---|---|---|
| below buy zone | `accumulate` | `add` |
| buy zone to base value | `wait for the buy zone` | `hold` |
| base value to sell zone | `avoid at this price` | `hold, do not add` |
| above sell zone | `avoid` | `trim or sell` |

## Triggers and timing

- Price triggers: the buy-zone and sell-zone boundaries and the base value.
- Time triggers: the next 10-K (last 10-K `filed` + 1 year), the next earnings date
  (`options.next_earnings_date`, secondary), and the end of any holding period the question named.
- Gates that depend on a filing (G1, G2, G4) are re-checked at each time trigger.

## Holdings rows (when `holdings.json` exists)

Per account: shares, average cost, current value, gain or loss at the current price, at each zone
boundary, at the base value and at every price the question named; then the tax lines from
`holdings.py` per `tax-ca.md`. The sell line compares cost to the zones: price above the sell zone →
`trim or sell: the model's value is realised`, whatever the cost; price below cost → the loss is stated
and the stance applies unchanged (the model does not anchor on cost).

## Short-term block (only when the question is short-horizon or ambiguous)

From `lens-short-term.md`: trend state, momentum, volatility regime, implied move to the next expiry,
events inside the horizon, relative strength; a `short-term stance` (`trend up` / `trend down` / `no trend`)
followed by the lens's base-rate line (`short_term.caveat`) and the rule that it never overrides a failed gate.
