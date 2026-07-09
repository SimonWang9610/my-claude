# Severity & disposition model

## Finding format

Every finding gets a sequential id `F-01`, `F-02`, … and records: requirement id (`AC-*`/`FR-*`/`NFR-*`
or `—`), suggested severity, one-line description, expected, actual, file:line. In-text flags use
`⚠️ **<Label>:** <one-line>`. **Severity is a suggestion** — the reviewer may override it.

## Severity

**Critical** — a stated requirement is not met; a false-positive test mapped to an `AC-*` (the AC has
no real verification, confirmed by the mutation test); a spec internal contradiction (requirements vs
tasks); a phantom baseline (retroactive spec fiction); the spec's tracking metadata claims
deliverables that don't exist, or contradicts itself; governance files modified in a feature PR; a new import of a
deprecated module; a stub returning fake success behind an AC.

**Major** — a new shared unit with no colocated test; weak types on a shared API; an error-swallowing
`catch` on a mutation; ephemeral state presented as persisted; client-generated server IDs; a test
that mirrors production logic instead of importing it; an unrelated runtime dependency; a keyboard/
event test on the wrong element type; a spec value claimed removed but still in the code; matcher
misuse that makes an assertion a no-op; a file-modification task whose sub-items didn't all land.

**Minor** — doc drift only (implementation is correct); existing tests don't cover a new branch
(green-but-hollow, no AC impact); deprecated code modified rather than removed; a loose count
assertion (`>= N`) that passes on stale data; doc-placeholder reverts; unrelated route changes;
console-only error handling on a non-critical path.

## What blocks a pass

Nothing is a *defect* until a human confirms it — QA records evidence, the reviewer dispositions. The
reviewer selects exactly one of the three outcomes defined in the report's Disposition block
(`report-format.md`): Approved, Changes requested, Blocked.

## What QA does and does not do

QA **does**: run the audits, write `qa-report.md`, and present findings for the reviewer to disposition.

QA **does not**: approve or block the branch; confirm or log defects; rewrite tests or production code
without explicit sign-off; merge or close anything.

## Human sign-off

The report is not a disposition. The branch stays un-mergeable until the reviewer completes the
Disposition block. On a re-run, the previous sign-off is **void** — a full re-disposition is required
(see `retest-cycle.md`).
