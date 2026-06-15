---
title: Hoist Static JSX and Static Defaults
impact: MEDIUM
impactDescription: static elements re-created per render add allocation and reconciliation noise
tags: rendering, hoist, static, props
---

## Hoist Static JSX and Static Defaults

Elements and objects that never change shouldn't be re-created on every render. Hoisting them to module scope makes them referentially identical across renders, letting React bail out of reconciling them and keeping memo boundaries intact.

```tsx
// Incorrect: re-created every render
function ConnectionStatus({ state }: { state: ConnState }) {
  const spinner = <CircularProgress size={16} />            // static element
  return state === 'connecting' ? spinner : <ConnectedBadge state={state} />
}
function Grid({ tileSx = { aspectRatio: '16/9' } }) { ... } // new default object/call

// Correct:
const SPINNER = <CircularProgress size={16} />
const DEFAULT_TILE_SX = { aspectRatio: '16/9' } as const
function ConnectionStatus({ state }: { state: ConnState }) {
  return state === 'connecting' ? SPINNER : <ConnectedBadge state={state} />
}
function Grid({ tileSx = DEFAULT_TILE_SX }) { ... }
```

The default-parameter case is sneaky: `= {…}` or `= () => {}` in a destructured prop evaluates fresh on each render, silently defeating any `memo` below. (With the React Compiler enabled, element hoisting is automated — focus on the default-parameter pattern, which the compiler also handles, and on hoisting for *clarity*.)
