---
name: score
description: >-
  Defines the my-invest scoring standard: red-flag gates, five equal-weight pillars of cited binary
  items, an owner-earnings valuation with fair value at 1, 2, 5 and 10 years, buy and sell zones, stance,
  confidence, tier, the action matrix and a labelled short-term lens, and how to read scorecard.json
  and what a narrative may say. Use when interpreting a scorecard or writing the narrative in analyze,
  find or digest; computed by score.py, not invoked by the user.
user-invocable: false
---

# score

Every judgment is a check with a published test, a cited source and a stated input; `score.py` runs the
checks and the arithmetic, so no agent scores by feel. Weights are equal because no published source
validates stock-level weights for a value investor; gates carry the published evidence, so gates come
first. Thresholds that could not be pinned to a primary text are labelled UNVERIFIED in their card and in
every output, and are never gates.

## The standard

- Gates: [gates.md](rules/gates.md). Any `fail` → tier `pass`, stance `avoid / exit`.
- Pillars, 20 points each, mean of binary items: [1 quality and moat](rules/pillar-1-quality.md) ·
  [2 financial strength](rules/pillar-2-strength.md) · [3 capital allocation](rules/pillar-3-capital-allocation.md) ·
  [4 valuation](rules/pillar-4-valuation.md) · [5 risks](rules/pillar-5-risk.md).
- Applicability: `financial`, `reit`, `utility` make Altman, Beneish, Greenblatt ranks and the
  owner-earnings model `n/a`; `manufacturer` uses Altman Z, `non-manufacturer` Z''. An item is `n/a`
  when its model does not apply, its denominator is undefined, or its input is null by design; `n/a`
  leaves the denominator. A collectible input that is missing is `no evidence`: it stays in and scores 0.
- Evidence-required items (G4, 1.5, 5.4, 5.5) are decided by the researcher's `evidence.json`; when the
  file is absent (a screen that never ran `analyze`) they are `pending` and excluded.
- Outlook first: expected-return scenarios by horizon, the months-ahead range, consensus, calibration and the recommendation logic: [outlook.md](rules/outlook.md).
- The strict value lens (owner-earnings fair value, zones, implied growth): [valuation.md](references/valuation.md) — one lens, never the headline.
- Action matrix, triggers and holdings rows: [action-matrix.md](references/action-matrix.md).
- Short-term lens (short or ambiguous horizons): [lens-short-term.md](rules/lens-short-term.md).
- Options operations shown with the stock's own contracts: [options-playbook.md](rules/options-playbook.md).
- Tiers: no failed gate and score ≥ 70 → `track closely`; 45–69 → `research deeper`; below 45 or a failed
  gate → `pass`. Cutoffs are this standard's opinion (DECISIONS D-8) and the output says so.

## Reading scorecard.json

Shape: [scorecard-schema.md](references/scorecard-schema.md). `items[id].status` tells you why an item
did not score; `pillars[n].zero_items` are the weaknesses to name; `action` holds the stance cells and
triggers; `short_term` is null unless the lens asked for it; `open_questions` are already ranked.
The dossier's Scorecard section follows [scorecard-template.md](references/scorecard-template.md), rendered
by `report.py`.

## What the narrative may say

Only what the scorecard, the facts and `research.md` contain, each figure with its marker. It may
explain, rank and connect, convert units and round for display when the unit is stated (evidence skill);
it may not compute new figures, soften a failed gate, or add an analyst-style target. Stance and tier words are used as written. Re-scoring is a new `score.py` run on
refreshed facts, never an edit of the result.
