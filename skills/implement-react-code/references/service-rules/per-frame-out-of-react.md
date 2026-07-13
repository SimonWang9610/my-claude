---
title: Per-Frame Values Never Enter React State
impact: HIGH
impactDescription: setState at 30–60×/s burns the frame budget on reconciliation — multiplied across every tile
tags: service, per-frame, rAF, refs, canvas, hot-path
---

**Rule:** Per-frame values (position, buffer level, drag coords) never enter React state — the
service emits; the consumer writes to a ref/DOM node in a rAF loop. For many elements changing
every frame (motion boxes, timeline ticks, waveforms), draw on one `<canvas>` instead of
mutating DOM nodes.

- CORRECT Example:

```ts
player.onTimeUpdate((ms) => { cursor.style.transform = `translateX(${msToPx(ms)}px)` })

// many changing elements → one canvas repaint per rAF tick
ctx.clearRect(0, 0, w, h)
for (const b of boxes) ctx.strokeRect(b.x, b.y, b.w, b.h)
```

- BAD Example:

```ts
player.onTimeUpdate(setPositionMs)   // re-render every frame
```
