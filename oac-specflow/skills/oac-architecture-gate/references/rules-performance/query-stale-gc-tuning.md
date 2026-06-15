---
title: Tune staleTime Deliberately; Prevent Refetch Storms
impact: MEDIUM
impactDescription: default staleTime 0 refetches on every mount/focus — multiplied across components
tags: query, staleTime, refetch, network
---

## Tune staleTime Deliberately; Prevent Refetch Storms

TanStack Query's default `staleTime` is `0`: every new mount of a consumer and every window refocus triggers a background refetch. With many components sharing queries (a camera grid where each tile uses camera config), defaults produce refetch storms — network chatter, server load, and render churn from arriving responses.

```tsx
// Per-domain defaults at client construction:
const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000 } },   // app-wide floor
})

// Per-query, matched to actual data volatility:
useQuery({
  queryKey: cameraKeys.detail(id),
  queryFn: () => api.getCamera(id),
  staleTime: 5 * 60_000,        // camera config changes rarely
})
```

Review checklist:
- Is `staleTime` deliberate (set app-wide and/or per-domain), or accidental default-0?
- `refetchInterval` polling: is the interval justified, and is it disabled when hidden (`refetchIntervalInBackground: false`)? Should this be a push channel (WebSocket → `setQueryData`) instead of polling?
- For genuinely-live data, polling many keys individually multiplies requests — batch endpoints or push updates.

`staleTime` (when refetch happens) vs `gcTime` (when unused cache is dropped) are independent; raising `gcTime` for instant back-navigation is a separate, also-legitimate tweak.
