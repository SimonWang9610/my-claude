---
description: Audit the implemented branch and produce a sign-off-ready QA report, optionally authoring journey tests.
---
# spec:qa

Audit the implemented branch against its spec and produce a sign-off-ready report (optionally authoring end-to-end journey tests).

---

**Purpose.** After implementation, verify the branch is mergeable: the tests actually prove the behavior, the specs honestly describe the work, nothing crept out of scope, no failure is silently swallowed, and consumers still integrate. QA **audits** and surfaces evidence for a human to disposition; it does not approve or block. The one thing it may *author* is end-to-end journey tests — optional, and only behind a human-approved plan; the per-unit tests are written at implement, not here.

**Precondition — enter QA only after the human test gate passes (a human has manually tested the validated build and signed off).**

## Spec Artifacts

Read the spec's artifacts under `.specflow/specs/<name>/` and write `qa-report.md` there (plus `journey-plan.md` if the optional journey stage runs); audit the implementation + tests in the target repo, where any authored end-to-end tests are also written.
- **Required:** `.meta.yaml`, `requirements.md`, `design.md`, `tasks.md` — STOP and report if any is missing.
- **Optional:** a prior `qa-report.md` (re-run comparison); an open PR (prior-review context); prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*` (the project's build/test/end-to-end commands and conventions); the target repo (code + tests under audit).

## Gate / exit

Passes only when the build and existing suite are green; every audit family has run and its hits are logged; every AC-mapped test survives the mutation mindset (no false-positive green); and each finding carries a suggested severity. Findings are human-dispositioned — no pass until the reviewer signs off (Approved / Changes requested / Blocked).

## Steps

1. **Discover context** — read every spec artifact and the implementation + changed files; STOP and report if a required artifact is missing.
2. **Build gate** — run the project's build + test commands from steering; STOP and report if either is red (audit nothing on a broken branch).
3. **Spec authenticity** — confirm the specs honestly describe the work (commit order, baseline, workflow type, phase/task honesty, requirement↔task consistency, spec↔code value drift).
4. **Scope-creep check** — flag changes outside the feature's scope (governance files, placeholder steering, identity, unrelated deps/routes/CI).
5. **Coverage + false-positive forensics** — detect gap classes, false-positive/mutation-survivable tests, mock-shape drift, thin coverage, loose types.
6. **Silent-failure scan** — flag swallowed errors, stubs returning fake success, ephemeral state shown as persisted, client-generated server IDs.
7. **Consumer + regression** — verify each direct consumer still integrates; assess blast radius for shared-surface changes.
8. **(Optional) Author end-to-end journey tests** — only if the project supports end-to-end tests and coverage is wanted: extract journeys from the user stories, get the journey plan approved by a human, then author one test per approved journey (the end-to-end layer above implement's per-unit tests).
9. **Write `qa-report.md`** — assemble the report: per-section results (incl. end-to-end test results if Step 8 ran), the `F-<n>` findings table (suggested severity + disposition checkboxes), reviewer checklist, timing, disposition block.
10. **Communicate outcome** — present findings for human disposition; QA reports evidence, never approves/blocks, and rewrites no existing test without sign-off. Any tracker status transition is human-only. Optional — if the project defines a tracker integration, run it.
