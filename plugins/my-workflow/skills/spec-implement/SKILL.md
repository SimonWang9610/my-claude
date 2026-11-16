---
name: spec-implement
description: >-
  Use this skill when planned or clearly scoped work should be written: "implement this", "build the
  plan", "do T-3", "write the acceptance tests", or "go" after a plan, even if they never say
  "implement". Writes a failing check per criterion, then the code under the project's linter, and
  stops to ask when the design does not fit. Not for planning (use my-workflow:spec-plan) or judging
  (use my-workflow:spec-review).
argument-hint: "[T-<n>… | checks] [path to a workflow.yaml]"
---

# spec-implement

Rules: `conventions.md` and `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (unexpanded →
`../../shared/`); already loaded in this conversation → do not read them again. Mode per the spec rules. Other paths are relative to this folder.
Input: the tasks, spec and design. `T` ids → only those. `checks` → step 2 only. No plan → a change
of a few files goes ahead; bigger → ask for a plan.

## Steps

1. **Ground** — the design files of the units touched; the rest through `/my-workflow:audit-truth`
   (the example to copy, the tests to extend). Find the project's format, lint and type-check
   commands; never install one.
2. **Checks first** — per `AC`, one check at the outermost surface it names, asserting the outcome,
   in a test or check file listed in the task's Files, with the literal ids (`AC-1.2`, its `FN`s) in
   its title or a comment. Run it: it must fail for the missing behaviour, not a broken setup. No
   test setup → a check script under the spec folder's `checks/`; never build a framework.
3. **Implement** — task by task, per the design's units and `references/principles.md`.
4. **Verify** — per task: format, lint, type-check, its check. All pass → done; never before.
5. **Record** — spec mode: the task's row done, with the files actually touched; its criterion's
   `Check` line; `progress`. Last task → `spec-check coverage --run --write`. Inside an agent →
   return these instead.

## Stop and ask

Never work around these:

- the design cannot be built as written, is incomplete, or conflicts with the code;
- a change is needed outside the task's files;
- a check or lint fails twice;
- a check or lint would have to be disabled or loosened (a workaround), or a criterion cannot pass
  (a waiver): the spec rules.
