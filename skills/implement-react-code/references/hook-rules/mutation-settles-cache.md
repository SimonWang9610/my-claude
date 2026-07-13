---
title: Every Mutation Settles the Cache and Surfaces Its Error
impact: HIGH
impactDescription: an unsettled cache shows pre-mutation data; a swallowed catch hides the failure from the UI
tags: mutation, invalidation, error-state
---

**Rule:** Every write is a `useMutation` that settles the cache in `onSuccess` — invalidate the
families the contract's invalidation graph names, or `setQueryData`. Errors surface via
`mutation.isError`/`error`.

- CORRECT Example:

```tsx
const addDevice = useMutation({
  mutationFn: api.addDevice,
  onSuccess: () => queryClient.invalidateQueries({ queryKey: deviceKeys.lists() }),
})
```

- BAD Example:

```tsx
const onAdd = async () => { try { await api.addDevice(input) } catch (e) { console.error(e) } }
// no useMutation: cache never settles (stale list), no error state for the UI
```
