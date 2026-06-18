---
title: One Owner per Fact
impact: CRITICAL
impactDescription: duplicated facts inevitably disagree
tags: state, duplication, consistency
---

## One Owner per Fact

Every fact in the app must have exactly one authoritative owner. When the same fact lives in two places (two stores, a store and a component, a store and the URL), synchronization code appears, then fails.

Common duplication smells:

- The same `selectedX` in two stores "for convenience".
- A modal's open state in a store **and** mirrored in local state.
- Filter values in a store **and** in URL params, synced via effect.
- Two stores each keeping their own copy of "current user".

**Incorrect:**

```tsx
const usePlayerStore = create<PlayerState>()(/* ... selectedCameraId ... */)
const useSidebarStore = create<SidebarState>()(/* ... activeCameraId (duplicate) ... */)
// + a useEffect somewhere keeping them aligned
```

**Correct:**

```tsx
// One owner; the other consumer subscribes to it
const useSelectionStore = create<SelectionState>()((set) => ({
  selectedCameraId: null,
  select: (id) => set({ selectedCameraId: id }),
}))
// Sidebar and Player both read useSelectionStore
```

Any `useEffect` whose job is "keep A equal to B" is direct evidence of this defect; the fix is deleting one of A/B, not improving the sync.
