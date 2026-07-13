---
title: Derive Values in Render, Never Mirror into State
impact: HIGH
impactDescription: an effect-mirrored copy double-renders a stale frame and drifts out of sync
tags: derived-state, useEffect, useState
---

**Rule:** A value computable from state/props is computed in render (or `useMemo`) — never
mirrored into state by an effect. The fix is deletion, not memoization.

- CORRECT Example:

```tsx
const fullName = `${firstName} ${lastName}`
```

- BAD Example:

```tsx
const [fullName, setFullName] = useState('')
useEffect(() => setFullName(`${firstName} ${lastName}`), [firstName, lastName])
```
