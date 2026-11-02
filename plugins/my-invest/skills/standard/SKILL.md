---
name: standard
description: >-
  Defines how my-invest reaches a verdict and what proof it must carry: red-flag gates, five equal-weight
  pillars of cited binary items, the forward outlook (expected-return scenarios by horizon, months-ahead
  range, consensus with its base rate), the strict owner-earnings value as a labelled lens, the
  recommendation logic by position and trend, confidence with its band, the short-term lens, options on
  real contracts, Canadian tax lines; and the proof contract every conclusion obeys — no verdict rather
  than a default hold, the case against, the track record, what could change the answer, what could not be
  verified, every return beside its benchmark. Use when interpreting scorecard.json or writing the
  analyst's note or the advisor's narrative; computed by score.py and metrics.py, not invoked by the user.
user-invocable: false
---

# standard

Every judgment is a check with a published test, a cited source and a stated input; `metrics.py` and
`score.py` run the checks and the arithmetic, so no agent scores by feel. Weights are equal because no
published source validates stock-level weights for a value investor; gates carry the published evidence,
so gates come first. Thresholds that could not be pinned to a primary text are labelled UNVERIFIED in
their card and in every output, and are never gates.

## How a verdict is formed

- Gates: [gates.md](rules/gates.md). Any `fail` → tier `pass`, stance `avoid / exit`.
- Pillars, 20 points each, mean of binary items: [1 quality and moat](rules/pillar-1-quality.md) ·
  [2 financial strength](rules/pillar-2-strength.md) · [3 capital allocation](rules/pillar-3-capital-allocation.md) ·
  [4 valuation](rules/pillar-4-valuation.md) · [5 risks](rules/pillar-5-risk.md).
- Applicability: `financial`, `reit`, `utility` make Altman, Beneish, Greenblatt ranks and the
  owner-earnings model `n/a`; `manufacturer` uses Altman Z, `non-manufacturer` Z''. An item is `n/a`
  when its model does not apply, its denominator is undefined, or its input is null by design; `n/a`
  leaves the denominator. A collectible input that is missing is `no evidence`: it stays in and scores 0.
- Evidence-required items (G4, 1.5, 5.4, 5.5) are decided by the analyst's `evidence.json`; when the
  file is absent (a screen that never ran an analysis) they are `pending` and excluded.
- Outlook first — scenarios by horizon, the months-ahead range, consensus, calibration and the
  recommendation logic: [outlook.md](rules/outlook.md). The headline is the base expected return at the
  user's horizon against the return the risk demands, never a single-number target.
- The strict value lens (owner-earnings fair value, zones, implied growth): [valuation.md](references/valuation.md) — one lens, labelled "a strict value investor's price", never the headline.
- Action matrix, triggers and holdings rows: [action-matrix.md](references/action-matrix.md).
- Short-term lens (short or ambiguous horizons): [lens-short-term.md](rules/lens-short-term.md).
- Options operations shown with the stock's own contracts: [options-playbook.md](rules/options-playbook.md).
- Canadian tax lines for stated holdings: [tax-ca.md](references/tax-ca.md).
- Tiers: no failed gate and score ≥ 70 → `track closely`; 45–69 → `research deeper`; below 45 or a failed
  gate → `pass`. Cutoffs are this standard's opinion (DECISIONS D-8) and the output says so.

## What a conclusion must carry (the proof contract)

A beginner cannot check the arithmetic, so the answer must show the reader how to distrust it. Every
answer and every analyst's note carries, in this order after the verdict:

1. **The scenarios and their inputs** — bear, base, bull per horizon with the growth, multiple and
   cash-return assumptions and their markers; consensus as a secondary row with its base rate.
2. **The case against** — the strongest reasons the verdict could be wrong, written by the same analyst
   and weighed on merit, each tied to a figure, an item id or a cited passage. Conflict alone is not a
   reason for `hold`: the verdict is committed when the evidence leans and called balanced only when it is.
3. **The track record** — the simulated record (`metrics.calibration.record`: the same method at each past
   fiscal year, forecast vs realised vs SPY over the same window, labelled simulated and in-sample) and
   the real one (`history/log.md`: what this advisor said before about the stock, at what price, and what
   the price and SPY did since). Every return stands beside its benchmark over the same window.
4. **What could change the answer** — observable events with a date or price, each naming the item or gate
   it would flip.
5. **What could not be verified** — every `no evidence` or pending item, null metric with its reason, stale
   figure and refused page; gaps are shown beside the conclusion, never summarised away.

Rules that bind the whole:

- **No verdict beats a fake one.** When the scorecard is missing or older than one trading day and cannot
  be refreshed, or a required script failed, the answer is `no verdict` with the failing stage; never a
  default `hold`, never a stance recalled from memory.
- **Confidence** is the printed formula (coverage, agreement, outlook spread, freshness) shown as a number
  with its band — ≥ 80 strong evidence, 65–79 solid, 45–64 mixed, below 45 thin — and what lowers it.
  The bands are this standard's labels, not probabilities, and the output says so once.
- **Claim typing.** Sections and tables are tagged *computed by scripts* or *the analyst's reading*; a
  judgment never borrows a figure's marker as if it were a fact. A post or forum view never supports a
  figure.
- **The rule before the score.** Thresholds are stated in the rule cards and never chosen on the dates
  they are then evaluated on; the simulated record says its thresholds are in-sample.

## Reading scorecard.json

Shape: [scorecard-schema.md](references/scorecard-schema.md). `items[id].status` tells you why an item
did not score; `pillars[n].zero_items` are the weaknesses to name; `action.recommendation` holds the cell
for the reader's position with the levels and markers that produced it; `short_term` is null unless the
lens asked for it; `open_questions` are already ranked. The dossier's Scorecard section follows
[scorecard-template.md](references/scorecard-template.md), rendered by `report.py`.

## The note and the narrative

The analyst's note and the advisor's narrative share the slots in [note.md](references/note.md); `report.py`
reads them into the answer. They may say only what the scorecard, the facts and `research.md` contain,
each figure with its marker. They may explain, rank and connect, convert units and round for display
when the unit is stated (evidence skill); they may not compute new figures, soften a failed gate, or add
a target of their own. Stance, tier and recommendation words are used as written. Re-scoring is a new
`score.py` run on refreshed facts, never an edit of the result.
