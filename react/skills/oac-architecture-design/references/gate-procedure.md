# Gate procedure — verifiable-unit gate

The gate question, the three blocking triggers, the review procedure, and the output
formats. Read when running the gate. Paths are relative to this `references/` directory.

---

## Contents

- [Why this gate exists](#why-this-gate-exists)
- [Procedure](#procedure)
- [The three blocking triggers](#the-three-blocking-triggers)
- [Output formats](#output-formats)
- [Scope boundary](#scope-boundary)

---

## Why this gate exists

A God-component has no isolation seam, so the only way to "test" it is to mock the whole
host — which exercises nothing inside it. A dual-source-of-truth lets an AC be true in
one owner and false in the other at once. A spec that never asks the verifiable-unit
question piles behavior into whichever large host already exists, with no testable seam.
This gate asks that question before the design is accepted.

---

## Procedure

Run at **gate altitude** — architecture and data flow, not line-by-line:

1. **Scope.** Take the unit/file list from `design.md` (layer map, Component Impact
   section), plus any files created during implementation if re-running against code.
   List them before reading.
2. **Map the structure.** Sketch actual data flow for the surfaces in scope: where each
   fact lives (component state, Zustand, Query cache, Context), who writes it, who reads
   it, how components compose. Note LOC and effect/hook counts per unit. Misdiagnosis
   comes from skipping this.
3. **Scan for defects, confirm against a rule.** Walk the P1–P7 violation signals in
   `principle-checks.md` (priority: `state-` → `zustand-` → `query-` → `compose-` →
   `layer-`). When a surface looks wrong, open the specific `core/<name>.md` and confirm
   against its right/wrong example — never cite a rule from memory. The three blocking
   triggers map onto the highest-priority categories (crosswalk in `principle-checks.md`).
4. **Confirm against the code.** Verify each candidate trigger against the actual
   file (not assumption); note the path. A pattern technically "wrong" but harmless in
   context is not a blocking trigger.
5. **Write the output and resolve every trigger** (formats below).

---

## The three blocking triggers

Hard blocks — the design cannot be accepted while any trigger is unresolved. Resolve
each via an extraction plan or a recorded justification.

### Trigger 1 — God-component / God-hook

- **Fires when:** a component past ~400 LOC, or a hook mixing ≥2 of CRUD/data-fetch,
  UI-state management, and lifecycle side-effects.
- **Confirm against:** `core/compose-extract-hooks.md`, `core/layer-feature-folders.md`;
  add `core/compose-explicit-variants.md` if the bloat comes from mode flags.
- **Required fix:** extract a render-only component (data + callbacks via props) and
  named single-responsibility hooks (one concern each, invocable via `renderHook`); the
  host becomes a thin orchestrator.
- **The check:** can this unit's behavior be exercised in isolation without mocking the
  entire host?

### Trigger 2 — Server-state-in-Zustand / dual-source-of-truth

- **Fires when:** the spec introduces or preserves a server-derived field in a Zustand
  slice or `localStorage`; a `useEffect(() => setX(...), [serverData])` mirror; or two
  owners for one fact (Query cache + a store holding the same entity list).
- **Confirm against:** `core/state-no-server-data-in-stores.md`,
  `core/state-single-source-of-truth.md`, `core/state-derive-dont-store.md`,
  `core/query-no-effect-fetching.md`, `core/zustand-persist-discipline.md`.
- **Required fix:** server state moves to `useQuery`; Zustand holds only UI keys
  (selected id, open/closed, wizard step); selection is derived at read time
  (`serverList.find(x => x.id === selectedId)`); writes go through `useMutation` with
  `onSuccess: () => queryClient.invalidateQueries(...)`.
- **The check:** is there a single authoritative owner for every fact this spec touches?

### Trigger 3 — Testability seam missing

- **Fires when:** a behavior the spec introduces can only be tested by mocking its entire
  host. Signals: a test plan leaning on `vi.mock('../hooks/useLargeHook')` at module
  level; behavior nested in a God-unit with no callable surface; behavior added to a
  God-unit with no extraction plan.
- **Confirm against:** `core/compose-extract-hooks.md`, `core/layer-service-isolation.md`,
  `core/query-no-effect-fetching.md`.
- **Required fix:** every unit the spec introduces exposes a seam — a component
  renderable with a static props fixture, or a hook invocable via `renderHook` with
  controlled inputs.
- **The check:** could a test writer exercise each behavior without mocking the host?

---

## Output formats

Record the result in `design.md` under `## Architecture Gate` (or, when re-running against
code, in the verification report the caller names).

**Review (structure map + findings):**

```markdown
## Architecture Gate — Review
### Structure map
<state ownership / data flow for the surfaces in scope; LOC + effect counts per unit>
### Findings
| # | Trigger | Rule (core/) | Unit / path | Finding |
|---|---------|--------------|-------------|---------|
| 1 | God-component | compose-extract-hooks | src/.../Foo.tsx (612 LOC) | fetch + UI + 4 effects, no render-only seam |
```

**PASS:**

```markdown
## Architecture Gate — Result
PASS. Checked: God-component/hook, server-state-in-Zustand, testability seam.
No triggers fired on: [surfaces checked].
```

**FAIL (blocking)** — record and resolve before hand-off:

```markdown
FAIL — [Trigger name]
Unit: [name] at [file path]
Reason: [one sentence — why this unit fails the trigger]
Rule confirmed against: core/<name>.md
Required action: [extraction plan | move server state to useQuery | expose testability seam]
```

**Justification (recorded exception)** — under `## Architecture Gate — Justifications`:

```markdown
JUSTIFICATION — [Trigger name]
Unit: [name] at [file path]
Why extraction is deferred: [specific reason — e.g. "this change only adds a read-only
field to an existing surface; extraction is scoped to a separate refactor"]
Test strategy without extraction: [how the behavior is tested despite the missing seam]
Approved by: [author / reviewer]
```

A recorded justification satisfies the gate. Any later re-run checks for this block; if
it is absent and the trigger still fires, the gate reports FAIL (blocking).

---

## Scope boundary

This gate does NOT:
- Review code line-by-line for style, correctness, or over-engineering.
- Replace test-quality forensics (those audit the suite after code lands).
- Enforce a shared-component immutability rule (that belongs to the caller, not this gate).
- Define the target principles (those are P1–P7 in `principle-examples.md`).

It does ONE thing: asks whether each spec behavior maps onto an independently verifiable
unit, at architecture altitude, using the bundled rules, before the design is accepted.
