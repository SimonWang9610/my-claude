---
title: Every Subscription Has a Teardown
impact: HIGH
impactDescription: leaked listeners/players accumulate; performance degrades over session time
tags: cleanup, useEffect, leaks, video, listeners
---

## Every Subscription Has a Teardown

Performance that degrades over a session (growing memory, rising CPU, eventually dropped frames) is usually leaks: effects that subscribe, attach, or create without returning a cleanup. In a multi-camera app the heavy offenders are player instances, media streams, WebSocket handlers, rAF loops, and `window`/`document` listeners.

**Audit every `useEffect` that:**
- calls `addEventListener` / `.on(...)` / `subscribe(...)` → must return the matching remove/off/unsubscribe
- creates a player/connection/worker → must return `.destroy()`/`.close()`/`.terminate()`
- starts `requestAnimationFrame`/`setInterval` → must cancel/clear

**Classic leak (re-attach without detach on dep change):**

```tsx
useEffect(() => {
  player.on('error', handleError)         // attaches again on every `player` change
}, [player])                              // old player still holds handleError
```

**Correct:**

```tsx
useEffect(() => {
  player.on('error', handleError)
  return () => player.off('error', handleError)
}, [player, handleError])
// handleError must be stable — either defined at module scope or wrapped in useCallback.
// An unstable handleError re-subscribes on every render, defeating the cleanup.
```

Remember effects re-run on dependency change, not just unmount — cleanup must be correct for both. StrictMode's double-invoke in dev is the cheap leak detector: if mounting twice breaks the component, a teardown is missing.
