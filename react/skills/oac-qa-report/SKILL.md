---
name: oac-qa-report
description: >
  Audits a handed-off React/TS feature branch into one sign-off-ready qa-report.md: build gate,
  spec-authenticity, scope-creep, coverage + false-positive forensics, silent-failure, and
  consumer/regression checks — every finding classified Critical/Major/Minor with an F-<n> id and a
  human-disposition block. Evidence only: never approves, blocks, or rewrites tests. Use when a
  branch is handed off for QA review before merge.
---

# oac-qa-report

Audit a finished branch against the spec artifacts the caller names; emit one `qa-report.md`.
Evidence only — never writes or rewrites a test, never approves or blocks. Those are human calls.

## Inputs

- The **feature branch** under review.
- The **spec artifacts** at the paths the caller supplies (requirements.md, design.md, tasks.md,
  `contracts/` — whichever exist). Treat them as claims to verify, not ground truth.
- The project's **build + test commands**.

## Procedure

1. **Gate on a clean build.** Build the branch and run the existing suite once with the project's
   build and test commands. If either is red, STOP and report — never audit a broken branch.
   → `references/audit-catalogue.md` §0.
2. **Run the audit families**, logging each hit as a finding with its `⚠️` flag: spec-authenticity
   (§1), scope-creep (§2), coverage + false-positive (§3), silent-failure (§4). For test-quality
   detection mechanics, invoke the `oac-test-forensics` skill (gap classes, false positives,
   mutation survivability) and check tests against the `oac-test-contract` six rules — do not
   duplicate their mechanics here.
3. **Verify consumers + regression** — confirm each direct consumer still integrates and assess
   blast radius for shared-surface changes. → `references/audit-catalogue.md` §5.
4. **Classify every finding** Critical / Major / Minor and give it an `F-<n>` id.
   → `references/severity-model.md`.
5. **Assemble `qa-report.md`** at the caller-named location, in the section order, findings table,
   reviewer checklist, timing, and disposition format of `references/report-format.md`.
6. **Communicate the outcome** for human disposition — QA never approves or blocks, and rewrites no
   test without sign-off. On a re-run, compare against the prior report first.
   → `references/severity-model.md` §Disposition, `references/retest-cycle.md`.

## References

- [`audit-catalogue.md`](references/audit-catalogue.md) — the build gate plus the audit families
  (authenticity, scope-creep, coverage/false-positive, silent-failure) and consumer/regression, each
  check with its flag wording.
- [`report-format.md`](references/report-format.md) — the `qa-report.md` section order, findings
  table, reviewer checklist, timing summary, and disposition block.
- [`severity-model.md`](references/severity-model.md) — Critical/Major/Minor definitions, the `F-<n>`
  id scheme, and the disposition / human-sign-off model.
- [`retest-cycle.md`](references/retest-cycle.md) — re-run comparison (fixed / still-failing / new /
  regression / stable) and the prior-sign-off-void rule.
- `oac-test-forensics` skill (invoke by name) — gap-class + false-positive + mutation-survivability
  detection (the coverage dimension).
- `oac-test-contract` skill (invoke by name) — the six per-test quality rules.
