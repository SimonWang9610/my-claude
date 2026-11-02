# Holdings — what the question may state and what holdings.json holds

Accepted inline forms (any order, several positions, one or more tickers):
"I have 120 AAPL at $150 in my TFSA", "200 shares of GOOGL, average cost 135, non-registered", "RRSP: 50 AAPL @ 180".
Account types: `RRSP` (also RRIF, LIRA → treated as RRSP), `TFSA` (also FHSA), `NONREG` (non-registered, taxable,
margin, cash). Currency of the cost: USD unless the question says CAD. Optional: a marginal tax rate ("my marginal
rate is 43%"), a holding period or target date, and prices to evaluate ("what if it hits 400").

```jsonc
{ "ticker": "AAPL", "as_of": "2026-10-14", "currency": "USD",
  "positions": [ { "account": "TFSA", "shares": 120, "avg_cost": 150.0 } ],
  "marginal_rate": 0.43,                       // null when not stated
  "eval_prices": [400.0],                      // prices the question named
  "horizon_end": null }                        // ISO date when a holding period was named
```

`holdings.py` parses the question text (or takes `--json`), writes this file to the store, and prints the
outcome and tax tables as JSON for `report.py`. Nothing about the accounts is stored beyond this file, and
the user can delete it. Tax rules and their citations: [tax-ca.md](../../standard/references/tax-ca.md).
