---
name: spec-review
description: >-
  Use this skill when the user asks whether work is right or finished: "review this", "does it meet
  the spec", "is this design sound", "check my diff", "ready to merge", or before calling work done.
  Runs the checks, reports each requirement proven or not, and keeps only reproduced findings; ends
  in accept, accept with fixes or rework. Edits nothing. Not for designing (use
  my-workflow:spec-design).
argument-hint: "[code | design] [target] [path to a workflow.yaml]"
---

# spec-review

Rules: `conventions.md` and `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (unexpanded →
`../../shared/`); already loaded in this conversation → do not read them again. Mode per the spec rules. Other paths are relative to this folder.

- **Target** — the argument → the spec's branch against its base → this session's latest change → the
  uncommitted diff. No spec → the target's stated contract.
- **Mode** — code, or design (`design.md` and `design/`). A design reviewed at its gate → return the
  report; write no status.
- A second round covers the earlier issues and the new diff.

## Steps

1. **Independence** — this session wrote it and the size is not light → a fresh read-only context,
   given only paths and check commands; else mark the report "same context".
2. **Test** (code) — the `Check` commands, lint and format, the existing tests for the area. Cannot
   run → unverifiable.
3. **Validate** — `spec-check coverage --run` (design: `spec-check design`); each id not ok → an
   issue unless waived. No spec → judge each criterion, labelled judged.
4. **Review** — against, highest first: the spec · project rules, quoted · the design · existing
   conventions · at most 5 axes of `references/standard.md`.
   - code: error paths · tests a stub would pass · callers of changed code · departures from the
     design · unapproved workarounds.
   - design: each unit has one responsibility and a human could take it over ·
     `../spec-design/references/answers.md` · no padding.
5. **Confirm** — reproduce each candidate → a finding; only readable → "read, not run"; refuted →
   drop.
6. **Report** — `assets/review.md`, about 10 issues, most severe first. Spec mode: set `verdict`;
   save the report only when it is not accept.

| Severity | Is | Verdict |
|---|---|---|
| blocker | an id uncovered · an unapproved workaround · data loss · a security path | rework |
| major | wrong behaviour on a reachable path | accept with fixes |
| minor | the rest | accept |

## Rules

- Never edit the target; a probe runs in a temp copy.
- Never flag speculation, style without a quoted rule, what a linter enforces, or an equal
  alternative.
