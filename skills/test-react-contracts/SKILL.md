---
name: test-react-contracts
description: >
  Authors React unit tests that prove contracts (Vitest · RTL · MSW) — driving each unit
  through its test seam, asserting the states its contract exposes, and naming every test
  for the AC it verifies. Use when writing unit tests for new or changed React code or
  hardening weak coverage. Not for implementing the code under test (use
  implement-react-contracts), checking coverage after (use check-react-implementation),
  or E2E journey tests (the dedicated e2e agent owns those). Output: test files, each
  named for the AC it proves.
---

# test-react-contracts

Tests prove the contract: each test exercises a unit through its **Test seam** and asserts
the **observable signals** its contract exposes, labeled by the **AC** it verifies. A test
that can't be written that way is a design finding, not a testing problem — raise it.
Unit tests only — journey/E2E tests are authored from the approved plan by the dedicated
e2e agent, not here.

## Inputs

- **design.md + contracts** — the Test strategy table (AC → level → location) is the work
  list (unit-level rows only); each contract's Test seam is the harness; States exposed
  are the assertion targets. Absent → derive from the ACs and the code's observed
  conventions.
- **Direct instructions** — caller steering; narrows scope, never waives quality rules.

## Rules

Read before authoring; cite rules in review notes:

- [rules/unit-testing.md](./rules/unit-testing.md) — harness per seam, MSW at the boundary,
  async discipline, lifecycle & leak guards
- [rules/test-quality.md](./rules/test-quality.md) — cross-cutting: labels, assertions,
  fixtures, the mutation litmus

## Procedure

1. **Scope** — walk the Test strategy table's unit-level rows; each uncovered row is a
   work item at its stated location. No table → derive one from ACs + contracts.
2. **Author unit tests** — per [rules/unit-testing.md](./rules/unit-testing.md) and
   [rules/test-quality.md](./rules/test-quality.md), one file per owning unit.
3. **Self-check** — every AC row covered (coverage is a grep for the ID); each new test
   fails when its production condition is inverted (mutation litmus, spot-check the
   critical ones); suite runs deterministically — no sleeps, no order dependence.
4. **Steer** — raise and pause, never work around:
   - a unit only exercisable by standing up its host → **missing seam** (design gap);
   - an assertion only possible via implementation details → missing observable signal in
     the contract.

**Output:** test files only — coverage IS the grep of the ID-carrying labels; no manifest
is authored. Concise and goal-accurate — no redundant cases, no snapshot dumps.
