# test-contract — rule detail with before→after examples

Six rules; all must pass before a test task is marked complete. Running example: a generic
`DeviceListPage` backed by `useDevices` (TanStack Query v5) and `useDeviceFilters` (Zustand).
External citations are links in `sources.md`.

## Contents

- [§1 — Clause→test mapping](#1--clausetest-mapping)
- [§2 — Outcome, not implementation](#2--outcome-not-implementation)
- [§3 — Production-typed fixtures](#3--production-typed-fixtures)
- [§4 — No tautology, no arrange-act-no-assert](#4--no-tautology-no-arrange-act-no-assert)
- [§5 — Real QueryClient for query-config NFRs](#5--real-queryclient-for-query-config-nfrs)
- [§6 — One-shot greps become enduring CI guards](#6--one-shot-greps-become-enduring-ci-guards)

---

## §1 — Clause→test mapping

**Statement.** Every `describe`/`it` label embeds the AC or NFR ID it covers, verbatim, so
`grep -r "AC-14.3" src/` returns both the test and the unit it exercises. A fully green suite
with unmapped tests is not a PASS for the ACs those tests could cover.

```ts
// BEFORE — identity unknown; "is AC-14.3 covered?" is unanswerable
it('should call onSort with correct column', () => { /* ... */ })

// AFTER — ID embedded verbatim; grep -r "AC-14.3" src/ returns this test + its unit
describe('AC-14.3: clicking a column header sorts the table by that column', () => {
  it('sorts ascending on first header click', () => { /* ... */ })
})
```

**Check.** For each AC/NFR ID the task covers, `grep -r "<ID>" src/` returns at least one
`describe`/`it` label, and that test runs green independently. (If the project tags tests,
`vitest run --tag <ID>` can filter the same way — but the grep is the coverage contract.)

**Anti-pattern.** A test named "calls onSort" carries no AC identity — coverage cannot be
queried, and "all green" proves nothing about which ACs are exercised.

---

## §2 — Outcome, not implementation

**Statement.** Assert rendered text, accessible role/state, navigation, or returned value.
`toHaveBeenCalled` alone is acceptable only for a side effect with no DOM representation, and
even then a user-visible assertion must accompany it. Drive interaction with
`userEvent.setup()` + `await user.*` — never bare `fireEvent`.

```tsx
// BEFORE — asserts the mock was called; passes even if the UI never updates
const user = userEvent.setup()
await user.click(header)
expect(onSort).toHaveBeenCalledWith('name', 'asc')

// AFTER — primary assertion is the observable result; the spy is secondary
const user = userEvent.setup()
await user.click(header)
expect(screen.getByRole('columnheader', { name: /name/i }))
  .toHaveAttribute('aria-sort', 'ascending')
expect(onSort).toHaveBeenCalledWith('name', 'asc')  // secondary, not sole
```

**Check.** No new test uses `toHaveBeenCalled()` as the sole assertion for a behavior that
renders something. Mutation test: invert the production condition — if the test still passes,
the assertion is a proxy.

**Anti-pattern.** A sort test asserting only `onSort` was called, or a card test asserting
`getByText(message)` where `message` is the exact prop passed in — neither can fail.

---

## §3 — Production-typed fixtures

**Statement.** Every fixture or stub is typed `satisfies <ProdType>`; every MSW handler is typed
with the production `ApiResponse<T>`. A shape that can drift silently from the production type
is a compile error waiting to be missed — force it to break at compile time instead.

```ts
// BEFORE — untyped literal; drifts silently when Device gains a required field
const mockDevice = { id: '1', name: 'Front Door', status: 'online' }

// AFTER — compile error the moment Device grows a required field this omits
import type { Device } from '@/lib/types/device'
const mockDevice = {
  id: '1', name: 'Front Door', status: 'online',
  firmwareVersion: '3.2.1', locationId: 'loc-42',
} satisfies Device

// MSW handler typed with the production response type
import { http, HttpResponse } from 'msw'
import type { DeviceListResponse } from '@/lib/types/api'
export const handlers = [
  http.get<never, never, DeviceListResponse>('/api/devices', () =>
    HttpResponse.json({ devices: [mockDevice], total: 1 }),
  ),
]
```

**Check.** No bare inline fixture literals; each is `satisfies <ProdType>` or returned by a
typed MSW handler. Adding a required field to the prod type must break the fixture at compile
time.

**Anti-pattern.** A hand-rolled fixture missing several production fields — any component branch
on those fields is untestable, and the omission is invisible until runtime.

---

## §4 — No tautology, no arrange-act-no-assert

**Statement.** Every test must be able to FAIL: at least one `expect()` exercises a path that
differs under different input; no assertion is a mathematical identity over the test's own
input; behavior ACs perform an action before asserting.

```tsx
// BEFORE — no expect(); green regardless of implementation
it('submits the filter form', async () => {
  const user = userEvent.setup()
  render(<DeviceFilterForm {...props} />)
  await user.click(screen.getByRole('button', { name: /apply/i }))
})

// AFTER — asserts the observable result of the submit action
it('AC-7.2: shows filtered count after filters are applied', async () => {
  const user = userEvent.setup()
  render(<DeviceFilterForm {...props} />)
  await user.click(screen.getByRole('button', { name: /apply/i }))
  expect(await screen.findByText(/3 devices match/i)).toBeInTheDocument()
})
```

**Check.** Grep the file for `it(`/`test(` blocks with no `expect` — any match is a FAIL. For
each remaining assertion, confirm the asserted value is not simply the input echoed back.

**Anti-pattern.** A test that renders and submits a form with zero `expect()` — green no matter
what the handler does.

---

## §5 — Real QueryClient for query-config NFRs

**Statement.** Any NFR naming a TanStack Query config value (`staleTime`, `gcTime`,
`refetchOnWindowFocus`, `retry`, `enabled`, …) must be asserted inside a real
`QueryClientProvider`. Mocking the hook bypasses the config — the NFR is never exercised.

```tsx
// BEFORE — mocks useQuery; refetchOnWindowFocus is never exercised
vi.mock('@tanstack/react-query', () => ({ useQuery: () => ({ data: mockData }) }))
it('NFR-3: data is not refetched on window focus', () => {
  render(<DeviceListPage />)
  expect(screen.getByText('Front Door')).toBeInTheDocument()
})

// AFTER — real QueryClient; the config is directly exercised
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
function renderWithQuery(ui: React.ReactElement, client: QueryClient) {
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>)
}

const fetchSpy = vi.spyOn(globalThis, 'fetch')
  .mockResolvedValue(new Response(JSON.stringify(mockDeviceList)))
it('NFR-3: does not refetch on window focus (refetchOnWindowFocus: false)', async () => {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
  })
  client.setQueryData(['devices'], mockDeviceList)
  renderWithQuery(<DeviceListPage />, client)
  act(() => window.dispatchEvent(new FocusEvent('focus')))
  expect(fetchSpy).toHaveBeenCalledTimes(0)
})
```

**Check.** For every query-config NFR, at least one test renders inside a real
`QueryClientProvider` and makes an assertion that would fail if the config value were removed.

**Anti-pattern.** A `staleTime` NFR whose only test mocks the query hook — the cache behavior the
NFR specifies is never run.

---

## §6 — One-shot greps become enduring CI guards

**Statement.** Any NFR phrased "no occurrences of X in source" must become a checked-in Vitest
assertion (glob + `expect`) or an ESLint rule. A one-shot PR-review grep is not enforcement — it
vanishes after merge.

```ts
// AFTER — resident Vitest guard checked in alongside the feature
// src/features/theming/__tests__/no-hardcoded-hex.test.ts
import { globSync } from 'glob'
import { readFileSync } from 'fs'

const HEX_PATTERN = /#[0-9a-fA-F]{3,6}\b/g
const COMPONENT_FILES = globSync('src/components/**/*.{ts,tsx}')

describe('NFR-1: no hardcoded hex colors in component files', () => {
  for (const file of COMPONENT_FILES) {
    it(`${file} contains no hardcoded hex literals`, () => {
      const matches = readFileSync(file, 'utf-8').match(HEX_PATTERN) ?? []
      expect(matches).toHaveLength(0)
    })
  }
})
```

Prefer an ESLint rule (`no-restricted-syntax`) when the pattern is expressible as a lint rule.

**Check.** For every "no occurrences of X" NFR, confirm a corresponding Vitest file or ESLint
rule entry exists. An NFR with no CI-resident guard is a FAIL.

**Anti-pattern.** An NFR banning hardcoded hex, satisfied once by a PR-review grep, then silently
regressed by a later commit with no CI step to catch it.
