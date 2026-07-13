---
title: Map Failures to Typed Errors at the Boundary
impact: HIGH
impactDescription: a console.error-only catch is invisible to the UI — the promised error state can never render
tags: service, errors, error-state
---

**Rule:** Failures map to the contract's error type at the service boundary — never a swallowed
`catch`.

- CORRECT Example:

```ts
catch (e: unknown) { throw new StreamError('connect-failed', { cause: e }) }
```

- BAD Example:

```ts
catch (e) { console.error(e) }   // invisible to the UI — no error state can render
```
