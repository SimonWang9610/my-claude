# State ownership — where a fact lives and its concrete design

## Decision tree — where does a fact live?

```
Fetched from / owned by the server?
├─ yes → server cache (query hook). Hold keys client-side; derive the entity at read time.
└─ no  → shared across unrelated subtrees, or a persisted preference?
         ├─ yes → client store.
         └─ no  → reload-safe / shareable (tab, filter, selected id)? → URL params
                  └─ no → shared within one subtree, with invariants? → lifted state / context provider
                          └─ no → component-local (useState/useReducer; useRef when it never renders)
```

Always the **narrowest tier that holds the fact** — reach for a heavier one only when the
lighter cannot carry it.

**URL-addressable state:** decide at design time which UI states deserve a URL — tab,
filter, sort, selected entity, wizard step, and whether a modal is a route. A URL-held
state gets back-button and deep-link behavior for free; a state that should have been
URL-held is unfixable later without rework. The URL is the owner then — no mirrored copy
in a store.

## One owner per fact

Every fact has exactly one authoritative owner; all other consumers derive it at read time.
An effect whose job is "keep A equal to B" means deleting A or B, not improving the sync.

```ts
// ✗ mirrored copy, synced by an effect — drifts, extra render
useEffect(() => setOnlineCount(devices.filter(d => d.online).length), [devices])
// ✓ derive at read time
const onlineCount = devices.filter(d => d.online).length
```

Never seed local state from a prop snapshot — it silently ignores later parent updates:

```tsx
// ✗ const [name, setName] = useState(device.name)
// ✓ read the prop; for an editable draft, reset by identity
<DeviceEditForm key={device.id} device={device} />
```

## Server facts → server cache

Reads go through query hooks under one typed key scheme per domain; each write declares the
keys it invalidates or updates. Never copy server data into a store or local state — hold
the key, resolve at read time.

```ts
useQuery({ queryKey: deviceKeys.list(), queryFn: api.getDevices })
useMutation({ mutationFn: api.addDevice,
  onSuccess: () => queryClient.invalidateQueries({ queryKey: deviceKeys.list() }) })
```

**Every write contract declares its semantics** — "who refetches after save" must never be
ambiguous:

- **Invalidate-and-refetch** (default): simple, always consistent; UI shows pending until
  the refetch lands.
- **Optimistic update**: only when the UX demands instant feedback; the contract must then
  also declare the **rollback** (restore the snapshot on error) and the error signal shown.
- **Concurrent writes** to the same entity: name the policy — last-write-wins, disable
  while pending, or server version check surfaced as a conflict error.

```ts
// optimistic contract = update + rollback + settle, declared together
useMutation({ mutationFn: api.renameDevice,
  onMutate: async (next) => { /* snapshot + optimistic cache write */ },
  onError: (_e, _v, ctx) => queryClient.setQueryData(deviceKeys.detail(id), ctx.prev),
  onSettled: () => queryClient.invalidateQueries({ queryKey: deviceKeys.detail(id) }) })
```

## Concrete state designs — pick by fact profile

| Fact profile | Concrete design |
|--------------|-----------------|
| Local, ephemeral (input draft, open flag) | `useState` / `useReducer` in the component |
| Transient, never renders (timer id, last pointer position) | `useRef` |
| One behaviour reused by several components | custom hook owning its own state, exposing an intent-named API |
| Shared within one subtree, with invariants | context provider owning the state; consumers see `{ state, actions }` |
| Client-only facts across unrelated subtrees; persisted preferences | store slice — one domain, intent-named actions, narrow selectors, UI-free |
| Continuous / high-frequency / imperative source (playback position, socket) | listenable class or service (emitter/observable) + one bridging hook — per-frame values never enter React state |
| Server-owned entities | query hook + key factory + mutation invalidation |

The provider is the only place that knows how shared state is implemented — consumers can't
tell `useState` from a store behind the interface, so the design can change without them:

```tsx
const FiltersCtx = createContext<{ state: Filters; actions: FilterActions } | null>(null)
```

A listenable service emits outside React; one hook bridges it in:

```ts
const engine = createPlayerEngine({ onPosition: ms => emitter.emit('position', ms) })
const positionMs = useSyncExternalStore(subscribeToPosition, getPosition)
```

Store slices hold discrete, UI-free facts with intent-named actions — never raw setters,
view flags, or element refs:

```ts
// ✗ { videoRefs: Map<string, HTMLVideoElement>, showErrorToast: true, positionMs: 41712 }
// ✓ { selectedId: string | null, focusDevice(id): void, exitFocus(): void }
```

No module-scope mutable state — registries and controllers live in a ref, context, or
store; module scope leaks across tests and users.
