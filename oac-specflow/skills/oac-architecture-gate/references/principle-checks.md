# Principle checks — P1–P7 violation signals and bundled-rule crosswalk

Use when reviewing against a single principle: the signals are grep/read patterns that reveal a
violation; the crosswalk points at the bundled rule file with right/wrong examples. All crosswalk
paths are relative to this `references/` directory. Never cite a rule from memory — read the file.

General best practices for a React 19 + Vite + TypeScript + Zustand + TanStack Query + MUI + Vitest project.

---

## P1 — server state in TanStack Query

**Signals**
- A Zustand slice whose state holds a fetched entity array/object, or a setter named `setX` fed from `useQuery` data.
- `useEffect(() => setStoreX(queryData), [queryData])` — the copy-and-sync tell.
- `localStorage.setItem` / `persist(...)` middleware wrapping server data.
- A `useState` seeded once from `useQuery` data and never reconciled.

**Crosswalk:** `rules-architecture/state-no-server-data-in-stores.md`,
`rules-architecture/state-single-source-of-truth.md`,
`rules-architecture/state-ownership-decision.md`,
`rules-architecture/zustand-persist-discipline.md`.

---

## P2 — render-only components + single-responsibility hooks + soft ceiling

**Signals**
- A component or hook file past the soft ceiling (component > ~400 LOC, hook > ~300 LOC) with no `// ARCH-EXCEPTION:` line.
- A single hook with many effects + many public methods mixing CRUD + UI + lifecycle.
- A component body containing `useEffect` data fetching, derived computation, and JSX interleaved rather than delegating to named hooks.

**Crosswalk:** `rules-architecture/compose-extract-hooks.md`,
`rules-architecture/layer-feature-folders.md`,
`rules-architecture/layer-unidirectional-deps.md`,
`rules-architecture/query-no-effect-fetching.md`.

---

## P3 — one owner per fact; derive, don't sync

**Signals**
- `useEffect(..., [serverData])` or `useEffect(..., [prop])` whose body calls a `setState` mirroring the dependency.
- A `useState<Entity | null>` paired with a `useQuery` for the same entity list.
- Filter/selection state written into the URL or a store via an effect rather than derived at read time.

**Crosswalk:** `rules-architecture/state-derive-dont-store.md`,
`rules-architecture/state-no-prop-to-state-copy.md`,
`rules-architecture/query-select-transform.md`,
`rules-architecture/state-single-source-of-truth.md`.

---

## P4 — writes via useMutation; errors via onError/isError

**Signals**
- `api.*` / `axios.*` / client write methods called directly inside an event handler (no `useMutation` wrapper).
- `catch (e) { console.error(e) }` with no UI error surface.
- An un-awaited write — the production failure path is never exercised because tests `mockResolvedValue`.
- No `invalidateQueries` after a successful write → stale list after mutation.
- An error string pushed into Zustand instead of read from `mutation.error`.

**Crosswalk:** `rules-architecture/query-mutation-invalidation.md`,
`rules-architecture/query-key-factory.md`,
`rules-architecture/query-no-effect-fetching.md`.

---

## P5 — testability seam per AC

**Signals**
- An AC behavior whose only test mocks the parent's whole hook (`vi.mock('../hooks/useX')`) — the behavior under test is inside the mock.
- A module-level `vi.mock` that bypasses the exact logic an AC names.
- An AC with no component renderable via providers and no hook callable via `renderHook` that isolates it.
- A declared-but-never-called mock assertion (callback AC with no `fireEvent` / `expect(mock).toHaveBeenCalled`).

**Crosswalk:** `rules-architecture/compose-extract-hooks.md`,
`rules-architecture/compose-children-over-render-props.md`,
`rules-architecture/layer-service-isolation.md`.

---

## P6 — token-layer selection

**Signals**
- A hard-coded hex (`#RRGGBB`) in `sx`, `styled()`, `createTheme`, or inline `style`.
- A raw color-scale class (e.g. `bg-gray-900`) instead of a semantic design-token class.
- A CSS-var-backed semantic token used as an SVG `fill`/`stroke` (SVG cannot resolve CSS vars — must be a static hex token).
- A theming/dark-mode NFR asserted only by CSS-class presence in JSDOM (cannot resolve the variable — false positive).

**Crosswalk:** no bundled architecture rule file maps directly — confirm against the project's
design-token documentation and enforce with a CI guard (ESLint/Vitest rule banning raw hex and raw scale classes).

---

## P7 — no module-scope mutable domain state

**Signals**
- A top-level `let`, mutable `Map`/`Set`, or `new ClassInstance()` at module scope accumulating domain state.
- A lazily-wired module-scope array/registry empty at test time → a silent no-op AC.
- A module-scope Map with no `_resetForTest()` export, or a test file touching such a module without `beforeEach(() => _resetForTest())`.
- Test-order-dependent failures / flaky CI traced to shared module state.

**Crosswalk:** `rules-architecture/zustand-slice-organization.md`,
`rules-architecture/zustand-no-component-coupling.md`,
`rules-architecture/state-ownership-decision.md`.

---

## Trigger → principle → bundled-rule map

| Blocking trigger | Principles | Primary bundled rules |
|------------------|------------|----------------------|
| **1 — God-component / God-hook** | P2 | `compose-extract-hooks.md`, `layer-feature-folders.md`, `compose-explicit-variants.md` |
| **2 — Server-state-in-Zustand / dual-source-of-truth** | P1, P3 | `state-no-server-data-in-stores.md`, `state-single-source-of-truth.md`, `state-derive-dont-store.md`, `query-no-effect-fetching.md`, `zustand-persist-discipline.md` |
| **3 — Testability seam missing** | P5 (underwritten by P2) | `compose-extract-hooks.md`, `layer-service-isolation.md`, `query-no-effect-fetching.md` |

P4 (write paths), P6 (token layering), and P7 (module-scope state) are not blocking triggers in
themselves, but a violation surfaced during the gate is recorded as a finding and resolved before
phase exit.

---

## Quick decision: where does this fact live?

```
Is the value fetched from / owned by the server?
├─ yes → TanStack Query cache (P1). Never copy to Zustand/useState/localStorage.
└─ no  → Is it shared across unrelated components / persisted as UI preference?
         ├─ yes → Zustand slice (UI state only).
         └─ no  → component-local useState / useRef.

Need both server data and a selection?
└─ keep the KEY in client state, DERIVE the entity at read time (P3). No sync effect.

Mutating the server?
└─ useMutation; invalidate in onSuccess; cleanup in onSettled; error via isError (P4).

Adding a color?
└─ pick the token layer by context (P6). No hex in sx/theme; no raw color-scale class.

Need cross-render accumulation (index, registry, abort controllers)?
└─ React context / Zustand / useRef. If a module Map is unavoidable: export _resetForTest() (P7).
```
