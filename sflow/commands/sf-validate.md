---
description: Run the blocking validation gate — clause-to-test coverage plus the architecture gate.
---
# sf:validate

The cheap machine pre-gate before `/sf-qa`: no spec advances while a stated intent is
unproven. Reads `.meta.yaml` + the spec artifacts (checks over an absent optional artifact
are SKIP); records the architecture-gate result into `design.md`; steering as context.

**Steps** — run every check; report status + one-line finding each:

1. **Requirements completeness** — every story has ≥1 AC.
2. **AC shape** — every AC/NFR carries a stable ID (`AC-<story#>.<n>` / `NFR-<n>`) and
   observable Given/When/Then phrasing.
3. **Design consistency** — every AC in `design.md` exists in `requirements.md`; every
   `contracts/<unit>.md` traces to ≥1 AC.
4. **Task DAG** — `tasks.md` acyclic (list any cycle).
5. **Shared-unit immutability** — no ADOPTED unit modified vs base (report unit + importers).
6. **PR body** — no issue-closing keywords adjacent to `#N`; skip if no open PR.
7. **Phase ledger** — every phase preceding `spec-qa` in `.meta.yaml` `phase_status` is
   `completed`, or `skipped` with a recorded reason (this command gates `spec-qa`'s entry).
8. **Clause→test coverage** (blocking) — every AC / testable NFR maps to ≥1 passing
   observable-outcome test, and every `qa-journey-plan.md` journey to an end-to-end test
   (NOT-automated entries are SKIP); emit the table `AC-ID | Test | File | Status`.
9. **Architecture gate** (blocking) — no God-unit, dual source of truth, or missing
   testability seam without a recorded justification in `design.md`.

**Exit.** Output `VALIDATED` only when every check is PASS (or SKIP where inapplicable);
any blocking FAIL → `BLOCKED (N failing checks)`.
