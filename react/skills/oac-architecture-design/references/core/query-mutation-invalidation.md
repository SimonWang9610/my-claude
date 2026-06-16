---
title: Mutations Must Settle the Cache
impact: HIGH
impactDescription: un-invalidated mutations leave the UI showing pre-mutation data
tags: query, mutations, invalidation, optimistic
---

## Mutations Must Settle the Cache

Every `useMutation` must reconcile the cache on success: either invalidate affected query families or update them directly (`setQueryData`). Manual choreography — calling `refetch()` from components, passing "reload" callbacks down props, or full page state resets — indicates the mutation isn't owning its consequences.

**Incorrect:**

```tsx
const rename = useMutation({ mutationFn: api.renameCamera })
// caller: rename.mutate(...); then props.onSaved() → parent calls refetch() ...
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
