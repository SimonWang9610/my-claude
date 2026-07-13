---
title: Keep Per-Frame Values Out of sx
impact: MEDIUM
impactDescription: a dynamic sx value mints a fresh Emotion class per value; a per-render styled() remounts the subtree
tags: mui, sx, emotion, styling, hot-path
---

**Rule:** Continuously-changing values use plain `style`, not `sx`; never create `styled()`
inside a component body.

- CORRECT Example:

```tsx
<Box style={{ width: `${progress}%` }}/>   // plain inline style, no class churn
```

- BAD Example:

```tsx
<Box sx={{ width: `${progress}%` }}/>      // fresh CSS class per value
```
