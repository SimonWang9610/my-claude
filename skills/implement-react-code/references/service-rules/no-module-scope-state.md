---
title: No Module-Scope Mutable State
impact: HIGH
impactDescription: module-scope mutables are shared across every consumer and test — order-dependent failures, silent leaks
tags: service, module-scope, state, test-isolation
---

**Rule:** No top-level `Map`/array/`let` accumulating domain state — state lives in the instance
`create` returns (or a ref/store on the React side).

- CORRECT Example:

```ts
export function createRegistry() {
  const controllers = new Map<string, AbortController>()   // instance-scoped
  return { register, abortAll }
}
```

- BAD Example:

```ts
const controllers = new Map<string, AbortController>()     // module scope — leaks across tests
```
