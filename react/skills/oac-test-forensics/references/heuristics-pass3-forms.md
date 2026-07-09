# Pass 3 forms — false-positive

Grep/read recipes and before→after examples for Pass 3. Examples use a neutral "list + detail" feature
(`DeviceListPage`, `useDevices`, `DeviceRecord`).

## Form 1 — Tautology / arrange-act-no-assert

```bash
# blocks with no expect
awk '/it\(|test\(/{n=$0;b=""} /expect\(/{b="y"} /\}\)/{if(n && !b) print FILENAME": "n; n=""}' <file>.test.tsx
# tautology: getByText of the exact prop passed in
grep -nE 'getByText\((\w+)\)' <file>.test.tsx
```

```tsx
// TAUTOLOGY — asserts the prop passed in; cannot fail
render(<StatusBanner message={message} />)
expect(screen.getByText(message)).toBeInTheDocument()

// FIXED — assert a derived outcome the component is responsible for
render(<StatusBanner status={{ ...base, severity: 'error' }} />)
expect(screen.getByRole('alert')).toHaveTextContent(/connection lost/i)
```

## Form 2 — Mock-shape drift (fixture shape != production TS type)

```bash
grep -nE 'const \w*(mock|fixture|stub)\w* = \{' <file>.test.tsx | grep -v 'satisfies'
grep -nE 'mockResolvedValue\(\{|mockReturnValue\(\{' <file>.test.tsx
```

```ts
// DRIFT — omits a field the permission branch reads; branch never runs
const mockRecord = { id: '1', name: 'Front Door', online: true }

// FIXED — typed with satisfies; omitting a required field is a compile error
import type { DeviceRecord } from '@/lib/types/device'
const mockRecord = {
  id: '1', name: 'Front Door', online: true,
  scopeId: 'site-7', permissions: [],
} satisfies DeviceRecord
```

## Form 3 — Un-awaited write hidden by `mockResolvedValue`

```bash
grep -nE 'assertOk\(|return (this\.)?(post|put|patch|delete)\(' <source>.ts | grep -v 'await'
grep -nE 'mockResolvedValue|mockResolvedValueOnce' <file>.test.tsx
```

```ts
// BUG HIDDEN — assertOk not awaited; always-resolving mock means the failure path never runs
async updateRecord(body) {
  const res = this.put('/records', body)
  assertOk(res)  // missing await
}

// CONFIRM false positive: mock a rejection — a correct test must fail
apiClient.put = vi.fn().mockRejectedValue(new Error('500'))
await expect(updateRecord(body)).rejects.toThrow()  // currently passes green
```

## Form 4 — CSS-class presence instead of resolved value

JSDOM does not resolve CSS custom properties, so `toHaveClass('bg-accent')` proves nothing about the
rendered color. Assert a value JSDOM can resolve (static hex, an inline style the component computes),
or move the contract to a CI guard (Vitest source-grep / ESLint rule banning hardcoded hex — Rule 6).

```bash
grep -nE 'toHaveClass\(|className.*toContain' <file>.test.tsx
```

```tsx
// FALSE POSITIVE — class presence; actual dark color never verified
expect(button).toHaveClass('bg-accent')

// BETTER — assert a value JSDOM resolves, or rely on a CI guard for the no-hardcoded-hex contract
expect(button).toHaveStyle({ color: 'rgb(252, 252, 252)' })
```

## Form 5 — Query-config never exercised (no real QueryClient)

```bash
grep -nE "vi\.mock\(.*react-query|vi\.mock\(.*useQuery|mockReturnValue\(\{ data" <file>.test.tsx
grep -nE 'QueryClientProvider|new QueryClient' <file>.test.tsx  # expect a hit; none = suspect
```

```tsx
// FALSE POSITIVE — hook mocked; staleTime/refetchOnWindowFocus never exercised
vi.mock('@tanstack/react-query', () => ({ useQuery: () => ({ data: mockData }) }))
it('NFR-3: does not refetch on focus', () => {
  render(<ListPage />)
  expect(screen.getByText('Item')).toBeInTheDocument()  // proves nothing about config
})

// FIXED — real QueryClient per test; the NFR would fail if the config were removed
it('NFR-3 AC-8.1: does not refetch on window focus (staleTime Infinity)', async () => {
  const fetchSpy = vi.fn().mockResolvedValue(mockList)
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(<QueryClientProvider client={client}><ListPage fetch={fetchSpy} /></QueryClientProvider>)
  await screen.findByText('Item')   // wait for initial load
  fetchSpy.mockClear()
  fireEvent.focus(window) // window/document events have no userEvent equivalent — bare fireEvent is the accepted exception
  await Promise.resolve()  // let any async refetch start, then assert it did not
  expect(fetchSpy).not.toHaveBeenCalled()
})
```

---

## Matcher misuse (false-positive amplifier across passes)

```bash
grep -nE '\.toContain\(' <file>.test.tsx | grep -vE 'className|textContent|string'
grep -nE 'getByRole|getByText' <file>.test.tsx | grep 'toBeTruthy'
grep -nE 'toBeGreaterThanOrEqual|>=' <file>.test.tsx
```

- `toContain` on a single `HTMLElement` — use `toContainElement`.
- `toBeTruthy()` on a `getBy*` result — the query already throws if absent; `toBeTruthy` is dead code.
- `toBeGreaterThanOrEqual(N)` / `>= N` count assertions — a stale-data regression still passes.

Usually **medium** confidence unless you confirm the operand type makes the matcher a no-op (**high**).
