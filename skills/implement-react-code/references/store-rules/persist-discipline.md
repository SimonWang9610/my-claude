---
title: Persist Only a Versioned Whitelist
impact: HIGH
impactDescription: blanket persistence resurrects transient state; unversioned schema changes crash returning users
tags: zustand, persist, partialize, migration
---

**Rule:** Every `persist` has a `partialize` whitelist plus `version` + `migrate` — never blanket
persistence.

- CORRECT Example:

```ts
persist(creator, {
  name: 'layout', version: 2,
  partialize: s => ({ gridSize: s.gridSize, theme: s.theme }),
  migrate: (persisted, version) => upgrade(persisted, version),
})
```

- BAD Example:

```ts
persist(creator, { name: 'layout' })   // whole store persisted, unversioned — drag state resurrects
```
