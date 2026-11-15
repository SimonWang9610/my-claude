---
name: spec-plan
description: >-
  Plans a spec's work as tasks.md: ordered tasks, each tied to the acceptance criteria it serves, its
  files and the check that proves it; a coverage table; each task sized normal or complex; batches
  whose files do not overlap; and the decision whether to delegate batches to agents, on which model
  and with which stack skills. Use as the plan step of a spec, or on "plan this", "break this into tasks", "who should build what". Not for choosing an approach
  (use my-workflow:spec-design).
argument-hint: "[requirements | path to a workflow.yaml]"
---

# spec-plan

Follow `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (if shown unexpanded: `../../shared/conventions.md`
from this skill's folder). Other paths are relative to this skill's folder.

1. **Context** — per the conventions' Spec mode; the input is the spec and, when there is one, the
   design. Their `Open:` leaves an approach, structure or contract undecided → take a small one as a
   stated `D`, or stop and say a design is needed.
2. **Tasks** — in build order, about 8 (more → the design is too coarse, or split the spec), each
   with what it does, the `AC` or `R` it serves, its files, the check that proves it and the tasks
   it depends on. By kind:
   - feature — the acceptance checks for a batch come before its code; a new layout → T1 is its
     scaffold, a prerequisite of every other task.
   - bug — T1 the failing reproduction as a test, then the fix, then the neighbours' checks.
   - improvement — T1 the must-not-change checks seen passing and the baseline measured; every later
     task shippable alone with those checks still passing.
3. **Coverage** — every `AC` and `R` is served by at least one task; one that is not is flagged, never
   dropped.
4. **Size** — complex: a new contract, concurrency, a security or data-migration path, or no existing
   example to copy; else normal.
5. **Batches** — group tasks whose file sets do not overlap; keep each criterion within one batch.
   Delegate when ≥2 batches are independent, or independent acceptance checks pay off (several
   behavioural criteria); else the session builds it. Per batch: the owner, the model (strong when it
   holds a complex task, else standard) and the installed skills this batch's work needs (the
   conventions' Knowledge; spec mode: from the implement step's `skills`).
6. **Write** — `assets/tasks.md`. `Open:` uncovered criteria and undecided points.
