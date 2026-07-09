---
title: Make the Derived Shape Part of the Query Contract
impact: MEDIUM
impactDescription: an unspecified derived shape gets re-invented per component, duplicating logic
tags: query, select, derived-data, contract
---

## Make the Derived Shape Part of the Query Contract

**Decision:** when a unit needs a derived shape of server data (filtered, sorted, indexed,
mapped to a view model), decide that shape *at design time* and record it as part of the query
hook's contract. The named hook (`useOnlineCameras`, `useCameraById`) is the one home for the
transformation, expressed with the query's `select` option — memoized against the cached data
and shared by every caller. Don't leave each component to reshape inline, and never store a
transformed copy in a client store (see `state-no-server-data-in-stores`).

**Contract — one named hook per derived shape:**

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
    select: (cameras) => cameras.find((c) => c.id === id),
  })
}
```

Record in each affected contract: the query key it reads and the exact selected return type,
so the transformation has exactly one home. The re-render narrowing this buys at runtime —
`select` + tracked properties so a component re-renders only when *its* slice changes — is the
performance facet, in the `oac-implementation-review` skill (`query-narrow-subscriptions`).
