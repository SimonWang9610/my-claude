---
title: Optimistic Updates Snapshot and Roll Back
impact: HIGH
impactDescription: without the snapshot/rollback pair, a failed write leaves phantom data on screen
tags: mutation, optimistic-update, rollback
---

**Rule:** An optimistic update snapshots the previous value in `onMutate` and rolls back in
`onError`; `onSettled` re-syncs. Apply when the contract promises optimistic behaviour.

- CORRECT Example:

```tsx
useMutation({ mutationFn: api.rename,
  onMutate: async (next) => {
    await queryClient.cancelQueries({ queryKey: deviceKeys.detail(next.id) })
    const prev = queryClient.getQueryData(deviceKeys.detail(next.id))
    queryClient.setQueryData(deviceKeys.detail(next.id), next)
    return { prev }
  },
  onError: (_e, next, ctx) => queryClient.setQueryData(deviceKeys.detail(next.id), ctx?.prev),
  onSettled: (next) => queryClient.invalidateQueries({ queryKey: deviceKeys.detail(next.id) }),
})
```

- BAD Example:

```tsx
useMutation({ mutationFn: api.rename,
  onMutate: (next) => queryClient.setQueryData(deviceKeys.detail(next.id), next),
})   // no snapshot, no rollback — a failed write leaves phantom data on screen
```
