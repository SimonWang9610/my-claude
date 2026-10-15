# facts.json — the contract between scripts, the researcher and the report

One file per ticker at `<project>/data/stocks/<TICKER>/facts/facts.json`, rewritten by `facts.py` (incrementally); `series.json`, `scorecard.json`, `holdings*.json` and `last_run.json` sit beside it in `facts/`. Every figure-bearing object
carries `src` (an `S<n>` id resolving in `sources`) or, for derived values, `inputs`. `null` means not
available; the reason sits in `missing` (fetched fields) or a `reason` key beside the null (derived). Any
object may carry a `note` explaining a fallback.

```jsonc
{
  "ticker": "AAPL", "cik": "0000320193", "name": "Apple Inc.", "sic": "3571",
  "sector_class": "manufacturer",            // manufacturer | non-manufacturer | financial | reit | utility (SIC table below)
  "sector_etf": "XLK",                       // SIC → sector ETF table in market.py
  "retrieved": "2026-10-14T15:02:11Z",
  "changed": ["prices", "market"],           // groups whose content changed this run: prices, fundamentals, filings, macro, market, options; `reused` lists cached groups
  "sources": { "S1": { "class": "primary|secondary|derived|social", "what": "", "url": "", "as_of": "", "retrieved": "" } },
  "price": { "last": 0.0, "date": "", "high_52w": 0.0, "low_52w": 0.0, "shares_out": 0, "market_cap": 0.0,
             "ytd_return": 0.0, "return_1y": 0.0, "return_5y_cagr": 0.0, "return_10y_cagr": 0.0,
             "close_5y_ago": 0.0, "close_at": {}, "splits": [ { "date": "", "ratio": 0.0 } ], "src": "S3" },
  "fundamentals": {
    "annual": [ { "fy": 2025, "period_end": "", "form": "10-K", "filed": "", "accn": "",
        "revenue": 0, "cogs": 0, "gross_profit": 0, "sga": 0, "rd": 0, "operating_income": 0, "interest_expense": 0,
        "pretax_income": 0, "income_tax": 0, "net_income": 0, "eps_diluted": 0.0, "shares_diluted": 0,
        "ocf": 0, "capex": 0, "da": 0, "dividends_paid": 0, "buybacks": 0, "debt_issued": 0, "debt_repaid": 0, "equity_issued": 0,
        "total_assets": 0, "current_assets": 0, "cash": 0, "receivables": 0, "inventory": 0, "ppe_net": 0, "goodwill_intangibles": 0,
        "current_liabilities": 0, "st_debt": 0, "lt_debt": 0, "total_liabilities": 0, "equity": 0, "retained_earnings": 0,
        "taxes_payable": 0, "goodwill_impairment": 0, "src": "S1" } ],   // newest first, ≤10 fiscal years, USD
    "shares_history": [ { "fy": 2025, "shares_diluted": 0 } ],
    "concept_map": { "revenue": ["Revenues"], "sga": "sum: SellingAndMarketingExpense + GeneralAndAdministrativeExpense" },
    "missing": [ { "field": "", "fy": 0, "reason": "" } ]
  },
  "macro": { "dgs10": 0.0, "dgs10_date": "", "src": "S4", "erp": 4.2, "erp_date": "2026-10-01", "erp_src": "S5", "units": "percent" },
  "market": {                                // market.py; Yahoo = secondary, Bank of Canada = primary
    "spy":    { "return_1m": 0.0, "return_3m": 0.0, "return_6m": 0.0, "return_12m": 0.0, "return_24m": 0.0, "above_200d": true, "src": "S7" },
    "sector": { "etf": "XLK", "return_1m": 0.0, "return_3m": 0.0, "return_6m": 0.0, "return_12m": 0.0, "above_200d": true, "src": "S7" },
    "fx_usdcad": { "rate": 0.0, "date": "", "src": "S8" }   // https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json
  },
  "options": {                               // options.py; secondary; on failure the fields are null and `reason` says why. All ratios and returns are fractions
    "as_of": "", "expiry_used": "", "days_to_expiry": 0, "atm_iv": 0.0, "implied_move_pct": 0.0, "implied_move_abs": 0.0,
    "put_call_oi_ratio": 0.0, "put_oi": 0, "call_oi": 0, "max_pain": 0.0, "next_earnings_date": "", "src": "S9",
    "contracts": [ { "anchor": "price|buy_zone|sell_zone|down_10|up_10", "type": "call|put", "strike": 0.0, "expiry": "", "days": 0,
                     "bid": 0.0, "ask": 0.0, "mid": 0.0, "last": 0.0, "oi": 0, "iv": 0.0,
                     "premium_pct": 0.0, "annualized_pct": 0.0, "breakeven": 0.0, "protection_cost_pct": null } ]
  },
  "momentum": {                              // momentum.py from series.json and market; derived
    "return_1m": 0.0, "return_3m": 0.0, "return_6m": 0.0, "return_12m": 0.0, "return_12m_skip_1m": 0.0,
    "ma50": 0.0, "ma200": 0.0, "above_ma50": true, "above_ma200": true, "ma50_above_ma200": true,
    "pct_from_52w_high": 0.0,                // positive fraction: distance below the 52-week high
    "realized_vol_30d": 0.0, "realized_vol_1y": 0.0,
    "rel_strength_spy_6m": 0.0, "rel_strength_sector_6m": 0.0, "inputs": [] },
  "filings_recent": [ { "form": "8-K", "filed": "", "items": "2.02,9.01", "url": "", "src": "S2" } ],   // 8-K, 10-K, 10-Q for three years back (gates G1, G2)
  "filings_window": { "from": "2023-10-15", "to": "2026-10-14", "complete": true },                  // complete=false when the feed starts later than `from`
  "news_since": "2026-10-13",                                                                          // the researcher's window start (last run), separate from filings_recent
  "insiders": null,                          // null by design in v1 → dependent items are n/a
  "consensus": null,                         // null by design in v1
  "metrics": { /* unchanged metrics.py contract: piotroski, altman, beneish, accrual_ratio, roic[], roiic_5y,
                  gross_profitability, gross_margin_5y_change, revenue_cagr_5y, revenue_declines_consecutive_10y,
                  net_debt_to_owner_earnings, goodwill_impairment_5y, owner_earnings, fcf, owner_earnings_series[],
                  fcf_series[], cash_returned[], shares_diluted_adjusted[], gate_inputs, freshness, shareholder_yield,
                  dilution_5y, retained_earnings_test, graham_number, earnings_yield, return_on_capital, earnings_history,
                  valuation {params, scenarios, fair_value_today, by_horizon, buy_zone_below, sell_zone_above, agreement,
                  implied_growth_at_price} */ }
}
```

