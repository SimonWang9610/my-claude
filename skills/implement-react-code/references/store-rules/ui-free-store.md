---
title: The Store Knows Nothing About the UI
impact: HIGH
impactDescription: a UI-aware store inverts the dependency direction and can't be tested without rendering
tags: zustand, boundaries, domain-state
---

**Rule:** The store compiles with zero imports from `react`/components/MUI — it holds domain
facts (the error condition), never element refs or presentation state (the snackbar's visibility).

- CORRECT Example:

```ts
interface StreamState {
  streamErrors: DeviceError[]   // the domain fact; the component watching it renders the snackbar
}
```

- BAD Example:

```ts
interface StreamState {
  videoRefs: Map<string, HTMLVideoElement>   // DOM handles in the store
  showErrorSnackbar: boolean                 // presentation state
}
```
