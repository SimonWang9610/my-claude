# Task anatomy + worked `tasks.md`

## Field shape per task type

Every task is one checklist item with a fixed set of fields. Keep fields on their own lines.

### Implementation task
```
- [ ] Impl: <UnitName> (<kind>)
      Contract:   contracts/<file>.md
      Depends on: [<task names>] | no new dependencies
      Traces to:  contracts/<file>.md
      Exit check: compiles, no TS errors; contract public API + exposed states satisfied
```
`<kind>` ∈ component · hook · store (Zustand) · service · API module.

### Test task (per AC / testable NFR)
```
- [ ] Test: <AC-ID or NFR-ID> — <behavior summary>
      Under test: <UnitName>  (render() a component | renderHook a hook)
      Describe:   'AC-<story>.<n>: <behavior summary>'
      It:         '<observable outcome>'
      Traces to:  <AC-ID or NFR-ID>
      Exit check: describe/it present, not .skip, green in CI; grep -r '<AC-ID>' src/ returns test + source
```

### Edge-case task
```
- [ ] Edge: <UnitName> — <error | empty | loading | boundary>
      Assert:     <what the user sees — rendered text / role / disabled state>
      Traces to:  contracts/<file>.md   (the unit whose edge this is)
      Exit check: describe/it green in CI asserting the user-visible outcome
```

## Rules the shape enforces
- **No orphan** — every task has a `Traces to:` (AC/NFR-ID or a contract file). No trace ⇒ delete or assign.
- **Observable exit** — an Exit check is a command result or a green test, never "looks done".
- **One unit per impl task, one AC per test task** — keeps the count formula exact.

## Worked `tasks.md`
Feature: filterable device list. Contracts: `apiClient.md`, `useDeviceFilters.md`,
`useDeviceQuery.md`, `DeviceList.md`, `DeviceListPage.md`. ACs: `AC-1.1`, `AC-1.2`, `AC-2.1`.
NFR: `NFR-1` (list query `staleTime` = 30 s).

```markdown
## Implementation tasks  (leaf-first)
- [ ] Impl: apiClient (service)
      Contract: contracts/apiClient.md · Depends on: no new dependencies
      Traces to: contracts/apiClient.md
      Exit check: compiles, no TS errors; fetchDevices() returns Device[] per contract
- [ ] Impl: useDeviceFilters (store)
      Contract: contracts/useDeviceFilters.md · Depends on: no new dependencies
      Traces to: contracts/useDeviceFilters.md
      Exit check: compiles; store exposes { status, query, setStatus, setQuery } per contract
- [ ] Impl: useDeviceQuery (hook)
      Contract: contracts/useDeviceQuery.md · Depends on: [apiClient]
      Traces to: contracts/useDeviceQuery.md
      Exit check: compiles; returns { data, isPending, isError } with staleTime 30_000
- [ ] Impl: DeviceList (component)
      Contract: contracts/DeviceList.md · Depends on: [useDeviceQuery, useDeviceFilters]
      Traces to: contracts/DeviceList.md
      Exit check: compiles; renders loading / empty / error / list states the contract names
- [ ] Impl: DeviceListPage (component)
      Contract: contracts/DeviceListPage.md · Depends on: [DeviceList]
      Traces to: contracts/DeviceListPage.md
      Exit check: compiles; composes DeviceList + filter controls per contract

## Test tasks  (one per AC + testable NFR)
- [ ] Test: AC-1.1 — filtering by status narrows the list
      Under test: DeviceList (render) · Describe: 'AC-1.1: filtering by status narrows the list'
      It: 'shows only online devices when status filter is Online'
      Traces to: AC-1.1
      Exit check: green in CI; grep -r 'AC-1.1' src/ returns test + DeviceList
- [ ] Test: AC-1.2 — clearing filters restores the full list
      Under test: DeviceList (render) · Describe: 'AC-1.2: clearing filters restores the full list'
      It: 'shows every device after Clear filters is pressed'
      Traces to: AC-1.2 · Exit check: green in CI; grep -r 'AC-1.2' src/ returns test + source
- [ ] Test: AC-2.1 — selecting a device navigates to its detail
      Under test: DeviceListPage (render) · Describe: 'AC-2.1: selecting a device navigates to its detail'
      It: 'navigates to /devices/:id when a row is clicked'
      Traces to: AC-2.1 · Exit check: green in CI; grep -r 'AC-2.1' src/ returns test + source
- [ ] Test: NFR-1 — device list query caches for 30 s
      Under test: useDeviceQuery (renderHook in a real QueryClientProvider)
      Describe: 'NFR-1: device list query staleTime is 30s'
      It: 'does not refetch within 30s of a successful load'
      Traces to: NFR-1 · Exit check: green in CI; assertion runs against a real QueryClient

## Edge-case tasks
- [ ] Edge: DeviceList — error   · Assert: alert 'Could not load devices' is shown
      Traces to: contracts/DeviceList.md · Exit check: green in CI
- [ ] Edge: DeviceList — empty   · Assert: 'No devices match' message, no rows
      Traces to: contracts/DeviceList.md · Exit check: green in CI
- [ ] Edge: DeviceList — loading · Assert: skeleton/progressbar shown, no flash of empty
      Traces to: contracts/DeviceList.md · Exit check: green in CI
```

Count check: 5 units + (3 ACs + 1 NFR) + 3 edge cases = **12 tasks**. Matches the list above.
