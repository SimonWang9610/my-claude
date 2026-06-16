---
title: Mark Expensive Updates as Non-Urgent
impact: MEDIUM
impactDescription: keeps typing/clicking responsive while heavy renders happen in background
tags: rerender, useTransition, useDeferredValue, responsiveness
---

## Mark Expensive Updates as Non-Urgent

When one interaction triggers both a cheap urgent update (the input's own value) and an expensive one (re-filtering a large event list, re-laying-out a grid), React 18+ can keep the urgent one snappy if the expensive one is marked non-urgent — it becomes interruptible and won't block keystrokes.

**`useDeferredValue`** when a fast-changing value drives an expensive subtree:

```tsx
function EventSearch() {
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)
  const isStale = query !== deferredQuery
  return (
    <div>
      <TextField value={query} onChange={(e) => setQuery(e.target.value)} />
      <div style={{ opacity: isStale ? 0.6 : 1 }}>
        <EventResults query={deferredQuery} />   {/* must be memo'd */}
      </div>
    </div>
  )
}
```

**`useTransition`** when the code initiating the update wants a pending flag:

```tsx
const [isPending, startTransition] = useTransition()
const switchLayout = (size: GridSize) => startTransition(() => setGridSize(size))
```

Caveats reviewers must apply: these reschedule work, they don't shrink it — if the expensive render is avoidable (virtualization, memo boundaries, narrower subscriptions), fix that first; and the subtree consuming the deferred value must be memoized, otherwise it re-renders with the urgent pass anyway and the deferral is a no-op.
