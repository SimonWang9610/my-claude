---
title: Mutations Must Settle the Cache
impact: HIGH
impactDescription: un-invalidated mutations leave the UI showing pre-mutation data
tags: query, mutations, invalidation, optimistic
---

## Mutations Must Settle the Cache

Every `useMutation` must reconcile the cache on success: either invalidate affected query families or update them directly (`setQueryData`). Manual choreography — calling `refetch()` from components, passing "reload" callbacks down props, or full page state resets — indicates the mutation isn't owning its consequences.

**TanStack Query v5 note:** `onSuccess`/`onError`/`onSettled` callbacks are removed from `useQuery` in v5 — they only work on `useMutation` and `queryClient.defaultOptions`. If reviewed code passes these to `useQuery`, flag it and move the side effects to a `useEffect` on `data`/`error` in the component, or to `useMutation` callbacks:

**Incorrect (manual choreography):**

```tsx
const rename = useMutation({ mutationFn: api.renameCamera })
// caller: rename.mutate(...); then props.onSaved() → parent calls refetch() ...
```

**Incorrect (onSuccess on useQuery — removed in v5):**

```tsx
// Do NOT do this in v5:
const { data } = useQuery({
  queryKey: cameraKeys.detail(id),
  queryFn: () => api.getCamera(id),
  onSuccess: (data) => setTitle(data.name),  // removed in TanStack Query v5
})
```

**Correct (side effect on data change):**

```tsx
const { data } = useQuery({
  queryKey: cameraKeys.detail(id),
  queryFn: () => api.getCamera(id),
})
useEffect(() => {
  if (data) setTitle(data.name)
}, [data])
```

**Correct:**

```tsx
const rename = useMutation({
  mutationFn: api.renameCamera,
  onSuccess: (updated) => {
    queryClient.setQueryData(cameraKeys.detail(updated.id), updated)
    queryClient.invalidateQueries({ queryKey: cameraKeys.lists() })
  },
})
```

Optimistic updates (`onMutate` snapshot → rollback in `onError` → `invalidateQueries` in `onSettled`) are the upgrade path for latency-sensitive interactions; recommend them only where users actually notice the wait.
