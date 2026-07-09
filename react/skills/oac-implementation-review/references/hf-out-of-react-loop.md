---
title: Keep Per-Frame Values Out of React's Render Loop
impact: CRITICAL
impactDescription: rendering per frame burns the entire 16ms budget on reconciliation
tags: high-frequency, video, refs, rAF, playback
---

## Keep Per-Frame Values Out of React's Render Loop

Values that change at frame rate or near it — playback position/PTS, buffer levels, stream bitrate, audio meters — must not be React state. A `setState` 30–60×/second forces reconciliation of the subscribing subtree every frame; in a multi-camera grid this multiplies by tile count and the frame budget is gone before any real work happens.

The pattern: React renders the *static structure once*; a rAF loop or event callback writes the changing value directly to the DOM (or canvas) through refs. React state holds only discrete facts (playing/paused, seek target, selected camera).

**Incorrect:**

```tsx
function Timeline() {
  const [positionMs, setPositionMs] = useState(0)
  useEffect(() => player.onTimeUpdate(setPositionMs), [])   // 30–60 renders/s
  return <div className="cursor" style={{ left: msToPx(positionMs) }} />
}
```

**Correct:**

```tsx
function Timeline() {
  const cursorRef = useRef<HTMLDivElement>(null)
  useEffect(
    () =>
      player.onTimeUpdate((ms) => {
        cursorRef.current!.style.transform = `translateX(${msToPx(ms)}px)`
      }),
    // player omitted: it must be a stable module-level ref or a useRef value that
    // never changes identity after mount. If player can change, add it to deps.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  )
  return <div ref={cursorRef} className="cursor" />
}
```

Prefer `transform` over `left/top` (compositor-only, no layout). If the value lives in a Zustand store, use `store.subscribe` (transient) instead of the reactive hook. Components that *display* the value at low precision (a "00:01:23" readout) can subscribe to a quantized derivative (e.g., whole seconds) — that's 1 render/s instead of 60.
