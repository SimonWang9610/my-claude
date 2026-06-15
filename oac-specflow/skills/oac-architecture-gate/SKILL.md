---
name: oac-architecture-gate
description: >
  Verifiable-unit architecture gate. For any change that introduces or alters a component, hook,
  store, or write path, answers one question: does the behavior map onto an independently verifiable
  unit — renderable or invocable in isolation without mocking its host? Runs entirely from bundled
  rules under references/; never invokes an external skill.
---

# oac-architecture-gate

> **Does each spec map onto an independently verifiable unit — renderable/invocable in isolation without mocking its host?**

If the answer is no, the gate blocks and requires an extraction plan or a recorded justification
before the phase can close. The review runs at architecture altitude, not line-by-line: the
question is "does this unit have a testability seam?", not "is this code well-written?"

---

## When to use

When a spec introduces or changes a component, hook, store, or write path and you must confirm
each named behavior is independently testable before a phase is allowed to close — whether that
is the design-exit check (after the Shared Component Plan is produced) or the validate-phase
blocking check.

---

## Instructions

1. **Read `references/how-to-use-bundled-rules.md`** — full category index and priority order
   (`state-` → `zustand-` → `query-` → `compose-` → `layer-` → `react19-`).
2. **Map structure first** — sketch state ownership, data flow, and LOC/effect counts for each
   surface in scope before judging anything.
3. **Check the three blocking triggers** (below). For each candidate, open the specific
   `references/rules-architecture/<name>.md` and confirm against its examples — never cite from
   memory. If a clear high-frequency hazard surfaces, consult `references/rules-performance/<name>.md`; otherwise skip to step 4.
4. **Write the gate result** per the formats in `references/gate-procedure.md`. Unresolved
   triggers block phase exit. Resolve by an extraction plan that creates the missing seam, or a
   recorded justification in `design.md → ## Architecture Gate — Justifications`.

### Blocking triggers

1. **God-component / God-hook** — component past ~400 LOC, or a hook mixing two or more of
   CRUD/data-fetching, UI-state management, and lifecycle side-effects.
2. **Server-state-in-Zustand / dual-source-of-truth** — server-derived field stored in Zustand
   or localStorage, a `useEffect` mirroring server data into state, or two owners for the same fact.
3. **Testability seam missing** — a spec behavior reachable only by mocking its entire host hook
   or component at the module level.

---

## References

- [`gate-procedure.md`](references/gate-procedure.md) — full procedure (scope → map → check →
  confirm → report) and all report formats (Review Report, PASS, FAIL, Justification).
- [`how-to-use-bundled-rules.md`](references/how-to-use-bundled-rules.md) — index of all bundled
  rule files by category and priority order; trigger → rule crosswalk.
- [`principle-examples.md`](references/principle-examples.md) — P1–P7 right/wrong code sketches
  with rationale and cited sources.
- [`principle-checks.md`](references/principle-checks.md) — per-principle violation signals and
  trigger → principle → rule crosswalk.
- [`rules-architecture/`](references/rules-architecture/) — 23 bundled architecture rule files
  (rationale + incorrect/correct examples). Read the specific file when a surface is suspect.
- [`rules-performance/`](references/rules-performance/) — 22 bundled performance rule files.
  Non-blocking; consult only when a clear performance hazard surfaces.
