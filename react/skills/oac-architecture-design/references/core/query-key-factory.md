---
title: Centralize Query Keys in Typed Factories
impact: MEDIUM-HIGH
impactDescription: inline keys drift and break invalidation silently
tags: query, keys, invalidation
---

## Centralize Query Keys in Typed Factories

Query keys are the cache's addressing scheme. Inline ad-hoc keys (`['cameras', id]` here, `['camera', id]` there) drift apart, and invalidation silently misses entries. Define one key factory per domain and import it everywhere keys are used — queries, mutations, invalidations, prefetches.

**Correct pattern:**

```tsx
// src/features/cameras/api/keys.ts
export const cameraKeys = {
  all: ['cameras'] as const,
  lists: () => [...cameraKeys.all, 'list'] as const,
  list: (filters?: CameraFilters) => [...cameraKeys.lists(), filters] as const,
  details: () => [...cameraKeys.all, 'detail'] as const,
  detail: (id: string) => [...cameraKeys.details(), id] as const,
}

// Invalidate every camera list, regardless of filters:
queryClient.invalidateQueries({ queryKey: cameraKeys.lists() })
```

The hierarchy is the point: broader keys prefix narrower ones so one invalidation can target a whole family. Review flag: any string-literal query key outside the factory file.

**Prefer `queryOptions()` to co-locate key and `queryFn`:**

```tsx
import { queryOptions } from '@tanstack/react-query'

// src/features/cameras/api/queries.ts
export const cameraDetailOptions = (id: string) =>
  queryOptions({
    queryKey: cameraKeys.detail(id),
    queryFn: () => api.getCamera(id),
  })

// Consumer — key and fn travel together; no risk of mismatched queryKey
const { data } = useQuery(cameraDetailOptions(id))
// Prefetch uses the same options object
await queryClient.prefetchQuery(cameraDetailOptions(id))
```

`queryOptions()` is the v5-idiomatic way to package a query definition. Use the key factory inside it; the factory still centralizes key shapes.
