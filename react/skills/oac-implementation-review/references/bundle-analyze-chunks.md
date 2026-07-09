---
title: Measure the Bundle; Split Chunks Deliberately
impact: MEDIUM
impactDescription: bundle work without measurement optimizes the wrong things
tags: bundle, vite, rollup, visualizer, manualChunks
---

## Measure the Bundle; Split Chunks Deliberately

Never recommend bundle changes from vibes. Generate a treemap first:

```ts
// vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer'
export default defineConfig({
  plugins: [react(), visualizer({ filename: 'stats.html', gzipSize: true })],
})
```

Read the treemap for: duplicate dependencies (two date libs, lodash + lodash-es), accidentally-bundled dev tooling, heavy single-feature libs that should be lazy (`bundle-route-lazy`), and one giant vendor chunk that re-downloads entirely when any dependency bumps.

Deliberate vendor splitting separates stable cores (long-cache) from churning app code:

```ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'vendor-react': ['react', 'react-dom'],
        'vendor-mui': ['@mui/material', '@emotion/react', '@emotion/styled'],
      },
    },
  },
},
```

Cautions: over-splitting creates request waterfalls (chunk A imports chunk B imports chunk C) — keep manual chunks few and coarse; and for an Electron-packaged desktop app, network download size matters less, but parse/evaluate time at startup still does — weight findings toward startup execution cost, not transfer size.
