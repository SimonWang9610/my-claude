---
title: Pass Expensive Subtrees as children
impact: MEDIUM
impactDescription: a stateful wrapper re-renders everything it wraps on every internal tick
tags: children, rerender, composition, hot-path
---

**Rule:** A component with fast-changing internal state receives expensive subtrees as
`children`/element props instead of creating them — elements the parent created don't re-render
on the wrapper's ticks.

- CORRECT Example:

```tsx
function SplitLayout({ left, right }: SplitProps) {
  const [pos, setPos] = useState(0)          // drag ticks…
  return <div>{left}{right}</div>            // …but the elements were created once by the parent
}
```

- BAD Example:

```tsx
function SplitLayout() {
  const [pos, setPos] = useState(0)                        // drag ticks…
  return <div><CameraGrid/><EventTimeline/></div>          // …re-render both subtrees every tick
}
```
