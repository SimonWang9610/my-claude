---
name: oac-journey-tests
description: >
  Authors end-to-end journey tests for a feature's user stories using Vitest + React Testing Library.
  Extracts journeys from requirements (US-* / AC-*), gates on explicit human approval of the plan,
  then writes one test per approved journey (grouped by user story) with happy- and error-path
  coverage and a traceability manifest. Use when a feature needs E2E coverage beyond per-unit tests
  and an approval gate is required before any test code is written. Trigger: "write journey tests",
  "E2E tests for this feature", "journey plan", or after per-unit tests are done.
---

# oac-journey-tests

> End-to-end tests for whole user flows — the layer above the per-unit tests. Plan the journeys, get a human to approve the scope, then author.

Per-unit and component tests are written when the unit is built. This skill adds the **end-to-end** layer: tests that drive the running app through a complete user story. It never writes E2E code before a human approves the journey plan — scope is a human decision, not an inference.

## When to use

When a feature needs end-to-end coverage of its user flows (beyond the per-unit tests already written) and a human must approve which journeys are automated before any test code is written. Suitable for any project running Vitest + React Testing Library; also works with Playwright or Cypress — the discipline is runner-abstracted.

## Instructions

1. **Extract the journeys.** From the requirements' user stories (`US-*` / `AC-*`), write each journey `J-<n>` in plain English — steps, expected outcome, CRUD type, ACs covered — and a "not automated" list with reasons. Write the plan to `qa-journey-plan.md`. → `references/journey-plan.md`.
2. **Approval gate (blocking).** Present the plan and STOP. Accept `approve` / `revise: <feedback>` / `skip J-<n>` / `add: <description>`. Write no E2E code until you have an explicit `approve`. → `references/journey-plan.md`.
3. **Set up the harness + page object.** Find or create a way to drive the app to the feature; build a page object with stable locators for the elements the approved journeys touch. → `references/authoring.md`.
4. **Author one test per approved journey**, grouped by user story; name each by its `J-<n>` and the ACs it covers. Happy-path journeys stub their writes to succeed; every write must also have an error-path journey that forces the failure. → `references/authoring.md`.
5. **Write the traceability manifest** — journey → test → AC — so coverage is auditable.

The runner, harness, and intercept mechanism are the project's — read the steering files; this skill carries the discipline, not the tooling.

## References

- [`journey-plan.md`](references/journey-plan.md) — the `qa-journey-plan.md` format and the human approval gate.
- [`authoring.md`](references/authoring.md) — page object, happy/error-path setup, naming, and the traceability manifest (runner-abstracted).
