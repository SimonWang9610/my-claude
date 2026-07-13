---
title: Transient Subscribe for Fast-Changing Store State
impact: HIGH
impactDescription: a reactive selector on a per-frame value re-renders the component 30–60 times a second
tags: zustand, subscribe, per-frame, rerender, hot-path
---

**Rule:** A store fact updating many times a second is consumed via `store.subscribe` writing to
a ref/DOM node — not a reactive selector. If the *design* placed a per-frame value in the store,
that's a design defect — raise it (the owning service should emit it).

- CORRECT Example:

```tsx
useEffect(() => useStore.subscribe(s => {
  cursorRef.current.style.transform = `translateX(${msToPx(s.positionMs)}px)`
}), [])
```

- BAD Example:

```tsx
const pos = useStore(s => s.positionMs)      // re-renders 30–60×/s
return <div style={{ left: msToPx(pos) }}/>
```
