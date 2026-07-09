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

// Component: declarative intent only — one atomic selector per value
const focusCamera = useLayoutStore((s) => s.focusCamera)
```

**Selecting multiple fields — use `useShallow`:** reading several fields in one call without a shallow comparator causes unnecessary re-renders because the selector returns a new object reference every time. Import `useShallow` from `zustand/react/shallow` (not `zustand/shallow`):

```tsx
import { useShallow } from 'zustand/react/shallow'

// Incorrect — new object every render even if values didn't change
const { gridSize, focusedId } = useLayoutStore((s) => ({ gridSize: s.gridSize, focusedId: s.focusedId }))

// Correct
const { gridSize, focusedId } = useLayoutStore(
  useShallow((s) => ({ gridSize: s.gridSize, focusedId: s.focusedId }))
)
// Or prefer two atomic selectors — no useShallow needed
const gridSize  = useLayoutStore((s) => s.gridSize)
const focusedId = useLayoutStore((s) => s.focusedId)
```

Alternatively, wrap the store in a named hook that exposes atomic selectors so callers never need to remember `useShallow`.

Review flags: `useStore.setState` called from components; multiple components implementing the same transition slightly differently; actions named after UI events (`onButtonClick`) instead of domain intent (`focusCamera`); multi-field object selectors without `useShallow`.
