---
title: Use Transient Subscriptions for High-Frequency Values
impact: HIGH
impactDescription: per-frame reactive updates render-thrash the tree
tags: zustand, subscribe, refs, video, high-frequency
---

## Use Transient Subscriptions for High-Frequency Values

Values that update many times per second (playback position/PTS, scrub position, drag coordinates, pointer position for PTZ) must not flow through reactive hooks — `useStore(s => s.position)` re-renders the component on every tick. Subscribe transiently and write to refs/DOM directly; let React render only on discrete changes (play/pause, seek-end).

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

Even better when possible: keep per-frame values out of the store entirely (emit from the player service via callback/event, store only discrete session state). Architecture review flags the *placement*; render cost details live in `react-performance-review`.
