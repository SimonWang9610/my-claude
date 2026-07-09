---
name: oac-journey-plan
description: >
  Plans end-to-end journey coverage from a feature's user stories (US-<n>) and acceptance criteria
  (AC-<story>.<n>): extracts journeys (J-<n>) into a qa-journey-plan.md — which flows are automated,
  which aren't (with reasons) — and gates on explicit human approval. Produces the plan only, no
  test code. Use when a feature needs E2E coverage: "plan the E2E tests", "which flows to automate".
---

# oac-journey-plan

Given: the feature's user stories and acceptance criteria (document paths supplied by the caller).
Produce: `qa-journey-plan.md` at the caller-named location, human-approved.

## Instructions

1. **Extract the journeys** from the user stories (`US-<n>` / `AC-<story>.<n>`) into `J-<n>`
   entries, plus a "NOT automated" list. → `references/journey-plan.md` for the exact format.
2. **Check coverage.** Every user story has ≥1 journey; every write journey has an error-path
   counterpart listed (the failure the automation must force). ACs not covered by any journey
   appear in "NOT automated" with a reason — never silently dropped.
3. **Approval gate (blocking).** Present the plan and STOP for human approval.
   → `references/journey-plan.md` for the response protocol.

The approved plan is the scope contract for later E2E authoring: tests are written only for
listed journeys, one per `J-<n>`.

## References

- [`journey-plan.md`](references/journey-plan.md) — the `qa-journey-plan.md` format and the
  human approval-gate protocol.
