# Performance check — diagnose, route, steer

A diagnostic, not a rule pile: find the level the cause lives at, fix at that level. Most
React performance problems are architecture problems wearing an implementation costume —
memoizing over a structural cause is a bandage that silently rots.

## When to run

During self-check for hot paths (per-frame, large list, main interaction) and perf NFRs;
or on a reported symptom. Cold path, no NFR, no symptom → exit. No browser available
(headless/CI agent) → record the diagnostic as **deferred**, never fabricate measurements;
perf NFR rows still verify through their Test strategy harnesses.

## Measure before touching anything

A perf fix without a measurement is a guess; the measurement is also the evidence for any
gap raised.

| Symptom | Measure with |
|---------|--------------|
| Re-render cascade / slow interaction | React Profiler — which components render, how often, why |
| Slow mount / janky scroll | Profiler mount cost · row count vs virtualization |
| Slow startup | bundle analyzer — what ships eagerly that shouldn't |
| Dropped frames on continuous input | flame chart — work per tick, who schedules it |

## Root-cause ladder — walk top-down

Diagnose from architecture downward; a fix applied below the cause's level is a bandage.

1. **State placement** — is the fact owned higher than its consumers need, re-rendering a
   whole subtree per change? Is a per-frame/continuous value in React state at all?
   → design-level cause.
2. **Subscription width** — do consumers subscribe to more than they render (whole store,
   whole query result, whole context value)? → optimize-hooks.
3. **Boundary containment** — is an expensive subtree inside a fast-ticking wrapper
   (children-as-props), missing a memo boundary, missing the design's code-split point, or
   an unvirtualized unbounded list? → optimize-components; a *missing* boundary the design
   never named → design-level cause.
4. **Micro** — only after 1–3 pass: per-frame class minting, unstable deps, redundant work
   in render.

## Route the fix

- **Implementation-level cause** (2–4, within the contract): apply
  [optimize-hooks.md](./optimize-hooks.md) / [optimize-components.md](./optimize-components.md),
  re-measure, done.
- **Design-level cause** (1, or a boundary the design drew wrong): raise a **DESIGN GAP**
  (friction — or defect when the contract mandates the slow structure), measurement
  attached as evidence, per SKILL.md § Steer the design. Do not patch locally what the
  design must fix.

```markdown
DESIGN GAP — DeviceGrid · friction
Contract says: selection state lives in the grid store; tiles subscribe to the store
Code shows: Profiler — every tile re-renders on any selection change (48 renders/click)
Suggestion: per-tile `useIsSelected(id)` selector, or selection via context split from data
Status: blocked pending decision
```

## Memory — leaks are emergent, check the cycle

Every unit can pass its teardown rule and the session still leak — verify the *cycle*, not
the units. Run when the diff touches subscriptions, services, caches, or a long-lived
screen.

**Measure:** repeat the mount → use → unmount cycle (navigate away and back ×3), diff heap
snapshots; growth that survives GC is a leak. Allocation timeline names the retainer;
detached DOM nodes point at listener leaks. This diagnostic is one-shot and needs a real
browser — the *repeatable* guards (unmount teardown, StrictMode survival, timer counts)
are unit tests: see the test skill's lifecycle & leak guards.

**Cause ladder (top-down, same routing):**

1. **Lifecycle never closed on a real path** — a service `create` whose `destroy` is
   unreachable on some navigation/error path; if the contract's lifecycle has no owner for
   that path → design gap.
2. **Subscription outlives its owner** — listener/interval/observer missing its teardown
   (use-hooks), or a `store.subscribe` outside React never unsubscribed.
3. **Unbounded accumulation** — module-scope maps/registries (must not exist), caches with
   no eviction, query cache holding infinite-list pages forever (set `gcTime`/`maxPages`).
4. **Closure retention** — a memoized callback/ref capturing a large snapshot (full list,
   video frame) that only needed an id.

## Guardrail — memo that requires contortions is a design signal

If a memo boundary can only hold by forcing props stable through tricks (deps laundering,
JSON.stringify, deep-compare), the boundary is drawn wrong — raise it, don't ship the
contortion. Correctness beats performance; a "fast" fix that changes behaviour is a defect.
