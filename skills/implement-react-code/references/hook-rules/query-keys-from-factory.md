---
title: Query Keys Come from the Domain Factory
impact: HIGH
impactDescription: ad-hoc string keys drift apart and invalidation silently misses entries
tags: query, query-keys, invalidation
---

**Rule:** Query keys come from the domain's typed factory (hierarchical `all → lists → detail`) —
never an inline string-literal key.

- CORRECT Example:

```tsx
useQuery({ queryKey: deviceKeys.detail(id), queryFn: () => api.getDevice(id) })
```

- BAD Example:

```tsx
useQuery({ queryKey: ['devices', id], queryFn: () => api.getDevice(id) })   // stringly, unfactored
```
