---
name: oac-implementation
description: >
  Guides the coding disciplines that honor a fixed architecture (design.md + contracts/ are
  your inputs): conforming to the contract, honest TypeScript, correct hooks and states, and
  performance — wasted re-renders, render cost, bundle splitting, high-frequency data, and
  TanStack Query subscription/cache tuning. Reach for it when writing or optimizing the code
  inside a unit whose contract is settled (React 19 + TS + Zustand + TanStack Query v5).
---

# oac-implementation

Implementation altitude: the contract and the architecture are settled inputs handed to you.
Write the code inside the unit to satisfy them — **do not re-open** the public API, the state
placement, or the layer boundaries. If the contract is ambiguous or missing a case you must
handle, surface the gap to the caller rather than inventing a wider API.

**Design → implementation handoff.** The architecture is fixed; its outputs are what each
discipline below reacts to. The **state-ownership map** says which state is local, in Zustand,
or in the Query cache — so you subscribe narrowly and never mirror server data. The
**query-key design** fixes the keys and derived shapes — so you narrow subscriptions and wire
mutations against them. The **unit contracts** fix the public API and promised states — so you
conform exactly and render every state. The **composition plan** fixes the component/hook
seams — so you memoize at those cut points and keep components out of components. These are
disciplines that *honor* decisions already made; where a discipline has a design-side twin,
it names the `oac-architecture-design` skill.

Tests for this unit are authored separately (invoke `oac-test-contract` by name for that).

## Procedure

1. **Read first.** Read the contract and the architecture decisions for this unit, plus the
   file's imports — reuse the existing component/hook/type/query-key/store-slice, don't add a
   second one.
2. **Check the Compiler once.** Look for `babel-plugin-react-compiler` in `vite.config`/`babel`;
   it inverts all memoization advice. See `react19-modern-apis`.
3. **Conform to the contract** — exact props/return types, and every promised state actually
   rendered (`contract-conformance`, `data-states`).
4. **Type it honestly** — no `any`, discriminated-union state, exact prop types
   (`typescript-discipline`).
5. **Get the hooks right** — Rules of Hooks, truthful deps, derive-don't-store, effects only for
   external sync + teardown (`hooks-correctness`).
6. **Write the React 19 idiom, not the legacy ceremony** (`react19-modern-apis`).
7. **Then optimize** — apply a performance reference only when the code you're writing touches
   that concern (or a profile confirms a hot path). Correctness and conformance come first;
   don't pre-optimize a cold path.

Open a reference when the code you are writing touches its concern. Paths are relative to this
skill's `references/`. Rules marked **↔ arch: `<name>`** have a design-side twin in the
`oac-architecture-design` skill — that rule decided *what*; this one governs *how* in code.

## Correctness & idioms (apply to every unit)

| File | When to open |
|------|--------------|
| [`contract-conformance.md`](references/contract-conformance.md) | Always — match the declared public API, props, return type, and promised states; no drift |
| [`data-states.md`](references/data-states.md) | The unit reads a query or runs a mutation — render loading/error/empty/success, don't ship a happy-path-only screen. Consume server data via the query hook, never a mirrored copy. **↔ arch: `state-no-server-data-in-stores`** |
| [`query-mutation-wiring.md`](references/query-mutation-wiring.md) | Writing a mutation — settle the cache (`onSuccess` invalidate/`setQueryData`), v5 callback placement, optimistic update + rollback. **↔ arch: `query-mutation-invalidation`** |
| [`typescript-discipline.md`](references/typescript-discipline.md) | Typing state, props, refs, events, or boundary data — no `any`, model states as a discriminated union |
| [`hooks-correctness.md`](references/hooks-correctness.md) | Any hook usage — placement, dependency arrays, derived state, effects. Derive in render/`useMemo`, never `useEffect` + `setState`. **↔ arch: `state-derive-dont-store`** |
| [`react19-modern-apis.md`](references/react19-modern-apis.md) | `ref`/`forwardRef`, context, form submit/mutation pending state, or any memoization decision |

