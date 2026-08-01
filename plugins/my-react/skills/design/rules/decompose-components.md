# Decompose components — right-sized units

## One responsibility per unit

Components render; logic lives in named single-purpose hooks. A hook owning ≥2 of
data-fetch / UI-state / lifecycle splits by concern.

```tsx
// ✗ one tile owning connection mgmt + gestures + rendering
function CameraTile() { /* fetch + 4 effects + handlers + 200 lines of JSX */ }
// ✓ named hooks own the logic; the component composes them
const stream = useStreamConnection(url)
const ptz = usePtzGestures(id)
return <TileLayout stream={stream} {...ptz.handlers} />
```

## Compose, don't configure

3+ structural boolean props → recompose into parts the caller orders; separate variant
components instead of a `mode` prop; children for composition — a render callback only when
the parent injects data the caller lacks.

```tsx
// ✗ toggle soup — 2⁵ configurations nobody can verify
<Tile hideControls showTimestamp compact noBorder isPtzEnabled />
// ✓ the caller composes the parts it wants
<Tile><Tile.Surface /><Tile.Timestamp />{cam.ptz && <Tile.PtzOverlay />}</Tile>
```

## Independently verifiable

Every unit must be exercisable via its own surface — a component via props/providers, a
hook via controlled inputs, a service via its interface — never by standing up its host. A
behaviour reachable only through its host has a missing seam: extract it into a named unit.

```ts
// ✗ the behaviour under test lives inside a mock — nothing is exercised
vi.mock('../hooks/useDeviceScreen')
// ✓ the extracted unit is exercised directly
renderHook(() => useDeviceFilters({ devices, query }))
```

## Right-size the cut — blast radius first

Splitting and merging are design changes with their own blast radius; never apply them
blindly. Before any cut:

- **Name the payoff** — which rule it satisfies or which AC it isolates. No payoff, no cut.
- **Count the importers forced to change.** A split that ripples through N callers, or a
  merge that couples unrelated responsibilities, is worse than the smell it fixes — keep
  the seam and record the debt instead.
- **Keep the cut inside the current scope** — one unit or one interface. A cut that leaks
  beyond it is an Open item for the caller, not a silent refactor.

Soft ceilings (~400-line component, ~300-line hook) are signals to evaluate, not triggers
to cut.

## Performance boundaries are design decisions

Design decides **where**, implementation decides how:

- **Code-split points** — lazy-load routes and heavy optional widgets (editors, players,
  chart libs); the split point is a unit boundary, name it in the architecture.
- **Containment for expensive subtrees** — a memo boundary is an architecture seam: the
  contract on that boundary must promise stable props, or the memo is a lie.
- **Unbounded lists virtualize** — any list whose length the server controls gets a
  virtualization boundary; decide it now, retrofitting one reshapes the component tree.
