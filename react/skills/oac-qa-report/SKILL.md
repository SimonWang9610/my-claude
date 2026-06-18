---
name: oac-qa-report
description: >
  Audits a handed-off React/TypeScript feature branch and produces a single sign-off-ready
  qa-report.md covering: build gate, spec-authenticity audit, scope-creep check, test-coverage
  and false-positive forensic sweep (via oac-test-forensics), silent-failure detection, and
  consumer/regression verification. Classifies every finding Critical/Major/Minor with an F-id;
  surfaces evidence only — does not approve, block, or rewrite tests. Trigger when a developer
  hands off a branch for QA review and a structured, human-dispositioned report is required
  before merge. Keywords: QA report, audit, feature branch, sign-off, coverage forensics,
  false positive, silent failure, scope creep, spec authenticity, consumer regression.
---

# oac-qa-report

> Audit the branch a developer hands off, and produce one report a reviewer signs off on. QA surfaces evidence; the human dispositions.

This is an **audit**, not a test-writing stage: it verifies that the tests already on the branch prove the behavior, that the specs honestly describe the work, that nothing crept out of scope, and that consumers still integrate. It never writes or rewrites tests, and it never approves or blocks — those are human calls.

## When to use

When a feature branch is handed off for verification and you must produce a single QA report a reviewer signs off on. The report confirms: the build and existing suite are green; the tests actually fail when the behavior breaks; the specs match the work; no change escaped the feature's scope; no failure is silently swallowed; and consumers still render.

## Instructions

1. **Gate on a clean build.** Build the branch and run the existing suite with the project's commands (from the steering files). If either is red, STOP and report — never audit a broken branch. → `references/audit-catalogue.md` §0.
2. **Run the audit families**, logging each hit as a finding with its `⚠️` flag: spec-authenticity (§1), scope-creep (§2), coverage + false-positive (§3), silent-failure (§4). For the test-quality detection mechanics, apply the sibling skills below — do not duplicate them.
3. **Verify consumers + regression** — confirm each direct consumer still integrates and assess blast radius for shared-surface changes. → `references/audit-catalogue.md` §5.
4. **Classify every finding** Critical / Major / Minor and give it an `F-<n>` id. → `references/severity-model.md`.
5. **Assemble `qa-report.md`** in the section order, findings-table, reviewer-checklist, timing, and disposition format of `references/report-format.md`.
6. **Communicate the outcome** for human disposition — QA never approves or blocks, and rewrites no test without sign-off. On a re-run, compare against the prior report first. → `references/severity-model.md` §Disposition, `references/retest-cycle.md`.

## References

- [`audit-catalogue.md`](references/audit-catalogue.md) — the build gate plus the audit families (authenticity, scope-creep, coverage/false-positive, silent-failure) and consumer/regression, each check with its flag wording.
- [`report-format.md`](references/report-format.md) — the `qa-report.md` section order, findings table, reviewer checklist, timing summary, and disposition block.
- [`severity-model.md`](references/severity-model.md) — Critical/Major/Minor definitions, the `F-<n>` id scheme, and the disposition / human-sign-off model.
- [`retest-cycle.md`](references/retest-cycle.md) — re-run comparison (fixed / still-failing / new / regression / stable) and the prior-sign-off-void rule.
- [`../oac-test-forensics/SKILL.md`](../oac-test-forensics/SKILL.md) — gap-class + false-positive + mutation-survivability detection (the coverage dimension).
- [`../oac-test-contract/SKILL.md`](../oac-test-contract/SKILL.md) — the six per-test quality rules.
