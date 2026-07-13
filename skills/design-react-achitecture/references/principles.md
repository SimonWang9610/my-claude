# Architecture principles (R1–R11)

The complete rule set this skill applies — self-contained, no external rule files needed. Every rule
is a design-time decision recorded as a boundary or interface; the code samples show the smell and
its fix, not implementations to copy. Priority = the order below: state defects cost the most,
composition the least.

## State — who owns each fact

- **R1 · One owner per fact.** Every fact has exactly one authoritative owner; all other consumers
  derive it at read time. Never duplicate-and-sync — a side-effect whose job is "keep A equal to B"
  means deleting A or B, not improving the sync.

  ```ts
  // ✗ stored copy, kept aligned by an effect — drifts, extra render
  useEffect(() => setOnlineCount(devices.filter(d => d.online).length), [devices])
  // ✓ derive at read time
  const onlineCount = devices.filter(d => d.online).length
  ```

- **R2 · Server data lives in the server cache (TanStack Query).** Reads go through the query layer
  under one typed key scheme per domain. Each write declares its **invalidation graph** — the key
  families it invalidates or updates on success — and exposes an error state. A derived shape
  (filtered/sorted view) belongs to one named query hook, not per-consumer reshaping. Never copy
  server data into a client store, local state, or localStorage: hold the **key**, resolve the
  entity at read time.

  ```ts
  // ✗ effect-fetch traps data; the store copy goes stale after any write
  useEffect(() => { api.getDevices().then(d => store.setDevices(d)) }, [])
  // ✓ the query owns reads; the write declares what it invalidates
  useQuery({ queryKey: deviceKeys.list(), queryFn: api.getDevices })
  useMutation({ mutationFn: api.addDevice,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: deviceKeys.list() }) })
  ```

- **R3 · Narrowest tier that works** (tree below): component-local → lifted/context → URL params
  (reload-safe, shareable) → client store (client-only facts) → server cache. Never seed local state
  from a prop snapshot.

  ```tsx
  // ✗ prop snapshot — silently ignores later parent updates
  const [name, setName] = useState(device.name)
  // ✓ read the prop directly; for an editable draft, reset per entity by identity
  <DeviceEditForm key={device.id} device={device} />
  ```

- **R4 · Client stores hold one domain of discrete, UI-free facts.** One domain per store (slices
  for a large-but-coherent one); intent-named operations, not raw setters; only facts that change on
  user action — continuous/high-frequency values are emitted by their service. Persistence is
  whitelisted and versioned, never blanket. The store knows nothing of the view layer.

  ```ts
  // ✗ UI refs + view flags + a per-frame value in one store
  { videoRefs: Map<string, HTMLVideoElement>, showErrorToast: true, positionMs: 41712 }
  // ✓ one domain, intent-named ops, discrete facts; position stays in the service
  { selectedId: string | null, streamErrors: DeviceError[], focusDevice(id): void, exitFocus(): void }
  ```

- **R5 · No module-scope mutable state.** Cross-render accumulation (registries, controllers) lives
  in context, a store, or a ref — module-scope mutables leak across tests and users.

  ```ts
  // ✗ module-scope registry — shared across every consumer and test
  const controllers = new Map<string, AbortController>()
  // ✓ owned by the unit that accumulates it
  const controllers = useRef(new Map<string, AbortController>())
  ```

## Units — responsibility and verifiability

- **R6 · One responsibility per unit.** Components render; logic lives in named single-purpose
  hooks. A hook owning ≥2 of data-fetch / UI-state / lifecycle splits by concern. Soft ceilings
  ~400-line component / ~300-line hook — past them, split or record an exception with its reason.

  ```tsx
  // ✗ one tile owning connection mgmt + gestures + rendering
  function CameraTile() { /* fetch + 4 effects + handlers + 200 lines of JSX */ }
  // ✓ named hooks own the logic; the component composes them
  const stream = useStreamConnection(url)
  const ptz = usePtzGestures(id)
  return <TileLayout stream={stream} {...ptz.handlers} />
  ```

