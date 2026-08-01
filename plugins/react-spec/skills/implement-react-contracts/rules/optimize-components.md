# Optimize components — hot paths only

Optimize when the path is hot (per-frame, large list, main interaction). Clear code first.
**With `babel-plugin-react-compiler` configured, skip all manual memoization below.**

## memo at expensive boundaries, with stable props

Place `memo` at the expensive-subtree boundary (not leaves) — then every prop crossing it
must be stable, or the memo is silently defeated: hoist static objects/JSX to module scope,
`useCallback` the handlers.

```tsx
const TILE_STYLE = { aspectRatio: '16/9' } as const
// ✗ both props fresh every render — memo defeated
<Tile onSelect={() => select(id)} style={{ aspectRatio: '16/9' }} />
// ✓
<Tile onSelect={select} style={TILE_STYLE} />
```

## Pass expensive subtrees as children

A wrapper with fast-changing internal state receives expensive subtrees as
`children`/element props — elements the parent created don't re-render on the wrapper's
ticks.

```tsx
// ✗ drag ticks re-render both grids every frame
function SplitLayout() { const [pos] = useState(0); return <div><CameraGrid/><Timeline/></div> }
// ✓ created once by the parent, immune to pos ticks
function SplitLayout({ left, right }: SplitProps) { const [pos] = useState(0); return <div>{left}{right}</div> }
```

## Defer heavy non-urgent updates

Expensive renders driven by typing/dragging: `useDeferredValue`/`useTransition`, with the
deferred subtree memo'd — otherwise blocked keystrokes.

```tsx
const deferred = useDeferredValue(query)
return <EventResults query={deferred} />   // EventResults is memo'd
```

## Virtualize long lists

Lists that can exceed ~50–100 non-trivial rows get a virtualizer; long *static* offscreen
sections can use CSS `content-visibility: auto` instead.

```tsx
const v = useVirtualizer({ count: events.length, getScrollElement, estimateSize: () => 56 })
```

## Code-split heavy panels; import by direct path

Lazy-load routes and heavy conditionally-opened panels (`React.lazy` + `Suspense`) at the
split points the design named; import icons/library modules by specific path, never a
mega-barrel.

```tsx
const SettingsDialog = lazy(() => import('@/features/settings/SettingsDialog'))
import Videocam from '@mui/icons-material/Videocam'   // not { Videocam } from the barrel
```

## Per-frame values bypass the styling system

Continuously-changing values use plain `style` — a dynamic `sx`/css-prop value mints a
fresh class per value; never create `styled()` inside a component body.

```tsx
// ✗ <Box sx={{ width: `${progress}%` }} />   // fresh CSS class per value
// ✓ <Box style={{ width: `${progress}%` }} />
```
