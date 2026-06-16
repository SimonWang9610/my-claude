---
title: Composition over Boolean Prop Proliferation
impact: MEDIUM-HIGH
impactDescription: each boolean doubles the state space; combinations become untestable
tags: composition, props, api-design
---

## Composition over Boolean Prop Proliferation

When a component accretes boolean props (`hideHeader`, `compact`, `withToolbar`, `isOverlayMode`), each one doubles its configuration space and the component body fills with branches. Restructure so callers compose what they need instead of toggling what they don't.

**Incorrect:**

```tsx
<VideoTile camera={cam} hideControls showTimestamp compact noBorder isPtzEnabled />
```

**Correct (expose parts; callers compose):**

```tsx
<VideoTile camera={cam}>
  <VideoTile.Surface />
  <VideoTile.Timestamp />
  {cam.ptz && <VideoTile.PtzOverlay />}
</VideoTile>
```

Review thresholds: 1–2 booleans is normal; 3+ booleans that alter *structure* (not just styling) is a finding. Pair with `compose-compound-components` for the target pattern and `compose-explicit-variants` when the booleans actually encode distinct modes.
