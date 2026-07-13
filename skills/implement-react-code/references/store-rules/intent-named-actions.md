---
title: Transitions Live in Intent-Named Store Actions
impact: MEDIUM
impactDescription: inline setState transitions drift apart across components and make state changes untraceable
tags: zustand, actions, setState
---

**Rule:** State transitions live in intent-named store actions (`focusDevice`, not `onClick`);
components call the action, never compute next-state inline or call raw `setState`.

- CORRECT Example:

```ts
// in the store — the transition has one owner and a domain name
focusDevice: (id) => set(s => ({ gridSize: 1, previousGrid: s.gridSize, focusedId: id })),
exitFocus:   () => set(s => ({ gridSize: s.previousGrid, focusedId: null })),
```

- BAD Example:

```tsx
// in a component — next-state computed inline, re-implemented slightly differently elsewhere
useLayoutStore.setState(s => ({ gridSize: 1, previousGrid: s.gridSize, focusedId: id }))
```
