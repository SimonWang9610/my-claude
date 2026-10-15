# scorecard.json — written by score.py, read by report.py and the analyze skill

```jsonc
{
  "ticker": "AAPL", "as_of": "2026-10-14", "mode": "full|screen", "sector_class": "manufacturer",
  "price": 343.87, "price_src": "S3",
  "gates": { "G1": { "result": "pass|fail|n/a", "value": null, "test": "…", "markers": ["S2"], "note": "" } },
  "items": { "1.1": { "score": 1, "status": "scored|n/a|no evidence|pending", "value": 0.82, "test": "…",
                      "markers": ["S1","S6"], "unverified": false, "evidence_required": false, "note": "" } },
  "pillars": { "1": { "points": 20.0, "earned": 5, "applicable": 5, "zero_items": [], "na_items": ["1.2"], "unverified_items": [] } },
  "score": 63, "tier": "research deeper", "stance": "sell zone",       // stance = zone word; action.cells = the verbs for holding / not holding
  "zones": { "buy_below": 103.97, "sell_above": 175.77, "base_today": 148.53, "bear_today": 81.11, "bull_today": 175.77 },
  "fair_value": { "1": {"bear":0,"base":0,"bull":0}, "2": {}, "5": {}, "10": {} },
  "implied_cagr": { "1": {"bear":0,"base":0,"bull":0}, "2": {}, "5": {}, "10": {} },
  "required_return": 0.0941,
  "confidence": { "value": 78, "coverage": 0.93, "agreement": 0.36, "freshness": 1.0 },
  "action": { },                   // per action-matrix.md; action.options = [{op, fits_because, contract {type, strike, expiry, days, mid, oi, iv}, pay_or_receive, best_case, worst_case, markers}] per options-playbook.md
  "short_term": null,
  "open_questions": [ { "id": "3.4", "text": "…" } ],
  "sources": { "S<s>": { "class": "derived", "what": "score.py gates, items and action matrix from S…", "url": "file://…/scorecard.json" } }
}
```

`implied_cagr[h][scenario]` = `(V_h / price)^(1/h) − 1`. `action` follows [action-matrix.md](action-matrix.md);
`short_term` follows [lens-short-term.md](../rules/lens-short-term.md) and is null unless requested.

Evidence-required items (G4, 1.5, 5.4, 5.5) read `evidence.json`, written by the researcher:

```jsonc
{ "as_of_10k": "0000320193-25-000079", "judged": "2026-10-14",
  "G4":  { "verdict": "pass|fail|no evidence", "marker": "S100", "quote": "≤15 words", "where": "auditor.txt" },   // one log row per filing; items may share its marker
  "1.5": { "verdict": "pass|fail|no evidence", "marker": "S100", "quote": "…", "where": "item-1.txt", "moat_sources": ["intangible assets"] },
  "5.4": { "verdict": "…", "marker": "…", "quote": "…", "where": "item-9a.txt" },
  "5.5": { "verdict": "…", "marker": "…", "quote": "", "where": "full.txt", "method": "grep: 10%|single customer|major customer — no revenue-concentration hit" } }   // quote may be empty when the verdict rests on a grep
```

A missing `evidence.json` marks those items `pending` and excludes them from denominators (screen mode uses the file when it exists).
