---
title: Don't Copy Props into State
impact: HIGH
impactDescription: prop copies silently ignore parent updates
tags: state, props, key-reset
---

## Don't Copy Props into State

Initializing state from a prop (`useState(props.x)`) snapshots it once; later prop changes are ignored, producing "why didn't it update" bugs.

**Incorrect:**

```tsx
function CameraTile({ camera }: { camera: Camera }) {
  const [name, setName] = useState(camera.name) // frozen at mount
  ...
}
```

**Correct — pick by intent:**

```tsx
// (a) Display only: use the prop directly
<Typography>{camera.name}</Typography>

// (b) Editable draft that should reset when the entity changes: key reset
<CameraEditForm key={camera.id} camera={camera} />
function CameraEditForm({ camera }) {
  const [name, setName] = useState(camera.name) // OK: remounts per camera.id
}

// (c) Controlled: lift the state, pass value + onChange
```

The `key`-reset pattern (b) is the legitimate use of prop-initialized state — call it out as correct when seen, don't flag it.
