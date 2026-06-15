# Gate procedure — oac-architecture-gate

Full review procedure, report formats, trigger detail, and scope boundary. Read when running the gate.

---

## Why this gate exists

A God-component has no isolation seam, so the only way to "test" it is to mock the whole host —
which exercises nothing inside it. A dual-source-of-truth lets an AC be true in one owner and
false in the other simultaneously. A spec flow that never asks the verifiable-unit question lets
feature specs pile behavior into whichever large host already exists, and agents improvise
unspecced logic with no testable seam. This gate inserts that question into the lifecycle.

**External practice:**
- React docs — custom hook extraction: https://react.dev/learn/reusing-logic-with-custom-hooks
- Feature-Sliced Design — hard feature boundaries: https://feature-sliced.design/
- bulletproof-react — explicit feature public API: https://github.com/alan2207/bulletproof-react/blob/master/docs/project-structure.md
- TanStack — server vs client state: https://tanstack.com/query/v4/docs/framework/react/guides/does-this-replace-client-state
- TkDodo — copying server data into state opts out of background updates: https://tkdodo.eu/blog/practical-react-query
- TkDodo — derive at read time, not with effects: https://tkdodo.eu/blog/deriving-client-state-from-server-state

---

## Procedure

Run the review at **gate altitude** (architecture, not line-by-line):

1. **Scope.** Take the file list from `design.md` → Component Impact / surfaces section, plus any
   files modified or created during implementation. List them before reading.

2. **Map the structure first.** Sketch actual data flow for the surfaces in scope: where state
   lives (component state, Zustand stores, Query cache, Context), who writes each fact, who reads
   it, and how components compose. Note the LOC and effect/hook counts of each unit in scope.
   Misdiagnosis comes from skipping this step.

3. **Check against bundled rules in priority order.** Open `how-to-use-bundled-rules.md` for the
   index, then read the specific `rules-architecture/<name>.md` whenever a surface looks like it
   might violate it. Priority: `state-` (CRITICAL) → `zustand-` (HIGH) → `query-` (HIGH) →
   `compose-` (MEDIUM-HIGH) → `layer-` (MEDIUM) → `react19-` (LOW-MEDIUM). The three blocking
   triggers map onto the highest-priority categories — see the crosswalk in `principle-checks.md`.
   Do not cite a rule from memory — confirm against the file's incorrect/correct examples.

4. **Confirm against the code.** For each candidate trigger, verify against the actual code (not
   assumption), note the file path, and assess honestly. A pattern that's technically "wrong" but
   harmless in context is not a blocking trigger.

5. **Write the Review Report and run the extraction/justification gate** (formats below).

---

## The three blocking triggers

These are **hard blocks**. A phase cannot close while any trigger is unresolved. Resolve via an
extraction plan or a recorded justification.

### Trigger 1 — God-component / God-hook

**Condition:** A component past ~400 LOC, or a hook mixing two or more of CRUD/data-fetching,
UI-state management, and lifecycle side-effects.

**Confirm against:** `rules-architecture/compose-extract-hooks.md`,
`rules-architecture/layer-feature-folders.md`. Cross-check `compose-explicit-variants.md` if the
bloat comes from mode flags.

**Required extraction pattern:** extract a render-only component (data + callbacks via props, no
state or effects) and named single-responsibility hooks (one hook per concern, each independently
invocable via `renderHook`). The host becomes a thin orchestrator.

**The check:** "Can this component/hook's behavior be exercised in an isolated test without mocking
the entire host?"

### Trigger 2 — Server-state-in-Zustand / dual-source-of-truth

**Condition:** The spec introduces or preserves: a server-derived field in a Zustand slice or
`localStorage`; a `useEffect(() => setX(...), [serverData])` mirror; or two owners for the same
fact (Query cache + Zustand slice holding the same entity list).

