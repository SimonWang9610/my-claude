# Services and boundaries — one-way dependencies

## Dependencies point inward: ui → hooks/state → api/services

Feature folders expose one public entry point; no deep cross-feature imports. When a lower
unit must notify an upper one, invert with a callback/event so the arrow stays inward.

```ts
// ✗ a service importing a store — upward arrow, cycle risk
import { usePlaybackStore } from '../store'
// ✓ the service emits; the feature hook wires it inward
createPlayerEngine({ onPosition: ms => usePlaybackStore.getState().setPosition(ms) })
```

## Side effects live behind services

Imperative/stateful integrations (sockets, players, device/IPC bridges, timers) are service
units with create/destroy lifecycles, bridged to React by one dedicated hook. The service
boundary doubles as the testability seam.

```ts
// ✗ SDK instantiated inside a component effect — unswappable, leaks on unmount races
useEffect(() => { const hls = new Hls(); hls.loadSource(url) }, [url])
// ✓ a service owns the lifecycle; one hook bridges it to React
const player = useStreamPlayer(url)   // wraps services/streamPlayer.createStreamPlayer()
```

No central manager owning all state and interactions — that recreates God-unit coupling
under a new name. A central *service* is only for a genuinely shared imperative resource
behind a boundary.

## Parse at the boundary; errors are typed

External data (API responses, storage, URL params) is parsed by a schema **at the
boundary**; everything inward trusts the types — no defensive re-checking downstream.
Errors cross the boundary as a typed union the contract names (retryable vs fatal), so
each unit's `error` state maps to a concrete, testable shape — never a bare `unknown`.

```ts
// boundary owns the shape; consumers never see raw JSON
const DeviceSchema = z.object({ id: z.string(), name: z.string(), online: z.boolean() })
type DeviceError = { kind: 'network'; retryable: true } | { kind: 'forbidden'; retryable: false }
```

## Races have an owner

For async outside the query layer (service events, debounced search, param-driven
requests), the owning unit's contract declares: **who cancels** on unmount/param change,
and the **stale-response guard** — a late response for an old input must never overwrite
fresh state.

```ts
// ✓ the hook owns cancellation; stale responses are dropped at the seam
useEffect(() => {
  const ctl = new AbortController()
  search(query, ctl.signal).then(r => setResults(r))   // rejects on abort — never applies
  return () => ctl.abort()
}, [query])
```

## Contain failures deliberately

Decide per surface where error/suspense boundaries sit — which subtree fails or suspends
independently — so one failing widget never blanks the feature.

```tsx
// ✓ each tile fails/suspends alone; the grid survives
<ErrorBoundary fallback={<TileError />}>
  <Suspense fallback={<TileSkeleton />}><CameraTile id={id} /></Suspense>
</ErrorBoundary>
```
