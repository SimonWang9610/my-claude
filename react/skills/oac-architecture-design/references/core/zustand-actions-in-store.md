---
title: Keep Mutation Logic in Store Actions
impact: HIGH
impactDescription: scattered setState logic makes state transitions untraceable
tags: zustand, actions, encapsulation
---

## Keep Mutation Logic in Store Actions

All logic that decides *how* state changes belongs in named store actions. Components call intent-named actions; they never reach in with raw `setState` or compute next-state themselves. This makes every possible state transition discoverable in one file and trivially testable without React.

**Incorrect:**

```tsx
function GridControls() {
  const setState = useLayoutStore.setState
  const onExpand = (id: string) =>
    setState((s) => ({
      focusedId: id,
      gridSize: s.gridSize === '1x1' ? s.previousGrid : s.gridSize,
      previousGrid: s.gridSize,           // business rule living in a component
    }))
}
```

**Correct:**

```tsx
const useLayoutStore = create<LayoutState>()((set) => ({
  gridSize: '2x2',
  previousGrid: '2x2',
  focusedId: null,
  focusCamera: (id: string) =>
    set((s) => ({ focusedId: id, previousGrid: s.gridSize, gridSize: '1x1' })),
  exitFocus: () => set((s) => ({ focusedId: null, gridSize: s.previousGrid })),
}))

// Component: declarative intent only
const focusCamera = useLayoutStore((s) => s.focusCamera)
```

Review flags: `useStore.setState` called from components; multiple components implementing the same transition slightly differently; actions named after UI events (`onButtonClick`) instead of domain intent (`focusCamera`).
