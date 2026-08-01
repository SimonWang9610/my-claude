---
name: evaluate
description: >
  Evaluates a React design, implementation diff, or test suite against its binary
  evidence-typed rubric — per-axis scores derived from countable checks, severity-ranked
  findings, a mechanical verdict (PASS / CONDITIONAL / BLOCK), and, for designs, a
  foundation signal saying when refactoring the blast radius is worth it. Run with fresh
  eyes after the authoring step: "evaluate design" after design, "evaluate implementation"
  and "evaluate tests" after an implement phase. Not for the pre-merge verdict
  (use my-react:review) or building the atlas (use my-react:audit). Output: one
  evaluation report per mode.
---

# evaluate

Every judgment is a **check**: binary, evidence-typed, defined in the mode's rubric.
Scores and verdicts are derived from check outcomes by the framework's fixed mapping —
you run checks and collect evidence; arithmetic does the rest.

Two uses of the same rubric:

- **Improve** (author, right after authoring) — run the checks on your own output, fix
  what any axis ≤2 reveals, ONE bounded loop; internal working process, no report.
  Mechanical evidence keeps self-evaluation honest — judgment-only self-review is worth
  less than nothing. Design-scale work only; implementation and tests are evaluated
  once, after all implementation tasks complete, not per batch.
- **Verify** (independent, at a gate) — evaluate work you did not author, from its
  artifacts alone; keep your context free of the author's reasoning. Produces the
  evaluation report; findings only — leave every file untouched, fixing belongs to the
  author's next pass.

**Hard limits (verify):** edit nothing · report only evidence-backed check outcomes ·
one pass per invocation (re-evaluation is the caller's next spawn).

## Modes and inputs

| Mode | Evaluates | Inputs | Rubric |
|------|-----------|--------|--------|
| `design` | design.md + contracts/ (+ ledgers) | requirements/ACs, atlas | [references/rubric-design.md](./references/rubric-design.md) |
| `implementation` | the diff (task, wave, or phase scope) | contracts, ACs, red baseline ref | [references/rubric-implementation.md](./references/rubric-implementation.md) |
| `tests` | the test files in scope | contracts (Test seams, States), ACs | [references/rubric-tests.md](./references/rubric-tests.md) |

Scale, verdict mapping, report template, and the foundation signal live once in
[references/framework.md](./references/framework.md). The caller names the mode(s) and
the scope; implementation + tests usually run together on a phase diff.

## Procedure

1. **Scope** — list the artifacts/files in scope; read the rubric for the mode.
2. **Prefer executed evidence** — run what runs before judging what doesn't: the named
   tests, typecheck, the must-not greps. A command output outranks a prose judgment.
   Deep runtime cost questions route through [rules/performance-check.md](./rules/performance-check.md)
   (hot paths, perf NFRs, subscription/service/cache diffs).
3. **Run the checks** — every rubric check in scope, explanation before outcome, evidence
   per the check's stated form (grep hit, command output, path:line, ID trace). A fact
   you need but the artifacts lack → `/my-react:audit query "<question>"`.
4. **Derive** — axis scores and verdict from check outcomes per framework.md; failed
   checks become findings, severity-ranked; design mode additionally derives the
   foundation signal from the ledgers.
5. **Report** — the framework's report template, returned to the caller. The report is
   an intermediate artifact — consumed at the gate, never persisted. Compact: findings
   carry facts, the verdict carries the decision, nothing restates artifact content.

## Routing failed checks

- Cause is in the code within its contract → finding with fix direction.
- Cause is the design (wrong ownership, missing seam, boundary drawn wrong) → **DESIGN
  GAP** finding with evidence; the caller routes it to the design fast path.
- Cause predates the diff (inherited from existing code) → foundation item, not a
  finding against the author.
