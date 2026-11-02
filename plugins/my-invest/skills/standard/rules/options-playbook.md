# Options playbook — four operations, explained with the stock's own numbers

Educational, not advice: each suggestion shows how an option would work on this stock today, using
contracts from the live chain (secondary data, Yahoo) and the model's zones. `score.py` selects the
operations whose conditions hold and `report.py` renders them with the glosses below. Options can lose
the entire premium, selling calls caps the upside, and assignment can happen before expiry; every
rendering says so once.

## Contract selection (options.py `contracts`)

Expiry: the first monthly expiry at least 30 days out (the next one when the horizon is longer than its
days). Strikes: the listed strike nearest to each anchor — current price, buy zone, sell zone, price × 0.90,
price × 1.10. For each contract: type, strike, expiry, days, bid, ask, mid, last, open interest, implied
volatility; derived: premium per share (mid), premium as % of price, annualised % (premium ÷ price × 365 ÷
days), breakeven, and for puts the protection cost as % of position.

## Operations and when each applies

**O1 Covered call — "get paid to agree to sell at a price you already like".** You own at least 100 shares
and the model stance is `hold, do not add` or `trim or sell`. Sell one call per 100 shares at the strike
nearest the sell zone (or price × 1.10 when the sell zone is below the price). You receive the premium
now. Best case: shares called away at the strike plus the premium kept. Worst case: the stock falls (you
still own it; the premium softens the fall by its amount) or it rockets past the strike and you miss the
gain above it. Beginner notes: pick a strike you would be happy to sell at; the shares can be taken from you
any time before expiry; do it in a non-registered or TFSA account only if the broker allows (RRSP rules
vary; check).

**O2 Protective put — "insurance on a gain you do not want to lose".** You own shares with a large gain and
the stance is `trim or sell` or the short-term lens says `trend down`. Buy one put per 100 shares at the
strike nearest price × 0.90 for the expiry after your decision date. You pay the premium. Best case: the
price falls far below the strike and the put pays the difference. Worst case: the price does not fall and the
premium is lost (the cost of insurance, shown as % of the position). Beginner notes: insurance has a price
every time you renew it; compare the cost with simply selling part of the position.

**O3 Cash-secured put — "get paid to wait for your buy price".** You do not own the stock (or want more),
the stance is `wait for the buy zone` or `avoid at this price`, and a strike exists at or below the buy
zone. Sell one put at that strike and keep the cash to buy 100 shares. You receive the premium. Best case:
the stock stays above the strike and you keep the premium. Worst case: the stock falls far below the strike
and you must buy at the strike, now worth less (which is the price you said you wanted, minus the premium).
Beginner notes: the cash is locked until expiry; if the stock collapses you own it at the strike.

**O4 Long call — "a small bet that the price rises, with a known maximum loss".** Only when the price is at
or below the buy zone and no gate failed. Buy one call at the strike nearest the current price for the
expiry after the next earnings date. You pay the premium; that is the most you can lose. Best case: the
price rises well above the strike plus the premium. Worst case: the price stays below the strike and the
whole premium is lost, often even if the stock rises a little, because time decay eats the value. Beginner
notes: most long calls expire worthless; size it as money you can lose.

**Not now.** When no condition holds, the section says why in one line (for example: "price is above the
sell zone and you hold none, so there is no operation here except waiting"). A failed gate shows only O2
for existing holders and nothing else.

## Glosses used in the rendering

call · put · premium · strike · expiry · covered · assignment · time decay · breakeven — one plain line each,
printed under "Words used here" when the term appears.
