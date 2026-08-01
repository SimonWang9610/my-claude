# Optimize hooks — hot paths only

Optimize when the path is hot (per-frame, large list, main interaction). Clear code first.

## Narrow every subscription

Subscribe to the slice rendered, not the whole result. Queries: `select` the shape the
consumer displays (v5 also tracks accessed fields). Stores: per-field selectors, never the
whole store.

```tsx
// ✗ re-renders on every query field, incl. isFetching ticks
const q = useQuery(deviceListOptions)
return <>{q.data?.find(c => c.id === id)?.name}</>
// ✓
const { data: device } = useQuery({ ...deviceListOptions, select: cams => cams.find(c => c.id === id) })

// ✗ const store = useDeviceStore()          // any store change re-renders
// ✓ const selectedId = useDeviceStore(s => s.selectedId)
```

## Don't subscribe to state only used in callbacks

A value read only inside an event handler doesn't need a subscription — read it at call
time.

```ts
// ✗ re-renders on every selection change just to have it in the handler
const selectedId = useDeviceStore(s => s.selectedId)
const onExport = () => exportDevice(selectedId)
// ✓ read at call time — no subscription
const onExport = () => exportDevice(useDeviceStore.getState().selectedId)
```

## Split hooks with independent dependencies

One hook re-computing everything when any input changes re-renders all its consumers.
Independent concerns → independent hooks, each with its own dependency set.

```ts
// ✗ filter change re-runs the sort; sort change re-runs the filter
useFilteredSortedDevices(devices, query, sortKey)
// ✓
const filtered = useDeviceFilters(devices, query)
const sorted = useDeviceSort(filtered, sortKey)
```

## Transient high-frequency values live in refs

A per-frame/continuous value (pointer position, playback ms) that doesn't drive render goes
in a ref or stays in its service — `setState` per frame renders per frame.

```ts
// ✗ const [pos, setPos] = useState(0); engine.onPosition(setPos)   // 60 renders/s
// ✓ const posRef = useRef(0); engine.onPosition(ms => { posRef.current = ms })
```

## Deliberate staleTime

The default `staleTime: 0` refetches on every mount and refocus — a storm across shared
keys. Set an app-wide default and tune per query per the contract.

```ts
new QueryClient({ defaultOptions: { queries: { staleTime: 30_000 } } })
```
