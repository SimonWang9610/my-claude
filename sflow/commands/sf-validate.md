---
description: Run the blocking validation gate — clause-to-test coverage plus the architecture gate.
---
# sf:validate

The blocking gate: the existing checks PLUS clause→test coverage and the architecture gate.

---

**Purpose.** No spec reaches `validated` while a stated intent is unproven. A gate that only confirms ACs *exist* — never that each maps to a named passing test, never reviewing architecture beyond shared-unit immutability — lets hollow tests, God-units, and dual-source-of-truth through. This stage adds those two gates as blocking failures.

## Spec Artifacts

Read the spec's artifacts under `.specflow/specs/<name>/`; report the result to the caller (and record the architecture-gate result into `design.md` when the workflow has one).
- **Required:** the spec's `workflow.yaml` snapshot + `.meta.yaml` (required-phase check); the spec artifacts the workflow declares (`requirements.md`, `design.md`, `contracts/`, `tasks.md` — or `analysis.md`/`describe.md` on the lighter workflows; checks over artifacts the workflow omits are SKIP).
- **Optional:** an open PR (Check 6); prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*`; the target repo (codebase under audit).

## Gate / exit

Output `VALIDATED` only when every check is PASS (or SKIP where inapplicable); any blocking FAIL → `BLOCKED (N failing checks)`.

## Checks

Report status + one-line finding for each:

1. **Requirements completeness** — every story has ≥1 AC.
2. **EARS notation** — all requirements use valid EARS.
3. **Design consistency** — every `FR-N`/AC in `design.md` exists in `requirements.md`; every `contracts/<unit>.md` traces to ≥1 AC.
4. **Task DAG** — `tasks.md` is acyclic (list any cycle).
5. **Shared-unit immutability** — no ADOPTED unit modified vs base (report the unit + importers).
6. **PR body** — no issue-closing keywords adjacent to `#N` in an open PR; skip if none.
7. **Required phases** — every `required: true` phase that precedes validate in the spec's `workflow.yaml` is `complete`/`skipped` in `.meta.yaml` (later phases, e.g. qa/drift, are not expected yet).
8. **Clause→test coverage** (blocking) — every AC / testable NFR maps to ≥1 passing, observable-outcome test; emit the clause→test table (AC-ID | Test | File | Status).
9. **Architecture gate** (blocking) — no God-unit, dual-source, or missing testability seam without a recorded justification in `design.md`.

Report: the summary line, each check's status + finding, the Check 8 table, and Check 9's surfaces/justifications.
