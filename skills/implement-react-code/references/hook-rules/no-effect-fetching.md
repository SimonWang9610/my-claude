---
title: Fetch with useQuery, Never useEffect
impact: HIGH
impactDescription: effect-fetching races on fast param changes, re-implements caching badly, and traps data in one consumer
tags: query, useEffect, fetching, race
---

**Rule:** Server reads go through `useQuery`, never `useEffect` + fetch + `setState`.

- CORRECT Example:

```tsx
useQuery({ queryKey: deviceKeys.detail(id), queryFn: () => api.getDevice(id) })
```

- BAD Example:

```tsx
useEffect(() => { api.getDevice(id).then(setDevice) }, [id])   // races on id change; no cache
```
