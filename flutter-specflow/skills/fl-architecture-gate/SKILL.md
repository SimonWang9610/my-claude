---
name: fl-architecture-gate
description: >
  Lightweight verifiable-unit architecture gate for Flutter. For any change that introduces or alters a
  widget, state holder (notifier/bloc/cubit/controller), repository, or service, answers one question:
  does each spec behavior map onto an independently verifiable unit — a widget renderable via pumpWidget
  with injected fakes, or a state holder / repository / service invocable in pure dart test with
  constructor-injected fakes — without mocking its host? The rule corpus and worked examples live in the
  companion fl-architecture-design skill (applied proactively at design time); this gate only verifies.
---

# fl-architecture-gate

> **Does each spec map onto an independently verifiable unit — a widget renderable via `pumpWidget` with injected fakes, or a state holder / repository / service invocable in pure `dart test` with constructor-injected fakes — without mocking its host widget or holder?**

If the answer is no, the gate blocks and requires an extraction plan or a recorded justification before
the phase can close. The review runs at architecture altitude, not line-by-line: the question is "does
this unit have a testability seam?", not "is this code well-written?"

This skill is **lightweight by design** — it carries only the verification: the gate question, the three
blocking triggers, and the report formats. The architecture **rules, worked examples, and the rule index
live in the companion [`fl-architecture-design`](../fl-architecture-design/SKILL.md) skill**, which
applies them *proactively while the design is authored*. The gate confirms the result against those same
rules; it does not re-teach them.

---

## When to use

- **Design-exit check** — after `fl-architecture-design` has produced the design + Shared Widget Plan,
  confirm each named AC behavior lives in a unit that has a testability seam before the design phase
  closes.
- **Validate-phase blocking check** — confirm the implemented units match the planned structure and
  none of the three blocking triggers fired during implementation.

---

## Instructions

1. **Map structure first** — sketch state ownership, data flow across the four layers (UI → Provider →
   Data → Service), dispose/subscription counts, and `build()` size per widget surface before judging
   anything. Misdiagnosis comes from skipping this step.
2. **Check the three blocking triggers** (below). For each candidate, confirm against the specific rule
   in the design skill's corpus — open `../fl-architecture-design/references/core/<name>.md` (e.g.
   `core/testability-seam.md`) and its examples, never cite from memory; use the violation signals and
   trigger→rule crosswalk in `../fl-architecture-design/references/principle-checks.md`. Open
   `../fl-architecture-design/references/conditional/performance/` only when a clear performance hazard is visible. For the project's state-management package idioms, the separate `fl-riverpod` skill applies (`../fl-riverpod/SKILL.md`). The rule index is
   `../fl-architecture-design/references/how-to-use-bundled-rules.md`.
3. **Write the gate result** per the formats in `references/gate-procedure.md`. Unresolved triggers
   block phase exit. Resolve by an extraction plan that creates the missing seam, or a recorded
   justification in `design.md → ## Architecture Gate — Justifications`.

### Blocking triggers

1. **God-widget / God-holder / logic-in-build** — a widget with a very large `build()` mixing multiple
   concerns, business logic or IO inside `build()`, or a state holder mixing data-fetching + UI-state +
   lifecycle side-effects with no isolation seam.
2. **Layer violation / dual-source-of-truth** — a widget calling a repository or service directly (P1
   break), server data cached in a holder field instead of read from the repository SSOT (P3 break), or
   two owners for the same fact.
3. **Testability seam missing** — a behavior reachable only by mocking the entire parent widget or
   holder; a hidden singleton (`Service.instance` looked up inside a class); or a `BuildContext` passed
   into a service or repository.

---

## References

- [`gate-procedure.md`](references/gate-procedure.md) — the gate's own procedure (scope → map → check →
  confirm → report) and all report formats (Review Report, PASS, FAIL, Justification).
- The rule corpus — applied at design, confirmed against here — lives in the design skill:
  - [`fl-architecture-design/…/how-to-use-bundled-rules.md`](../fl-architecture-design/references/how-to-use-bundled-rules.md) — the rule index (13 `core/` rules + the `conditional/` packs) and trigger → rule crosswalk.
  - [`fl-architecture-design/…/core/`](../fl-architecture-design/references/core/) — the 13 high-level universal rules (open the specific file when a surface is suspect).
  - [`fl-architecture-design/…/principle-checks.md`](../fl-architecture-design/references/principle-checks.md) — per-principle violation signals + trigger crosswalk.
  - [`fl-architecture-design/…/principle-examples.md`](../fl-architecture-design/references/principle-examples.md) — P1–P8 right/wrong Dart sketches.
  - [`fl-architecture-design/…/conditional/performance/`](../fl-architecture-design/references/conditional/performance/) — performance pack (consult only when a concrete hazard surfaces; non-blocking). For Riverpod package idioms, see the separate `fl-riverpod` skill (`../fl-riverpod/SKILL.md`).
