# request.json — what the question asked, extracted once, consumed by every script and agent

Written by the skill at `<DATA>/stocks/<TICKER>/request.json` (one per ticker per run; `find` writes
`<DATA>/find/<date>-<slug>-request.json`). Nothing in the pipeline hard-codes a horizon, lens, peer list,
margin of safety or growth rate: each comes from here or from a stated default the file records.

```jsonc
{
  "question": "what about the apple stock",                 // verbatim
  "asked_at": "2026-10-14T20:10:00Z",
  "tickers": ["AAPL"],                                        // resolved from names; the skill confirms against facts.name
  "horizons_years": [1, 2, 5, 10],                            // from the question: "next 3 years" → [3]; "by 2030" → [years until 2030]; "this quarter" → [0.25]; none → default [1, 2, 5, 10]
  "horizon_source": "default|question",
  "lens": "long|short|both",                                  // under a year → short; years → long; unclear → both
  "lens_source": "question|inferred",
  "intent": "overview|sell|buy|compare|what_if|news|filing|holdings|other",
  "holdings_text": "",                                         // the holdings phrases verbatim, for holdings.py; "" when none
  "peers_requested": [],                                       // tickers or names the user named to compare with; else the researcher's peers
  "margin_of_safety": null,                                    // from the question ("40% safety margin") else config default (recorded by score.py)
  "what_if": { "growth": null, "erp": null, "price": [] },     // "if growth is 5%" → growth 0.05; "if it hits 400" → price [400]
  "dates": [],                                                 // decision dates the user named ("before December", "at year end")
  "account_types": [],                                         // from holdings_text
  "wants": ["price", "news", "peers", "industry", "options", "holdings", "short_term"],   // sections the question asks for; the advisor drops the rest from chat
  "constraints": []                                            // anything else stated, verbatim ("I don't want to sell before 2027", "no options")
}
```

How scripts consume it: `metrics.py --horizons <years>` (comma list, fractional allowed) and `--g-base`,
`--erp`, `--mos` from `what_if` and `margin_of_safety`; `score.py` reads the horizons present in the
valuation and `request.json` for lens, holdings and intent; `options.py --horizon-days` from the longest
horizon under a year or the nearest named date; `compare.py --peers` from `peers_requested`, else the
industry file's peers; `report.py` renders the horizon rows that exist and the sections in `wants`.

The skill fills this file by reading the question; when something is ambiguous it states the assumption
in `constraints` ("assumed 5 years: question said 'long term'") so the advisor can say it in the answer.
