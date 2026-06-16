---
title: Fetch with useQuery, Never useEffect
impact: HIGH
impactDescription: hand-rolled effect fetching reimplements caching badly and races
tags: query, useEffect, fetching
---

## Fetch with useQuery, Never useEffect

`useEffect` + `fetch` + `setState` hand-rolls what TanStack Query already provides — and gets it wrong: no caching, no dedup, race conditions on fast param changes, no retry, loading/error flags managed manually, and the fetched data lands in component state where nothing else can reuse it.

**Incorrect:**

```tsx
function CameraDetail({ id }: { id: string }) {
  const [camera, setCamera] = useState<Camera | null>(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    setLoading(true)
    api.getCamera(id).then((c) => { setCamera(c); setLoading(false) }) // races on id change
  }, [id])
}
```

**Correct:**

```tsx
function CameraDetail({ id }: { id: string }) {
  const { data: camera, isPending } = useQuery({
    queryKey: cameraKeys.detail(id),
    queryFn: () => api.getCamera(id),
  })
}
```

Acceptable non-Query effects: subscribing to push channels (WebSocket/IPC) — though those should feed `queryClient.setQueryData` or a service module, and imperative one-shot calls inside event handlers may use `queryClient.fetchQuery`/mutations instead of raw fetch.
