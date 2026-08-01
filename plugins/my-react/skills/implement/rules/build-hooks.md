# Build hooks — authoring a custom hook

## One purpose, intent-named surface

A hook owns one concern; ≥2 of data-fetch / UI-state / lifecycle → split. Inputs are
controlled parameters (no hidden globals); the return is a fully-typed object with
intent-named fields — exactly the contract's signature, no `any`.

```ts
// ✗ grab-bag: fetches, filters, and manages a dialog
function useDevices() { /* query + filter state + modal flag */ }
// ✓ each hook one concern, composed by the component
function useDevices(): UseDevicesResult { /* query only */ }
function useDeviceFilters(devices: Device[], query: string): Device[] { /* derive */ }
```

## Stable returns

Identity stability is part of the hook's contract, not an optimization. An unstable
return is a **latent correctness bug**: harmless while nothing watches its identity, then
the first consumer that puts it in an effect's dep array loops ("Maximum update depth
exceeded") and every memo downstream is silently defeated. Without react-compiler,
deliver it manually — callbacks via `useCallback` with functional updates
(dependency-free where possible), derived objects/arrays via `useMemo`; with the compiler
configured, it memoizes these automatically and the manual wrappers are noise.

```ts
// ✗ fresh object + fresh callback every render
return { filters: { query, sort }, reset: () => setQuery('') }
// ✓
const reset = useCallback(() => setQuery(''), [])
return useMemo(() => ({ filters, reset }), [filters, reset])
```

## Own your teardown; survive StrictMode

Whatever the hook subscribes to, creates, or schedules, it tears down — and setup/teardown
must be idempotent across StrictMode's double-invoke (mount → unmount → mount must not
leak or double-subscribe).

```ts
useEffect(() => {
  const conn = createConnection(url)   // created per effect run
  return () => conn.destroy()          // destroyed per cleanup — pairs survive double-invoke
}, [url])
```

## Bridge external stores with useSyncExternalStore

A hook exposing a service/listenable value subscribes via `useSyncExternalStore` — never a
hand-rolled effect + setState (tearing, missed updates).

```ts
const positionMs = useSyncExternalStore(engine.subscribe, engine.getPosition)
```

## Exercisable in isolation

Runs under `renderHook` with controlled inputs and asserted returns — needing its host
component to stand up means the surface is wrong: lift the dependency into a parameter.

```ts
renderHook(() => useDeviceFilters({ devices: fixture, query: 'door' }))
```
