---
title: Never Define a Component Inside a Component
impact: HIGH
impactDescription: an inline component is a new type every render — the subtree unmounts and remounts, losing state
tags: component-identity, remount, state-loss
---

**Rule:** Hoist every component definition to module scope; an inline definition remounts its
subtree on each parent render (a playing video restarts, form state vanishes).

- CORRECT Example:

```tsx
function StatusBadge({ status }: BadgeProps) { return <Chip label={status}/> }

function Panel({ status }: PanelProps) {
  return <StatusBadge status={status}/>
}
```

- BAD Example:

```tsx
function Panel({ status }: PanelProps) {
  function StatusBadge() { return <Chip label={status}/> }   // new type every render
  return <StatusBadge/>
}
```
