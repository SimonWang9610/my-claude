---
name: oac-task-design
description: >
  Turns an approved design.md + contracts/ into an ordered tasks.md: one buildable task per
  contract unit in leaf-first dependency order, one test task per AC (AC-<story>.<n>) and testable
  NFR, plus edge-case tasks (error/empty/loading/boundary) — every task carrying a Traces-to ref
  and a verifiable Exit check, no orphans — then groups independent units into parallel waves so
  implementation runs them concurrently. Use once the design and contracts are ready and the work
  needs breaking into a dependency-ordered, parallel-wave build/test plan.
---

# oac-task-design

**Given** (paths the caller supplies): `design.md`, `contracts/` (one file per unit), and the
acceptance criteria (`AC-<story>.<n>`) + NFRs the design traces to.
**Produce:** `tasks.md` at the location the caller names — an ordered, fully traceable task list.

Complete every step below *before* writing `tasks.md`. Open a reference when you reach it.

## Procedure

### 1. One implementation task per contract unit
For each file in `contracts/`, emit exactly one implementation task. Never merge two units into
one task; never split one unit across two.
→ `references/task-anatomy.md` for the exact field shape.

### 2. Order leaf-first by dependency
A unit that depends on no other *new* unit comes first; a consumer follows all its dependencies.
Services and shared utilities → hooks/stores → leaf components → container components/pages.
Tag each task `depends on: [task names]` or `no new dependencies`. A consumer task is not startable
until every dependency task is done.
→ `references/task-anatomy.md` for a worked dependency chain.

### 2b. Derive the parallel-wave plan
From the `depends on:` edges, group units into build **waves**: Wave 1 = every unit with
`no new dependencies`; Wave *n* = every unit whose dependencies all complete in earlier waves.
Units in the same wave share no dependency path, so implementation builds them concurrently (one
Work/Test pair each). Maximize width — drop each unit to the earliest wave its dependencies allow.
→ `references/task-anatomy.md` for a worked wave grouping.

### 3. One test task per AC + testable NFR
For every `AC-<story>.<n>` and every testable `NFR-<n>` the contracts trace to, emit one test task.
Use the exact Describe/It fields from `references/task-anatomy.md` so `grep -r "AC-2.1" src/`
returns both test and source — copy the AC-ID and its behavior summary verbatim from the contract.
Assert the observable outcome (rendered text, accessible role/state, navigation), never
`toHaveBeenCalled` alone.

### 4. Edge-case tasks
For each unit, enumerate the observable edge cases no AC task already covers — error, empty, loading,
boundary — and emit one test task each with its user-visible assertion.
→ `references/edge-cases.md` for the per-unit-kind checklist + stack-specific triggers and assertions.

### 5. Traceability + Exit check on every task
Every task — implementation, test, and edge-case — carries both:
- **Traces to:** an AC/NFR-ID *or* a contract file. A task with neither is an **orphan** — assign it
  or delete it; never ship one.
- **Exit check:** a condition mechanically verifiable as true when done — see
  `references/task-anatomy.md` for the exact impl/test check strings.

### 6. Assemble + count-check
Write `tasks.md` with four sections — **Implementation** (leaf-first) · **Test (per AC/NFR)** ·
**Edge-case** · **Parallel plan** (the waves from step 2b). Then verify the count:

```
total tasks = (contract units) + (ACs + testable NFRs) + (Σ edge cases per unit)
```

If the count is off, a unit, AC, or edge case was dropped or duplicated — reconcile before finishing.
→ `references/task-anatomy.md` for a full worked `tasks.md`.

## References
- [`task-anatomy.md`](references/task-anatomy.md) — exact fields per task type + a complete worked
  `tasks.md`. Open at each step above that points to it.
- [`edge-cases.md`](references/edge-cases.md) — which of error/empty/loading/boundary apply to each
  unit kind, the TanStack Query / Zustand / MUI trigger, and the RTL assertion to write. Open in step 4.
