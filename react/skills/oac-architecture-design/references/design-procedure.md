# Design procedure

Step-by-step checklist for authoring `design.md` and `contracts/` against the 22
architecture rules. Work every step in order. All paths are relative to this
`references/` directory; open the named `core/<name>.md` before you commit a decision.

---

## Step 1 — Assign units to feature folders and layers

Read `core/layer-feature-folders.md`, `core/layer-unidirectional-deps.md`. List every
unit with its layer (ui / hooks / store / api / services) and role suffix (`*Page`,
`*Panel`, `use*`, `*Store`, `*Api`, `*Service`). Verify dependency arrows point only
inward (ui → hooks/store → api/services); redesign any unit that skips or reverses a
layer before proceeding. This unit list is the spine of the contracts in Step 7.

---

## Step 2 — Choose the state-ownership tier per fact

Read `core/state-ownership-decision.md`, `core/state-single-source-of-truth.md`,
`core/state-derive-dont-store.md`. For each fact the feature holds:

| Tier | Use when |
|------|----------|
| Local `useState`/`useReducer` | one component, dies with unmount |
| Lifted `useState` / narrow Context | shared by a sibling subtree, passed as props |
| URL search params | selected tab, filters, detail id — survives reload, shareable |
| Zustand slice | client UI state shared across unrelated components; **never server data** |
| TanStack Query | anything fetched from / owned by the server |

Keep each fact at its narrowest tier. One owner per fact — derive the rest at read
time, never duplicate, never sync with an effect. Record each decision in `design.md`.

---

## Step 3 — Server-state path: TanStack Query as SSOT

Read `core/state-no-server-data-in-stores.md`, `core/query-no-effect-fetching.md`,
`core/query-key-factory.md`, `core/query-mutation-invalidation.md`,
`core/query-select-transform.md`.

- Reads use `useQuery`/`useInfiniteQuery` with a centralized, typed query-key factory
  (prefer `queryOptions()`). No `useEffect` + fetch + setState.
- Writes use `useMutation`; `onSuccess` invalidates or `setQueryData` the affected
  keys — no manual `refetch()` choreography, no `onSuccess` on `useQuery` (removed in v5).
- Server data is never copied into Zustand, `useState`, or `localStorage`.
- Derived shapes come from `select`, not stored copies; a selection keeps only the
  key in client state and resolves the entity at read time.

---

## Step 4 — Zustand store shape

Read `core/zustand-actions-in-store.md`, `core/zustand-slice-organization.md`,
`core/zustand-no-component-coupling.md`, `core/zustand-persist-discipline.md`.

- One domain per store/slice; no mega-store, no per-component confetti stores.
- Mutation logic lives in intent-named store actions, not scattered `setState` in
  components; multi-field reads use `useShallow` or atomic selectors.
- Stores expose domain operations and import nothing from `react`/components/MUI.
- `persist` only whitelisted UI fields via `partialize`, with `version` + `migrate`.

---

## Step 5 — Component composition and hook extraction

Read `core/compose-extract-hooks.md`, `core/compose-avoid-boolean-props.md`,
`core/compose-explicit-variants.md`.

- Components render; logic, effects, and derivations live in named
  single-responsibility hooks (`useDeviceFilters`, `useDeviceSelection`).
- Soft ceiling: ~400 LOC per component, ~300 LOC per hook. Past it, split — or carry
  an `// ARCH-EXCEPTION: <reason>` line and record the justification in `design.md`.
- 3+ boolean props altering *structure* → restructure with composition, compound
  components, or explicit variant components.

---

## Step 6 — Per-unit testability seam

Read `core/compose-extract-hooks.md`, `core/layer-service-isolation.md`. For **every**
unit from Step 1, state exactly how it is exercised in isolation:

- Component → `render()` behind a providers wrapper; no module-level mock of its host hook.
- Hook → `renderHook` with injected/mocked services and controlled inputs.
- Service/API module → wrapped behind an interface, reached only through hooks/stores.

A unit testable only by mocking its entire host is a **design defect** — fix it here by
extracting the behavior into a named hook or service boundary. This is what makes the
Step-1 units independently verifiable at the gate; carry the seam into each contract.

---

## Step 7 — Write the contracts and the design doc

**`contracts/<unit>.md`** — one per unit from Step 1, in the Contract skeleton shape from
`SKILL.md`; fill **Testability seam** with the isolation path decided in Step 6.

**`design.md`** — the layer map (Step 1), state-ownership decisions (Step 2),
server-state path (Step 3), Zustand shape (Step 4), composition notes (Step 5), and an
`## Architecture Gate` section (leave a blank `### Justifications` subsection). Then run
the Verify step (`gate-procedure.md`) before hand-off.

---

This is the **proactive design pass** — build the structure against the rules before any
code exists. The gate is the **lightweight verification pass** — it checks the output
once. Same rules, two moments.
