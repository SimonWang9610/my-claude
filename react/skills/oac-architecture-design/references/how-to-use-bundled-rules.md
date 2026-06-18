# How to use the bundled rules

Index of all bundled rule files by category. When a surface looks like it might violate a rule,
open that rule file by its relative path and read it — each file carries the rationale plus an
incorrect/correct example pair. Do not cite a rule from memory; confirm against the examples.

---

## Contents

- [Reading procedure](#reading-procedure)
- [Architecture rules — core/](#architecture-rules--core-23-files)
- [Performance rules — conditional/performance/](#performance-rules--conditionalperformance-22-files)
- [Trigger → rule map](#trigger--rule-map)

---

## Reading procedure

1. Walk the categories in **priority order** (tables below). For each surface in scope, decide
   which category it touches, then open the specific `core/<name>.md` (or
   `conditional/performance/<name>.md`) before concluding.
2. The three blocking triggers (verified in this skill's Verify step and detailed in `gate-procedure.md`) map onto the highest-priority
   architecture categories — see "Trigger → rule map" at the bottom.

All paths below are relative to this `references/` directory.

---

## Architecture rules — `core/` (23 files)

Priority: `state-` (CRITICAL) → `zustand-` (HIGH) → `query-` (HIGH) → `compose-` (MEDIUM-HIGH) → `layer-` (MEDIUM) → `react19-` (LOW-MEDIUM).

### 1. State Ownership & Placement — `state-` (CRITICAL)
- `core/state-ownership-decision.md` — local useState → lifted → Zustand → TanStack Query; keep state as local as possible.
- `core/state-no-server-data-in-stores.md` — server data lives in TanStack Query; never mirrored into Zustand/useState.
- `core/state-derive-dont-store.md` — values computable from existing state/props are derived, never stored.
- `core/state-no-prop-to-state-copy.md` — don't copy props into state; use the prop directly or a `key` reset.
- `core/state-single-source-of-truth.md` — each fact has exactly one owner.

### 2. Zustand Store Design — `zustand-` (HIGH)
- `core/zustand-actions-in-store.md` — mutation logic in store actions, not scattered `setState` in components.
- `core/zustand-slice-organization.md` — one domain per store/slice; split mega-stores, merge confetti stores.
- `core/zustand-no-component-coupling.md` — stores expose domain operations, never know about components/UI.
- `core/zustand-transient-subscribe.md` — high-frequency values use `subscribe`/refs, not reactive hooks.
- `core/zustand-persist-discipline.md` — `persist` only whitelisted fields via `partialize`; version + migrate.

### 3. Server State / TanStack Query — `query-` (HIGH)
- `core/query-no-effect-fetching.md` — no `useEffect` + fetch + setState; use `useQuery`.
- `core/query-key-factory.md` — centralized, typed query-key factories per domain.
- `core/query-mutation-invalidation.md` — mutations invalidate/update affected queries; no manual refetch.
- `core/query-select-transform.md` — shape/derive server data with `select`, not in components or stored copies.

### 4. Component Composition — `compose-` (MEDIUM-HIGH)
- `core/compose-avoid-boolean-props.md` — don't accrete `isX`/`hideY` props; restructure with composition.
- `core/compose-compound-components.md` — multi-part widgets share state via internal context.
- `core/compose-children-over-render-props.md` — prefer `children`/slots over `renderX` props for static content.
- `core/compose-extract-hooks.md` — components past their threshold of mixed logic+JSX: extract logic into custom hooks. **(Trigger 1 / Trigger 3 anchor.)**
- `core/compose-explicit-variants.md` — divergent behavior → separate variant components, not mode flags.

### 5. Layering & Module Structure — `layer-` (MEDIUM)
- `core/layer-feature-folders.md` — organize by feature (components/hooks/store/api per feature).
- `core/layer-unidirectional-deps.md` — dependencies point one way: ui → hooks/state → services.
- `core/layer-service-isolation.md` — side-effectful integrations wrapped in service modules, accessed via hooks/stores. **(Trigger 3 seam anchor.)**

### 6. React 19 Idioms — `react19-` (LOW-MEDIUM)
- `core/react19-modern-apis.md` — `ref` as a prop (no `forwardRef`), `use(Context)` over `useContext`.

---

## Performance rules — `conditional/performance/` (22 files)

Architecture-first gate; consult only when a clear performance hazard surfaces on a high-frequency
path. Record as **non-blocking**. Priority: `hf-` (CRITICAL) → `rerender-` (HIGH) → `render-` (MEDIUM-HIGH) → `query-` (MEDIUM) → `bundle-` (MEDIUM).

### 1. High-Frequency Data Paths — `hf-` (CRITICAL)
- `conditional/performance/hf-out-of-react-loop.md` — per-frame values bypass React: rAF + refs/direct DOM/canvas.
- `conditional/performance/hf-throttle-event-streams.md` — pointermove/wheel/scroll handlers coalesced per frame.
- `conditional/performance/hf-canvas-for-dynamic-overlays.md` — rapidly-changing visuals drawn on canvas.
- `conditional/performance/hf-effect-cleanup.md` — every subscription/listener has a teardown.

### 2. Re-render Elimination — `rerender-` (HIGH)
- `conditional/performance/rerender-zustand-selectors.md` — subscribe to the smallest slice; never the whole store.
- `conditional/performance/rerender-defer-reads.md` — callback-only reads use `getState()`, not a reactive subscription.
- `conditional/performance/rerender-memo-boundaries.md` — `memo` expensive subtrees at the right cut points.
- `conditional/performance/rerender-no-inline-components.md` — never define components inside components.
- `conditional/performance/rerender-context-splitting.md` — split contexts by change-rate; separate state from dispatch.
- `conditional/performance/rerender-children-as-props.md` — pass subtrees as `children` to skip re-renders.
- `conditional/performance/rerender-functional-updates.md` — functional `setState` + lazy `useState(() => ...)` initializers.
- `conditional/performance/rerender-transitions-deferred.md` — `useTransition`/`useDeferredValue` for responsive input.

### 3. Rendering & DOM Cost — `render-` (MEDIUM-HIGH)
- `conditional/performance/render-virtualize-lists.md` — lists beyond ~50–100 rows are virtualized.
- `conditional/performance/render-mui-styling-cost.md` — stable `sx`/`styled`; no fresh style objects per render in hot paths.
- `conditional/performance/render-hoist-static-jsx.md` — static JSX and default props hoisted out of components.
- `conditional/performance/render-content-visibility.md` — `content-visibility: auto` for long offscreen sections.
- `conditional/performance/render-conditional-ternary.md` — ternaries over `&&` for conditional render.

### 4. Data Layer Performance — `query-` (MEDIUM)
- `conditional/performance/query-stale-gc-tuning.md` — deliberate `staleTime`; prevent refetch storms.
- `conditional/performance/query-narrow-subscriptions.md` — `select` + `notifyOnChangeProps` to narrow re-renders.

### 5. Bundle & Startup (Vite) — `bundle-` (MEDIUM)
- `conditional/performance/bundle-route-lazy.md` — `React.lazy` + `Suspense` for routes and heavy panels.
- `conditional/performance/bundle-barrel-imports.md` — no wildcard/barrel imports that defeat tree-shaking.
- `conditional/performance/bundle-analyze-chunks.md` — measure with `rollup-plugin-visualizer`; split vendor chunks deliberately.

---

## Trigger → rule map

| Blocking trigger | Primary bundled rules to confirm against |
|------------------|------------------------------------------|
| **1 — God-component / God-hook** | `core/compose-extract-hooks.md`, `core/layer-feature-folders.md`, `core/compose-explicit-variants.md` |
| **2 — Server-state-in-Zustand / dual-source-of-truth** | `core/state-no-server-data-in-stores.md`, `core/state-single-source-of-truth.md`, `core/state-derive-dont-store.md`, `core/query-no-effect-fetching.md`, `core/zustand-persist-discipline.md` |
| **3 — Testability seam missing** | `core/compose-extract-hooks.md`, `core/layer-service-isolation.md`, `core/query-no-effect-fetching.md` |