## sector_class from SIC

| SIC range | class |
|---|---|
| 2000–3999 | manufacturer |
| 6000–6799 except 6798 | financial |
| 6798 | reit |
| 4900–4999 | utility |
| everything else | non-manufacturer |

## Normalization rules (edgar.py)

- `10-K` facts only; `fp` = `FY`; `end` matches the fiscal year end; flow fields span a full year.
- Several filings for one period: latest `filed` wins, except `shares_diluted` and `eps_diluted`, which take the
  earliest `filed` fact (as originally reported) so that split adjustment from `price.splits` applies uniformly.
- Outflows (`capex`, `dividends_paid`, `buybacks`, `debt_repaid`) are stored positive.
- Composite fallbacks are recorded in `concept_map` as `"sum: A + B"`, used only when every aggregate concept is absent.
- Every unmatched field is `null` and listed in `missing`.

## series.json

`{"ticker", "src", "retrieved", "dates": [], "close": [], "adj_close": [], "dividends": [{"date","amount"}],
"splits": [{"date","ratio"}]}` for ten years, arrays aligned. `SPY.json` and `<SECTOR_ETF>.json` in the same
shape live under `<project>/data/market/` for the relative-strength inputs. `last_run.json` beside facts.json holds
the incremental state (`periodic_seen`, `price_checked_for`).
