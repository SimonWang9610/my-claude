---
title: Organize by Feature, Not File Type
impact: MEDIUM
impactDescription: type-based folders scatter each feature across the tree
tags: layering, folders, structure
---

## Organize by Feature, Not File Type

Group code by feature so each feature is self-contained and deletable; keep only genuinely shared primitives in `shared/`.

```
src/
├── features/
│   ├── camera-grid/
│   │   ├── components/      # GridLayout, CameraTile, ...
│   │   ├── hooks/           # useGridLayout, ...
│   │   ├── store.ts         # layout store (client state)
│   │   ├── api/             # queries, mutations, keys.ts
│   │   └── index.ts         # public surface of the feature
│   ├── playback/
│   └── ptz/
├── shared/                  # design-system wrappers, generic hooks/utils
├── services/                # player engine, WebSocket, IPC (see layer-service-isolation)
└── app/                     # router, providers, shell
```

Two enforcement points that make this real rather than cosmetic:
- **Public surface**: other features import only from `features/x` (its `index.ts`), never deep paths into its internals.
- **Promotion rule**: code used by 2+ features moves to `shared/` explicitly; features never import from sibling features' guts.

Review flag: `import ... from '../../another-feature/components/...'` — cross-feature deep imports are the defect, regardless of folder cosmetics.

> If the existing project has its own established structure, don't enforce this retroactively; but try to make the new features organized this way as much as possible, and enforce it for all future features. Over time, the new structure will become dominant and the old structure can be refactored or sunset as needed.