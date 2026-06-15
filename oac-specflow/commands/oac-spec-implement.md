# oac-spec:implement

Plan the work into `(WorkAgent, TestAgent)` phases and execute them; "completed" means an AC-traceable outcome test passes.

---

You are the implementation agent for the oac-specflow framework. This command **merges the original `/implement` with the `(WorkAgent, TestAgent)` phased-execution model** (formerly a separate `/spec-phase`) — it both plans the execution phases and runs them, so no separate phase stage is needed.

**Purpose.** Build the spec's tasks under a paired-agent contract that makes test evidence structural: every surface is owned by a **WorkAgent** and verified by a paired **TestAgent**, and a unit is "completed" only when a named, AC-traceable, outcome-asserting test passes — so "completed" can't mean "a checkbox" or "existing tests ran".

## Spec Artifacts

Write planning artifacts (`phases.md`, and `tasks.md` status updates) under `.specflow/specs/<name>/`. The implementation **code** is written to the target repo, **not** here.
- **Required:** `requirements.md`, `design.md`, `contracts/`, `tasks.md` — run the matching commands if missing.
- **Optional:** `.meta.yaml` issue-tracker field (Steps 0–1; project-specific); prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*`; the target repo (where code is written).

## Gate / exit

Exits only when every `(WorkAgent, TestAgent)` group is **Completed** — the WorkAgent met its handoff criteria, the TestAgent's AC-traceable outcome tests are green, shared-component immutability held — and `tasks.md`/`phases.md` record the test that satisfies each AC.

## Steps

0. **Link tracker issue** (first run; project-specific) — scan the spec docs for issue keys, confirm with the user, validate, append to `.meta.yaml`; skip if no tracker. Apply: _oac-jira-status-automation.
1. **Move issues in-progress** (project-specific) — transition each linked issue forward. Apply: _oac-jira-status-automation.
2. **Plan the phases** — group tasks into ordered phases of one-to-one `(WorkAgent, TestAgent)` pairs; persist to `phases.md` (resumable). WorkAgent owns its surfaces + contracts + AC-IDs + handoff criteria; TestAgent's pass criteria are the test contract. Apply: oac-test-contract.
3. **Execute each phase** (coordination loop) — per pair:
   - WorkAgent builds its surfaces to their contracts (write paths included), then hands off on its criteria. Apply: architecture-principles, engineering-discipline.
   - TestAgent writes the AC-named outcome test against the contract's seam and runs it green. Apply: oac-test-contract, test-quality.
   - Copy an adopted shared unit instead of modifying it. Apply: architecture-principles.
   A phase advances only when all groups are Completed; update `tasks.md` and `phases.md`.

## Instructions & references

- [oac-test-contract](../skills/oac-test-contract/SKILL.md) — the 6-rule test contract; the TestAgent's pass criteria.
- [architecture-principles](../rules/architecture-principles.md) — how units and write paths are built; the shared-unit boundary.
- [engineering-discipline](../rules/engineering-discipline.md) — smallest change, surgical edits, conventions, iteration budget.
- [test-quality](../rules/test-quality.md) — the bar a group's tests meet before it is Completed.
- [_oac-jira-status-automation](_oac-jira-status-automation.md) — the project's issue-tracker transition playbook (project-specific; delete if no tracker).
