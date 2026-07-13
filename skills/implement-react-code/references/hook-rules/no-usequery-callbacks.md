---
title: No onSuccess/onError on useQuery (v5)
impact: HIGH
impactDescription: the callbacks were removed in v5 — code carrying them silently never runs
tags: query, v5-migration, useEffect
---

**Rule:** `onSuccess`/`onError`/`onSettled` do not exist on `useQuery` in v5 — side-effects on
data go in a `useEffect` on `data`/`error`.

- CORRECT Example:

```tsx
const { data } = useQuery({ queryKey, queryFn })
useEffect(() => { if (data) setTitle(data.name) }, [data])
```

- BAD Example:

```tsx
useQuery({ queryKey, queryFn, onSuccess: d => setTitle(d.name) })   // removed in v5 — never runs
```
