---
title: Place State at the Right Level
impact: CRITICAL
impactDescription: wrong placement is the root cause of most state-management pain
tags: state, ownership, zustand, query, useState
---

## Place State at the Right Level

Every piece of state should live in the most local place that satisfies its readers. Walk this decision tree for each state atom:

1. **Server-owned data** (fetched, mutated via API) → TanStack Query. Full stop.
2. **Used by one component** → `useState`/`useReducer` in that component.
3. **Used by a small subtree** → lift to the common parent, pass down (or a narrow Context if prop-drilling exceeds ~2–3 levels).
4. **Genuinely app-wide client state** (auth session, layout mode, active camera grid config) → Zustand store.
5. **URL-representable** (selected tab, filters, detail id) → router search params, so it survives reload and is shareable.
6. **Feature-specific but cross-cutting** (e.g. camera layout shared by camera grid and PTZ control) → Zustand store owned by the feature folder, not global.

**Incorrect (global by default):**

```tsx
// Everything dumped into one global store "to be safe"
const useAppStore = create((set) => ({
  isSettingsDialogOpen: false,   // used by one component
  hoveredCameraId: null,         // transient UI detail
  cameras: [],                   // server data
}))
```

**Correct:**

```tsx
// Dialog open state: local
const [open, setOpen] = useState(false)

// Server data: query
const { data: cameras } = useQuery({ queryKey: cameraKeys.list(), queryFn: fetchCameras })

// Truly shared client state: store
const useLayoutStore = create<LayoutState>()((set) => ({
  gridSize: '2x2',
  setGridSize: (gridSize) => set({ gridSize }),
}))
```

Review heuristic: for each store field, ask "who reads this, who writes this?" If the answer is one component, demote it. If the answer is "the server is the real owner," move it to Query.
