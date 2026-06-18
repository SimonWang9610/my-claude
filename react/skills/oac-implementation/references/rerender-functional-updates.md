---
title: Functional setState and Lazy Initializers
impact: MEDIUM
impactDescription: value-dependent callbacks churn identity; eager initializers pay full cost every render
tags: rerender, useState, useCallback, lazy-init
---

## Functional setState and Lazy Initializers

**Functional updates** keep callbacks dependency-free and therefore identity-stable:

```tsx
// Incorrect: depends on count → new function each change → breaks memo'd children
const increment = useCallback(() => setCount(count + 1), [count])
// Correct: no dependency → stable forever
const increment = useCallback(() => setCount((c) => c + 1), [])
```

**Lazy initialization** matters when the initial value is expensive — `useState(expensive())` executes `expensive()` on *every* render and discards the result after mount:

```tsx
// Incorrect: parses on every render
const [layout, setLayout] = useState(parseLayoutConfig(raw))
// Correct: parses once at mount
const [layout, setLayout] = useState(() => parseLayoutConfig(raw))
```

Cheap literals (`useState(0)`, `useState(null)`) don't need the function form — flagging those is noise. Look for: JSON.parse, localStorage reads, array building, anything iterating data in a `useState(...)` argument.
