---
title: Place memo at Expensive Boundaries — and Keep Props Stable
impact: HIGH
impactDescription: memo on the right subtree stops cascades; unstable props make it useless
tags: rerender, memo, useCallback, useMemo, props
---

## Place memo at Expensive Boundaries — and Keep Props Stable

(Skip if the React Compiler is enabled — it inserts this for you; remove leftover ceremony instead. See `react19-modern-apis` in `oac-implementation`.)

`memo` pays off at boundaries where a cheap parent re-renders often but an expensive subtree's props rarely change — e.g., a grid container tracking selection above camera tiles. It is wasted on leaf components rendering three DOM nodes, and *defeated* whenever any prop is a fresh reference each render.

**The defeat pattern (memo present, useless):**

```tsx
const CameraTile = memo(function CameraTile({ camera, onSelect, style }: Props) { ... })

function Grid() {
  return cams.map((c) => (
    <CameraTile
      key={c.id}
      camera={c}
      onSelect={() => select(c.id)}      // new function per render
      style={{ aspectRatio: '16/9' }}     // new object per render
    />
  ))
}
```

**Correct:**

```tsx
const TILE_STYLE = { aspectRatio: '16/9' } as const        // hoist static

function Grid() {
  const select = useSelectionStore((s) => s.select)         // store actions are stable
  return cams.map((c) => (
    <CameraTile key={c.id} camera={c} onSelect={select} style={TILE_STYLE} />
  ))
}
// Tile calls onSelect(camera.id) — pass the id at call site instead of binding per-item.
```

Verify the memo actually holds: every prop must be primitive, hoisted, from-store-stable, or `useCallback`/`useMemo`-stabilized. A `memo` with one unstable prop is dead weight — don't add it, or fix the prop.
