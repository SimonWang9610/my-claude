---
description: Implement each wave's tasks with independent test and implementation agents; completed means the AC-traceable test passes.
---
# sf:implement

Execute tasks.md wave by wave under an evidence contract that makes "completed" structural:
an AC-named, outcome-asserting test passes — authored independently of the implementation —
so "completed" can never mean "a checkbox" or "existing tests ran". Updates `tasks.md`
status under `.specflow/specs/<name>/`; code goes to the target repo. Requires `tasks.md` +
`design.md` + `contracts/`; optional `qa-journey-plan.md` (drives step 4); steering as
context.

**Steps.**

1. **Author tests per wave batch** — a test agent writes each task's AC-named outcome
   tests from the contracts (test files only; tests derive from contracts, never from the
   code under test); run them: **red per task**, failing on behavior, not setup — record
   the ref.
2. **Implement per wave batch** — a separate implementation agent (never the test author)
   builds to the contracts (source only); a wrong-looking test is raised, never edited;
   copy an adopted shared unit instead of modifying it.
3. **Verify per task** — tests **green**, AND test paths byte-unchanged since red;
   modified → redo the task with a fresh test/impl pair. Chunked batch pairs run
   concurrently.
4. **Journeys** — `qa-journey-plan.md` exists → per entry: **NEW** → author the
   end-to-end test (`J-<n>` + AC IDs in the name); **MODIFY** → update the named existing
   test (a material change to an existing test is surfaced, never silent); run to green.
   Unautomatable journeys stay in the plan's NOT-automated table.

**Exit.** Every task's AC-traceable outcome test is green and byte-unchanged since
authoring; journey tests green (or the plan's skip note stands); shared-unit immutability
held; `tasks.md` records the test satisfying each AC; the flow's bound review pass leaves
no unresolved Critical/Major finding.
