# Use hooks — correctness when calling them

## Effects synchronize with the outside world — nothing else

An effect exists only to subscribe/attach/sync with something external, and every
subscription returns its teardown. Interaction logic goes in event handlers, not effects.

```tsx
// ✗ listener leaks on every re-run
useEffect(() => { player.on('error', onErr) }, [player])
// ✓ teardown matches the subscription
useEffect(() => {
  player.on('error', onErr)
  return () => player.off('error', onErr)
}, [player, onErr])
```

## Derive, don't mirror

A value computable from state/props is computed in render (or `useMemo`) — never mirrored
into state by an effect. The fix is deletion, not memoization.

```tsx
// ✗ double-renders a stale frame, drifts
useEffect(() => setFullName(`${first} ${last}`), [first, last])
// ✓
const fullName = `${first} ${last}`
```

## Never seed state from a prop

`useState(props.x)` freezes the mount-time value. Read the prop directly; for an editable
draft, remount per entity with `key`.

```tsx
// ✗ const [name, setName] = useState(device.name)
// ✓ <DeviceEditForm key={device.id} device={device} />
```

## Functional updates and lazy initializers

`set(c => c + 1)` keeps callbacks dependency-free and identity-stable;
`useState(() => expensive())` runs the initializer once.

```tsx
// ✗ new identity per count · parses every render
const inc = useCallback(() => setCount(count + 1), [count])
const [cfg] = useState(parseConfig(raw))
// ✓
const inc = useCallback(() => setCount(c => c + 1), [])
const [cfg] = useState(() => parseConfig(raw))
```

## Dependencies are honest

Include everything the effect reads; never omit a dependency to silence a loop — the loop
is a symptom of wrong structure. Escape hatches, in order: functional updates,
`useEffectEvent` (or a ref) so the effect reads the latest value without re-triggering,
or split the effect.

```ts
// ✗ dep omitted "to avoid re-running" — reads a stale onSave forever
useEffect(() => { conn.on('save', onSave) }, [conn])
// ✓ reads latest without re-subscribing
const onSaveEvent = useEffectEvent(onSave)
useEffect(() => { conn.on('save', onSaveEvent); return () => conn.off('save', onSaveEvent) }, [conn])
```

## Async results check staleness before applying

An async effect's result can land after the input changed or the component unmounted —
abort (or check a cancelled flag) so a stale response never overwrites fresh state. This
implements the contract's race owner. Server reads: `useQuery` already handles it.

```ts
useEffect(() => {
  const ctl = new AbortController()
  search(query, ctl.signal).then(setResults)   // rejects on abort — never applies
  return () => ctl.abort()
}, [query])
```

## Fetch with useQuery, never useEffect

Effect-fetching races on fast param changes, re-implements caching badly, and traps data in
one consumer. Keys come from the domain's typed factory — never inline literals — or
invalidation silently misses entries. No `onSuccess`/`onError` on `useQuery` (removed in
v5); side-effects on data go in an effect on `data`/`error`.

```tsx
// ✗ races on id change; no cache; stringly key
useEffect(() => { api.getDevice(id).then(setDevice) }, [id])
// ✓
useQuery({ queryKey: deviceKeys.detail(id), queryFn: () => api.getDevice(id) })
```

## Every mutation settles the cache and surfaces its error

A write is a `useMutation` that settles the keys the contract's invalidation graph names;
errors surface via `mutation.isError`, never a swallowed catch. When the contract promises
optimistic behaviour: snapshot in `onMutate`, roll back in `onError`, re-sync in `onSettled`
— without the pair, a failed write leaves phantom data on screen.

```tsx
// ✗ cache never settles (stale list); failure invisible to the UI
const onAdd = async () => { try { await api.addDevice(input) } catch (e) { console.error(e) } }
// ✓
useMutation({ mutationFn: api.addDevice,
  onSuccess: () => queryClient.invalidateQueries({ queryKey: deviceKeys.lists() }) })
```
