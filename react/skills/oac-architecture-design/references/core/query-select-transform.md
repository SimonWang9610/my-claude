---
title: Shape Server Data with select
impact: MEDIUM
impactDescription: component-side reshaping duplicates logic and re-runs every render
tags: query, select, derived-data
---

## Shape Server Data with select

When components need a derived shape of server data (filtered, sorted, indexed, mapped to view models), use the query's `select` option — it's memoized against the cached data, shared by every caller of the wrapping hook, and keeps components free of transformation logic. Don't reshape inline in each component, and never store a transformed copy in state (see `state-no-server-data-in-stores`).

**Correct:**

```tsx
function useOnlineCameras() {
  return useQuery({
    queryKey: cameraKeys.lists(),
    queryFn: api.getCameras,
    select: (cameras) => cameras.filter((c) => c.status === 'online'),
  })
}

function useCameraById(id: string) {
  return useQuery({
    queryKey: cameraKeys.lists(),
    queryFn: api.getCameras,
    select: (cameras) => cameras.find((c) => c.id === id), // narrow subscription
  })
}
```

A bonus: `select` narrows re-renders — a component using `useCameraById` only re-renders when *its* camera changes, not the whole list. Wrap queries in named domain hooks (`useOnlineCameras`) so the transformation has exactly one home.
