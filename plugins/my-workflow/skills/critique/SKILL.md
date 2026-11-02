---
name: critique
description: >-
  Reviews finished work (a diff or a design) against its spec, the project's rules, its design and a
  quality standard of binary checks per axis (correctness, reliability, security, performance,
  maintainability and more), reporting only verified findings with evidence and a verdict: accept,
  accept with fixes or rework. Use on "review this", "critique this diff", "is this design sound",
  or before calling work finished. Not for designing (use my-workflow:decide).
argument-hint: "[code | design] [target] [spec]"
---

# critique

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Scope** — target: the argument, else this session's latest code change or design, else the
   uncommitted diff (or the branch against its base). Spec: the argument, else the session's, else a
   `Q` (spec file? — default: none; the target's stated contract stands in). Mode: a diff or code →
   code; a design or an architecture → design.
2. **Independence** — this session wrote the target → review it in a fresh read-only context when the
   host offers one (only the target, the mode, the spec and design as text or the paths of files the
   user named, and the done-when commands; never this session's reasoning) and report what it returns;
   else review it here and mark the report "Review: same context".
3. **Standard**, highest first: the spec · a project rule quoted with path:line · the design's
   decisions · existing conventions, shown by an example path · at most 5 axes from
   `skills/critique/references/standard.md` · the stack's rules from the conventions' Knowledge
   sources.
4. **Find** — per lens, what the standard requires → what is there → candidates:
   - code: behaviour against each `R`; error paths; tests that would still pass with the bug (in a
     temp copy, set each changed decision to the behaviour an `R` forbids); whole changed files and
     their callers; each picked axis's checks.
   - design: every `R` covered; `shared/kinds.md` § Design must answer for its kind; the "Check before
     writing" list of the part skill behind each section it has (Structure →
     `skills/scaffold-project-structure/SKILL.md`, Components → `skills/design-component/SKILL.md`, UI
     state → `skills/analyze-ui-state/SKILL.md`); options realistic and the pick following from them.
5. **Verify** — first `/my-workflow:verify` in run mode, or this session's verify report when the code
   has not changed since. Then reproduce each candidate (a test, grep or script in a temp copy; never
   edit the target or install) → a finding; only readable, not runnable → a finding marked "read, not
   run"; refuted → drop. Never flag speculation on unreachable inputs, style without a quoted rule,
   what a linter enforces, or an equally valid alternative. A defect on lines a diff leaves unchanged
   is only counted.
6. **Report** — `templates/review.md`; at most about 10 issues, most severe first, the rest counted.
   Severity: blocker = an `R` not done, data loss or a security path; major = wrong behaviour on a
   reachable path; minor = the rest. Verdict: any blocker → rework; any major → accept with fixes;
   else accept. `Open:` the issues to fix, most severe first.
