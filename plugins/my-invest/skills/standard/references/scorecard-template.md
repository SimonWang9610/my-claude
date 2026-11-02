# Scorecard section — fixed shape

Written by the scorer into the dossier under `## Scorecard`. Figures carry markers; `n/a` and
`no evidence` are written as those words. Nothing is added or reordered. `[S<d>]` below is the
derived-source row the quant registers for `metrics.py` output (class `derived`, what: `metrics.py
scorecard inputs and valuation per valuation.md from S…`); the horizon rows, parameters and the
confidence line cite it, because their numbers are that script's output.

```markdown
## Scorecard — as of <YYYY-MM-DD>

**Tier:** <track closely | research deeper | pass> · **Score:** <n>/100 · **Stance:** <buy zone | hold | sell zone | avoid> · **Confidence:** <n>/100
Price <$x> [S<n>] vs buy zone below <$x> and sell zone above <$x> (base fair value <$x>, bear <$x>, bull <$x>) [S<n>].

### Gates
| Gate | Result | Evidence |
|---|---|---|
| G1 Bankruptcy or receivership (8-K Item 1.03, 3 yrs) | pass | none in filings index [S2] |
| … | … | … |

### Pillars
| Pillar | Points | Scored 0 or no evidence | n/a (reason) | UNVERIFIED threshold items (per card) |
|---|---|---|---|---|
| 1 Business quality and moat | <p>/20 | 1.3 gross profitability 0.21 [S1] | 1.2 | |
| 2 Financial strength | <p>/20 | … | | 2.2 |
| 3 Management and capital allocation | <p>/20 | … | 3.5 | |
| 4 Valuation and margin of safety | <p>/20 | … | | 4.5 |
| 5 Risks and red flags | <p>/20 | … | | 5.2 |

### Fair value by horizon (per share, <scenario basis>) [S<n>]
| Horizon | Bear | Base | Bull | |
|---|---|---|---|---|
| today | | | | [S<d>] |
| 1 yr | | | | [S<d>] |
| 2 yr | | | | [S<d>] |
| 5 yr | | | | [S<d>] |
| 10 yr | | | | [S<d>] |

Implied growth at price <g>% vs base scenario <g>% [S<d>]. Parameters: r <x>%, bear r <x>%, terminal g <x>%, margin of safety <x>% [S<d>].

### Confidence
<n>/100 = 0.5 × coverage <x> + 0.3 × agreement <x> + 0.2 × freshness <x> (weights are this standard's opinion, valuation.md) [S<d>, S<s>]. Tier cutoffs 70 / 45 are this standard's opinion (D-8) [S<s>].

### Open questions (kept in scorecard.json; the dossier shows one merged list instead)
- <item id> — <what is missing and where it would come from>
- freshness <value> — <which input is stale and when it refreshes> (only when freshness < 1)
```
