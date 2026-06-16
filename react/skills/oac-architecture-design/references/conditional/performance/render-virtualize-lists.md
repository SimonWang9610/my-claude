---
title: Virtualize Long Lists
impact: MEDIUM-HIGH
impactDescription: DOM cost scales with rendered rows, not data; virtualization caps it
tags: rendering, lists, virtualization, scroll
---

## Virtualize Long Lists

Rendering every row of a long list (event logs, alarm history, camera directories, timeline entries) creates DOM proportional to data size: slow mounts, heavy layout, janky scroll. Virtualization renders only the visible window plus overscan — cost becomes constant.

Threshold: lists that can exceed ~50–100 rows of non-trivial content should be virtualized. Static short lists should not (virtualization adds complexity and breaks Ctrl-F).

```tsx
import { useVirtualizer } from '@tanstack/react-virtual'

function EventLog({ events }: { events: SecurityEvent[] }) {
  const parentRef = useRef<HTMLDivElement>(null)
  const virtualizer = useVirtualizer({
    count: events.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 56,
    overscan: 8,
  })
  return (
    <div ref={parentRef} style={{ overflow: 'auto', height: '100%' }}>
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map((row) => (
          <EventRow
            key={events[row.index].id}
            event={events[row.index]}
            style={{ position: 'absolute', top: 0, transform: `translateY(${row.start}px)`, height: row.size }}
          />
        ))}
      </div>
    </div>
  )
}
```

Use stable item keys (entity ids, never array index — rows shift as the window moves). `@tanstack/react-virtual` fits this stack alongside TanStack Query; pair with `useInfiniteQuery` for endless logs. For mostly-static long pages (not scrolling data), `render-content-visibility` is the lighter alternative.
