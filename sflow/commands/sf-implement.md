---
description: Implement each unit to its contract and write the AC-traceable tests until green.
---
# sf:implement

Plan the work into `(TestAgent, WorkAgent)` phases and execute them test-first; "completed" means an AC-traceable outcome test passes.

---

**Purpose.** Build the spec's tasks under a paired-agent contract that makes test evidence structural: a **TestAgent** authors the AC test red-before-green, a separate **WorkAgent** implements it to green (never editing the test), and a unit is "completed" only when that named, AC-traceable, outcome-asserting test passes and is unmodified — so "completed" can't mean "a checkbox" or "existing tests ran".

This command merges the original `/implement` with the `(TestAgent, WorkAgent)` phased-execution model — it both plans the execution phases and runs them, so no separate phase stage is needed.

## Spec Artifacts

Write planning artifacts (`phases.md`, and `tasks.md` status updates) under `.specflow/specs/<name>/`. The implementation **code** is written to the target repo, **not** here.
- **Required:** the workflow's planning artifacts — `tasks.md` + `design.md` + `contracts/` (feature/brownfield), `tasks.md` + `analysis.md` (bugfix), or `describe.md` alone (quickfix: the one AC is the task).
- **Optional:** prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*`; the target repo (where code is written).

## Gate / exit

Exits only when every `(TestAgent, WorkAgent)` group is **Completed** — the TestAgent's AC-traceable outcome test is green and byte-unchanged since it was written, the WorkAgent met its handoff criteria, shared-unit immutability held — `tasks.md`/`phases.md` record the test that satisfies each AC, and the branch passes `oac-implementation-review` (no unresolved Critical/Major finding).

## Steps

1. **Plan the phases** — group tasks into the parallel waves `tasks.md` declares (independent units run concurrently), each unit a one-to-one `(TestAgent, WorkAgent)` pair; persist to `phases.md` (resumable; a single-pair spec, e.g. a quickfix, may run as one pair without `phases.md`). TestAgent's pass criteria are the AC test contract; WorkAgent owns the surfaces + contracts + AC-IDs + handoff criteria.
2. **Execute each unit** — `test → red → impl → green`, per pair:
   - TestAgent writes the AC-named outcome test against the contract's seam and runs it to confirm it **FAILS** (red) before any implementation — test files only.
   - WorkAgent builds the surfaces to their contracts (write paths included) until the test passes (**green**); it never creates or edits a test.
   - Copy an adopted shared unit instead of modifying it.
   A unit is Completed only when its test is green and unmodified since the TestAgent wrote it; update `tasks.md` and `phases.md`.
3. **Branch review** — once every unit is green, a ReviewAgent runs `oac-implementation-review` across the changed files; Critical/Major findings loop back to a WorkAgent (never the test) and re-review until none remain.
