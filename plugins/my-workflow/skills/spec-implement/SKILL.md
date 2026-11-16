---
name: spec-implement
description: >-
  Use this skill when planned or clearly scoped work should be written: "implement this", "build the
  plan", "do T-3", "write the acceptance tests", or "go" after a plan, even if they never say
  "implement". Writes a failing test per criterion in the project's own suite, then the code under its
  linter, and stops to ask when the design does not fit. Not for planning (use my-workflow:spec-plan) or judging
  (use my-workflow:spec-review).
argument-hint: "[T-<n>… | tests] [path to a workflow.yaml]"
---

# spec-implement

Rules: `conventions.md`, `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (else `../../shared/`), read
once per conversation. Mode per the spec rules. Other paths: this folder.
Input: the tasks, spec and design. `T` ids → only those. `tests` → step 2 only. No plan → a change
of a few files goes ahead; bigger → ask for a plan.

## Steps

1. **Ground** — the design files of the units touched; the rest through `/my-workflow:audit-truth`
   (the example to copy: the current pattern, never a legacy one; the tests to extend). Find the project's format, lint and type-check
   commands; never install one.
2. **Evidence first** — per `AC`, its evidence (the spec rules): normally one test in the project's
   suite at the outermost surface it names, asserting the outcome. Run it: it must fail for the
   missing behaviour, not a broken setup. Its command → the `Evidence` line. No test setup → say
   so once under **Needs you**; never build a framework.
3. **Implement** — task by task, per the design's units and `references/principles.md`.
4. **Verify** — per task: format, lint, type-check, its criteria's evidence (observed → run the
   product and record what was seen). All pass → done; never before.
5. **Record** — spec mode: the task's row done, with the files actually touched; its criteria's
   `Evidence` lines ✅; `progress`. Last task → `spec-check coverage --run --write`. Inside an
   agent → return these instead.

## Stop and ask

Never work around these:

- the design cannot be built as written, is incomplete, or conflicts with the code;
- a change is needed outside the task's files;
- a test or lint fails twice;
- a test or lint would have to be disabled or loosened (a workaround), or a criterion cannot pass
  (a waiver): the spec rules.
