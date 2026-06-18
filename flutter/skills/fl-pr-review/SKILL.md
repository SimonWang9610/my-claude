---
name: fl-pr-review
description: >
  Reviews a Flutter/Dart pull request or local diff against the Flutter specflow architecture
  rules (P1–P8, verifiable-unit gate), Riverpod code-gen idioms (@riverpod, Notifier,
  AsyncNotifier), Dart 3 patterns (sealed classes, records, exhaustive switch), and
  flutter_test + Mocktail test-quality rules. Produces a severity-classified (Critical /
  Major / Minor), rule-cited report. GitHub posting is opt-in and confirm-first; the human
  makes the merge decision.

  Use when: "review this Flutter PR", "review the diff/branch", "check this PR against the
  rules", "run a PR review", "audit this branch against the flutter rules", "check the diff
  for architecture violations", "review my Flutter changes".
---

# fl-pr-review

Reviews a Flutter/Dart PR (or local diff) against the Flutter specflow architecture corpus
(P1–P8, verifiable-unit gate, state-management idioms, test-quality) and produces a
severity-classified, rule-cited report. The human makes the merge decision.

## Contents

- [When to use](#when-to-use)
- [Inputs](#inputs)
- [What is reviewed](#what-is-reviewed)
- [Severity tiers](#severity-tiers-one-line-each)
- [Instructions](#instructions)
- [References](#references)

---

## When to use

- Before merging a Flutter feature branch: verify it doesn't violate layering, testability,
  state-ownership, or test-quality rules.
- As a spot-check on a local diff before opening a PR.
- When a code-review comment mentions "architecture" or "testability" and you want a
  structured second opinion against the bundled corpus.
- After implementation lands and you want forensics on the test suite (false positives,
  missing AC coverage).

Not a substitute for running the actual test suite. This skill reads the diff and reasons
against the bundled rules; it does not execute Flutter tests.

---

## Inputs

| Input | How to provide |
|-------|----------------|
| **GitHub PR number** | `gh pr diff <n>` is used to acquire the diff (default) |
| **Base ref** | `git diff <base>...HEAD` — e.g. `git diff main...HEAD` |
| **Working-tree diff** | `git diff` or `git diff --staged` for uncommitted changes |
| **Default** | Current branch vs merge-base with the default branch (`git diff $(git merge-base HEAD origin/HEAD)...HEAD`) |

If no input is specified, the reviewer acquires the diff from the current branch vs its
merge-base with the default remote branch.

---

## What is reviewed

Every changed Dart file is classified by unit kind (widget / state holder / repository /
service / domain model / DI-composition / test), then each unit kind is checked against the
rules that apply to it — architecture first (blocking), then test-quality, then engineering
discipline, then performance (advisory only).

**Only changed code (diff hunks) is reviewed.** Surrounding context is read as needed to
understand data flow and ownership; the rest of the repo is not audited.

---

## Severity tiers (one line each)

- **Critical** — blocks merge; maps to "Request changes" (architecture gate triggers, layer
  violations, SSOT breaks, false-positive tests).
- **Major** — should fix before merge; reviewer's call (wrong state-ownership tier, missing
  `dispose`, no test for an AC, domain model lacks value equality).
- **Minor** — advisory/nit; does not block (performance suggestions with no measured hazard,
  theming tokens, naming conventions).

Full definitions with Flutter examples: `references/severity-model.md`.

---

## Instructions

1. Acquire the diff and list changed Dart files + hunks (see Step 1 in
   `references/review-procedure.md`).
2. Classify each file by unit kind; sketch data flow (Step 2).
3. Run rule passes in priority order, opening each bundled rule file to confirm — never from
   memory (Steps 3a–3g in `references/review-procedure.md`).
4. Confidence-filter: only report high-confidence findings (Step 4).
5. Assemble the report per the template in `references/report-format.md`.
6. If the human requests GitHub posting, confirm before executing (Step 6 in the procedure).

Full procedure with exact rule file paths and pass order: `references/review-procedure.md`.

---

## References

| File | Purpose |
|------|---------|
| `references/review-procedure.md` | Full step-by-step procedure, rule-file paths, pass order |
| `references/severity-model.md` | Three tiers with Flutter examples, rule IDs, verdict mapping |
| `references/report-format.md` | Report template + opt-in GitHub posting commands |
| `../fl-architecture-design/references/how-to-use-bundled-rules.md` | Rule index (13 core + `conditional/performance/`) — corpus lives in `fl-architecture-design`; Riverpod idioms in `../fl-riverpod/SKILL.md` |
| `../fl-architecture-design/references/gate-procedure.md` | Verifiable-unit gate procedure + PASS/FAIL formats (Verify step of fl-architecture-design) |
| `../fl-test-contract/SKILL.md` | Six authoring-time test-quality rules |
| `../fl-test-forensics/SKILL.md` | Three gap-class passes (no-spec, miss-behavior, false-positive) |
| `../../rules/architecture-principles.md` | P1–P8 principles |
| `../../rules/test-quality.md` | Test quality rules |
| `engineering-discipline` | Discipline rules (scope, surgical changes) |
