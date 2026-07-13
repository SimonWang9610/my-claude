---
title: Functional setState Updates and Lazy Initializers
impact: MEDIUM
impactDescription: closure-reading callbacks churn identity (breaking memoized children); non-lazy expensive initializers re-run every render
tags: useState, useCallback, identity, lazy-init
---

**Rule:** Use functional updates (`set(c => c + 1)`) to keep callbacks dependency-free and
stable, and lazy initializers (`useState(() => expensive())`) for expensive initial values.

- CORRECT Example:

```tsx
const increment = useCallback(() => setCount(c => c + 1), [])
const [config] = useState(() => parseLayoutConfig(raw))
```

- BAD Example:

```tsx
const increment = useCallback(() => setCount(count + 1), [count])   // new identity per count
const [config] = useState(parseLayoutConfig(raw))                   // parses on every render
```
