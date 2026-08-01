# Implementation rubric — axes C · S · R · H

Binary checks per axis; classes and derivation in [framework.md](./framework.md).
Capabilities gate every rule-card citation: read package.json once; a card for an absent
library or the wrong react/compiler setup never cites. Rule cards:
`skills/implement/rules/` (hooks, components, stores/services) ·
`skills/design/rules/` (ownership, boundaries).

## C — Conformance: the contract kept, observably

| id | class | check | evidence |
|----|-------|-------|----------|
| c1 | cliff | public surface matches the contract name-for-name, type-for-type | read |
| c2 | cliff | the batch's named tests are green with test paths byte-unchanged vs the red baseline ref (no ref provided → outcome `unverifiable`, reported) | command |
| c3 | core | stated must-nots hold; MODIFY units' listed importers compile and pass their KEEP tests | grep + command |
| c4 | core | every promised state is reachable through the public surface | trace |
| c5 | core | design.md § Blast radius dispositions executed — UPDATE tests assert the amended AC, KEEP tests still pass | command |

## S — Simplicity & readability: the diff is proportional to its AC and reads clean

| id | class | check | evidence |
|----|-------|-------|----------|
| s1 | core | every hunk serves the task's AC (unrelated edits, drive-by refactors, new dead code fail) | read |
| s2 | core | each need is met by the existing unit/type/query key/store slice where one exists | grep |
| s3 | polish | each abstraction serves ≥2 call sites, or stays inline | grep |
| s4 | core | code reads intention-first — names reveal role, one term per concept, matching the codebase's idiom | read |

## R — Runtime: the diff's runtime cost is earned

Route deep questions through `skills/evaluate/rules/performance-check.md`.

| id | class | check | evidence |
|----|-------|-------|----------|
| r1 | core | hot paths (per-frame, large list, main interaction) satisfy the `optimize-*` rule cards | read + cite |
| r2 | core | every subscription selects only consumed facts; every setup pairs with its teardown | read |
| r3 | cliff | growth is bounded — caches evicted, effects converge, listeners removed | read |
| r4 | polish | cold paths stay clear code — optimization spent only where measured | read |

## H — Honesty: failures surface, deviations are raised

| id | class | check | evidence |
|----|-------|-------|----------|
| h1 | core | every unhappy path lands in its contracted error/empty/boundary state — caught errors re-surface through it | trace |
| h2 | cliff | every deviation from the contract carries a DESIGN GAP block | grep |
| h3 | cliff | test seams intact — the unit stays reachable through its contract seam; green came from satisfying tests, not weakening them | read |
