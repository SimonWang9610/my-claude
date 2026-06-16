---
title: Extract Logic into Custom Hooks
impact: MEDIUM-HIGH
impactDescription: monolithic components mix concerns that can't be tested or reused
tags: composition, hooks, separation-of-concerns
---

## Extract Logic into Custom Hooks

When a component interleaves substantial logic (subscriptions, derived calculations, multi-step handlers, effect orchestration) with JSX, extract the logic into named custom hooks. The component becomes the view; the hook becomes the testable, reusable behavior unit. This is the React analogue of pulling logic out of a Flutter widget into a notifier/controller.

**Smells indicating extraction:**
- Component > ~150 lines with mixed concerns
- 3+ `useEffect` blocks managing unrelated lifecycles
- The same useState/useEffect cluster duplicated across components
- Logic you'd want to unit test but can't without rendering

**Pattern:**

```tsx
// Before: 300-line CameraTile with connection mgmt + gestures + rendering
// After:
function CameraTile({ camera }: CameraTileProps) {
  const stream = useStreamConnection(camera.streamUrl)   // lifecycle + retry
  const ptz = usePtzGestures(camera.id)                  // pointer math + throttle
  return <TileLayout stream={stream} {...ptz.handlers} />
}
```

Each hook should have a single answerable purpose ("manages one stream's connection lifecycle"). Hooks returning 10 unrelated values are the same monolith relocated — split them (one hook per concern).
