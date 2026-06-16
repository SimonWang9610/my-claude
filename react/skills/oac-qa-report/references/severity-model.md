# Severity & disposition model

## Finding format

Every finding gets a sequential id `F-01`, `F-02`, … and records: requirement id (`AC-*`/`FR-*`/`NFR-*`
or `—`), suggested severity, one-line description, expected, actual, file:line. In-text flags use
`⚠️ **<Label>:** <one-line>`. **Severity is a suggestion** — the reviewer may override it.

## Severity

**Critical** — a stated requirement is not met; a false-positive test mapped to an `AC-*` (the AC has
no real verification, confirmed by the mutation test); a spec internal contradiction (requirements vs
tasks); a phantom baseline (retroactive spec fiction); `.meta.yaml` claims deliverables that don't
exist, or a phase-status contradiction; governance files modified in a feature PR; a new import of a
deprecated module; a stub returning fake success behind an AC.

**Major** — a new shared unit with no colocated test; weak types on a shared API; an error-swallowing
`catch` on a mutation; ephemeral state presented as persisted; client-generated server IDs; a test
that mirrors production logic instead of importing it; an unrelated runtime dependency; a keyboard/
event test on the wrong element type; a spec value claimed removed but still in the code; matcher
misuse that makes an assertion a no-op; a file-modification task whose sub-items didn't all land.

**Minor** — doc drift only (implementation is correct); existing tests don't cover a new branch
(green-but-hollow, no AC impact); deprecated code modified rather than removed; a loose count
assertion (`>= N`) that passes on stale data; steering placeholders; unrelated route changes;
console-only error handling on a non-critical path.

## What blocks a pass

Nothing is a *defect* until a human confirms it — QA records evidence, the reviewer dispositions. The
reviewer selects exactly one outcome:

- **Approved** — every finding accepted or dismissed; no blockers remain.
- **Changes requested** — confirmed defects (named in the findings table) must be fixed and QA re-run.
- **Blocked** — a fundamental issue prevents meaningful review (build broken, spec missing).

## What QA does and does not do

QA **does**: run the audits, write `qa-report.md`, present findings, and (on accept) offer to file a
follow-up tracker issue *only* after the reviewer approves.

QA **does not**: approve or block the branch; confirm or log defects; rewrite tests or production code
without explicit sign-off; transition tracker status (QA status is set by the human — see the
project's tracker playbook); merge or close anything.

## Human sign-off

The report is not a disposition. The branch stays un-mergeable until the reviewer completes the
Disposition block. On a re-run, the previous sign-off is **void** — a full re-disposition is required
(see `retest-cycle.md`).
