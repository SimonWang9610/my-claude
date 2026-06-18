# Design procedure

Step-by-step checklist for authoring `design.md` and `contracts/` against the
React specflow architecture rules. Work through every step in order. All paths
are relative to this `references/` directory.

---

## Contents

- [Step 1 — Assign units to feature folders and layers](#step-1--assign-units-to-feature-folders-and-layers)
- [Step 2 — Choose the state-ownership tier per fact](#step-2--choose-the-state-ownership-tier-per-fact)
- [Step 3 — Server state path: TanStack Query as SSOT](#step-3--server-state-path-tanstack-query-as-ssot)
- [Step 4 — Zustand store shape](#step-4--zustand-store-shape)
- [Step 5 — Component composition and hook extraction](#step-5--component-composition-and-hook-extraction)
- [Step 6 — Per-unit testability seam](#step-6--per-unit-testability-seam-p5)
- [Step 7 — Conditional packs and hand-off](#step-7--conditional-packs-and-hand-off)

---

## Step 1 — Assign units to feature folders and layers

Read `core/layer-feature-folders.md` and `core/layer-unidirectional-deps.md`. List
every unit with its layer (ui / hooks / store / api / services) and role suffix
(`*Page`, `*Panel`, `use*`, `*Store`, `*Api`, `*Service`). Verify dependency arrows
point only inward (ui → hooks/store → api/services); redesign any unit that skips or
reverses a layer before proceeding.

---

## Step 2 — Choose the state-ownership tier per fact

Read `core/state-ownership-decision.md`, `core/state-single-source-of-truth.md`, and
`core/state-derive-dont-store.md`. For each piece of state:

- **Local `useState`** — one component only, no sharing, dies with unmount.
- **Lifted `useState`** — shared by a sibling subtree; passed as props.
- **Zustand slice** — client UI state shared across unrelated components (open modals,
  selected tab, sidebar collapse). Never server data.
- **TanStack Query** — anything fetched from / owned by the server.

Do not promote state beyond its narrowest tier. One owner per fact — derive at read
time, never duplicate. Record each decision in `design.md`.

---

## Step 3 — Server state path: TanStack Query as SSOT

Read `core/state-no-server-data-in-stores.md`, `core/query-no-effect-fetching.md`,
`core/query-key-factory.md`, and `core/query-mutation-invalidation.md`.

- All server reads use `useQuery`/`useInfiniteQuery` with a centralized query-key
  factory. No `useEffect` + fetch + setState pattern.
- All writes use `useMutation`; `onSuccess` invalidates or updates affected queries;
  no manual refetch.
- Server data never copied into Zustand or `localStorage`.
- Derivations / transformations applied via `select`, not stored copies.

---

## Step 4 — Zustand store shape

Read `core/zustand-actions-in-store.md`, `core/zustand-slice-organization.md`, and
`core/zustand-no-component-coupling.md`.

- One domain per store/slice; no mega-stores.
- Mutation logic lives inside store actions, not scattered in component handlers.
- Stores expose domain operations and have no knowledge of components or JSX.

---

## Step 5 — Component composition and hook extraction

Read `core/compose-extract-hooks.md`, `core/compose-avoid-boolean-props.md`, and
`core/compose-explicit-variants.md`.

- Components render; logic, effects, and derivations live in named single-responsibility
  hooks (`useDeviceFilters`, `useDeviceSelection`).
- Soft ceiling: ~400 LOC for a component, ~300 LOC for a hook. Past the ceiling, split
  or carry an `// ARCH-EXCEPTION: <reason>` comment approved at design exit.
- Boolean-prop accretion (`isX`, `hideY`) is a signal to restructure with composition
  or explicit variant components.

---

## Step 6 — Per-unit testability seam (P5)

Read `core/compose-extract-hooks.md` and `core/layer-service-isolation.md`. For
**every** unit from Step 1, state explicitly how it will be exercised in isolation:

- Component → renderable with a providers wrapper via `render()`; no module-level mock
  of the host hook.
- Hook → callable via `renderHook` with constructor-injected or mocked services.
- Service/API module → wrapped behind an interface; accessed only through hooks/stores
  (never called directly in components).

A unit testable only by mocking its entire host is a **design defect**. Fix it here:
extract the behavior into a named hook or service boundary. Record the seam statement
in each `contracts/<unit>.md`.

---

## Step 7 — Conditional packs and hand-off

**Conditional** `conditional/performance/` — open only when a concrete performance
hazard surfaces (high-frequency data paths, virtualized lists, bundle size). Advisory
only, non-blocking.

**Record and hand off** — Write `design.md` (layer map, state-ownership decisions,
server-state path, Zustand shape, composition notes, blank
`## Architecture Gate — Justifications` section). Write `contracts/<unit>.md` for every
unit (kind/layer, public API, data shapes, AC-IDs traced to this unit, testability seam,
direct dependencies). Then run this skill's Verify step (`references/gate-procedure.md`) at phase exit.

---

This skill is the **proactive design pass** — build the structure against the rules
before any code is written. The gate is the **lightweight verification pass** — it
checks the output once. Same rules, two moments.
