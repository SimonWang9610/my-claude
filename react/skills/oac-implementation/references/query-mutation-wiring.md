---
title: Wire the Mutation Callbacks and Optimistic Rollback
impact: HIGH
impactDescription: mis-wired mutation callbacks leave the cache stale or the UI stuck mid-write
tags: query, mutations, optimistic, rollback, onSuccess
---

## Wire the Mutation Callbacks and Optimistic Rollback

The invalidation graph — which families a write invalidates or updates — is fixed by the
design (see the `oac-architecture-design` skill — `query-mutation-invalidation`). This is how
you wire it in code.

**Settle the cache in `onSuccess`** — invalidate the affected families or write them directly:

```tsx
const rename = useMutation({
  mutationFn: api.renameCamera,
  onSuccess: (updated) => {
    queryClient.setQueryData(cameraKeys.detail(updated.id), updated)
    queryClient.invalidateQueries({ queryKey: cameraKeys.lists() })
  },
})
```

**v5 callback placement:** `onSuccess`/`onError`/`onSettled` exist on `useMutation` and
`queryClient.defaultOptions` only — they were removed from `useQuery` in v5. A side effect on
query data goes in a `useEffect` on `data`/`error`, never a `useQuery` callback:

```tsx
// ✗ removed in v5
useQuery({ queryKey: cameraKeys.detail(id), queryFn: ..., onSuccess: (d) => setTitle(d.name) })
// ✓
const { data } = useQuery({ queryKey: cameraKeys.detail(id), queryFn: ... })
useEffect(() => { if (data) setTitle(data.name) }, [data])
```

**Optimistic update + rollback** — for latency-sensitive writes users actually notice:
snapshot in `onMutate`, roll back in `onError`, reconcile in `onSettled`:

```tsx
const rename = useMutation({
  mutationFn: api.renameCamera,
  onMutate: async (next) => {
    await queryClient.cancelQueries({ queryKey: cameraKeys.detail(next.id) })
    const prev = queryClient.getQueryData(cameraKeys.detail(next.id))
    queryClient.setQueryData(cameraKeys.detail(next.id), next)
    return { prev }
  },
  onError: (_e, next, ctx) => queryClient.setQueryData(cameraKeys.detail(next.id), ctx?.prev),
  onSettled: (_d, _e, next) =>
    queryClient.invalidateQueries({ queryKey: cameraKeys.detail(next.id) }),
})
```

Reach for optimism only where the wait is visible; otherwise a plain `onSuccess` invalidate is
simpler and correct. Mutation *states* (`isPending`/`isError` on the trigger) are covered by
`data-states`.
