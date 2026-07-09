# How to use the bundled rules

Index of all bundled rule files by category. When a surface looks like it might violate a rule,
open that rule file by its relative path and read it — each file carries the rationale plus an
incorrect/correct example pair. Do not cite a rule from memory; confirm against the examples.

---

## Contents

- [Reading procedure](#reading-procedure)
- [Architecture rules — core/](#architecture-rules--core-22-files)
- [Trigger → rule map](#trigger--rule-map)

---

## Reading procedure

1. Walk the categories in **priority order** (tables below). For each surface in scope, decide
   which category it touches, then open the specific `core/<name>.md` before concluding.
2. The three blocking triggers (the verifiable-unit gate, detailed in `gate-procedure.md`) map onto the highest-priority
   architecture categories — see "Trigger → rule map" at the bottom.

All paths below are relative to this `references/` directory.

---

## Architecture rules — `core/` (22 files)

Priority: `state-` (CRITICAL) → `zustand-` (HIGH) → `query-` (HIGH) → `compose-` (MEDIUM-HIGH) → `layer-` (MEDIUM).

Each rule here is a **design decision** — what to decide and record in `design.md`/`contracts/`.
Rules marked **↔ impl: `<name>`** have a coding-discipline twin in the `oac-implementation` skill:
the same topic seen from the implementation lens (how to honor the decision in code). Decide here;
the twin governs the code that carries it out.

### 1. State Ownership & Placement — `state-` (CRITICAL)
- `core/state-ownership-decision.md` — local useState → lifted → Zustand → TanStack Query; keep state as local as possible.
- `core/state-no-server-data-in-stores.md` — server data lives in TanStack Query; never mirrored into Zustand/useState. ↔ impl: `data-states`.
- `core/state-derive-dont-store.md` — values computable from existing state/props are derived, never stored. ↔ impl: `hooks-correctness`.
- `core/state-no-prop-to-state-copy.md` — don't copy props into state; use the prop directly or a `key` reset.
- `core/state-single-source-of-truth.md` — each fact has exactly one owner.

### 2. Zustand Store Design — `zustand-` (HIGH)
- `core/zustand-actions-in-store.md` — mutation logic in store actions, not scattered `setState` in components.
- `core/zustand-slice-organization.md` — one domain per store/slice; split mega-stores, merge confetti stores.
- `core/zustand-no-component-coupling.md` — stores expose domain operations, never know about components/UI.
- `core/zustand-transient-placement.md` — high-frequency/per-frame values don't belong in the store; emit them from the service, keep only discrete session state. ↔ impl: `rerender-transient-subscribe`.
- `core/zustand-persist-discipline.md` — `persist` only whitelisted fields via `partialize`; version + migrate.

### 3. Server State / TanStack Query — `query-` (HIGH)
- `core/query-no-effect-fetching.md` — no `useEffect` + fetch + setState; use `useQuery`.
- `core/query-key-factory.md` — centralized, typed query-key factories per domain.
- `core/query-mutation-invalidation.md` — design each mutation's invalidation graph (families invalidated/updated); no manual refetch. ↔ impl: `query-mutation-wiring`.
- `core/query-select-transform.md` — the derived shape is part of the query hook's contract; shape with `select`, not in components or stored copies. ↔ impl: `query-narrow-subscriptions`.

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

---

## Trigger → rule map

| Blocking trigger | Primary bundled rules to confirm against |
|------------------|------------------------------------------|
| **1 — God-component / God-hook** | `core/compose-extract-hooks.md`, `core/layer-feature-folders.md`, `core/compose-explicit-variants.md` |
| **2 — Server-state-in-Zustand / dual-source-of-truth** | `core/state-no-server-data-in-stores.md`, `core/state-single-source-of-truth.md`, `core/state-derive-dont-store.md`, `core/query-no-effect-fetching.md`, `core/zustand-persist-discipline.md` |
| **3 — Testability seam missing** | `core/compose-extract-hooks.md`, `core/layer-service-isolation.md`, `core/query-no-effect-fetching.md` |
