---
name: fl-pr-review
description: >
  Reviews a Flutter/Dart PR or local diff against the Flutter architecture rules (P1–P8),
  Riverpod code-gen idioms (@riverpod, Notifier, AsyncNotifier), Dart 3 patterns (sealed
  classes, records, exhaustive switch), and flutter_test + Mocktail test-quality rules —
  producing a severity-classified (Critical / Major / Minor), rule-cited report; GitHub
  posting is opt-in and confirm-first, and the human makes the merge call. Use to review a
  Flutter PR, branch, or diff against the rules. Not for React review (use
  review-react-changes). Output: a rule-cited severity report.
---

# fl-pr-review

Reviews a Flutter/Dart PR (or local diff) against the Flutter architecture corpus
(P1–P8, verifiable-unit gate, state-management idioms, test-quality) and produces a
severity-classified, rule-cited report. The human makes the merge decision. Does not execute
Flutter tests.

## Inputs

| Input | How to provide |
|-------|----------------|
| **GitHub PR number** | `gh pr diff <n>` |
| **Base ref** | `git diff <base>...HEAD` — e.g. `git diff main...HEAD` |
| **Working-tree diff** | `git diff` or `git diff --staged` |
| **Default** | `git diff $(git merge-base HEAD origin/HEAD)...HEAD` |

## What is reviewed

Every changed Dart file is classified by unit kind (widget / state holder / repository /
service / domain model / DI-composition / test), then checked against applicable rules —
architecture first (blocking), then test-quality, then engineering discipline, then
performance (advisory only). Only diff hunks are reviewed; surrounding context is read as
needed for data flow and ownership.

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
6. If the human requests GitHub posting, confirm before executing (Step 6 in the procedure;
   commands in `references/github-posting.md`).

Full procedure with exact rule file paths and pass order: `references/review-procedure.md`.

---

## References

| File | Purpose |
|------|---------|
| `references/review-procedure.md` | Full step-by-step procedure, rule-file paths, pass order |
| `references/severity-model.md` | Three tiers with Flutter examples, rule IDs, verdict mapping |
| `references/report-format.md` | Report template |
| `references/github-posting.md` | Opt-in GitHub posting: PR resolution, REST fallback, single batched review (inline comments + verdict event) |
| `references/how-to-use-bundled-rules.md` | Rule index (13 core + `conditional/performance/`) — corpus lives in `fl-architecture-design`; Riverpod idioms in the `fl-riverpod` skill |
| `references/gate-procedure.md` | Verifiable-unit gate procedure + PASS/FAIL formats (Verify step of fl-architecture-design) |
| `fl-test-contract` skill | Six authoring-time test-quality rules (invoke by name) |
| `fl-test-forensics` skill | Three gap-class passes (no-spec, miss-behavior, false-positive) (invoke by name) |

Always-on rules — `architecture-principles` (P1–P8), `test-quality`, and
`engineering-discipline` — are linked into `.claude/rules/` at install and apply ambiently;
no file path needed.
