---
name: critique
description: >-
  Reviews finished work (a diff, a design or a document) against its spec, the project's rules and
  its design, reporting only verified findings with evidence and a verdict: accept, accept with fixes
  or rework. Use when a spec says review on, or on "review this", "critique this diff", "is this design
  sound", "does this meet the spec". Not for designing (use my-spec:decide).
argument-hint: "[code | design | doc] [target] [spec]"
---

# critique

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Scope** — target: the argument, else this session's latest deliverable. Spec: the argument, else
   the session's, else none (the target's stated contract stands in). Mode from the target: a diff or
   code → code; `design.md` or an architecture → design; a document → doc.
2. **Independence** — this session wrote the target and you can spawn → the `reviewer` agent with the
   target, mode, spec and design paths and the verify commands; report what it returns.
3. **Standard**, highest first: the spec · a project rule quoted with path:line · the design's
   decisions · existing conventions, shown by an exemplar path.
4. **Find** — per lens, what the standard requires → what is there → candidates:
   - code: behaviour against each `R`; error paths; tests that would still pass with the bug (in a
     temp copy, set each changed decision to the behaviour an `R` forbids); security from source to
     sink; whole changed files and their callers; an installed review skill for this stack as one more
     lens.
   - design: every `R` covered; the "Check before writing" list in `skills/<part>/SKILL.md` for each
     section the design has; options realistic and the pick following from them.
   - doc: every `R` present, claims sourced, fit for the reader.
5. **Verify** — first run the spec's `verify` in a temp copy; it cannot run here (never install into
   the real environment) → `unverifiable — <reason>`; a stand-in run is evidence, not a pass, and an
   `R` only a proxy shows is unverifiable. Then reproduce each candidate (a test, grep or script, in a
   temp copy; never edit the target or install) → a finding; only readable, not runnable → a finding
   marked `read, not run`; refuted → drop. Never flag speculation on unreachable inputs, style without
   a quoted rule, what a linter enforces, or an equally valid alternative. A defect on lines a diff
   leaves unchanged is only counted.
6. **Report** — `templates/review.md`. Severity: blocker = an `R` unmet, data loss or a security path;
   major = wrong behaviour on a reachable path; minor = the rest. Verdict: any blocker → rework; any
   major → accept with fixes; else accept. Gate; next: the skill that made the target (decide, build
   or write).
