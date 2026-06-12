---
title: Use content-visibility for Long Offscreen Sections
impact: MEDIUM
impactDescription: skips layout/paint for offscreen content without JS
tags: rendering, css, content-visibility, layout
---

## Use content-visibility for Long Offscreen Sections

For long pages of mostly-static sections (settings pages, report views, dashboards with many panels), `content-visibility: auto` lets the browser skip rendering work for offscreen sections entirely — no virtualization code needed.

```css
.report-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 480px;  /* placeholder size: prevents scrollbar jumping */
}
```

When to choose what:
- **Dynamic, uniform, data-driven rows** (event logs) → JS virtualization (`render-virtualize-lists`): also caps React component count.
- **Static, heterogeneous sections** (long settings/report page) → `content-visibility`: zero JS, React components still mount (effects run) but layout/paint is skipped.

Always pair with `contain-intrinsic-size`, or scroll position jumps as sections materialize. Not a fix for React render cost — components inside still render in the React sense; this saves browser layout/paint only.
