# React / TS detection heuristics

Grep/read recipes and before→after examples for each detection pass. Targets React + Vitest + RTL +
Zustand + TanStack Query. Grep commands narrow where to read — confirm every hit by reading the file.

Examples use a neutral "list + detail" feature (`DeviceListPage`, `useDevices`, `DeviceRecord`); substitute
your own surfaces.

---

## Behavior enumeration (Pass 1 input)

**Component** — open the file and enumerate:

```bash
# render branches: ternaries, && guards, early returns
grep -nE '\?|&&|return null|return <' <Component>.tsx | grep -vE '//'
# exposed handlers
grep -nE 'on[A-Z]\w+\s*[:=]' <Component>.tsx
```

**Hook** — side-effects and public surface:

```bash
grep -nE 'useEffect|useQuery|useMutation|useInfiniteQuery|subscribe|\.on\(' <hook>.ts
grep -nE 'return \{|return \[' <hook>.ts
```

**api / lib** — exported contracts and error paths:

```bash
grep -nE 'export (async )?function|export const \w+ = (async )?\(' <file>.ts
grep -nE 'catch|throw|assertOk|return (null|undefined|\{)' <file>.ts
```

A behavior that appears here with no criterion ID (`AC-<story>.<n>` / `NFR-<n>`) in `requirements.md` is
a `no-spec-coverage` (improvised) finding.

---

## Pass 2 shapes — `tests-pass-but-miss-behavior`

### Shape A — RTL render-without-assert (no triggering action)

```bash
grep -nE 'it\(|test\(' <file>.test.tsx          # locate test blocks
grep -nE 'fireEvent|userEvent|\.click\(|act\(' <file>.test.tsx  # check action present
# flag blocks that have render+getBy but no event call
```

```tsx
// MISS — names a sort behavior, never fires the click, checks a structural proxy
it('calls onSort with the column id', () => {
  render(<DataTable columns={cols} onSort={onSort} />)
  expect(screen.getAllByRole('columnheader').length).toBeGreaterThan(0)
})

// FIXED — fire the action, assert the observable outcome
it('AC-14.3: header click sorts by that column ascending', () => {
  render(<DataTable columns={cols} onSort={onSort} />)
  fireEvent.click(screen.getByRole('columnheader', { name: /name/i }))
  expect(screen.getByRole('columnheader', { name: /name/i }))
    .toHaveAttribute('aria-sort', 'ascending')
  expect(onSort).toHaveBeenCalledWith('name', 'asc')
})
```

### Shape B — Zustand/TanStack hook read without exercising the action

The test asserts a setter was called but not the side-effect the criterion names (e.g. cache invalidation).

```bash
grep -nE 'invalidateQueries|setQueryData|getState\(\)|\.mockReturnValue' <file>.test.tsx
```

```tsx
// MISS — asserts the setter; the criterion's behavior (cache invalidation) is never checked
expect(setScopeFilter).toHaveBeenCalledWith('site-a')

// FIXED — exercise through a real QueryClient and assert the invalidation
const client = new QueryClient()
const spy = vi.spyOn(client, 'invalidateQueries')
renderWithClient(<ScopeFilterToggle />, client)
fireEvent.click(screen.getByRole('switch', { name: /this site only/i }))
expect(spy).toHaveBeenCalledWith({ predicate: expect.any(Function) })
```

When the criterion's truth lives in the TanStack cache but the test asserts a shadow Zustand copy (or vice
versa), that is a **wrong-owner** finding — assert the authoritative owner.

### Shape C — `useEffect` / query lifecycle untested

```bash
grep -nE 'useEffect|refetchInterval|refetchOnWindowFocus|subscribe' <source>
grep -nE 'advanceTimersByTime|runAllTimers|fireEvent.focus|unmount\(\)' <file>.test.tsx
# if no hit in tests → lifecycle likely untested; confirm with mutation
```

### Shape D — `waitFor` / fake-timers masking timing

`waitFor` with a generous timeout hides a timing requirement (debounce, stagger, delayed retry).

```tsx
// MASKING — waitFor swallows a 500ms stagger criterion; passes at any timing
await waitFor(() => expect(panels).toHaveLength(4))

// FIXED — assert the timing deliberately with fake timers
vi.useFakeTimers()
render(<Grid items={four} />)
expect(screen.queryAllByTestId('frame')).toHaveLength(1)
act(() => vi.advanceTimersByTime(500))
expect(screen.queryAllByTestId('frame')).toHaveLength(2) // NFR-3: 500ms stagger
```

---

## Pass 3 forms — `false-positive`

### Form 1 — Tautology / arrange-act-no-assert

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

### Form 2 — Mock-shape drift (fixture shape != production TS type)

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

### Form 3 — Un-awaited write hidden by `mockResolvedValue`

```bash
grep -nE 'assertOk\(|return (this\.)?(post|put|patch|delete)\(' <source>.ts | grep -v 'await'
grep -nE 'mockResolvedValue|mockResolvedValueOnce' <file>.test.tsx
```

```ts
// BUG HIDDEN — assertOk not awaited; always-resolving mock means failure path never runs
async updateRecord(body) {
  const res = this.put('/records', body)
  assertOk(res)  // missing await
}

// CONFIRM false positive: mock a rejection — a correct test must fail
apiClient.put = vi.fn().mockRejectedValue(new Error('500'))
await expect(updateRecord(body)).rejects.toThrow()  // currently passes green
```

### Form 4 — CSS-class presence instead of resolved value

```bash
grep -nE 'toHaveClass\(|className.*toContain' <file>.test.tsx
```

JSDOM does not resolve CSS custom properties. `toHaveClass('bg-accent')` proves nothing about the rendered
color. Assert a value JSDOM can resolve (static hex, inline style the component computes) or move the
contract to a CI guard (Vitest source-grep / ESLint rule banning hardcoded hex).

```tsx
// FALSE POSITIVE — class presence; actual dark color never verified
expect(button).toHaveClass('bg-accent')

// BETTER — assert a value JSDOM resolves, or rely on a CI guard for the no-hardcoded-hex contract
expect(button).toHaveStyle({ color: 'rgb(252, 252, 252)' })
```

### Form 5 — Query-config never exercised (no real QueryClient)

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

// FIXED — real QueryClient; NFR would fail if config were removed
const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
const fetchSpy = vi.fn().mockResolvedValue(mockList)
it('NFR-3 AC-8.1: does not refetch on window focus (staleTime Infinity)', async () => {
  render(<QueryClientProvider client={client}><ListPage fetch={fetchSpy} /></QueryClientProvider>)
  await screen.findByText('Item')
  fetchSpy.mockClear()
  fireEvent.focus(window)
  await waitFor(() => expect(fetchSpy).not.toHaveBeenCalled())
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
