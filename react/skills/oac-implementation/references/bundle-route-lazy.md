---
title: Lazy-Load Routes and Heavy Panels
impact: MEDIUM
impactDescription: eager imports put rarely-used heavy code in the startup bundle
tags: bundle, lazy, suspense, code-splitting, vite
---

## Lazy-Load Routes and Heavy Panels

Everything statically imported from the entry tree ships in the startup bundle. Routes and heavy, conditionally-opened surfaces (settings dialogs, report/export views, chart panels, admin areas) should load on demand via `React.lazy` — Vite automatically code-splits dynamic imports.

```tsx
import { lazy, Suspense } from 'react'

const ReportsPage = lazy(() => import('@/features/reports/ReportsPage'))
const SettingsDialog = lazy(() => import('@/features/settings/SettingsDialog'))

<Route path="/reports" element={
  <Suspense fallback={<PageSkeleton />}>
    <ReportsPage />
  </Suspense>
} />

// Conditionally-mounted heavy dialog: nothing loads until first open
{settingsOpen && (
  <Suspense fallback={null}>
    <SettingsDialog onClose={...} />
  </Suspense>
)}
```

Judgment calls when splitting: the *primary* screen (the camera grid in a monitoring app) should stay eager — lazy-loading the thing users open the app for adds a flash for nothing. Heavy libraries used by one feature (chart libs, PDF/export, editors) are the highest-value splits. For predictable navigation, prefetch on hover/intent: call the same `import()` in `onMouseEnter` — Vite dedupes, so the later `lazy` resolves instantly.
