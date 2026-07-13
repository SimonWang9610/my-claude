---
title: Code-Split Heavy Panels and Import by Direct Path
impact: MEDIUM
impactDescription: eager imports and barrel files ship rarely-used heavy code in the startup bundle
tags: bundle, lazy, suspense, barrel-imports, tree-shaking
---

**Rule:** Lazy-load routes and heavy conditionally-opened panels (`React.lazy` + `Suspense`);
import icons and library modules by specific path, never through a mega-barrel.

- CORRECT Example:

```tsx
const SettingsDialog = lazy(() => import('@/features/settings/SettingsDialog'))
import Videocam from '@mui/icons-material/Videocam'
```

- BAD Example:

```tsx
import SettingsDialog from '@/features/settings/SettingsDialog'   // in the startup bundle
import { Videocam, Settings } from '@mui/icons-material'          // whole barrel graph
```
