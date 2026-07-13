---
title: Honest Types — Discriminated Unions over Boolean Bags
impact: HIGH
impactDescription: impossible states (isLoading && isError) compile and ship; laundered types hide holes until runtime
tags: typescript, discriminated-union, satisfies, any
---

**Rule:** No `any`, no `as`/`!` laundering; model variant and async state as a discriminated
union, not a bag of booleans; `satisfies` for fixtures and config; typed refs, events, and
boundary data. Applies at every level.

- CORRECT Example:

```ts
type State =
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'ready'; devices: Device[] }

const fixture = { id: '1', name: 'Door', status: 'online' } satisfies Device
```

- BAD Example:

```ts
type State = { isLoading: boolean; isError: boolean; data?: Device[] }   // impossible states compile
const device = raw as Device                                             // laundered — hole hidden
```
