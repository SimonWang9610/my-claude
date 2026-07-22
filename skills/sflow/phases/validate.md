# validate

The cheap machine pre-gate before `/sflow qa`: no spec advances while a stated intent is unproven.
Checks over an absent optional artifact are SKIP.

**Writes** the architecture-gate result into `design.md` · **Reads** `.meta.yaml` + the spec artifacts.

**Steps** — run every check; report status + a one-line finding each:
1. **Requirements** — every story ≥1 AC.
2. **AC shape** — every AC/NFR a stable ID + observable Given/When/Then.
3. **Design consistency** — every `design.md` AC exists in `requirements.md`; every provided unit
   interface traces to ≥1 AC.
4. **Task DAG** — `tasks.md` acyclic (list any cycle).
5. **Shared-unit immutability** — no ADOPTED unit modified vs base (report unit + importers).
6. **PR body** — no issue-closing keywords adjacent to `#N`; skip if no open PR.
7. **Phase ledger** — every phase before `spec-qa` is `completed` (or `skipped` with a reason).
8. **Clause→test** (blocking) — every AC / testable NFR maps to ≥1 passing outcome test, every journey
   to an E2E test (NOT-automated = SKIP); emit `AC-ID | Test | File | Status`.
9. **Architecture gate** (blocking) — no God-unit, dual source of truth, or missing seam without a
   recorded justification in `design.md`.

**Exit** — `VALIDATED` only when every check PASS (or SKIP); any blocking FAIL → `BLOCKED (N failing)`.