**Confirm against:** `rules-architecture/state-no-server-data-in-stores.md`,
`rules-architecture/state-single-source-of-truth.md`,
`rules-architecture/state-derive-dont-store.md`,
`rules-architecture/query-no-effect-fetching.md`,
`rules-architecture/zustand-persist-discipline.md`.

**Required fix pattern:** server state moves to `useQuery`; Zustand holds only UI-only keys
(selected ID, open/closed, wizard step). Client selection is derived at read time:
`const resolved = serverList.find(item => item.id === selectedId)`. Writes go through
`useMutation` with `onSuccess: () => queryClient.invalidateQueries(...)`.

**The check:** "Is there a single authoritative owner for every fact this spec touches?"

### Trigger 3 — Testability seam missing

**Condition:** A behavior the spec introduces can only be tested by mocking its entire host
component or hook. Signals: test plan relies on `vi.mock('../hooks/useLargeHook')` at module
level; behavior is nested inside a God-unit with no callable surface; the spec adds behavior to a
God-unit with no extraction plan.

**Confirm against:** `rules-architecture/compose-extract-hooks.md`,
`rules-architecture/layer-service-isolation.md`,
`rules-architecture/query-no-effect-fetching.md`.

**Required fix:** every unit the spec introduces must expose a testability seam — a component
independently renderable with a static props fixture, or a hook independently invocable via
`renderHook` with controlled inputs.

**The check:** "Could a test writer exercise each behavior without mocking the entire host?"

> **Performance note:** this gate is architecture-first. If a clear performance hazard surfaces on
> a high-frequency path while mapping structure, read the relevant `rules-performance/<name>.md`
> and note it briefly as a **non-blocking** observation. Performance is not a blocking trigger here.

---

## Review Report format

Record the gate result in the shape below, then write it into `design.md` (gate at design) or the validate report (gate at validate).

```markdown
## Architecture Gate — Review

### Structure map
<state ownership / data flow for the surfaces in scope; LOC + effect counts per unit>

### Findings
| # | Trigger | Rule (bundled) | Unit / path | Finding |
|---|---------|----------------|-------------|---------|
| 1 | God-component | compose-extract-hooks | src/.../Foo.tsx (612 LOC) | mixes fetch + UI + 4 effects, no render-only seam |
```

### PASS

```markdown
## Architecture Gate — Result
PASS. Checked: God-component/hook, server-state-in-Zustand, testability seam.
No triggers fired on: [list of surfaces checked].
```

The phase may close.

### FAIL (blocking)

Record under `## Architecture Gate — Findings`:

```markdown
FAIL — [Trigger name]
Unit: [ComponentName / hookName] at [file path]
Reason: [one sentence: why this unit fails the trigger]
Rule confirmed against: references/rules-architecture/<name>.md
Required action: [extraction plan | move server state to useQuery | expose testability seam]
```

The phase **cannot close** until the finding is resolved or a justification is recorded.

### Justification (recorded exception)

Record under `## Architecture Gate — Justifications`:

```markdown
JUSTIFICATION — [Trigger name]
Unit: [ComponentName / hookName] at [file path]
Why extraction is deferred: [specific reason — not "too large", but e.g. "being extracted in a
separate refactor spec; this spec only adds a read-only field to the existing surface"]
Test strategy without extraction: [how the behavior will be tested despite the missing seam]
Approved by: [author / reviewer]
```

A recorded justification satisfies the gate. The validate command checks for this block; if absent
and the trigger fires, the gate reports `FAIL (blocking)`.

---

## Scope boundary

This gate does NOT:
- Review code line-by-line for style, correctness, or over-engineering.
- Replace post-implementation test-quality forensics (those run after implementation).
- Enforce the shared-component immutability rule (that stays in the design / validate / implement commands).
- Define the target architecture principles (those are P1–P7 in `principle-examples.md`).

It does ONE thing: asks whether each spec maps onto an independently verifiable unit, at
architecture altitude, using the bundled rules, before a phase closes.
