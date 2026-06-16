---
title: Keep MUI Styling Out of the Hot Path
impact: MEDIUM-HIGH
impactDescription: per-render style objects and styled() factories churn Emotion's cache
tags: rendering, mui, sx, styled, emotion
---

## Keep MUI Styling Out of the Hot Path

MUI's `sx` and `styled()` run through Emotion at runtime. Three patterns to flag, in descending severity:

**1. `styled()` created inside a component** — a new styled component type per render: full remount of that subtree every time (same defect class as `rerender-no-inline-components`):

```tsx
function Tile() {
  const Frame = styled(Box)({ borderRadius: 8 })   // new type identity per render
  return <Frame>...</Frame>
}
// Fix: hoist to module scope.
```

**2. Dynamic values flowing through `sx`/`styled` in animated/hot paths** — every distinct value generates and inserts a new CSS class. A drag/progress value through `sx` means class generation per frame:

```tsx
<Box sx={{ width: `${progress}%` }} />                       // new class per value
// Fix for hot values: plain style (inline) or CSS variable + ref write:
<Box style={{ width: `${progress}%` }} />
```

**3. Fresh `sx` objects per render on memo'd children** — defeats `memo` (referential inequality). Hoist static `sx` to module constants; memoize the rare genuinely-dynamic ones.

Calibration: a static inline `sx` on a settings-page component is *fine* — Emotion caches by content; don't blanket-flag `sx`. The findings are: `styled` in render bodies (always), dynamic styling on per-frame values (always), and unstable `sx` only where it defeats an intentional memo boundary or sits in a profiler-confirmed hot path.
