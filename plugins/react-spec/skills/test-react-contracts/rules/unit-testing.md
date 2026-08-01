# Unit testing — harness per seam

Stack: Vitest + React Testing Library + MSW + user-event.

## The harness is the contract's Test seam

- **Component** → `render` with real providers (router, QueryClientProvider with test
  defaults: `retry: false`); drive with `user-event`; query by role/name.
- **Hook** → `renderHook` with controlled inputs; assert the returned surface; `rerender`
  for input changes.
- **Store** → call intent-named actions directly; assert state; `store.setState` only to
  arrange, never to assert.
- **Service** → instantiate via `create<Service>()` with fake transports/timers; assert
  emitted events and lifecycle.

Never mock the unit under test or its internals — a test whose behaviour lives inside a
mock exercises nothing. A unit that *needs* its host to run has a missing seam: raise it.

## Mock at the boundary the design named

Network via MSW handlers typed with production response types — not `vi.mock` of the api
module, not a mocked query hook (that bypasses the cache config NFRs specify). Config NFRs
(`staleTime`, `retry`, `refetchOnWindowFocus`) run against a **real QueryClientProvider**.

```ts
// ✗ vi.mock('../api/devices')                    // bypasses cache, key factory, config
// ✓ server.use(http.get('/api/devices', () => HttpResponse.json(fixture satisfies Device[])))
```

## Assert the contract's states

Every state in "States exposed" gets an assertion via its observable signal — loading
(skeleton role), error (`role="alert"`), empty, success — by role/name, the way a user
finds it.

```ts
server.use(http.get('/api/devices', () => HttpResponse.error()))
render(<DevicesPage />, { wrapper })
expect(await screen.findByRole('alert')).toHaveTextContent(/could not load/i)
```

## Async discipline

`await findBy*` / `waitFor` for anything crossing a tick — never a sleep. Debounce,
intervals, and retries run on fake timers, advanced explicitly and restored after.

```ts
vi.useFakeTimers()
await user.type(input, 'door')
await vi.advanceTimersByTimeAsync(300)   // the debounce the contract names
```

## Lifecycle & leak guards

The automatable half of the memory check — regression guards so leaks can't return:

- **Unmount tears down:** after `unmount()`, listeners are removed and `destroy` was
  called — assert the teardown, not just the absence of errors.
- **StrictMode survival:** mount the unit under `<StrictMode>`; double-invoke must not
  double-subscribe or leak (one active connection, not two).
- **Timers cleared:** `unmount(); expect(vi.getTimerCount()).toBe(0)`.

```ts
const { unmount } = renderHook(() => useStreamPlayer(url))
unmount()
expect(destroySpy).toHaveBeenCalledOnce()
expect(vi.getTimerCount()).toBe(0)
```
