---
title: Persist Deliberately — Partialize and Version
impact: MEDIUM
impactDescription: blanket persistence resurrects stale/transient state after reload
tags: zustand, persist, migration
---

## Persist Deliberately — Partialize and Version

`persist` without `partialize` writes the entire store — including transient state (errors, loading flags, selections) that should never survive a reload — and without `version`/`migrate`, any schema change crashes returning users with stale payloads.

**Incorrect:**

```tsx
export const useLayoutStore = create<LayoutState>()(
  persist((set) => ({ gridSize: '2x2', focusedId: null, dragState: null, /* ... */ }), {
    name: 'layout',
    // missing partialize, version, and migrate
  })
)
```

**Correct:**

```tsx
export const useLayoutStore = create<LayoutState>()(
  persist((set) => ({ /* ... */ }), {
    name: 'layout',
    version: 2,
    partialize: (s) => ({ gridSize: s.gridSize, theme: s.theme }), // whitelist
    migrate: (persisted, version) =>
      version < 2 ? migrateV1toV2(persisted) : (persisted as PersistedLayout),
  })
)
```

Review checklist: every `persist` has `partialize` (whitelist, not blacklist), a `version`, and a `migrate` path; nothing server-owned or transient is persisted.
