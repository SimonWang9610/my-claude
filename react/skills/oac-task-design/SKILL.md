---
name: oac-task-design
description: >
  Turns an approved design.md + contracts/ into an ordered tasks.md: one buildable task per
  contract unit in leaf-first dependency order, one test task per AC (AC-<story>.<n>) and testable
  NFR, plus edge-case tasks (error/empty/loading/boundary) — every task carrying a Traces-to ref
  and a verifiable Exit check, no orphans. Use once the design and contracts are ready and the work
  needs breaking into a dependency-ordered build/test plan.
---

# oac-task-design

**Given** (paths the caller supplies): `design.md`, `contracts/` (one file per unit), and the
acceptance criteria (`AC-<story>.<n>`) + NFRs the design traces to.
**Produce:** `tasks.md` at the location the caller names — an ordered, fully traceable task list.

Complete every step below *before* writing `tasks.md`. Open a reference when you reach it.

## Procedure

### 1. One implementation task per contract unit
For each file in `contracts/`, emit exactly one implementation task. Record: the unit kind
(component / hook / store / service / API module), the contract file it implements, and its
dependencies. Never merge two units into one task; never split one unit across two.
→ `references/task-anatomy.md` for the exact field shape.

### 2. Order leaf-first by dependency
A unit that depends on no other *new* unit comes first; a consumer follows all its dependencies.
Services and shared utilities → hooks/stores → leaf components → container components/pages.
Tag each task `depends on: [task names]` or `no new dependencies`. A consumer task is not startable
until every dependency task is done.

```
apiClient (service) ─▶ useDeviceQuery (hook) ─┐
useDeviceFilters (store) ─────────────────────┴─▶ DeviceList ─▶ DeviceListPage
order: apiClient · useDeviceFilters → useDeviceQuery → DeviceList → DeviceListPage
```

### 3. One test task per AC + testable NFR
For every `AC-<story>.<n>` and every testable `NFR-<n>` the contracts trace to, emit one test task.
**Copy this convention verbatim into each test task** so the implementer wires traceability:

> Test maps to a Vitest `describe`/`it` pair:
> ```ts
> describe('AC-<story>.<n>: <behavior summary>', () => {
>   it('<observable outcome>', () => { /* render + assert user-visible result */ });
> });
> ```
> The `describe` label is the AC-ID + its behavior summary verbatim from the contract. Coverage is a
> grep: `grep -r "AC-2.1" src/` must return both the test and the production unit. Assert observable
> outcome (rendered text, accessible role/state, navigation) — never `toHaveBeenCalled` alone.

Each test task records: the AC/NFR-ID, the unit under test (`render()` a component or `renderHook`),
and the `describe`/`it` strings derived from the AC wording.

### 4. Edge-case tasks
For each unit, enumerate the observable edge cases no AC task already covers — error, empty, loading,
boundary — and emit one test task each with its user-visible assertion.
→ `references/edge-cases.md` for the per-unit-kind checklist + stack-specific triggers and assertions.

### 5. Traceability + Exit check on every task
Every task — implementation and test — carries both:
- **Traces to:** an AC/NFR-ID *or* a contract file. A task with neither is an **orphan** — assign it
  or delete it; never ship one.
- **Exit check:** a condition mechanically verifiable as true when done.
  - Impl: "compiles with no TS errors; contract public API + exposed states satisfied."
  - Test: "`describe('AC-2.1: …'){ it('…') }` present, not `.skip`, green in CI; `grep -r 'AC-2.1' src/` returns test + source."

### 6. Assemble + count-check
Write `tasks.md` with three sections — **Implementation** (leaf-first) · **Test (per AC/NFR)** ·
**Edge-case**. Then verify the count:

```
total tasks = (contract units) + (ACs + testable NFRs) + (Σ edge cases per unit)
```

If the count is off, a unit, AC, or edge case was dropped or duplicated — reconcile before finishing.
→ `references/task-anatomy.md` for a full worked `tasks.md`.

## References
- [`task-anatomy.md`](references/task-anatomy.md) — exact fields per task type + a complete worked
  `tasks.md`. Open in step 1 and step 6.
- [`edge-cases.md`](references/edge-cases.md) — which of error/empty/loading/boundary apply to each
  unit kind, the TanStack Query / Zustand / MUI trigger, and the RTL assertion to write. Open in step 4.
