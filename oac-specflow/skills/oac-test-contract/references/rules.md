# test-contract — rule detail with before→after examples

Six rules; all must pass before a test task is marked complete. The running example uses a generic `DeviceListPage` backed by `useDevices` (TanStack Query) and `useDeviceFilters` (Zustand). External citations are links in `sources.md`.

---

## §1 — Clause→test mapping

**Statement.** Every `describe`/`it` string names the AC or NFR ID it covers. A fully green suite with unmapped tests is not a PASS for the ACs those tests could cover.

```ts
// BEFORE — identity unknown; "is AC-14.3 covered?" is unanswerable
it('should call onSort with correct column', () => { /* ... */ })

// AFTER — clause named; `vitest run --tag AC-14.3` returns this test
describe('AC-14.3: table column header click sorts by that column', () => {
  it('fires sort with column id and direction on header click', () => { /* ... */ })
})
```

**Check.** Grep the test file for the AC IDs the task covers; every ID must appear in at least one `describe`/`it` label and that test must be independently runnable and green.

**Anti-pattern.** A test named "calls onSort" carries no AC identity — coverage cannot be queried, and "all green" proves nothing about which ACs are exercised.

---

## §2 — Outcome, not implementation

**Statement.** Assert rendered text, accessible role/state, or returned value. `toHaveBeenCalled` alone is acceptable only for side effects with no DOM representation; a user-visible assertion must accompany it.

```tsx
// BEFORE — asserts the mock was called; passes even if the UI never updates
fireEvent.click(header)
expect(onSort).toHaveBeenCalledWith('name', 'asc')

// AFTER — primary assertion is the observable result
fireEvent.click(header)
expect(screen.getByRole('columnheader', { name: /name/i }))
  .toHaveAttribute('aria-sort', 'ascending')
expect(onSort).toHaveBeenCalledWith('name', 'asc')  // secondary
```

**Check.** No new test uses `toHaveBeenCalled()` alone for a behavior that renders something. Apply the mutation mindset: "If I invert this condition in production, does this test fail?" — if not, the assertion is a proxy or tautology.

**Anti-pattern.** A sort test asserting only `onSort` was called, or a card test asserting `getByText(message)` where `message` is the exact prop passed in — can never fail.

---

## §3 — Production-shaped fixtures

**Statement.** Every mock object or stub is typed with `satisfies <ProdType>`. MSW handlers are typed with production `ApiResponse<T>` types. A fixture whose shape can drift silently from the production type is not acceptable.

```ts
// BEFORE — untyped literal; drifts silently when Device gains a required field
const mockDevice = { id: '1', name: 'Front Door', status: 'online' }

// AFTER — compile error if Device grows a required field this object omits
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

**Check.** No bare inline fixture literals; each is `satisfies <ProdType>` or returned by a typed MSW handler. Adding a required field to the prod type must break the fixture at compile time.

**Anti-pattern.** A hand-rolled fixture missing several production fields — any component branch on those fields is untestable.

---

## §4 — No tautologies, no arrange-act-no-assert

**Statement.** Every test must be able to FAIL: at least one `expect()` exercises a path that differs under different input; no assertion is a mathematical identity over the test's own input; behavior ACs perform an action before asserting.

```tsx
// BEFORE — no expect(); green regardless of implementation
it('submits the filter form', async () => {
  render(<DeviceFilterForm {...props} />)
  fireEvent.click(screen.getByRole('button', { name: /apply/i }))
})

// AFTER — asserts the observable result of the submit action
it('AC-7.2: shows filtered count after filters are applied', async () => {
  render(<DeviceFilterForm {...props} />)
  fireEvent.click(screen.getByRole('button', { name: /apply/i }))
  expect(await screen.findByText(/3 devices match/i)).toBeInTheDocument()
})
```

**Check.** Grep the test file for `it(`/`test(` blocks containing no `expect`. Any match is a FAIL.

**Anti-pattern.** A test that renders and submits a form with zero `expect()` — green no matter what the handler does.

---

## §5 — Real QueryClient for query-config NFRs

**Statement.** Any NFR naming a TanStack Query config value (`staleTime`, `gcTime`, `refetchOnWindowFocus`, `retry`, `enabled`, …) must be asserted inside a real `QueryClientProvider`. Mocking the hook bypasses the config; the NFR is never exercised.

```tsx
// BEFORE — mocks useQuery; staleTime is never exercised
vi.mock('@tanstack/react-query', () => ({ useQuery: () => ({ data: mockData }) }))
it('NFR-3: data is not refetched on window focus', () => {
  render(<DeviceListPage />)
  expect(screen.getByText('Front Door')).toBeInTheDocument()
})

// AFTER — real QueryClient; config is directly exercised
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
function renderWithQuery(ui: React.ReactElement, client: QueryClient) {
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>)
}

it('NFR-3: does not refetch on window focus (staleTime = Infinity)', async () => {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  client.setQueryData(['devices'], mockDeviceList)
  renderWithQuery(<DeviceListPage />, client)
  fireEvent.focus(window)
  await waitFor(() => { expect(fetchSpy).toHaveBeenCalledTimes(0) })
})
```

**Check.** For every query-config NFR, at least one test renders inside a real `QueryClientProvider` and makes an assertion that would fail if the config value were removed.

**Anti-pattern.** A staleTime NFR whose only test mocks the query hook — the cache behavior the NFR specifies is never run.

---

## §6 — One-shot greps become enduring CI guards

**Statement.** Any NFR phrased as "no occurrences of X in source" must become either a checked-in Vitest assertion (glob + `expect`) or an ESLint rule. A one-shot PR-review grep is not sufficient.

```ts
// BEFORE — one-shot grep; enforcement disappears after merge

// AFTER — Vitest guard checked in alongside the feature
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

Alternatively, add an ESLint rule (`no-restricted-syntax`) when the pattern is expressible as a lint rule.

**Check.** For every "no occurrences of X" NFR, confirm a corresponding Vitest file or ESLint rule entry exists. An NFR with no CI-resident guard is a FAIL.

**Anti-pattern.** An NFR banning hardcoded hex, satisfied once by a PR-review grep, then silently regressed by a later bugfix commit with no CI step to catch it.
