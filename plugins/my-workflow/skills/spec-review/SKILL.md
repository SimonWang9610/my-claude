---
name: spec-review
description: >-
  Use this skill when the user wants to know whether work is right or finished: "review this", "does
  it meet the spec", "is this design sound", "check my diff", "is this ready to merge", or before
  calling any work done, even if they never say "review". Runs the checks, reports each requirement
  as proven, unproven or waived with evidence, and reviews the code or design against the project's
  rules and a quality standard, keeping only findings it could reproduce; ends in a verdict: accept,
  accept with fixes or rework. Edits nothing. Also the review step of a spec. Not for designing (use
  my-workflow:spec-design).
argument-hint: "[code | design] [target] [path to a workflow.yaml]"
---

# spec-review

Rules: `conventions.md` and `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (unexpanded → `../../shared/`).
Other paths are relative to this folder.

## Input

Per the spec rules' Spec mode.

- **Target** — the argument, else the spec's branch against its base, else this session's latest
  change or design, else the uncommitted diff.
- **Mode** — a diff or code → code; a design → design.
- Standalone with no spec → the target's stated contract stands in.
- Design mode while the spec's `current` step is design (the review before its gate) → no stage
  check, no status or verdict write; return the report.
- A second round after fixes covers the earlier issues and the new diff only, unless the fixes
  touched files outside it.

## Steps

1. **Independence** — this session wrote the target, and the size is not light → review it in a fresh
   read-only context when the host offers one (give it only the target, the mode, the spec and design
   paths and the check commands) and report what it returns; else review here and mark the report
   "Review: same context".
2. **Test** (code) — the spec's `Check` commands, the project's lint and format checks, then its
   existing tests for the touched area as their own regression line. Cannot run here → unverifiable,
   with the reason. A bug: the original reproduction again. An improvement: the measure against its
   target, and every must-not-change check.
3. **Validate** — code: `spec-check coverage --run`; its table is the validation. Each id not ok → an
   issue, unless waived. A check that only approximates the outermost surface is evidence, never
   done. Design: `spec-check design`. No spec files → judge each `AC` and `R` done, not done or
   unverifiable, labelled judged.
4. **Review** — the standard, highest first: the spec · a project rule quoted with `path:line` · the
   design's units and decisions · existing conventions, shown by an example path · at most 5 axes
   from `references/standard.md` · the stack's rules from the conventions' Knowledge sources.
   Candidates:
   - code: error paths · tests that would still pass with the bug · whole changed files and their
     callers · code that crosses a unit's boundary or departs from the design · a workaround or
     suppressed check with no approved `WA` · each picked axis's checks.
   - design: easy to follow · each unit states one responsibility, input, output and boundary, and a
     human could take it over; none split further than that needs · every workaround approved ·
     `../spec-design/references/answers.md` for its kind · the "Check before writing" list of the
     skill behind each section · each decision has its why.
5. **Confirm** — reproduce each candidate (a test, grep or script) → a finding; readable but not
   runnable → a finding marked "read, not run"; refuted → drop.
6. **Report** — `assets/review.md`; about 10 issues, most severe first, the rest counted. A finding a
   lint rule could catch → recommend the rule. Spec mode: set the step's `verdict`; leave the step in
   progress unless it is accept; save the report only when the verdict is not accept (light size:
   the verdict line and issues in the spec's Review section).

## Verdict

| Severity | Is | Verdict |
|---|---|---|
| blocker | an id not covered and not waived · an unapproved workaround · data loss · a security path | rework |
| major | wrong behaviour on a reachable path | accept with fixes |
| minor | the rest | accept |

## Rules

- Never edit the target or install into the real environment; a probe or a command that writes runs
  in a temp copy.
- Never the author's reasoning: judge the files and the runs.
- Never flag: speculation on unreachable inputs · style without a quoted rule · what a linter
  enforces · an equally valid alternative. A defect on lines the diff leaves unchanged is only
  counted.

## Output

The report per its template. `Open:` the issues to fix, most severe first.
