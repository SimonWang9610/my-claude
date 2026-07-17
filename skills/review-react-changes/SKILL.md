---
name: review-react-changes
description: >
  Review a PR or diff on three axes — specflow integrity (spec ↔ code alignment, QA/AC
  gates), code behavior (contract conformance, silent failures, test honesty, N+1), and
  quality (rules, scope creep, build). Severity-classified findings with evidence;
  gates block dishonest approvals. Use on "review this PR/diff/branch", re-verifies, or
  spec drift audits.
---

# review-react-changes

A review is a statement of fact: every finding carries evidence (`file:line`, command
output), every verdict passes the gates. **Merge-readiness and story-completeness are
different questions** — a clean approve must never imply both.

## Scope — authoritative primitives only

What changed comes from commit-scoped sources, never range diffs (they mix PR content
with merge-base drift):

- PR: `gh api repos/<o>/<r>/pulls/<n>/files --paginate --jq '.[].filename'`
- Local: `git show <sha> --name-only` per commit, or `git log <base>..<head> --name-only`
- Forbidden for scope/governance claims: `git diff <base>..<head> --name-only`

Any governance alarm (CI files, CODEOWNERS, `.claude/`, workflow/steering files) is
re-verified via the primitive before it's cited.

## Procedure

1. **Scope** — the changed-file list via the primitives above. A massive PR (10k+ lines)
   splits into focused modules — one reviewer agent per module with a scoped file list.
2. **Review the three axes** — read the matching reference before each pass:
   - [references/specflow.md](./references/specflow.md) — spec artifacts honest and
     aligned with the code; the mandatory gates
   - [references/behavior.md](./references/behavior.md) — the code does what the
     contracts/ACs say, and fails loudly
   - [references/quality.md](./references/quality.md) — rules conformance, scope creep,
     build verification
3. **Verify findings before posting** — re-read both sides of every falsifiable claim
   ("design says X, code says Y") from source. Large PRs: spawn an independent
   second-opinion agent that has not seen your findings; reconcile.
4. **Verdict** — per the policy below. Re-reviews use the fix-verification matrix:
   `| Finding | Previous | Fix claim | Verified? | Evidence |`.

## Severity → verdict

| Severity | Meaning | Effect |
|----------|---------|--------|
| CRITICAL | broken build/behavior · dishonest spec or tests | block |
| HIGH | contract violated · unmet AC · unbounded N+1 · silent write failure | request changes |
| WARNING | rule violation · bounded N+1 · missing edge/parity coverage | approve-with-notes |
| LOW | advisory | note |

The specflow gates can force a verdict regardless of code quality. Unmet ACs are
enumerated on the review itself — never silently routed into follow-up tickets.

## Output

Findings most-severe first — `<severity> · <file:line> — <what> — <evidence>` — then the
verdict and gate outcomes. Terse: no restating unchanged code; cap advisory findings so
the top severities stay visible; the human-facing summary in clear full sentences.
