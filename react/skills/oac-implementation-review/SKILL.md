---
name: oac-implementation-review
description: >
  Detect-side review of implemented React code, paired with `oac-implementation`: audits the green
  branch against the performance corpus (re-renders, render cost, bundle, high-frequency data,
  query tuning) and the architecture boundaries the design fixed — emitting severity-tagged
  findings (`R-<n>`, Critical/Major/Minor), each mapped to the reference card that fixes it.
  Evidence only: it never edits code — findings loop back to the implementer. Runs as the implement
  exit gate, before spec-qa. Use to review a unit or branch once its AC tests are green (React 19 +
  TS + Zustand + TanStack Query v5).
---

# oac-implementation-review

Review altitude: the code compiles and its AC tests are green — you audit whether it also honors
the **performance corpus** and the **architecture boundaries** the design set. Evidence only: emit
findings and cite the fix; the WorkAgent applies them. Never edit source or tests yourself.

**Inputs:** `design.md` + `contracts/` (the intended boundaries), `tasks.md`, and the branch diff
(changed `*.ts` / `*.tsx`).
**Trigger:** all implement units green, before the human code gate / spec-qa — the paired author
skill is `oac-implementation`.

## Procedure

1. **Scope the diff.** Review only changed units; open each unit's contract to know its intended
   shape and states.
2. **Performance lens.** For each changed unit, scan against the applicable cards below — open a
   card only when the code touches its concern. Flag a real regression on a live path, not a
   cold-path micro-opt: the implementer was told not to pre-optimize, so don't invent work.
3. **Architecture-boundary lens.** Check the code honored the design's boundaries — server state
   not copied into a store, no `useEffect` fetching, no prop→state mirror, layer/import direction,
   one owner per fact. Signals + grep patterns live in
   `oac-architecture-design/references/principle-checks.md` (the design skill owns them; you apply
   them to the built code).
4. **Emit findings.** One per issue: `R-<n>` · severity · `file:line` · the violated rule (cite the
   card or principle) · the one-line fix.
5. **Loop.** Critical/Major findings block the gate — hand them back, re-review after the fix until
   none remain. Minor findings are advisory.

## Severity

- **Critical** — a broken architecture boundary (server data in a store, effect-fetching, a layer
  violation) or a user-visible perf failure (jank on the main path, an un-virtualized large list, a
  route shipping the whole app). Blocks.
- **Major** — a clear wasted-render or render-cost regression on a real interaction path, a barrel
  import defeating tree-shaking, an untuned query causing refetch storms. Blocks.
- **Minor** — cold-path or micro-optimization. Advisory; does not block.

Each finding cites the card that fixes it (the mapping IS the corpus below); a boundary finding
cites the `oac-architecture-design` principle it violates.

## Performance corpus (the checklist)

Open a card only when a changed unit touches its concern. Rules marked **↔ arch: `<name>`** have a
design-side twin — a violation is also an architecture-boundary finding.

### Re-render control — `rerender-*`
| File | Flag when |
|------|-----------|
| [`rerender-zustand-selectors.md`](references/rerender-zustand-selectors.md) | Whole-store or fresh-object Zustand selector re-rendering on every change |
| [`rerender-defer-reads.md`](references/rerender-defer-reads.md) | A value read only in a callback is subscribed reactively instead of via `getState()` |
| [`rerender-transient-subscribe.md`](references/rerender-transient-subscribe.md) | Fast-changing store state read via a reactive selector, not transient `subscribe` + ref. **↔ arch: `zustand-transient-placement`** |
| [`rerender-memo-boundaries.md`](references/rerender-memo-boundaries.md) | Expensive subtree re-renders with no `memo` cut point, or unstable props defeat one |
| [`rerender-no-inline-components.md`](references/rerender-no-inline-components.md) | A component is defined inside another component |
| [`rerender-context-splitting.md`](references/rerender-context-splitting.md) | High- and low-change values share one context; state and dispatch not split |
| [`rerender-children-as-props.md`](references/rerender-children-as-props.md) | A stateful wrapper re-renders a static subtree it could take as `children` |
| [`rerender-functional-updates.md`](references/rerender-functional-updates.md) | `setState` from stale closure state; expensive initial state not lazy |
| [`rerender-transitions-deferred.md`](references/rerender-transitions-deferred.md) | Heavy update blocks input where `useTransition`/`useDeferredValue` fits |

### Render cost — `render-*`
| File | Flag when |
|------|-----------|
| [`render-virtualize-lists.md`](references/render-virtualize-lists.md) | A list beyond ~50–100 rows renders every row |
| [`render-mui-styling-cost.md`](references/render-mui-styling-cost.md) | Fresh `sx`/style objects per render on a hot path |
| [`render-hoist-static-jsx.md`](references/render-hoist-static-jsx.md) | Static JSX / default props recreated inside a component |
| [`render-content-visibility.md`](references/render-content-visibility.md) | Long offscreen sections rendered eagerly |
| [`render-conditional-ternary.md`](references/render-conditional-ternary.md) | `&&` on a numeric condition risks rendering `0` |

### Bundle — `bundle-*`
| File | Flag when |
|------|-----------|
| [`bundle-route-lazy.md`](references/bundle-route-lazy.md) | Route or heavy panel loaded eagerly, not `React.lazy` + `Suspense` |
| [`bundle-barrel-imports.md`](references/bundle-barrel-imports.md) | Wildcard/barrel import defeating tree-shaking |
| [`bundle-analyze-chunks.md`](references/bundle-analyze-chunks.md) | Vendor chunks unmeasured/unsplit on a size-sensitive entry |

### High-frequency data — `hf-*`
| File | Flag when |
|------|-----------|
| [`hf-out-of-react-loop.md`](references/hf-out-of-react-loop.md) | Per-frame value driven through React state instead of rAF + refs/DOM/canvas |
| [`hf-throttle-event-streams.md`](references/hf-throttle-event-streams.md) | `pointermove`/`wheel`/`scroll` handler not coalesced per frame |
| [`hf-canvas-for-dynamic-overlays.md`](references/hf-canvas-for-dynamic-overlays.md) | Rapidly-changing visuals as DOM nodes instead of canvas |
| [`hf-effect-cleanup.md`](references/hf-effect-cleanup.md) | A subscription/listener/timer with no teardown |

### Query tuning — `query-*`
| File | Flag when |
|------|-----------|
| [`query-narrow-subscriptions.md`](references/query-narrow-subscriptions.md) | A component re-renders on query fields it doesn't use; no `select`/tracked props. **↔ arch: `query-select-transform`** |
| [`query-stale-gc-tuning.md`](references/query-stale-gc-tuning.md) | Default `staleTime` causing refetch storms on a stable resource |