- **R7 · Every unit is independently verifiable.** A component exercisable via props/providers, a
  hook via controlled inputs, a service via its interface — never by standing up its host. A
  behaviour reachable only through its host has a missing seam: extract it into a named unit.

  ```ts
  // ✗ the behaviour under test lives inside the mock — the test exercises nothing
  vi.mock('../hooks/useDeviceScreen')
  // ✓ the extracted unit is exercised directly
  renderHook(() => useDeviceFilters({ devices, query }))
  ```

- **R8 · Compose, don't configure.** Extract logic into hooks; 3+ structural boolean props →
  recompose into parts; a multi-part widget = a parent owning shared state + part-components the
  caller orders; named slots for static content (a render callback only when the parent injects
  data the caller lacks); separate variant components instead of a `mode` prop.

  ```tsx
  // ✗ toggle soup — 2⁵ configurations nobody can verify
  <Tile hideControls showTimestamp compact noBorder isPtzEnabled />
  // ✓ the caller composes the parts it wants
  <Tile><Tile.Surface /><Tile.Timestamp />{cam.ptz && <Tile.PtzOverlay />}</Tile>
  ```

## Boundaries — direction and containment

- **R9 · Dependencies point one way: `ui → hooks/state → api/services`.** Feature folders with one
  public entry point; no deep cross-feature imports. When a lower unit must notify an upper one,
  invert with a callback/event so the arrow stays inward.

  ```ts
  // ✗ a service importing a store — upward arrow, cycle risk
  import { usePlaybackStore } from '../store'
  // ✓ the service emits; the feature hook wires it inward
  createPlayerEngine({ onPosition: ms => usePlaybackStore.getState().setPosition(ms) })
  ```

- **R10 · Side effects live behind services.** Imperative/stateful integrations (sockets, players,
  device/IPC bridges, timers) are service units with create/destroy lifecycles, bridged to React by
  one dedicated hook. The service boundary doubles as the testability seam (R7).

  ```ts
  // ✗ SDK instantiated inside a component effect — unswappable, leaks on unmount races
  useEffect(() => { const hls = new Hls(); hls.loadSource(url) }, [url])
  // ✓ a service owns the lifecycle; one hook bridges it to React
  const player = useStreamPlayer(url)   // wraps services/streamPlayer.createStreamPlayer()
  ```

- **R11 · Contain failures deliberately.** Decide per surface where error/suspense boundaries sit —
  which subtree fails or suspends independently — so one failing widget never blanks the feature.

  ```tsx
  // ✓ each tile fails/suspends alone; the grid survives
  <ErrorBoundary fallback={<TileError />}>
    <Suspense fallback={<TileSkeleton />}><CameraTile id={id} /></Suspense>
  </ErrorBoundary>
  ```

## Choosing an interaction mechanism

Pick the loosest coupling that carries it; reach for a heavier one only when the lighter cannot.

| Interaction | Mechanism |
|-------------|-----------|
| Server fact shared by many units | the shared query key — not prop-drilling, not a client copy |
| Parent ↔ child, local | props down, callbacks up |
| Client fact across an unrelated subtree | a store selector |
| React ↔ imperative resource / continuous stream | a service event, bridged by one hook |
| Cross-cutting client state with shared invariants | one feature-owned store |

No "central manager" owning all state and interactions — it recreates God-unit coupling under a new
name. A central *service* is only for a genuinely shared imperative resource behind a boundary.

## Where does a fact live?

```
Fetched from / owned by the server?
├─ yes → server cache (R2). Hold keys client-side; derive the entity at read time.
└─ no  → shared across unrelated components, or a persisted preference?
         ├─ yes → client store (R4).
         └─ no  → reload-safe / shareable (tab, filter, selected id)? → URL params (R3)
                  otherwise → component-local state or ref (R3, R5).
```
