---
title: Implement Exactly the Contract's Surface
impact: HIGH
impactDescription: undeclared props and missing states drift the unit away from what consumers and tests were wired to
tags: contract, props, api, conformance
---

**Rule:** Props name-for-name, type-for-type from the contract — no undeclared props, no widened
optionals, every promised state rendered. A case the contract missed is a design gap, not a new prop.

- CORRECT Example:

```tsx
// contract: DeviceTile({ device }) · states: unknown | online | offline
function DeviceTile({ device }: DeviceTileProps) {
  if (device.status === 'unknown') return <UnavailableTile/>
  return <Tile status={device.status}>{device.name}</Tile>
}
```

- BAD Example:

```tsx
// undeclared `showLabel` prop; the promised 'unknown' state is never rendered
function DeviceTile({ device, showLabel = true }) {
  return <Tile>{device.name}</Tile>
}
```
