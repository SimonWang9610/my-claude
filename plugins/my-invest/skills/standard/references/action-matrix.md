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

## Sizing frames and order levels (`size.py`) — this standard's own, labelled so

No published source sizes a trim for a retail holder, so the frames are plain arithmetic on the user's
own positions and are always shown together, with the advisor's pick marked:

| Frame | Shares to sell |
|---|---|
| cap at 15%, 12.5%, 10% of the accounts in scope | (position value − cap × total) ÷ price, rounded down |
| sell the gain, keep your cost invested | gain ÷ price, rounded down; what is kept is worth about the cost |
| recover your cost, keep the gain as house money | cost ÷ price, rounded up; what is kept is the gain |

Look-through: the stock's weight also counts the user's funds (fund position value × the stock's weight
in the fund, from `fund.json`), so a 15% outright line can be 20% in truth. Sell from taxable accounts
last; between registered accounts RRSP before TFSA (TFSA growth stays tax-free for good; an RRSP is taxed
on withdrawal anyway). A failed gate or an `exit` cell is not sized: the answer is sell.

Order levels, each named by its rule: the 50-day and 200-day averages (trailing trigger, pullback
entry), the 52-week high and low (a limit into strength; the floor where the trend reading flips), the
options-implied one-standard-deviation range to the first monthly expiry after the horizon (the upper
edge for a limit sell, the lower for a limit buy), and the next earnings date with its implied move.