## Performance corpus (apply per concern)

### Re-render control — `rerender-*`
| File | Gloss |
|------|-------|
| [`rerender-zustand-selectors.md`](references/rerender-zustand-selectors.md) | Subscribe to the smallest Zustand slice; never the whole store |
| [`rerender-defer-reads.md`](references/rerender-defer-reads.md) | Callback-only reads use `getState()`, not a subscription |
| [`rerender-transient-subscribe.md`](references/rerender-transient-subscribe.md) | Fast-changing store state read via transient `subscribe` + ref, not a reactive selector. **↔ arch: `zustand-transient-placement`** |
| [`rerender-memo-boundaries.md`](references/rerender-memo-boundaries.md) | `memo` expensive subtrees at the right cut points; keep props stable |
| [`rerender-no-inline-components.md`](references/rerender-no-inline-components.md) | Never define components inside components |
| [`rerender-context-splitting.md`](references/rerender-context-splitting.md) | Split contexts by change-rate; separate state from dispatch |
| [`rerender-children-as-props.md`](references/rerender-children-as-props.md) | Pass subtrees as `children` to skip their re-render |
| [`rerender-functional-updates.md`](references/rerender-functional-updates.md) | Functional `setState` + lazy `useState(() => …)` initializers |
| [`rerender-transitions-deferred.md`](references/rerender-transitions-deferred.md) | `useTransition`/`useDeferredValue` for responsive input |

### Render cost — `render-*`
| File | Gloss |
|------|-------|
| [`render-virtualize-lists.md`](references/render-virtualize-lists.md) | Lists beyond ~50–100 rows are virtualized |
| [`render-mui-styling-cost.md`](references/render-mui-styling-cost.md) | Stable `sx`/`styled`; no fresh style objects per render on hot paths |
| [`render-hoist-static-jsx.md`](references/render-hoist-static-jsx.md) | Hoist static JSX and default props out of components |
| [`render-content-visibility.md`](references/render-content-visibility.md) | `content-visibility: auto` for long offscreen sections |
| [`render-conditional-ternary.md`](references/render-conditional-ternary.md) | Ternaries over `&&` for numeric conditions |

### Bundle — `bundle-*`
| File | Gloss |
|------|-------|
| [`bundle-route-lazy.md`](references/bundle-route-lazy.md) | `React.lazy` + `Suspense` for routes and heavy panels |
| [`bundle-barrel-imports.md`](references/bundle-barrel-imports.md) | No wildcard/barrel imports that defeat tree-shaking |
| [`bundle-analyze-chunks.md`](references/bundle-analyze-chunks.md) | Measure with `rollup-plugin-visualizer`; split vendor chunks deliberately |

### High-frequency data — `hf-*`
| File | Gloss |
|------|-------|
| [`hf-out-of-react-loop.md`](references/hf-out-of-react-loop.md) | Per-frame values bypass React: rAF + refs/direct DOM/canvas |
| [`hf-throttle-event-streams.md`](references/hf-throttle-event-streams.md) | pointermove/wheel/scroll handlers coalesced per frame |
| [`hf-canvas-for-dynamic-overlays.md`](references/hf-canvas-for-dynamic-overlays.md) | Rapidly-changing visuals drawn on canvas |
| [`hf-effect-cleanup.md`](references/hf-effect-cleanup.md) | Every subscription/listener has a teardown |

### Query tuning — `query-*`
| File | Gloss |
|------|-------|
| [`query-narrow-subscriptions.md`](references/query-narrow-subscriptions.md) | `select` + tracked props to narrow re-renders. **↔ arch: `query-select-transform`** |
| [`query-stale-gc-tuning.md`](references/query-stale-gc-tuning.md) | Deliberate `staleTime`; prevent refetch storms |
