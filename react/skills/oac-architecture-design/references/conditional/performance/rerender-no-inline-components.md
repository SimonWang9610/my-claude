---
title: Never Define Components Inside Components
impact: HIGH
impactDescription: inline component types change identity per render, forcing full remounts
tags: rerender, remount, inline-components, state-loss
---

## Never Define Components Inside Components

A component defined inside another's body is a *new type* on every render. React sees a different element type, unmounts the old subtree and mounts a new one — destroying state (inputs lose focus, video elements re-initialize!) and paying full mount cost each time. This is worse than a re-render; it's a remount.

**Incorrect:**

```tsx
function CameraPanel({ camera }) {
  function StatusBadge() {                       // new type identity every render
    return <Chip label={camera.status} />
  }
  return <div><StatusBadge /><VideoSurface camera={camera} /></div>
}
```

**Correct:**

```tsx
function StatusBadge({ status }: { status: CameraStatus }) {
  return <Chip label={status} />
}
function CameraPanel({ camera }) {
  return <div><StatusBadge status={camera.status} /><VideoSurface camera={camera} /></div>
}
```

Same defect in disguise: `renderX` props invoked as `<props.renderRow />` (capitalized element) instead of called as a function, and components returned from hooks. In a video app this one is vicious — a remounted tile tears down and renegotiates its stream.
