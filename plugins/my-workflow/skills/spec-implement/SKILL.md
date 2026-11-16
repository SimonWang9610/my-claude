---
name: spec-implement
description: >-
  Use this skill when the user wants planned or clearly scoped work written: "implement this", "build
  the plan", "do T-3 to T-5", "write the code for X", "write the acceptance tests", even if they just
  say "go" after a plan or design. Writes a failing acceptance check per criterion first, then the
  change task by task in the project's own patterns under its linter and formatter, and marks a task
  done only when its checks pass. Stops and asks when the design does not fit; never works around it
  silently. Also the implement step of a spec. Not for planning (use my-workflow:spec-plan) or
  judging the result (use my-workflow:spec-review).
argument-hint: "[T-<n>… | checks] [path to a workflow.yaml]"
---

# spec-implement

Rules: `conventions.md` and `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (unexpanded → `../../shared/`).
Coding principles: `references/principles.md`. Other paths are relative to this folder.

## Input

Per the spec rules' Spec mode: the tasks, the spec, the design.

- `T` ids given → only those tasks and their files.
- `checks` given → step 2 only.
- No plan → a change of a few files with an obvious check goes ahead, its criteria as the checks;
  anything bigger → say a plan is needed.

## Steps

1. **Ground** — the facts given and the files the design names; the rest through
   `/my-workflow:audit-truth` (the closest example to copy, the tests to extend). Load the
   conventions' Knowledge sources for the units being written. Find the project's lint, format and
   type-check commands (manifest scripts, config files); none → say so, never install one.
2. **Checks first** — per `AC` in scope, one check at the outermost surface it names (a command, an
   endpoint, the UI, or a public function from the design's contracts), in the project's test setup,
   asserting the observable outcome. Write the literal ids it proves (`AC-1.2`, its `FN`s) in a
   comment or title string of the test, in a test or check file listed in the task's Files (the spec
   rules' Checks: tested). Run each: it must fail for the missing behaviour; an error naming the contract's
   missing surface counts, any other error is a broken setup. A criterion about content or
   configuration → a grep or read check, kept in a check script. No test setup → a check script
   beside the code; never build a test framework.
3. **Implement** — task by task, per the design's units and the project's patterns. A task's check is
   its criterion's check; unit tests cover only what that cannot reach. A check that touches user
   files → a temp home folder.
4. **Verify** — per task: format, then lint and type-check the touched files, then its check. All
   pass → done.
5. **Record** — inside an agent: return these, write none. Spec mode, per finished task: its row done (blocked: with the reason) and its Files
   set to the files actually touched, tests included; the plan's Progress line and the step's
   `progress`; its criterion's `Check` cell set to the command, marked done. Last task → `spec-check
   coverage --run --write` passes.

## Stop and ask

- The design cannot be built as written, is incomplete, or conflicts with the codebase → show the
  gap and the options; the user decides. Never deviate or work around it silently.
- A change is needed outside the task's files.
- A check or lint fails twice → what failed, what was tried, two ways forward.
- A check or lint would have to be disabled, loosened, skipped or deleted → that is a workaround
  (the spec rules' Workarounds).
- A criterion cannot be tested or made to pass → a waiver (same section).

## Rules

- Never report a task done while a check, lint or type-check on it fails.
- Assert outcomes, never internals.

## Output

Per task: status, files, check and lint results. `Open:` tasks not done, gaps, workarounds and
waivers awaiting approval.
