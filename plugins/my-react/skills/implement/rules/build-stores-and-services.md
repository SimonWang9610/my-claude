# Build stores and services — implementing the contract's shape

The contract fixed the state shape, actions, and lifecycle; these rules govern the bodies.

## Store actions are intent-named, defined in the store

Consumers call `focusDevice(id)`, never a raw `set` — mutation logic lives in the action
body, one place per invariant.

```ts
// ✗ component reaches in: store.set({ selectedId: id, panelOpen: true })
// ✓
create<DeviceState>()((set) => ({
  selectedId: null,
  panelOpen: false,
  focusDevice: (id: string) => set({ selectedId: id, panelOpen: true }),
}))
```

## Selectors return stable references

A selector minting a fresh object/array per call — `useStore(s => ({ a: s.a, b: s.b }))`,
`s => s.items.filter(...)` — is an infinite loop in Zustand v5 ("Maximum update depth
exceeded"): `useSyncExternalStore` sees a new snapshot every read, and v5 applies no
default equality. Wrap with `useShallow`, or select primitives one per call. A selector
returning a stored reference (`s => s.filters`) is already stable — don't flag.

## No server data in the store

The store holds keys/ids; entities resolve from the query cache at read time. An entity
copied into a store is stale after the first mutation.

## Persist by whitelist, versioned

`partialize` exactly the fields the contract marks persisted; set `version` + `migrate`.
Blanket persistence resurrects transient state after reload.

```ts
persist(config, { name: 'device-prefs', version: 2,
  partialize: (s) => ({ sortKey: s.sortKey }), migrate })
```

## Transient values subscribe outside render

A high-frequency fact consumed imperatively (canvas, video overlay) uses
`store.subscribe` in an effect/service — a selector hook renders per tick.

```ts
// vanilla subscribe(listener); the returned unsubscribe is the effect cleanup
useEffect(() => useDeviceStore.subscribe(s => draw(s.positionMs)), [draw])
```

## Service lifecycle is idempotent; errors are typed

`create<Service>(opts)` returns an instance owning its resources; `destroy()` releases
them and is safe to call twice; create-after-destroy works (StrictMode double-invoke,
retries). Failures throw the typed error union the contract names — never strings, never
swallowed catches.

## Coalesce high-frequency event streams

A service emitting per-frame/per-message throttles or batches before notifying React —
consumers get render-rate updates; the raw stream stays inside the service.

```ts
// ✗ socket.on('tick', ms => store.setPosition(ms))   // 60 store writes/s
// ✓ rAF-coalesced: latest value emitted at most once per frame
socket.on('tick', ms => { latest = ms; scheduleEmitOnce() })
```
