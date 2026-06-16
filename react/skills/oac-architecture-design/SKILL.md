---
name: oac-architecture-design
description: >
  Design-time skill: applies the React architecture rules — four concerns: state
  ownership/placement, server-state via TanStack Query as SSOT, Zustand store
  discipline, and component composition + the per-unit testability seam — *while
  authoring* design.md and contracts/. Carries the full rule corpus under
  references/. Also verifies its own output at phase exit: confirms each unit is
  independently verifiable via the verifiable-unit gate (three blocking triggers).
  Triggers on the spec-design stage and whenever you are structuring components,
  hooks, stores, or write paths.
---

# oac-architecture-design

**Design AGAINST the rules proactively, so the verify step rarely has to block.**

Author `design.md` and `contracts/<unit>.md` such that at design exit, each
blocking trigger is already a non-issue: no God-components, no server data in
Zustand, no unit lacking a testability seam.

---

## Purpose

Apply architecture principles P1–P7 as a *design-time authoring discipline* — not a
retroactive reviewer. You are building structure on paper before any TypeScript is
written. A seam missing from the design cannot be tested in the implementation; catch
it here.

---

## When to use

- The `spec-design` command stage (primary trigger).
- Structuring a feature's units from scratch: components, hooks, stores, query keys, services.
- Revisiting or extending `design.md` to add new units or change ownership decisions.

---

## Instructions

### 1. Load the rule index first

Open `references/how-to-use-bundled-rules.md` — it lists all 23 `core/` rules (always
applied) by priority category and the `conditional/performance/` pack. Keep it at hand
throughout.

### 2. Follow the design procedure

Open `references/design-procedure.md` and work through all 7 steps in order.

### 3. Key decisions

- **Feature-folder / layer assignment** — `references/core/layer-feature-folders.md`,
  `references/core/layer-unidirectional-deps.md`
- **State-ownership tier** (local useState → lifted → Zustand → TanStack Query) —
  `references/core/state-ownership-decision.md`
- **Server data is SSOT in TanStack Query, never mirrored to Zustand** —
  `references/core/state-no-server-data-in-stores.md`,
  `references/core/query-no-effect-fetching.md`
- **One owner per fact, derive the rest** —
  `references/core/state-single-source-of-truth.md`,
  `references/core/state-derive-dont-store.md`
- **Zustand store discipline** (actions in store, one domain per slice) —
  `references/core/zustand-actions-in-store.md`,
  `references/core/zustand-slice-organization.md`
- **Component composition over boolean-prop accretion** —
  `references/core/compose-extract-hooks.md`,
  `references/core/compose-avoid-boolean-props.md`
- **Every unit independently verifiable (testability seam)** —
  `references/core/compose-extract-hooks.md`,
  `references/core/layer-service-isolation.md`

### 4. Conditional packs — open only when the scenario applies

- `references/conditional/performance/` — concrete performance hazard surfaced (advisory,
  non-blocking).

### 5. Verify — the verifiable-unit gate

> **Token cost note:** this step reads only `references/gate-procedure.md` (lightweight).
> Do NOT re-open the full corpus under `core/` — that is for authoring (steps 1–4).

At design exit **and** at validate, confirm the gate question and the three blocking triggers:

> **Does each spec map onto an independently verifiable unit — renderable/invocable in isolation without mocking its host?**

**Three blocking triggers (hard blocks — phase cannot close while unresolved):**

1. **God-component / God-hook** — component past ~400 LOC, or a hook mixing two or more of
   CRUD/data-fetching, UI-state management, and lifecycle side-effects.
2. **Server-state-in-Zustand / dual-source-of-truth** — server-derived field stored in Zustand
   or localStorage, a `useEffect` mirroring server data into state, or two owners for the same fact.
3. **Testability seam missing** — a spec behavior reachable only by mocking its entire host hook
   or component at the module level.

For each trigger, write PASS or record an extraction plan / justification per
`references/gate-procedure.md` (report formats: Review Report, PASS, FAIL, Justification).
If this skill was applied correctly through steps 1–4, all triggers should be non-issues.

---

## References

| Resource | Path |
|----------|------|
| Rule index (read first) | `references/how-to-use-bundled-rules.md` |
| Step-by-step design procedure | `references/design-procedure.md` |
| Core rules (23, universal) | `references/core/` |
| Conditional packs | `references/conditional/` |
| Right/wrong principle sketches | `references/principle-examples.md` |
| Per-principle violation signals | `references/principle-checks.md` |
| Verification procedure + report formats | `references/gate-procedure.md` |
