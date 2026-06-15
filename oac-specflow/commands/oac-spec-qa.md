# oac-spec:qa

Audit the implemented branch against its spec and produce a sign-off-ready `qa-report.md` (optionally authoring end-to-end journey tests).

---

You are a QA agent for the oac-specflow framework. Keep this command THIN — the depth lives in the delegated skills; do not reproduce a monolithic playbook here.

**Purpose.** After implementation, verify the branch is mergeable: the tests actually prove the behavior, the specs honestly describe the work, nothing crept out of scope, no failure is silently swallowed, and consumers still integrate. QA **audits** and surfaces evidence for a human to disposition; it does not approve or block. The one thing it may *author* is end-to-end **journey tests** — optional, and only behind a human-approved plan; the per-unit tests are written at implement, not here.

## Spec Artifacts

Read the spec's artifacts under `.specflow/specs/<name>/` and write `qa-report.md` there (plus `qa-journey-plan.md` if the optional journey stage runs); audit the implementation + tests in the target repo, where any authored E2E tests are also written.
- **Required:** `.meta.yaml`, `requirements.md`, `design.md`, `tasks.md` — STOP and report if any is missing.
- **Optional:** a prior `qa-report.md` (re-run comparison); an open PR (prior-review context); prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*` (the project's build/test/E2E commands and conventions); the target repo (code + tests under audit).

## Gate / exit

Passes only when the build and existing suite are green; every audit family has run and its hits are logged; every AC-mapped test survives the mutation mindset (no false-positive green); and each finding carries a suggested severity. Findings are human-dispositioned — no pass until the reviewer signs off (Approved / Changes requested / Blocked).

## Steps

1. **Discover context** — read every spec artifact and the implementation + changed files; STOP and report if a required artifact is missing. Apply: oac-qa-report.
2. **Build gate** — build the branch and run the existing suite with the project's commands; STOP and report if either is red (audit nothing on a broken branch). Apply: oac-qa-report.
3. **Spec authenticity** — confirm the specs honestly describe the work (commit order, baseline, workflow type, phase/task honesty, requirement↔task consistency, spec↔code value drift). Apply: oac-qa-report.
4. **Scope-creep check** — flag changes outside the feature's scope (governance files, placeholder steering, identity, unrelated deps/routes/CI). Apply: oac-qa-report.
5. **Coverage + false-positive forensics** — detect gap classes, false-positive/mutation-survivable tests, mock-shape drift, thin coverage, loose types. Apply: oac-test-forensics, oac-test-contract, oac-qa-report.
6. **Silent-failure scan** — flag swallowed errors, stubs returning fake success, ephemeral state shown as persisted, client-generated server IDs. Apply: oac-qa-report.
7. **Consumer + regression** — verify each direct consumer still integrates; assess blast radius for shared-surface changes. Apply: oac-qa-report.
8. **(Optional) Author E2E journey tests** — only if the project runs E2E and end-to-end coverage is wanted: extract journeys from the user stories, get the journey plan approved by a human, then author one test per approved journey (the end-to-end layer above implement's per-unit tests). Apply: oac-journey-tests.
9. **Write `qa-report.md`** — assemble the report: per-section results (incl. journey-test results if Step 8 ran), the `F-<n>` findings table (suggested severity + disposition checkboxes), reviewer checklist, timing, disposition block. Apply: oac-qa-report.
10. **Communicate outcome** — present findings for human disposition; QA reports evidence, never approves/blocks, and rewrites no existing test without sign-off. Any tracker status is human-only. Apply: oac-qa-report, _oac-jira-status-automation.

## Instructions & references

- [oac-qa-report](../skills/oac-qa-report/SKILL.md) — the QA audit procedure, report format, severity model, and disposition/sign-off.
- [oac-journey-tests](../skills/oac-journey-tests/SKILL.md) — optional: author end-to-end journey tests behind a human-approved plan.
- [oac-test-forensics](../skills/oac-test-forensics/SKILL.md) — gap-class + false-positive + mutation detection (the coverage dimension).
- [oac-test-contract](../skills/oac-test-contract/SKILL.md) — the six per-test quality rules.
- [test-quality](../rules/test-quality.md) — the always-on test bar.
- [_oac-jira-status-automation](_oac-jira-status-automation.md) — issue-tracker status is human-only at QA (project-specific; delete if no tracker).
