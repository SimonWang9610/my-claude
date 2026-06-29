---
name: react-performance-review
description: Reviews and optimizes React rendering performance — wasted re-renders, slow frames, high-frequency data handling (video playback, gestures, live streams), list rendering, and Vite bundle size. Trigger when the user mentions React performance, lag, jank, dropped frames, slow UI, excessive re-renders, memoization questions (memo/useMemo/useCallback), large bundles, slow startup, or asks to review/profile/optimize React code for speed — including vague reports like "my app feels slow" or "is this component rendering too much". Targets React 19 + Vite + Zustand + TanStack Query v5 + MUI (client-side, no Next.js/RSC). Produces a prioritized findings report and a phased development plan.
---

# React Performance Review

Reviews React code for rendering and runtime performance problems, then produces a **Review Report** (prioritized findings) and a **Development Plan** (phased remediation). Targets client-side React 19 apps on Vite, with Zustand, TanStack Query, and MUI. Especially attentive to high-frequency data paths (video playback positions, live streams, pointer gestures) where React's render loop is the wrong tool.

Architecture problems (state ownership, store design, layering) belong to the sibling skill `react-architecture-review`. Performance findings often have architectural root causes — when so, name the root cause briefly and recommend that skill rather than redesigning the architecture here.

## Review Workflow

1. **Establish the symptom and budget.** What is actually slow — interaction lag, scroll jank, dropped video frames, slow startup, memory growth? At 60fps the frame budget is ~16ms. If the user reports no symptom, this is a preventive audit: prioritize the High/Critical categories and say so in the report.
2. **Prefer evidence over inspection.** If the app can be run, profile before concluding: React DevTools Profiler (which components render per interaction, and why), browser Performance panel (long tasks, layout thrash), `rollup-plugin-visualizer` for bundle questions. When only static review is possible, mark findings as suspected vs. confirmed — don't present static suspicion as measured fact.
3. **Check the React Compiler first.** Look for `babel-plugin-react-compiler` in the Vite/Babel config. If enabled, most manual memoization advice inverts (ceremony becomes noise to remove); if not, memoization rules apply as written. State which case applies at the top of the report.
4. **Walk the rule categories** in priority order, reading `rules/<name>.md` when code matches a rule's territory — each file has the rationale and incorrect/correct examples needed to confirm a finding. Attribute findings to file/line.
5. **Estimate impact honestly.** A re-render of a 3-element subtree is not a finding. Tie each finding to its blast radius: how often it fires (per frame? per keystroke? once?) × how much work it re-does.
6. **Write the Review Report**, then the **Development Plan** (formats below).

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | High-Frequency Data Paths | CRITICAL | `hf-` |
| 2 | Re-render Elimination | HIGH | `rerender-` |
| 3 | Rendering & DOM Cost | MEDIUM-HIGH | `render-` |
| 4 | Data Layer Performance | MEDIUM | `query-` |
| 5 | Bundle & Startup (Vite) | MEDIUM | `bundle-` |

## Quick Reference

### 1. High-Frequency Data Paths (CRITICAL)

Anything updating faster than ~10×/second must not flow through React's render cycle.

- `hf-out-of-react-loop` - Per-frame values (playback position, stream stats) bypass React: rAF + refs/direct DOM/canvas writes
- `hf-throttle-event-streams` - pointermove/wheel/scroll handlers coalesced to one update per frame via rAF throttling
- `hf-canvas-for-dynamic-overlays` - Rapidly-changing visuals (timelines, motion boxes, PTZ indicators) drawn on canvas, not as DOM element swarms
- `hf-effect-cleanup` - Every subscription/player/listener has a teardown; leaks compound into degradation

### 2. Re-render Elimination (HIGH)

- `rerender-zustand-selectors` - Subscribe to the smallest slice: per-field selectors, `useShallow` for multi-field, never whole-store
- `rerender-defer-reads` - State read only inside callbacks uses `getState()`, not a reactive subscription
- `rerender-memo-boundaries` - `memo` expensive subtrees at the right cut points, with props kept referentially stable
- `rerender-no-inline-components` - Never define components inside components (remount on every render)
- `rerender-context-splitting` - Split contexts by change-rate; separate state from dispatch
- `rerender-children-as-props` - Pass subtrees as `children` so a stateful wrapper's re-render skips them
- `rerender-functional-updates` - Functional `setState` + lazy `useState(() => ...)` initializers for stable callbacks and cheap mounts
- `rerender-transitions-deferred` - `useTransition`/`useDeferredValue` to keep input responsive during expensive updates

### 3. Rendering & DOM Cost (MEDIUM-HIGH)

- `render-virtualize-lists` - Lists beyond ~50–100 rows (event logs, camera lists, timelines) are virtualized
- `render-mui-styling-cost` - Stable `sx`/`styled` usage: no fresh style objects per render in hot paths, no `styled()` created inside components
- `render-hoist-static-jsx` - Static JSX hoisted out of components; static defaults hoisted out of props
- `render-content-visibility` - `content-visibility: auto` for long offscreen sections
- `render-conditional-ternary` - Ternaries over `&&` for conditional render (numeric/NaN leak pitfall)

### 4. Data Layer Performance (MEDIUM)

- `query-stale-gc-tuning` - Deliberate `staleTime`; prevent refetch storms (focus/mount/interval multipliers)
- `query-narrow-subscriptions` - `select` + `notifyOnChangeProps` so components re-render only for data they use

### 5. Bundle & Startup (MEDIUM)

- `bundle-route-lazy` - `React.lazy` + `Suspense` for routes and heavy, rarely-opened panels
- `bundle-barrel-imports` - No wildcard/barrel imports that defeat tree-shaking; import from specific paths
- `bundle-analyze-chunks` - Measure with `rollup-plugin-visualizer`; split vendor chunks deliberately (`manualChunks`)

## Review Report Format

```markdown
# Performance Review: <scope>

## Summary
2–4 sentences: the dominant cost driver, measured vs suspected, compiler status.

## Environment
React Compiler: enabled/disabled · Profiling done: yes (how) / static-only

## Findings

| # | Severity | Rule | Location | Finding | Evidence |
|---|----------|------|----------|---------|----------|
| 1 | Critical | hf-out-of-react-loop | PlaybackTimeline.tsx:18 | Position state updates 30×/s re-render grid | Profiler: 28ms commit per tick |

### Finding details
For each: current behavior → cost (frequency × work) → target pattern with code
sketch → expected effect. Distinguish measured evidence from static inference.
```

Severity: **Critical** = user-visible jank/dropped frames or per-frame React renders; **High** = wasted renders on hot interaction paths; **Medium** = cost that grows with data size; **Low** = micro-optimizations (only include when nearly free).

## Development Plan Format

```markdown
# Development Plan

## Phase 1 — Quick wins (independent, low-risk: selector fixes, memo boundaries, cleanup leaks)
- [ ] <change> — files, effort (S/M/L), how to verify (profiler before/after, fps)

## Phase 2 — Structural (hf-path rework, virtualization, canvas overlays; note dependencies)
- [ ] ...

## Phase 3 — Bundle & polish
- [ ] ...
```

Every item maps to finding numbers and names its verification (re-profile the same interaction, compare commit counts/durations, bundle size delta). Never recommend a Phase-2 rewrite when a Phase-1 selector fix removes the symptom — sequence so each phase's wins are validated before the next.
