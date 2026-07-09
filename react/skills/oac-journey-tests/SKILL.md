---
name: oac-journey-tests
description: >
  Authors end-to-end journey tests from a human-approved qa-journey-plan.md (Vitest + RTL + MSW):
  builds the harness and page object, writes one test per approved journey (grouped by user story)
  with happy- and forced-error paths, and emits a journey → test → AC manifest. Requires the
  approved plan as input (planning/approval is oac-journey-plan). Use to "write the journey tests" /
  "author the E2E tests" once a plan is approved.
---

# oac-journey-tests

Given: a human-approved `qa-journey-plan.md` (path supplied by the caller).
Produce: one E2E test per approved journey + a traceability manifest.

No approved plan → STOP: run `oac-journey-plan` first (or ask the caller for the approved plan).
Scope is the plan — write no test for a journey it doesn't list.

## Instructions

1. **Read the approved plan.** Any journey that proves unautomatable during authoring goes back
   to the human — never silently dropped.
2. **Set up the harness + page object.** Find or create a way to drive the app to the feature;
   build a page object with stable locators for the elements the approved journeys touch.
   → `references/authoring.md`.
3. **Author one test per approved journey**, grouped by user story; name each by its `J-<n>` and
   the ACs it covers. Happy-path journeys stub their writes to succeed; every write must also
   have an error-path journey that forces the failure. → `references/authoring.md`.
4. **Write the traceability manifest** — journey → test → AC — so coverage is auditable.

Stack: Vitest + React Testing Library + MSW + `userEvent`. Intercept writes with MSW; drive the UI
with `userEvent`. Match the project's existing test setup and harness conventions — this skill
carries the discipline, not the tooling.

## References

- [`authoring.md`](references/authoring.md) — page object, harness (Vitest + RTL + MSW),
  happy/error-path setup, naming, and the traceability manifest.
