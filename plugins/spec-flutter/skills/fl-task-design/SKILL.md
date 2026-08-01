---
name: fl-task-design
description: >
  Turns an approved design.md and contracts/ into tasks.md for a Flutter feature — one buildable
  task per unit in dependency order, a test task per acceptance criterion plus edge cases, with
  AC-ID traceability. Use after the design and contracts are approved and before
  implementation begins.
---

# fl-task-design

Turns a fixed, approved design into an ordered, traceable task list. The design and contracts
are already approved — this skill does not revisit architecture decisions.

---

## Procedure

### (a) One task per contract unit

Create one implementation task for every `contracts/<unit>.md`. Name the task after the unit
(e.g. `Implement DeviceRepository`, `Implement DeviceListNotifier`, `Implement DeviceListScreen`).
Each task must state its exit check: "exits when the unit's contract tests pass."

### (b) Order tasks by dependency (leaf-first)

Sequence tasks so that no task depends on a unit that has not yet been implemented:

1. **Pure domain models** — no dependencies; implement first.
2. **Services** — depend only on external HTTP/WS clients (not on repos or holders).
3. **Repositories** — depend on services and domain models.
4. **Notifiers / state holders** — depend on repositories.
5. **Leaf widgets and shared widgets** — depend only on domain models or primitive types.
6. **Composed screens / parent widgets** — depend on notifiers and leaf widgets.

When two units are at the same level and independent, they may be listed as parallel tasks.

### (c) One test task per AC and testable NFR

For every `AC-<story>.<n>` and testable `NFR-<n>` traced to a unit in its contract, add a
dedicated test task. Name the test task to match the AC-ID:

- `Test AC-1.1 — device list renders cached items on load`
- `Test NFR-2 — DeviceRepository retries up to 3 times on network error`

**AC-ID → Dart test-name convention (copy this inline — do not reference external files):**

A test task maps to a `group` / `test` / `testWidgets` name that contains the AC-ID as a
substring, so coverage is a single `grep` query or a `flutter test --plain-name` filter:

```dart
// widget test
testWidgets('AC-1.1 device list renders cached items on load', (tester) async { … });

// unit test
group('DeviceRepository', () {
  test('NFR-2 retries up to 3 times on network error', () async { … });
});
```

The `describe`/`group` label carries the unit name; the `test`/`testWidgets` label carries
the AC-ID and a plain-English behavior summary. Every AC-ID appears verbatim in exactly one
test label. Coverage check: `grep -r 'AC-1.1' test/` returns exactly one hit per AC.

### (d) Enumerate edge-case tasks

After the AC-driven test tasks, add tasks for predictable edge cases that the ACs do not
explicitly name:

- **Error state** — e.g. `Test error state — DeviceListNotifier surfaces repository failure`
- **Empty state** — e.g. `Test empty state — DeviceListScreen renders empty-list widget`
- **Loading state** — e.g. `Test loading state — DeviceListScreen shows skeleton during fetch`
- **Boundary / limit** — e.g. `Test boundary — repository rejects items beyond page limit`

Each edge-case task traces to the unit contract rather than an AC-ID.

### (e) Exit check and traceability on every task

Every task (implementation and test) must include:

- **Exit check** — the specific condition that makes the task done (a passing test name, a
  passing gate, a contract method that compiles and returns the right type).
- **Trace** — either an `AC-<story>.<n>` / `NFR-<n>` ID, or a reference to the unit contract
  (`contracts/<unit>.md`) if the task has no direct AC mapping.

### Output format

Write tasks as a numbered markdown list in `tasks.md`. Group them under headings that match the
dependency order from (b). Keep entries terse — facts only (unit names, exit checks, trace IDs,
contract paths), never sentences restating the contract:

```markdown
## Domain models
1. Implement DeviceModel — exit: `dart test` compiles; value-equality test passes. Trace: contracts/device-model.md

## Services
2. Implement DeviceApiClient — exit: unit test with fake HTTP client passes. Trace: contracts/device-api-client.md

## Repositories
3. Implement DeviceRepository — exit: unit tests pass. Trace: contracts/device-repository.md
4. Test AC-1.1 — device list renders cached items on load. Exit: `testWidgets('AC-1.1 …')` green. Trace: AC-1.1
5. Test NFR-2 — retries up to 3 times on network error. Exit: `test('NFR-2 …')` green. Trace: NFR-2

…
```
