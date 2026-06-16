---
title: Pass Subtrees as children to Skip Their Re-render
impact: MEDIUM-HIGH
impactDescription: state in a wrapper needlessly re-renders everything it wraps
tags: rerender, children, composition, lift-content
---

## Pass Subtrees as children to Skip Their Re-render

When a component re-renders, it re-executes the JSX *it creates*. But `children` (or element-typed props) it merely *receives* are the same element references as the previous render, so React skips re-rendering them. Therefore: a component with fast-changing internal state (hover tracking, drag/resize position, scroll listeners) should *receive* its expensive content rather than *create* it.

**Incorrect (the stateful component creates the subtree):**

```tsx
function SplitLayout() {
  const [pos, setPos] = useState(0.5)              // updates on every drag tick
  return (
    <div onPointerMove={handleDrag} style={gridFor(pos)}>
      <CameraGrid />                                {/* re-rendered per tick */}
      <EventTimeline />                             {/* re-rendered per tick */}
    </div>
  )
}
```

**Correct (the state owner receives content from above):**

```tsx
function SplitLayout({ left, right }: { left: ReactNode; right: ReactNode }) {
  const [pos, setPos] = useState(0.5)
  return (
    <div onPointerMove={handleDrag} style={gridFor(pos)}>
      {left}
      {right}
    </div>
  )
}

// Parent (which does NOT re-render during the drag) creates the elements once:
<SplitLayout left={<CameraGrid />} right={<EventTimeline />} />
```

Now drag ticks re-render only the layout div; the grid and timeline elements are referentially unchanged and skipped. This structural fix often replaces a `memo` — prefer it where it fits, since it's free and doesn't depend on prop stability. (The drag position itself is also an `hf-throttle-event-streams` candidate.)
