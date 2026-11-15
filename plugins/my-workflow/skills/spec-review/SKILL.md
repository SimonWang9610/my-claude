---
name: spec-review
description: >-
  Reviews finished work against its spec in three passes: testing (the spec's checks and the
  existing tests run), validation (each acceptance criterion and limit done, not done or
  unverifiable, with evidence) and code review (the project's rules, the design and a quality
  standard of binary checks per axis), reporting only reproduced findings and a verdict: accept,
  accept with fixes or rework. Also reviews a design. Use as the review step of a spec, or on
  "review this", "does it meet the spec", "is this design sound", or before calling work finished.
  Not for designing (use my-workflow:spec-design).
argument-hint: "[code | design] [target] [path to a workflow.yaml]"
---

# spec-review

Follow `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (if shown unexpanded: `../../shared/conventions.md`
from this skill's folder). Other paths are relative to this skill's folder.

Never edit the target or install into the real environment; a probe or a command that writes runs in
a temp copy.

1. **Context** — per the conventions' Spec mode. Target: the argument, else the spec's branch against
   its base, else this session's latest change or design, else the uncommitted diff. Mode: a diff or
   code → code; a design → design. Standalone with no spec → the target's stated contract stands in.
   A second round after fixes covers the earlier issues and the new diff only, unless the fixes
   touched files outside it.
2. **Independence** — this session wrote the target, and the size is not light → review it in a
   fresh read-only context when the host offers one (only the target, the mode, the spec and design paths and the check commands;
   never this session's reasoning) and report what it returns; else review here and mark the report
   "Review: same context".
3. **Test** (code) — the spec's `Check` commands, then the project's existing tests for the touched
   area as their own regression line. One that cannot run here → unverifiable, with the reason. A
   bug: the original reproduction is run again. An improvement: the measure is run against its
   target, and every must-not-change check.
4. **Validate** — per `AC` and `R`: done (a check that would fail without it passed), not done, or
   unverifiable — what would show it. A check that only approximates the outermost surface is
   evidence, never done. A design: every story and criterion is covered.
5. **Review** — the standard, highest first: the spec · a project rule quoted with `path:line` · the
   design's decisions · existing conventions, shown by an example path · at most 5 axes from
   `references/standard.md` · the stack's rules from the conventions' Knowledge sources. Candidates:
   - code: error paths; tests that would still pass with the bug; whole changed files and their
     callers; each picked axis's checks.
   - design: `../spec-design/references/answers.md` for its kind; the "Check before writing" list
     of the skill behind each section; options realistic and the pick following from them.
6. **Confirm** — reproduce each candidate (a test, grep or script) → a finding; only readable, not
   runnable → a finding marked "read, not run"; refuted → drop. Never flag speculation on
   unreachable inputs, style without a quoted rule, what a linter enforces, or an equally valid
   alternative. A defect on lines a diff leaves unchanged is only counted.
7. **Report** — `assets/review.md`; about 10 issues at most, most severe first, the rest counted.
   Severity: blocker = a criterion not done, data loss or a security path; major = wrong behaviour on
   a reachable path; minor = the rest. Verdict: any blocker → rework; any major → accept with fixes;
   else accept. Spec mode: set the step's `verdict`, and leave the step in progress unless it is
   accept; save the report only when the verdict is not accept (light size: the verdict line and
   issues in the spec's Review section). `Open:` the issues to fix, most severe first.
