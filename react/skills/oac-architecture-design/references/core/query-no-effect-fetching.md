---
title: Fetch with useQuery, Never useEffect
impact: HIGH
impactDescription: hand-rolled effect fetching reimplements caching badly and races
tags: query, useEffect, fetching
---

## Fetch with useQuery, Never useEffect

**Boundary:** server reads belong to the Query layer, not the component. `useEffect` + `fetch` + `setState` lands fetched data in local component state where no other consumer can reach it — the architectural defect (server data has no single owner). It also hand-rolls what Query provides: caching, dedup, retry, and race-safety on fast param changes. Server data is owned by the cache; a component subscribes to it, never sources it.

**Incorrect:**

```tsx
function CameraDetail({ id }: { id: string }) {
  const [camera, setCamera] = useState<Camera | null>(null)
  useEffect(() => {
    // races on id change; no caching, no dedup, no retry; data trapped in local state
    api.getCamera(id).then(setCamera)
  }, [id])
}
```

**Correct** — the read goes through `useQuery`, so the cache owns the data:

```tsx
function CameraDetail({ id }: { id: string }) {
  const { data: camera, isPending } = useQuery({
    queryKey: cameraKeys.detail(id),
    queryFn: () => api.getCamera(id),
  })
}
```

Loading-state mechanics (`isPending` vs `isLoading` in v5, background-refetch flags) are coding detail — see `oac-implementation` (`data-states`).

Acceptable non-Query effects: subscribing to push channels (WebSocket/IPC) — though those should feed `queryClient.setQueryData` or a service module; imperative one-shot calls inside event handlers may use `queryClient.fetchQuery`/mutations instead of raw fetch.
