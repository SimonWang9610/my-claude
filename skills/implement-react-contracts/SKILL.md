---
name: implement-react-contracts
description: >
  Implement React units against their contracts (or a direct request): level-specific
  rules for using/building/optimizing hooks and components, stores and services. Verifies
  its done-condition and raises DESIGN GAPs that steer the architecture; deep conformance
  checking lives in check-react-implementation.
---

# implement-react-contracts

Implementation altitude: the contract decided **what**; you decide **how**. When the *what*
fails at code level, classify and raise (§ Steer the design) — never widen an API, move
state ownership, or cross a boundary silently. With no formal contract, the same discipline
binds against the caller's request and the codebase's conventions.

## Inputs

- **Contracts** — `contracts/<group>.md` (+ `design.md` for wiring) or a contract delta;
  absent → the caller's request + observed conventions govern.
- **Tasks / ACs** — the behaviour to satisfy and its done-condition (gate, tests, typecheck).
- **Direct instructions** — caller steering; narrows the procedure, never waives the self-check.

## Rules

Read the relevant file before writing that kind of code; cite rules in review notes:

- [rules/use-hooks.md](./rules/use-hooks.md) — calling hooks correctly: effects, derived
  values, query/mutation wiring
- [rules/build-hooks.md](./rules/build-hooks.md) — authoring a custom hook: surface,
  stability, teardown, seam
- [rules/optimize-hooks.md](./rules/optimize-hooks.md) — subscription narrowing, hook
  splitting, transient values
- [rules/build-components.md](./rules/build-components.md) — contract surface, data states,
  types, composition
- [rules/optimize-components.md](./rules/optimize-components.md) — memo boundaries,
  deferral, virtualization, bundle
- [rules/build-stores-and-services.md](./rules/build-stores-and-services.md) — store action
  bodies, persistence, transient subscribe, service lifecycle, stream coalescing

**Priority:** a correctness rule beats a performance rule; a project fact (e.g.
`babel-plugin-react-compiler` configured — check once, it inverts manual-memoization advice)
beats generic advice. Optimize hot paths only (per-frame, large list, main interaction) —
clear code first, never pre-optimize a cold path.

## Procedure

1. **Scope** — from the contract/task: units to touch, behaviour expected, constraints in
   force. Read the target files and their imports first; **reuse** the existing
   component/hook/type/query-key/store-slice — never add a second one.
2. **Implement per level** — most changes are mixed-level (a filtered list touches
   component + hook rules at once); apply every rules file whose level the diff touches.
3. **Verify the done-condition** — the task's gate when one exists; otherwise typecheck +
   the relevant tests. Tests define behaviour — make the code satisfy them; NEVER rewrite
   a test to make failing code pass. Deep conformance checking (contract audit, rules
   re-scan, performance & memory) is `check-react-implementation`'s job after the phase —
   conform while writing; don't re-review your own diff.
4. **Steer the design** — when a governing decision is ambiguous, missing a case, or
   provably wrong, raise it; never silently deviate, never blindly implement a defect:

   | Gap | Looks like | Do |
   |-----|------------|-----|
   | **Ambiguity** | the contract is silent on a case you must handle | implement the narrowest safe interpretation; raise for the contract to be amended |
   | **Friction** | the design makes the code fight — missing seam, tangled responsibilities | don't force it with a hack; raise as a re-design candidate |
   | **Defect** | the decision is provably wrong at tech level | **stop — don't implement a known defect**; raise with evidence |

   One block per gap, attached to the result; pause for the caller on Friction/Defect:

   ```markdown
   DESIGN GAP — <unit> · ambiguity | friction | defect
   Contract says: <the line — or the convention observed>
   Code shows: <file:line, API doc, measured behaviour>
   Suggestion: <the amendment>
   Status: implemented narrowest-safe | blocked pending decision
   ```

**Output discipline:** diff + gap blocks only — concise, goal-accurate; cite AC/rule IDs,
no narration of unchanged code.
