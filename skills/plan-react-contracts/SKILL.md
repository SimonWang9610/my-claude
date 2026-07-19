---
name: plan-react-contracts
description: >
  Project an approved design (design.md + contracts/) into tasks.md — dependency-ordered
  tasks with parallel waves, each wave pre-split into a test batch (one TestAgent) and an
  impl batch (one WorkAgent); contract groups are the default task unit, rows are pointers
  (IDs, paths, gates), never restated contracts. Use after design approval, before
  implementation.
---

# plan-react-contracts

Project the approved design into an ordered work list. tasks.md adds **order and gates
only** — every fact lives in the design artifacts; rows are pointers (IDs, paths,
commands), never sentences restating contracts.

## Inputs

`design.md` (Units table, Test strategy) + `contracts/`, approved. Any completeness
failure → back to the design skill; never plan over a broken design.

## Procedure

1. **Verify inputs** — every MODIFY/NEW unit links a non-empty contract; every AC has a
   Test strategy row.
2. **One task per contract group, re-cut when task-shaped reasons demand** — groups were
   cut for design relatedness, which is the *default* task unit, not a law. Split a group
   whose units land in different waves or exceed one agent's bite; merge groups only when
   they cannot land separately (entangled deps). Every re-cut names its reason; every unit
   appears in exactly one task; each task lists the contract file(s) + unit names it
   covers. Depends-on = the task's units' deps, external to the task (EXISTING deps don't
   count).
3. **Point at tests, never restate** — each task lists its AC IDs (= its Test strategy
   rows). **Edge completeness check:** per unit walk error · empty · loading · boundary;
   a class the contract's States exposed demands but no AC row asserts gets one
   `Edge: <unit>·<class>` marker on the task — the test skill's rules fix the assertion.
4. **Derive waves** — Wave 1 = tasks with no unmet deps; wave *n* = deps all in earlier
   waves. Tasks in a wave build concurrently (group boundaries keep files disjoint).
5. **Split each wave into agent batches** — decided here with the whole plan in view,
   never at implement time. Per wave: one **test batch** (every task's AC rows + Edge
   markers — one TestAgent) and one **impl batch** (every task's units + contracts — one
   WorkAgent). Default batch = the whole wave; a wave over ~4 tasks or one context's
   worth of contracts is chunked into named task subsets — each chunk a test+impl pair,
   reason stated. Batches list task IDs only.
6. **Count-check** — tasks = contract groups ± recorded re-cuts; every task carries
   deps + ACs + gate; every AC appears in exactly one task; every task in exactly one
   batch pair. A mismatch means dropped or duplicated work — reconcile before hand-off.

## `tasks.md` shape

```markdown
# <Feature> — tasks

- [ ] T1: device-selection (contracts/device-selection.md)
      deps: none · ACs: AC-2.4 · Edge: DeviceTable·empty
      gate: group tests green, test files unchanged post-red · typecheck · must-nots grep
- [ ] T2: device-list (contracts/device-list.md)
      deps: T1 · ACs: AC-1.1, AC-2.1
      gate: same · importer AlarmsPage unbroken

## Waves
- W1: T1 — test batch: T1 · impl batch: T1
- W2: T2 — test batch: T2 · impl batch: T2
<a chunked wave instead lists pairs: `- W2, chunked (>4 tasks): W2a: T2, T3 — test
batch: T2, T3 · impl batch: T2, T3 · W2b: T4, T5 — …`>
```

**Output discipline:** terse and goal-accurate — field values are facts (IDs, paths, gate
commands); anything longer than a line belongs in the contract, not here.
