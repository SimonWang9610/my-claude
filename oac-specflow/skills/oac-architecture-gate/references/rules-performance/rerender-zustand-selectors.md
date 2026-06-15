---
title: Subscribe to the Smallest Store Slice
impact: HIGH
impactDescription: whole-store or object-returning selectors re-render on every store change
tags: rerender, zustand, selectors, useShallow
---

## Subscribe to the Smallest Store Slice

`useStore()` with no selector re-renders the component on *every* store change. A selector returning a fresh object (`s => ({a: s.a, b: s.b})`) is just as bad — new reference each time, fails equality, always re-renders. Select primitives, or wrap multi-field selections in `useShallow`.

**Incorrect:**

```tsx
const store = useLayoutStore()                            // everything
const { gridSize, theme } = useLayoutStore(
  (s) => ({ gridSize: s.gridSize, theme: s.theme })       // fresh object every time
)
```

**Correct:**

```tsx
const gridSize = useLayoutStore((s) => s.gridSize)        // primitive: cheap equality

import { useShallow } from 'zustand/react/shallow'
const { gridSize, theme } = useLayoutStore(
  useShallow((s) => ({ gridSize: s.gridSize, theme: s.theme }))
)
```

Also flag selectors doing fresh-array work per call (`s => s.items.filter(...)`) — they return new references on unrelated changes; move the derivation into the store (updated by actions) or memoize it. For values read only in callbacks, don't subscribe at all — see `rerender-defer-reads`.
