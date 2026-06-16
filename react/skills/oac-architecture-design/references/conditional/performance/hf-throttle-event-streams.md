---
title: Coalesce High-Rate Events to One Update per Frame
impact: CRITICAL
impactDescription: pointermove can fire faster than refresh rate; un-throttled handlers do redundant work
tags: high-frequency, gestures, pointermove, rAF, ptz
---

## Coalesce High-Rate Events to One Update per Frame

`pointermove`, `wheel`, `scroll`, and drag events can fire faster than the display refreshes. Doing per-event work (state updates, layout reads, store writes) wastes everything between frames. Store the latest event, schedule one rAF, process once per frame.

**Incorrect:**

```tsx
const onPointerMove = (e: PointerEvent) => {
  setDragPosition({ x: e.clientX, y: e.clientY })   // possibly 120+/s, each a render
}
```

**Correct:**

```tsx
function useRafThrottled<T>(apply: (v: T) => void) {
  const latest = useRef<T | null>(null)
  const scheduled = useRef(false)
  return useCallback((v: T) => {
    latest.current = v
    if (scheduled.current) return
    scheduled.current = true
    requestAnimationFrame(() => {
      scheduled.current = false
      apply(latest.current!)
    })
  }, [apply])
}

// PTZ gesture: apply writes to a ref/DOM or sends the control command —
// no React state involved during the gesture; commit to state on pointerup.
```

Also flag: layout reads (`getBoundingClientRect`) inside per-event handlers (read once on gesture start), and non-passive `wheel`/`touchmove` listeners that block scrolling without needing `preventDefault`.
