---
title: Every Effect Subscription Returns Its Teardown
impact: HIGH
impactDescription: leaked listeners/players/intervals accumulate over the session, degrading memory and frame rate
tags: useEffect, cleanup, leak
---

**Rule:** Effects exist only to synchronize with the outside world, and every
subscribe/attach/create returns its matching teardown.

- CORRECT Example:

```tsx
useEffect(() => {
  player.on('error', onErr)
  return () => player.off('error', onErr)
}, [player, onErr])
```

- BAD Example:

```tsx
useEffect(() => { player.on('error', onErr) }, [player])   // listener leaks on every re-run
```
