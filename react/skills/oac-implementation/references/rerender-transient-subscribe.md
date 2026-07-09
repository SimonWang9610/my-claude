---
title: Read Fast-Changing Store State via Transient subscribe
impact: HIGH
impactDescription: a reactive selector on a per-frame value re-renders the component every tick
tags: rerender, zustand, subscribe, refs, high-frequency
---

## Read Fast-Changing Store State via Transient subscribe

The architecture decides *where* a high-frequency value lives — per-frame values are emitted
from the service, not stored (see the `oac-architecture-design` skill —
`zustand-transient-placement`). When a fast-changing value nonetheless sits in a store and a
component must reflect it, do **not** read it with a reactive selector:
`useStore(s => s.positionMs)` re-renders 30–60×/s. Subscribe transiently and write straight
to a ref/DOM node, so React renders only on discrete changes (play/pause, seek-end).

**Incorrect:**

```tsx
function Timeline() {
  const position = usePlaybackStore((s) => s.positionMs) // re-renders ~30–60×/s
  return <div style={{ left: msToPx(position) }} />
}
```

**Correct:**

```tsx
function Timeline() {
  const cursorRef = useRef<HTMLDivElement>(null)
  useEffect(
    () =>
      usePlaybackStore.subscribe((s) => {
        if (cursorRef.current)
          cursorRef.current.style.transform = `translateX(${msToPx(s.positionMs)}px)`
      }),
    []
  )
  return <div ref={cursorRef} />
}
```

`subscribe` returns its own unsubscribe function — return it from the effect so the listener
tears down. The same pattern applies to a value emitted directly from a service: subscribe in
an effect, write to the ref, never `setState` per frame. For per-frame values that never need
to touch React at all, keep them out of the render loop entirely — see `hf-out-of-react-loop`.
