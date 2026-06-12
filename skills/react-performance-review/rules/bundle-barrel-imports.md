---
title: Don't Let Barrel Files Defeat Tree-Shaking
impact: MEDIUM
impactDescription: wildcard re-exports can pull entire directories into the bundle
tags: bundle, barrel, tree-shaking, imports, vite
---

## Don't Let Barrel Files Defeat Tree-Shaking

A barrel (`index.ts` of re-exports) makes every import of one symbol *parse and evaluate* the whole barrel graph. Rollup tree-shakes pure exports well in production, but anything with side effects (module-level registration, polyfills, CSS imports) survives shaking — and dev-mode cold start/HMR pays for the full graph regardless.

Rules of thumb:
- **Feature public-surface barrels** (a dozen exports) are fine and architecturally useful — keep them.
- **Mega-barrels** (`shared/index.ts` re-exporting 100 modules, or `export * from` chains) are the problem: imports of a button drag in chart helpers. Import from specific paths or split the barrel.
- **Icon libraries are the classic offender.** Check `@mui/icons-material` imports:

```tsx
// Slow dev, risky shaking — one import touches a 2000-module barrel:
import { Videocam, Settings } from '@mui/icons-material'
// Robust and fast:
import Videocam from '@mui/icons-material/Videocam'
import Settings from '@mui/icons-material/Settings'
```

(Or configure `optimizeDeps`/babel `transform-imports` to rewrite automatically.) Verify suspicions with the visualizer (`bundle-analyze-chunks`) instead of asserting from imports alone — modern Rollup shakes more than folklore claims.
