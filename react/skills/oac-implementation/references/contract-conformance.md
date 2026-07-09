---
title: Implement Exactly the Fixed Contract
impact: CRITICAL
impactDescription: a unit that drifts from its contract breaks every consumer wired to it
tags: contract, public-api, props, return-type, states, scope
---

## Implement Exactly the Fixed Contract

The contract and architecture are settled inputs. Your job is to make the code satisfy the
contract's declared surface — not to widen, rename, or re-decide it. Consume the architecture's
decisions (query keys, store slices, layer boundaries); do not invent parallel ones.

**Conform on every axis the contract names:**

| Contract element | Conformance means |
|------------------|-------------------|
| Exported names | Export exactly those; no extra public exports, no renames |
| Props | Same names + types; no undeclared props, no widened optionality |
| Return type | The component/hook returns the declared type (incl. every union member) |
| Promised states | Each named state (loading / error / empty / success / disabled) is reachable and observably rendered — see `data-states` |
| Data source | Read/write through the architecture's SSOT (the named query key, the named store slice) — never a second copy |
| Side effects | Only those the contract implies; no extra network calls, no writes to unowned state |

**Drift to avoid — the component satisfies the *happy path* but not the contract:**

```tsx
// Contract: CameraTile({ camera }: { camera: Camera }) renders name + a live/offline status,
//           and an "unavailable" state when camera.status === 'unknown'.
function CameraTile({ camera, showLabel = true }: Props) {   // ✗ undeclared prop `showLabel`
  return <div>{camera.name} — {camera.status}</div>          // ✗ 'unknown' state not handled
}
```

```tsx
// Conformant: exactly the declared props; every promised state rendered.
function CameraTile({ camera }: { camera: Camera }) {
  if (camera.status === 'unknown') return <UnavailableTile name={camera.name} />
  return <div>{camera.name} <StatusDot status={camera.status} /></div>
}
```

If the contract is ambiguous or under-specifies a case you must handle, stop and surface the
gap to the caller — do not silently guess a wider API. Filling a hole with an invented prop or
export is drift, and the next unit that was written against the real contract will break.
