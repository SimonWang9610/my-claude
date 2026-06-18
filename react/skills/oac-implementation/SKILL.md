---
name: oac-implementation
description: >
  Applies React 19 + TypeScript performance and idiom rules while implementing the code inside
  a unit — the contract and architecture are already fixed. Covers wasted re-renders and memo
  boundaries, render cost, bundle splitting, high-frequency data handling, TanStack Query
  subscription and cache tuning, and modern React 19 APIs. Use at the spec-implement stage,
  or whenever writing or optimizing code behind a fixed contract.
---

# oac-implementation

This skill operates at the **implementation altitude**: the design and contracts are settled; the
task is to write correct, performant code inside each unit without re-opening architecture
decisions.

---

## References

Open a reference file when the code you are writing touches that concern. All paths are relative
to this skill's `references/` directory.

---

### Re-render control — `rerender-*`

Prevent unnecessary re-renders that degrade perceived responsiveness.

| File | One-line gloss |
|------|----------------|
| [`rerender-zustand-selectors.md`](references/rerender-zustand-selectors.md) | Subscribe to the smallest Zustand slice; never the whole store |
| [`rerender-defer-reads.md`](references/rerender-defer-reads.md) | Callback-only reads use `getState()`, not a reactive subscription |
| [`rerender-memo-boundaries.md`](references/rerender-memo-boundaries.md) | `memo` expensive subtrees at the right cut points |
| [`rerender-no-inline-components.md`](references/rerender-no-inline-components.md) | Never define components inside components |
| [`rerender-context-splitting.md`](references/rerender-context-splitting.md) | Split contexts by change-rate; separate state from dispatch |
| [`rerender-children-as-props.md`](references/rerender-children-as-props.md) | Pass subtrees as `children` to skip re-renders |
| [`rerender-functional-updates.md`](references/rerender-functional-updates.md) | Functional `setState` + lazy `useState(() => ...)` initializers |
| [`rerender-transitions-deferred.md`](references/rerender-transitions-deferred.md) | `useTransition`/`useDeferredValue` for responsive input |

---

### Render cost — `render-*`

Reduce DOM construction and styling overhead on hot render paths.

| File | One-line gloss |
|------|----------------|
| [`render-virtualize-lists.md`](references/render-virtualize-lists.md) | Lists beyond ~50–100 rows are virtualized |
| [`render-mui-styling-cost.md`](references/render-mui-styling-cost.md) | Stable `sx`/`styled`; no fresh style objects per render in hot paths |
| [`render-hoist-static-jsx.md`](references/render-hoist-static-jsx.md) | Static JSX and default props hoisted out of components |
| [`render-content-visibility.md`](references/render-content-visibility.md) | `content-visibility: auto` for long offscreen sections |
| [`render-conditional-ternary.md`](references/render-conditional-ternary.md) | Ternaries over `&&` for conditional render |

---

### Bundle — `bundle-*`

Keep initial load small; split heavy code onto async boundaries.

| File | One-line gloss |
|------|----------------|
| [`bundle-route-lazy.md`](references/bundle-route-lazy.md) | `React.lazy` + `Suspense` for routes and heavy panels |
| [`bundle-barrel-imports.md`](references/bundle-barrel-imports.md) | No wildcard/barrel imports that defeat tree-shaking |
| [`bundle-analyze-chunks.md`](references/bundle-analyze-chunks.md) | Measure with `rollup-plugin-visualizer`; split vendor chunks deliberately |

---

### High-frequency data — `hf-*`

Handle per-frame or event-storm data without blocking the React render cycle.

| File | One-line gloss |
|------|----------------|
| [`hf-out-of-react-loop.md`](references/hf-out-of-react-loop.md) | Per-frame values bypass React: rAF + refs/direct DOM/canvas |
| [`hf-throttle-event-streams.md`](references/hf-throttle-event-streams.md) | pointermove/wheel/scroll handlers coalesced per frame |
| [`hf-canvas-for-dynamic-overlays.md`](references/hf-canvas-for-dynamic-overlays.md) | Rapidly-changing visuals drawn on canvas |
| [`hf-effect-cleanup.md`](references/hf-effect-cleanup.md) | Every subscription/listener has a teardown |

---

### Query tuning

Narrow what TanStack Query subscribes to and control cache lifetime.

| File | One-line gloss |
|------|----------------|
| [`query-narrow-subscriptions.md`](references/query-narrow-subscriptions.md) | `select` + `notifyOnChangeProps` to narrow re-renders |
| [`query-stale-gc-tuning.md`](references/query-stale-gc-tuning.md) | Deliberate `staleTime`; prevent refetch storms |

---

### React 19 APIs

Idioms that replace legacy patterns in React 19.

| File | One-line gloss |
|------|----------------|
| [`react19-modern-apis.md`](references/react19-modern-apis.md) | `ref` as a prop (no `forwardRef`), `use(Context)` over `useContext` |
