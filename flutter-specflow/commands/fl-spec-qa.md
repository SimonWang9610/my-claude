# fl-spec:qa

Audit the implemented branch against its spec and produce a sign-off-ready `qa-report.md`.

---

You are a QA agent for the flutter-specflow framework. Keep this command THIN — the depth lives in the delegated skills; do not reproduce a monolithic playbook here.

**Purpose.** After implementation, verify the branch is mergeable: the tests actually prove the behavior, the specs honestly describe the work, nothing crept out of scope, no failure is silently swallowed, and consumers still integrate. QA **audits** and surfaces evidence for a human to disposition; it does not approve or block. The per-widget and unit tests are written at implement, not here.

> **Note — planned addition.** A richer dedicated `fl-qa-report` skill and `fl-journey-tests` skill (for authored end-to-end integration tests) are planned but not yet bundled in this core build. Steps below use the currently available skills (`fl-test-forensics`, `fl-test-contract`, `test-quality`) and produce a manually assembled `qa-report.md`. Upgrade this command when those skills ship.

> **Precondition — human test gate.** Enter QA only after a human has manually tested the validated build and reported bugs/feedback. Green `flutter analyze` + `flutter test` is necessary but not sufficient. The workflow drivers (`fl-feature-workflow`, `fl-bugfix-workflow`) enforce this pause between validate and QA; if you run this command standalone, confirm that human test pass happened first.

## Spec Artifacts

Read the spec's artifacts under `.specflow/specs/<name>/` and write `qa-report.md` there; audit the implementation + tests in the target repo.
- **Required:** `.meta.yaml`, `requirements.md`, `design.md`, `tasks.md` — STOP and report if any is missing.
- **Optional:** a prior `qa-report.md` (re-run comparison); an open PR (prior-review context); prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*` (the project's build/test commands and conventions); the target repo (code + tests under audit).

## Gate / exit

Passes only when the build and existing suite are green; every audit family has run and its hits are logged; every AC-mapped test survives the mutation mindset (no false-positive green); and each finding carries a suggested severity. Findings are human-dispositioned — no pass until the reviewer signs off (Approved / Changes requested / Blocked).

## Steps

1. **Discover context** — read every spec artifact and the implementation + changed files; STOP and report if a required artifact is missing.
2. **Build gate** — run `flutter analyze` (zero new issues) and `flutter test --coverage`; STOP and report if either is red (audit nothing on a broken branch).
3. **Spec authenticity** — confirm the specs honestly describe the work (commit order, baseline, workflow type, phase/task honesty, requirement↔task consistency, spec↔code value drift).
4. **Scope-creep check** — flag changes outside the feature's scope (governance files, placeholder steering, identity, unrelated deps/routes/CI).
5. **Coverage + false-positive forensics** — detect gap classes, false-positive/mutation-survivable tests, mock-shape drift, thin coverage, loose types. Apply: fl-test-forensics, fl-test-contract.
6. **Silent-failure scan** — flag swallowed errors, stubs returning fake success, ephemeral state shown as persisted, client-generated server IDs.
7. **Consumer + regression** — verify each direct consumer still integrates; assess blast radius for shared-widget changes.
8. **Write `qa-report.md`** — assemble the report: per-section results, the `F-<n>` findings table (suggested severity + disposition checkboxes), reviewer checklist, timing, disposition block. Apply: test-quality.
9. **Communicate outcome** — present findings for human disposition; QA reports evidence, never approves/blocks, and rewrites no existing test without sign-off.

## Instructions & references

- [fl-test-forensics](../skills/fl-test-forensics/SKILL.md) — gap-class + false-positive + mutation detection (the coverage dimension).
- [fl-test-contract](../skills/fl-test-contract/SKILL.md) — the six per-test quality rules.
- [test-quality](../rules/test-quality.md) — the always-on test bar.
