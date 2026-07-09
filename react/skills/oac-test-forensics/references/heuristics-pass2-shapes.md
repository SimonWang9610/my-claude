# Pass 2 shapes — tests-pass-but-miss-behavior

Grep/read recipes and before→after examples for Pass 2. Targets React 19 + Vitest + RTL + Zustand +
TanStack Query v5. Greps narrow where to read — confirm every hit by reading the file. Examples use a
neutral "list + detail" feature (`DeviceListPage`, `useDevices`, `DeviceRecord`).

## Shape A — RTL render-without-assert (no triggering action)

```bash
grep -nE 'it\(|test\(' <file>.test.tsx                                # locate test blocks
grep -nE 'userEvent\.setup|fireEvent|\.click\(|act\(' <file>.test.tsx # is an action present?
# flag blocks that render + getBy but fire no event
```

```tsx
// MISS — names a sort behavior, never fires the click, checks a structural proxy
it('calls onSort with the column id', () => {
  render(<DataTable columns={cols} onSort={onSort} />)
  expect(screen.getAllByRole('columnheader').length).toBeGreaterThan(0)
})

// FIXED — fire the action with userEvent (pointer + keyboard fidelity), assert the observable outcome
it('AC-14.3: header click sorts by that column ascending', async () => {
  const user = userEvent.setup()
  render(<DataTable columns={cols} onSort={onSort} />)
  await user.click(screen.getByRole('columnheader', { name: /name/i }))
  expect(screen.getByRole('columnheader', { name: /name/i }))
    .toHaveAttribute('aria-sort', 'ascending')
  expect(onSort).toHaveBeenCalledWith('name', 'asc')
})
```

## Shape B — Zustand/TanStack read without exercising the action (wrong owner)

The test asserts a setter was called but not the side-effect the criterion names (e.g. cache
invalidation). When the criterion's truth lives in the TanStack cache but the test asserts a shadow
Zustand copy (or vice versa), that is a **wrong-owner** finding — assert the authoritative owner.

```bash
grep -nE 'invalidateQueries|setQueryData|getState\(\)|\.mockReturnValue' <file>.test.tsx
```

```tsx
// MISS — asserts the setter; the criterion's behavior (cache invalidation) is never checked
expect(setScopeFilter).toHaveBeenCalledWith('site-a')

// FIXED — exercise through a real QueryClient and assert the invalidation
it('AC-7.2: toggling scope filter invalidates the query cache', async () => {
  const user = userEvent.setup()
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const spy = vi.spyOn(client, 'invalidateQueries')
  renderWithClient(<ScopeFilterToggle />, client)
  await user.click(screen.getByRole('switch', { name: /this site only/i }))
  expect(spy).toHaveBeenCalledWith({ predicate: expect.any(Function) })
})
```

## Shape C — `useEffect` / query lifecycle untested

```bash
grep -nE 'useEffect|refetchInterval|refetchOnWindowFocus|subscribe' <source>
grep -nE 'advanceTimersByTime|runAllTimers|fireEvent.focus|unmount\(\)' <file>.test.tsx
# no hit in tests → lifecycle likely untested; confirm with a mutation
```

## Shape D — `waitFor` / fake-timers masking timing

`waitFor` with a generous timeout hides a timing requirement (debounce, stagger, delayed retry) — it
passes at any timing.

```tsx
// MASKING — waitFor swallows a 500ms stagger criterion
await waitFor(() => expect(panels).toHaveLength(4))

// FIXED — assert the timing deliberately with fake timers
vi.useFakeTimers()
render(<Grid items={four} />)
expect(screen.queryAllByTestId('frame')).toHaveLength(1)
await act(async () => { vi.advanceTimersByTime(500) })
expect(screen.queryAllByTestId('frame')).toHaveLength(2) // NFR-3: 500ms stagger
```
