---
title: Subscribe Only to What You Render
impact: MEDIUM
impactDescription: whole-store/fresh-object selectors — and subscriptions to handler-only values — re-render on every store change
tags: zustand, selectors, useShallow, getState, rerender
---

**Rule:** Select the atom you render; multi-field reads use `useShallow`; a value only used
inside an event handler is read with `getState()` at call time, not subscribed reactively.

- CORRECT Example:

```tsx
const filter = useDeviceStore(s => s.filter)
const pair = useDeviceStore(useShallow(s => ({ a: s.a, b: s.b })))
const onClick = () => api.snapshot(useDeviceStore.getState().positionMs)   // handler-only value
```

- BAD Example:

```tsx
const { devices, filter } = useDeviceStore()             // subscribes to everything
const pair = useDeviceStore(s => ({ a: s.a, b: s.b }))   // fresh object → re-render every change
const pos = useDeviceStore(s => s.positionMs)            // subscribed, but only used in onClick
```
