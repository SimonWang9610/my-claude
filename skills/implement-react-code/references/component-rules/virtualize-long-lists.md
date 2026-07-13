---
title: Virtualize Long Lists
impact: HIGH
impactDescription: DOM cost scales with data size — slow mounts, heavy layout, janky scroll
tags: virtualization, lists, render-cost, hot-path
---

**Rule:** Virtualize lists that can exceed ~50–100 non-trivial rows. For long *static* offscreen
sections, CSS `content-visibility: auto` (+ `contain-intrinsic-size`) is the zero-JS alternative.

- CORRECT Example:

```tsx
const v = useVirtualizer({ count: events.length, getScrollElement, estimateSize: () => 56 })
return v.getVirtualItems().map(row => <EventRow key={row.key} event={events[row.index]}/>)
```

- BAD Example:

```tsx
{events.map(e => <EventRow key={e.id} event={e}/>)}   // every row mounted
```
