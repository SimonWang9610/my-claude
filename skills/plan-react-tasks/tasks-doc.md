# Template — `tasks.md`

Four sections — Implementation (leaf-first) · Test · Edge-case · Parallel plan — closed by the
count check. Every task carries **Inputs · Depends on · Traces to · Gate**; the worked example
shows the shapes filled (gates abbreviated to their unit-specific items — the full gates below
still bind).

## Task shapes

```
- [ ] Impl: <UnitName> (<kind>, <MODIFY|NEW>)
      Inputs:     contracts/<file>.md (public API · exposed states · must-nots) + its unit-index row
      Depends on: [<impl task names>] | no new dependencies
      Traces to:  contracts/<file>.md · <the AC/NFR IDs on the contract's Traces-to line>
      Gate:       typechecks clean, no `any` in the public surface; API matches the contract
                  exactly; every exposed state reachable + observable; must-nots hold (grep/lint);
                  (MODIFY) listed importers unbroken; never edits its paired tests

- [ ] Test: <AC-ID or NFR-ID> — <description from the AC → Verification row>
      Inputs:     the row (level · location) · the owning contract's exposed states (the target)
      Depends on: same wave as Impl: <UnitName> — authored first, green once impl lands
      Traces to:  <AC-ID or NFR-ID>
      Gate:       observed RED before impl (failing on the behaviour, not on setup); green in CI,
                  no .skip/.only; describe carries '<ID>' verbatim — grep returns test + source;
                  asserts the contract's observable signal, a spy never sole (mutation litmus:
                  inverting the production condition turns it red); fixtures `satisfies` production
                  types; harness matches the level (config NFR → real QueryClientProvider ·
                  pattern ban → resident CI guard)

- [ ] Edge: <UnitName> — <error | empty | loading | boundary>
      Inputs:     the owning contract's exposed states (the signal to assert)
      Depends on: same wave as Impl: <UnitName>
      Traces to:  contracts/<file>.md
      Gate:       same as Test, with Traces-to naming the contract
```

## Worked example — "Devices" feature

From the design: DevicesPage (NEW), AddDeviceDrawer (NEW), useAddDevice (NEW), useDeviceSelection
(NEW), DeviceTable (MODIFY); useDevices and devicesApi are EXISTING — **no tasks**.
AC → Verification rows: AC-1.1, AC-2.1, NFR-3, NFR-1.

```markdown
## Implementation tasks  (leaf-first)
- [ ] Impl: useDeviceSelection (store, NEW)
      Inputs: contracts/use-device-selection.md · Depends on: no new dependencies
      Traces to: contracts/use-device-selection.md · AC-2.4
      Gate: compiles; exposes { selectedId, selectDevice, clear } per contract
- [ ] Impl: useAddDevice (hook, NEW)
      Inputs: contracts/use-add-device.md · Depends on: no new dependencies
      Traces to: contracts/use-add-device.md · AC-2.1
      Gate: compiles; mutation exposes error state; invalidates the device-list key on success
- [ ] Impl: DeviceTable (component, MODIFY)
      Inputs: contracts/device-table.md · Depends on: [useDeviceSelection]
      Traces to: contracts/device-table.md · AC-1.1, AC-2.4
      Gate: compiles; renders empty/populated/selected states; importer AlarmsPage unbroken
- [ ] Impl: AddDeviceDrawer (component, NEW)
      Inputs: contracts/add-device-drawer.md · Depends on: [useAddDevice]
      Traces to: contracts/add-device-drawer.md · AC-2.1
      Gate: compiles; renders form + error state per contract
- [ ] Impl: DevicesPage (component, NEW)
      Inputs: contracts/devices-page.md · Depends on: [DeviceTable, AddDeviceDrawer]
      Traces to: contracts/devices-page.md · AC-1.1, AC-2.1
      Gate: compiles; composes table + drawer per contract

## Test tasks  (one per AC → Verification row)
- [ ] Test: AC-1.1 — list renders sorted A→Z
      Inputs: row (component · DevicesPage.test.tsx) · DeviceTable exposed states
      Depends on: same wave as Impl: DevicesPage
      Traces to: AC-1.1 · Gate: green in CI; grep -r 'AC-1.1' src/ returns test + source
- [ ] Test: AC-2.1 — adding a device shows it in the list
      Inputs: row (component · DevicesPage.test.tsx) · AddDeviceDrawer exposed states
      Depends on: same wave as Impl: DevicesPage
      Traces to: AC-2.1 · Gate: green in CI; grep -r 'AC-2.1' src/ returns test + source
- [ ] Test: NFR-3 — no refetch on window focus
      Inputs: row (hook · real QueryClientProvider (T4) · useDevices.test.tsx)
      Depends on: no new dependencies (useDevices is EXISTING)
      Traces to: NFR-3 · Gate: green in CI against a real QueryClient
- [ ] Test: NFR-1 — no raw hex in source
      Inputs: row (CI guard (T5) · no-hardcoded-hex.test.ts)
      Depends on: no new dependencies
      Traces to: NFR-1 · Gate: resident glob-scan/ESLint guard runs on every CI change

## Edge-case tasks
- [ ] Edge: DeviceTable — empty
      Inputs: contract exposed states · Depends on: same wave as Impl: DeviceTable
      Traces to: contracts/device-table.md · Gate: green in CI — 'No devices' message, zero rows
- [ ] Edge: AddDeviceDrawer — error
      Inputs: contract exposed states · Depends on: same wave as Impl: AddDeviceDrawer
      Traces to: contracts/add-device-drawer.md · Gate: green in CI — error copy shown, form stays open
- [ ] Edge: DevicesPage — loading
      Inputs: contract exposed states · Depends on: same wave as Impl: DevicesPage
      Traces to: contracts/devices-page.md · Gate: green in CI — progressbar, no flash of empty

## Parallel plan  (units in a wave build concurrently, each with its test + edge tasks)
- Wave 1: useDeviceSelection · useAddDevice   (no new dependencies)
- Wave 2: DeviceTable · AddDeviceDrawer
- Wave 3: DevicesPage
```

**Count check:** 5 units + 4 AC → Verification rows + 3 edge cases = **12 tasks**. A mismatch means
a unit, criterion, or edge case was dropped or duplicated.
