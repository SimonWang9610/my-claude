---
title: Coalesce High-Rate Event Streams per Frame
impact: MEDIUM
impactDescription: pointermove/wheel/scroll fire faster than the display refreshes — per-event updates do redundant work
tags: service, events, rAF, throttle, hot-path
---

**Rule:** Coalesce high-rate events to one processed update per animation frame — buffer the
latest value, apply on rAF.

- CORRECT Example:

```ts
latest.current = value
if (!scheduled.current) {
  scheduled.current = true
  requestAnimationFrame(() => { scheduled.current = false; apply(latest.current) })
}
```

- BAD Example:

```ts
onPointerMove = (e) => update({ x: e.clientX, y: e.clientY })   // processes every event
```
