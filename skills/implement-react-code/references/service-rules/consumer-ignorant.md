---
title: Services Emit — They Never Import Their Consumers
impact: HIGH
impactDescription: an upward import (store/component) inverts the dependency direction and risks cycles
tags: service, boundaries, callbacks, dependency-direction
---

**Rule:** The service imports nothing from `react`, components, or stores — it emits through the
callbacks/events its contract declares; the hook wires them inward.

- CORRECT Example:

```ts
export function createPlayerEngine({ onPosition }: { onPosition: (ms: number) => void }) { /* … */ }

// hook side wires the arrow inward:
createPlayerEngine({ onPosition: (ms) => usePlaybackStore.getState().setPosition(ms) })
```

- BAD Example:

```ts
import { usePlaybackStore } from '../store'   // service importing a store — upward, cycle risk
export function createPlayerEngine() {
  onTick(ms => usePlaybackStore.getState().setPosition(ms))
}
```
