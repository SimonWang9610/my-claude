---
title: Derive Values, Don't Store Them
impact: CRITICAL
impactDescription: stored derivations drift out of sync and add redundant renders
tags: state, derived-state, useEffect
---

## Derive Values, Don't Store Them

If a value can be computed from existing props/state, compute it during render (or in a selector). Storing it — especially syncing it with `useEffect` — creates state drift and extra render passes.

**Incorrect:**

```tsx
const [cameras, setCameras] = useState<Camera[]>([])
const [onlineCount, setOnlineCount] = useState(0)

useEffect(() => {
  setOnlineCount(cameras.filter(c => c.status === 'online').length)
}, [cameras])
```

**Correct:**

```tsx
const onlineCount = cameras.filter(c => c.status === 'online').length
// or, in a Zustand selector:
const onlineCount = useCameraUiStore(s => s.visibleIds.length)
```

`useEffect` that only calls a setter from other state/props is the signature of this defect — flag every instance. The fix is deletion, not memoization.

**Implementation lens:** with this placement fixed, the coding discipline is to compute the value in render (or a `useMemo`/selector) — never a `useEffect` + `setState` sync. See the `oac-implementation` skill (`hooks-correctness`).

Reference: [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)
