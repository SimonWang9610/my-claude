---
title: Never Seed State from a Prop
impact: HIGH
impactDescription: the seed freezes the mount-time value and silently ignores every later parent update
tags: props, useState, key-reset
---

**Rule:** No `useState(props.x)` — read the prop directly, or remount per entity by identity
(`key`) for an editable draft.

- CORRECT Example:

```tsx
<DeviceEditForm key={device.id} device={device}/>   // fresh draft per entity, resets by identity
```

- BAD Example:

```tsx
const [name, setName] = useState(device.name)       // frozen at mount; parent updates ignored
```
