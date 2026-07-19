---
name: test-react-contracts
description: >
  Author unit and E2E tests against contracts (Vitest + RTL + MSW): the Test strategy
  table is the work list, each contract's Test seam the harness, States exposed the
  assertion targets; AC-labeled test names. Scopes: unit, e2e (from qa-journey-plan.md);
  default full. Use when writing or hardening tests.
argument-hint: "[unit | e2e]"
---

# test-react-contracts

Tests prove the contract: each test exercises a unit through its **Test seam** and asserts
the **observable signals** its contract exposes, labeled by the **AC** it verifies. A test
that can't be written that way is a design finding, not a testing problem — raise it.

## Scope argument

`/test-react-contracts <scope>` — omit for the full procedure.

- **unit** — skip step 3.
- **e2e** — skip step 2; journeys from a provided `qa-journey-plan.md`; standalone use
  with no plan → derive journeys from design.md's flows and pause for caller approval
  first.

## Inputs

- **design.md + contracts** — the Test strategy table (AC → level → location) is the work
  list; each contract's Test seam is the harness; States exposed are the assertion
  targets. Journeys come from `qa-journey-plan.md` (see Scope). Absent → derive from the
  ACs and the code's observed conventions.
- **Direct instructions** — caller steering; narrows scope, never waives quality rules.

## Rules

Read before authoring that kind of test; cite rules in review notes:

- [rules/unit-testing.md](./rules/unit-testing.md) — harness per seam, MSW at the boundary,
  async discipline, lifecycle & leak guards
- [rules/e2e-testing.md](./rules/e2e-testing.md) — journey tests: happy + forced-error,
  UI-only driving, traceability
- [rules/test-quality.md](./rules/test-quality.md) — cross-cutting: labels, assertions,
  fixtures, the mutation litmus

## Procedure

1. **Scope** — walk the Test strategy table; each uncovered row is a work item at its
   stated level and location. No table → derive one from ACs + contracts; derived unit
   rows proceed; derived journeys follow the e2e scope rule above.
2. **Author unit tests** — per [rules/unit-testing.md](./rules/unit-testing.md) and
   [rules/test-quality.md](./rules/test-quality.md), one file per owning unit.
3. **Author E2E tests** — per [rules/e2e-testing.md](./rules/e2e-testing.md): one test per
   journey, happy + forced-error paths.
4. **Self-check** — every AC row covered (coverage is a grep for the ID); each new test
   fails when its production condition is inverted (mutation litmus, spot-check the
   critical ones); suite runs deterministically — no sleeps, no order dependence.
5. **Steer** — raise and pause, never work around:
   - a unit only exercisable by standing up its host → **missing seam** (design gap);
   - an assertion only possible via implementation details → missing observable signal in
     the contract;
   - an unautomatable journey → back to the caller with the reason, never silently dropped.

**Output:** test files only — coverage IS the grep of the ID-carrying labels; no manifest
is authored. Concise and goal-accurate — no redundant cases, no snapshot dumps.
