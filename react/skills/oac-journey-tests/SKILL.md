---
name: oac-journey-tests
description: >
  Author end-to-end journey tests for a feature's user stories — but only after a human approves the
  journey plan. Extracts user journeys from the requirements, gates on explicit approval, then writes
  one E2E test per approved journey (grouped by user story) with happy- and error-path setup and a
  traceability manifest. Stack-agnostic E2E discipline; the runner and harness are the project's.
---

# oac-journey-tests

> End-to-end tests for whole user flows — the layer above the per-unit tests. Plan the journeys, get a human to approve the scope, then author.

Per-unit and component tests are written when the unit is built. This skill adds the **end-to-end** layer: tests that drive the running app through a complete user story. It never writes E2E code before a human approves the journey plan — scope is a human decision, not an inference.

## When to use

When a feature needs end-to-end coverage of its user flows (beyond the per-unit tests already written) and you want a human to approve which journeys are automated before any E2E code is written. Requires a project that runs an E2E runner (Playwright, Cypress, …) and a way to drive the running app.

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
