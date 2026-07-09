---
title: Don't Subscribe to State Used Only in Callbacks
impact: HIGH
impactDescription: subscribing for callback-only reads renders on changes the UI never shows
tags: rerender, zustand, getState, callbacks
---

## Don't Subscribe to State Used Only in Callbacks

A reactive subscription means "re-render me when this changes." If a value is only *read inside an event handler*, the component doesn't need to re-render when it changes — read it at call time with `getState()`.

**Incorrect:**

```tsx
function SnapshotButton() {
  const positionMs = usePlaybackStore((s) => s.positionMs)   // renders on every tick
  const onClick = () => api.snapshot(positionMs)
  return <Button onClick={onClick}>Snapshot</Button>
}
```

**Correct:**

```tsx
function SnapshotButton() {
  const onClick = () => api.snapshot(usePlaybackStore.getState().positionMs)
  return <Button onClick={onClick}>Snapshot</Button>
}
```

Same idea for React state: prefer the functional-update form (`set(c => c + 1)`) over depending on the current value, and for values needed by effects but not renders, mirror into a ref. The question to ask per subscription: "does the *rendered output* use this value?" If no, demote to `getState()`/refs.
