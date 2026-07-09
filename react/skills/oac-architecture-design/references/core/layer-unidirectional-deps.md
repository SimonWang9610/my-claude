---
title: Dependencies Point One Direction
impact: MEDIUM
impactDescription: upward imports create cycles and make layers untestable alone
tags: layering, dependencies, imports
---

## Dependencies Point One Direction

Establish a strict import direction and treat violations as defects:

```
app (shell/router/providers)
  ↓
features (components → hooks → store/api)
  ↓
shared (UI primitives, generic hooks)
  ↓
services (player engine, transport, IPC)   — knows nothing above it
```

Violations to flag:
- A **service** importing a store or component (services must expose callbacks/events; stores subscribe to services, never the reverse).
- A **store** importing components or MUI (see `zustand-no-component-coupling`).
- **shared/** importing from **features/** ("shared" that knows about features isn't shared).
- Circular imports between feature stores (extract the shared concept into its own module both depend on).

```tsx
// Incorrect: service pushes into a store it knows about
// services/playerEngine.ts
import { usePlaybackStore } from '@/features/playback/store'  // upward import

// Correct: service exposes events; the feature wires them
export function createPlayerEngine(opts: { onPosition: (ms: number) => void }) { ... }
// features/playback/hooks/usePlayerEngine.ts wires onPosition → store/refs
```

The wiring lives at the feature boundary, not inside the lower layer: the service stays ignorant of the store, and the hook connects the two.
