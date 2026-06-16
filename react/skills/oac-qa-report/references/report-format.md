# QA report format

`qa-report.md` is one document a reviewer signs off on. Write the sections in this order; omit a
section only with an explicit "none detected" line, never silently. The optional project-extension
sections (visual/design fidelity, E2E journeys, API-contract compliance) are included only if the
project runs them.

Status line: `✅ All green` / `⚠️ Findings detected` / `❌ Failures detected`.

```markdown
# QA Report — <Feature Name>

**Branch:** `<branch>`  ·  **Run:** <YYYY-MM-DD HH:MM UTC>  ·  **Status:** <✅ / ⚠️ / ❌>

> ⚠️ This report requires human sign-off. Automated results are findings, not dispositions.
> No defect is confirmed and no merge is granted until a reviewer completes the disposition below.

## Prior Review Status
<Force-push state + a row per prior review item: still-applies? → which F-id. "No prior reviews found." if none.>

## Build & Suite
<Build result; existing-suite pass/fail counts; STOP reason if the gate failed.>

## Spec Authenticity
| Check | Result |
|-------|--------|
| Commit order (spec before implementation) | |
| Baseline accuracy | |
| Workflow type matches the work | |
| Phase/task honesty | |
| Requirement ↔ task consistency | |
| Spec ↔ code value drift | |
<"Verified — lifecycle followed, no contradictions." if all pass.>

## Scope Creep
| # | Pattern | File(s) | Severity | Note |
|---|---------|---------|----------|------|
<"No scope creep detected." if none.>

## Silent Failure Patterns
| # | Pattern | File:line | Note |
|---|---------|-----------|------|
<"No silent-failure patterns detected." if none.>

## Test Coverage Audit
| Check | Result |
|-------|--------|
| New units have colocated tests | |
| New props/branches covered | |
| Shared-API types are tight (unions) | |
| Mock fixtures contain branching fields (no false positives) | |
| Matchers valid for operand types | |
| Tests import shared helpers (no duplication) | |
| AC-mapped tests survive the mutation test | |
<Details for any finding.>

## Test Suite Results
<Pass X / Y; list each failure with expected vs actual and the AC/FR it maps to.>

## Consumer Integration
| Consumer | File | Imports valid | Tests pass | Result |
|----------|------|---------------|------------|--------|

## Regression
| # | Scope (unit / shared / unrelated) | Description | Affected file(s) |
|---|-----------------------------------|-------------|------------------|
<"No regressions detected." if none.>

<!-- Optional project extensions — include only if the project runs them:
## Visual / Design Fidelity   (design-spec/Figma comparison)
## Journey (E2E) Tests
## API-Contract Compliance
-->

## Findings (pending reviewer disposition)
| # | Severity (suggested) | Requirement | Description | Expected | Actual | File | Disposition |
|---|----------------------|-------------|-------------|----------|--------|------|-------------|
| F-01 | | | | | | | ⬜ Defect / ⬜ Accept / ⬜ Dismiss |
<"No findings — all automated checks passed." if none.>

## Reviewer Verification
Mark `[x]` if verified by automation (cite evidence); leave `[ ]` and prefix `**HUMAN:**` where human
judgment is required; reference the relevant F-id on any unchecked item.
- [ ] All functional tests passing; every FR/AC covered; edge cases tested
- [ ] Test pass rate reflects real coverage (no green-but-hollow / false-positive)
- [ ] Spec authenticity findings dispositioned
- [ ] No scope creep, or accepted with justification
- [ ] No silent-failure patterns, or accepted with justification
- [ ] Consumers render correctly in context; regressions triaged
- [ ] **HUMAN:** Accessibility (keyboard, focus, screen reader, contrast)
- [ ] (re-runs) Previously confirmed defects now pass; no new defects from the fixes

## Timing
| Step | Start | End | Duration |
|------|-------|-----|----------|
<One row per step (ISO 8601); `SKIPPED` for skipped steps; a Total row.>

## Disposition
> This branch cannot merge until the reviewer selects exactly one.
- [ ] **Approved** — all findings accepted or dismissed; no blockers
- [ ] **Changes requested** — confirmed defects must be fixed before re-review
- [ ] **Blocked** — a fundamental issue prevents review (build broken, spec missing)

**Reviewer:** ____________  ·  **Date:** ____________
```
