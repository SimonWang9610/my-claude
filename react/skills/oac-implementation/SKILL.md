---
name: oac-implementation
description: >
  Guides the coding disciplines that honor a fixed architecture (design.md + contracts/ are
  your inputs): conforming to the contract, honest TypeScript, correct hooks and states, and the
  promised data states. Correctness only — performance (re-renders, render cost, bundle,
  high-frequency data, query tuning) is the paired `oac-implementation-review` skill, applied as
  the implement exit gate. Reach for it when writing the code inside a unit whose contract is
  settled (React 19 + TS + Zustand + TanStack Query v5).
---

# oac-implementation

Implementation altitude: the contract and the architecture are settled inputs handed to you.
Write the code inside the unit to satisfy them — **do not re-open** the public API, the state
placement, or the layer boundaries. If the contract is ambiguous or missing a case you must
handle, surface the gap to the caller rather than inventing a wider API.

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
7. **Don't pre-optimize** — write clear, correct code; don't reach for memoization or perf tricks
   preemptively. Performance is enforced separately by `oac-implementation-review` at the implement
   exit gate (wasted re-renders, render cost, bundle, high-frequency, query tuning) and looped back.

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
