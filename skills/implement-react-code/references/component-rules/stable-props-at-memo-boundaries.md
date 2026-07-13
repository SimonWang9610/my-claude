---
title: Stable Props at memo Boundaries
impact: MEDIUM
impactDescription: one inline object/arrow prop silently defeats memo, re-rendering the expensive subtree anyway
tags: memo, rerender, prop-stability, hot-path
---

**Rule:** Place `memo` at expensive subtree boundaries (not leaves) and keep every prop passed to
it stable — hoist static JSX and default objects to module scope. (With
`babel-plugin-react-compiler` configured, skip manual memoization entirely.)

- CORRECT Example:

```tsx
const TILE_STYLE = { aspectRatio: '16/9' } as const

<Tile onSelect={select} style={TILE_STYLE}/>
```

- BAD Example:

```tsx
<Tile onSelect={() => select(id)} style={{ aspectRatio: '16/9' }}/>   // both props fresh every render
```
