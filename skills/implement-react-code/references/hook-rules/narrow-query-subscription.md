---
title: Narrow Query Subscriptions with select and notifyOnChangeProps
impact: MEDIUM
impactDescription: components re-render for query changes they don't display
tags: query, select, notifyOnChangeProps, rerender, hot-path
---

**Rule:** Narrow what a query consumer subscribes to — `select` the slice it renders, destructure
only the fields used (v5 tracks accessed properties; `notifyOnChangeProps` pins it explicitly).

- CORRECT Example:

```tsx
const { data: device } = useQuery({ ...deviceListOptions, select: cams => cams.find(c => c.id === id) })
```

- BAD Example:

```tsx
const q = useQuery(deviceListOptions)
return <>{q.data?.find(c => c.id === id)?.name}</>   // re-renders on every field, incl. isFetching
```
