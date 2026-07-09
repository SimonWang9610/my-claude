---
title: Narrow Query Subscriptions with select and notifyOnChangeProps
impact: MEDIUM
impactDescription: components re-render for query changes they don't display
tags: query, select, notifyOnChangeProps, rerender
---

## Narrow Query Subscriptions with select and notifyOnChangeProps

The *derived shape itself* is a design decision — it belongs to the query hook's contract (see
the `oac-architecture-design` skill — `query-select-transform`). Here the concern is the
runtime facet: narrowing which changes re-render the consumer.

A `useQuery` consumer re-renders when any tracked part of the result changes. Two narrowing tools:

**`select`** — subscribe to a derived slice; the component re-renders only when the *selected output* changes (structural sharing makes unchanged selections referentially stable):

```tsx
// Tile re-renders only when ITS camera's record changes, not the whole list:
function useCamera(id: string) {
  return useQuery({
    queryKey: cameraKeys.list(),
    queryFn: api.getCameras,
    select: (cams) => cams.find((c) => c.id === id),
  })
}
```

**Tracked properties** — by default queries track which fields you destructure and only notify for those. Flag code that spreads the whole result (`const q = useQuery(...)` then `q.foo` everywhere, or `{...query}` passed down) — it opts into all notifications, including `isFetching` flipping on every background refetch. Destructure exactly what renders; for hard cases pin `notifyOnChangeProps: ['data', 'isPending']`.

The background-refetch flicker bug is the common manifestation: a list flashes/re-renders on focus refetch because something subscribed to `isFetching` it never displays.
