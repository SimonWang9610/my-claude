---
description: Implement each unit to its contract and write the AC-traceable tests until green.
---
# spec:implement

Plan the work into `(WorkAgent, TestAgent)` phases and execute them; "completed" means an AC-traceable outcome test passes.

---

**Purpose.** Build the spec's tasks under a paired-agent contract that makes test evidence structural: every surface is owned by a **WorkAgent** and verified by a paired **TestAgent**, and a unit is "completed" only when a named, AC-traceable, outcome-asserting test passes — so "completed" can't mean "a checkbox" or "existing tests ran".

This command merges the original `/implement` with the `(WorkAgent, TestAgent)` phased-execution model — it both plans the execution phases and runs them, so no separate phase stage is needed.

## Spec Artifacts

Write planning artifacts (`phases.md`, and `tasks.md` status updates) under `.specflow/specs/<name>/`. The implementation **code** is written to the target repo, **not** here.
- **Required:** `requirements.md`, `design.md`, `contracts/`, `tasks.md` — run the matching commands if missing.
- **Optional:** `.meta.yaml` issue-tracker field (Steps 0–1; project-specific); prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*`; the target repo (where code is written).

## Gate / exit

Exits only when every `(WorkAgent, TestAgent)` group is **Completed** — the WorkAgent met its handoff criteria, the TestAgent's AC-traceable outcome tests are green, shared-unit immutability held — and `tasks.md`/`phases.md` record the test that satisfies each AC.

## Steps

0. **Optional — if the project defines a tracker integration, run it** (first run) — scan the spec docs for issue keys, confirm with the user, validate, append to `.meta.yaml`; skip if no tracker.
1. **Optional — if the project defines a tracker integration, run it** — transition each linked issue forward.
2. **Plan the phases** — group tasks into ordered phases of one-to-one `(WorkAgent, TestAgent)` pairs; persist to `phases.md` (resumable). WorkAgent owns its surfaces + contracts + AC-IDs + handoff criteria; TestAgent's pass criteria are the test contract.
3. **Execute each phase** (coordination loop) — per pair:
   - WorkAgent builds its surfaces to their contracts (write paths included), then hands off on its criteria.
   - TestAgent writes the AC-named outcome test against the contract's seam and runs it green.
   - Copy an adopted shared unit instead of modifying it.
   A phase advances only when all groups are Completed; update `tasks.md` and `phases.md`.
