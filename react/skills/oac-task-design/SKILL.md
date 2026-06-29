---
name: oac-task-design
description: >
  Turns an approved design.md and contracts/ into tasks.md for a React feature — one buildable
  task per unit in dependency order, a test task per acceptance criterion plus edge cases, with
  AC-ID traceability. Use at the spec-tasks stage, after design is approved and before
  implementation begins.
---

# oac-task-design

## Procedure

Work through every step in order. Do not create tasks.md until all steps are complete.

---

### Step 1 — One task per contract unit

For each file in `contracts/`, create one implementation task. The task must state:
- The unit kind (component / hook / store / service / API module).
- The contract file it implements (e.g. `contracts/useDeviceFilters.md`).
- Its exit check: the unit compiles, passes its own type constraints, and the contract's
  public API is satisfied.

---

### Step 2 — Order by dependency (leaf-first)

Sort implementation tasks so that units with no dependencies on other new units come first.
Shared utilities and service modules before their consumers. A consumer task may not be started
until all its dependency tasks are complete.

Record a short dependency note on each task: `depends on: [task names]` or `no new dependencies`.

---

### Step 3 — Test task per AC and testable NFR

For every `AC-<story>.<n>` and every testable `NFR-<n>` in the contracts/, add one test task.

**AC-ID → Vitest test-name convention (copy this into every test task description):**

> A test task maps to a Vitest `describe` / `it` pair following the pattern:
> ```
> describe('AC-<story>.<n>: <behavior summary>', () => {
>   it('<observable outcome>', () => { ... });
> });
> ```
> The describe label is the AC-ID and its behavior summary verbatim from the contract.
> Coverage is a grep query: `grep -r "AC-2.1" src/` must return the test file and the
> production unit. A test task is done when that grep returns both.

Each test task states:
- The AC-ID or NFR-ID it covers.
- The unit under test (component rendered via `render()` or hook via `renderHook`).
- The describe/it names to use (derived from the AC wording).
- Its exit check: the named describe/it exists, is not skipped, and passes in CI.

---

### Step 4 — Edge-case tasks

For each contract unit, enumerate the observable edge cases not already covered by an AC task:

- **Error state** — API failure / mutation error surface visible to the user.
- **Empty state** — zero-item list / null data rendered correctly.
- **Loading state** — pending indicators shown; no flash of wrong content.
- **Boundary** — prop/input at its documented limit behaves correctly.

Add one test task per edge case. Each edge case task traces to its contract unit and states
the observable assertion (what the user sees, not which mock was called).

---

### Step 5 — Exit checks and AC traceability on every task

Every task in tasks.md — implementation and test — must include:

1. **Traces to:** either an AC-ID (e.g. `AC-2.1`) or a contract file (e.g. `contracts/useDeviceFilters.md`).
2. **Exit check:** a concrete, verifiable condition that is true when the task is done. Examples:
   - Implementation: "Unit renders without TypeScript errors; contract public API satisfied."
   - Test: "`describe('AC-2.1: ...') { it('...') }` passes in CI; grep returns both test and source."
3. **No orphan tasks:** every task is traceable. A task with no AC-ID and no contract reference
   is not allowed — either assign it or delete it.

---

### Step 6 — Assemble tasks.md

Write `tasks.md` with sections:

```
## Implementation tasks
[ordered list, leaf-first, each with: unit, contract ref, depends-on, exit check, traces-to]

## Test tasks
[one per AC-ID + NFR-ID, each with: AC/NFR-ID, unit under test, describe/it names, exit check]

## Edge-case tasks
[one per edge case, each with: unit, edge case label, observable assertion, exit check]
```

Total task count is: (number of contract units) + (number of ACs + testable NFRs) + (edge cases per unit × units).
