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

**Upgrade path — `queryOptions()`:** For even tighter co-location, the TanStack Query v5 `queryOptions()` helper bundles `queryKey` + `queryFn` (and optional defaults) into one reusable object that both `useQuery` and `queryClient.prefetchQuery`/`ensureQueryData` accept without duplication:

```tsx
// src/features/cameras/api/queries.ts
import { queryOptions } from '@tanstack/react-query'

export const cameraQueries = {
  list: (filters: CameraFilters) =>
    queryOptions({
      queryKey: cameraKeys.list(filters),
      queryFn: () => api.getCameras(filters),
      staleTime: 30_000,
    }),
  detail: (id: string) =>
    queryOptions({
      queryKey: cameraKeys.detail(id),
      queryFn: () => api.getCamera(id),
    }),
}

// Usage:
const { data } = useQuery(cameraQueries.detail(id))
await queryClient.prefetchQuery(cameraQueries.list(filters))
```

Prefer `queryOptions()` for new domain hooks; the plain key-factory pattern remains valid for invalidation-only call sites.
