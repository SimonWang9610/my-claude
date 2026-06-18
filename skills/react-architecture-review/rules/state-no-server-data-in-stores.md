---
title: Never Mirror Server Data into Client Stores
impact: CRITICAL
impactDescription: duplicated server state goes stale and causes inconsistency bugs
tags: state, zustand, query, server-state
---

## Never Mirror Server Data into Client Stores

Server data (anything fetched from an API and owned by a backend) belongs in TanStack Query's cache. Copying it into Zustand or `useState` creates a second source of truth that the Query cache can't invalidate — after a mutation, the store copy is stale and the UI lies.

**Incorrect:**

```tsx
const useCameraStore = create((set) => ({
  cameras: [] as Camera[],
  loadCameras: async () => {
    const cameras = await api.getCameras()
    set({ cameras })           // stale after any mutation elsewhere
  },
}))
```

**Correct:**

```tsx
// Query owns the data; components subscribe directly
function useCameras() {
  return useQuery({ queryKey: cameraKeys.lists(), queryFn: api.getCameras })
}

// Client store holds only client-owned facts ABOUT the data
const useSelectionStore = create<SelectionState>()((set) => ({
  selectedCameraId: null as string | null,
  select: (selectedCameraId: string) => set({ selectedCameraId }),
}))
```

The legitimate combination is *references*: stores may hold ids/selection/ordering that point into Query data, never the entities themselves. If derived shapes are needed, use Query's `select` option (see `query-select-transform`).

Flutter-migration note: this maps to the Riverpod discipline of `AsyncNotifierProvider` owning remote data while plain notifiers own UI state — the same separation, with Query playing the async-provider role.
