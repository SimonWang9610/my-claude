---
description: Decompose the design into dependency-ordered tasks with a test task per acceptance criterion.
---
# sf:tasks

Turn the design into trackable tasks; test authoring is never optional. Writes `tasks.md`
under `.specflow/specs/<name>/`. Requires `requirements.md` + `design.md` + `contracts/`
(run the producing command if missing); steering as context.

**Steps.**

1. **Decompose from contracts** — every introduced unit covered by exactly one task; each
   task lists its contract file(s), AC IDs, and completion gate.
2. **Test coverage** — every AC / testable NFR is assigned to test-authoring work naming
   the ID and its observable outcome (a dedicated test task, or the owning wave's test
   batch); uncovered edge classes are marked on their task (or `skipped` with a reason —
   never omitted silently).
3. **Order into waves + batches** — dependency DAG grouped into waves, then adjacent
   levels merged to fit **2–4 waves** (a wave is sized by one agent's context, never task
   count); each wave pre-split into one test batch + one impl batch (agent assignments
   decided here, never at implement time). Test authoring always precedes the
   implementation it covers — by task dependency or batch order.

**Exit.** Every `AC-<story#>.<n>` / testable `NFR-<n>` maps to test-authoring work naming
the ID and its observable outcome; the graph is a valid DAG in waves with batch pairs;
zero test work → `TASK-TD` with a one-sentence justification.
