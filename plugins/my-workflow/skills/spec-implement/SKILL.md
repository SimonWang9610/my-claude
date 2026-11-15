---
name: spec-implement
description: >-
  Implements a spec's planned tasks: first one black-box acceptance check per criterion, seen
  failing, then the change task by task in the project's own patterns with unit tests, each task's
  check run and its row marked done. Also implements only the given tasks, or writes only the
  acceptance checks. Use as the implement step of a spec, or on "implement this", "build the
  plan", "do T3–T5", "write the acceptance tests". Not for planning (use my-workflow:spec-plan) or
  judging the result (use my-workflow:spec-review).
argument-hint: "[T<n>… | checks] [path to a workflow.yaml]"
---

# spec-implement

Follow `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (if shown unexpanded: `../../shared/conventions.md`
from this skill's folder) and `references/principles.md`. Other paths are relative to this skill's
folder.

1. **Context** — per the conventions' Spec mode; the input is the tasks, the spec and the design.
   Given `T` ids → only those tasks and their files. Given `checks` → step 3 only. No plan: a change
   of a few files with an obvious check goes ahead, its criteria as the checks; anything bigger →
   say a plan is needed.
2. **Ground** — the facts already given and the files the design names; anything else through
   `/my-workflow:audit-truth` (the closest example to copy, the tests to extend). The conventions'
   Knowledge sources for the idioms, APIs and pitfalls of the units being written.
3. **Checks first** — per `AC` in scope, one check at the outermost surface it names (a command, an
   endpoint, the UI, or a public function from the design's contracts), in the project's test setup,
   asserting the observable outcome, never internals. Run each: it must fail for the missing
   behaviour, not for a broken setup; an error naming the contract's missing surface counts, any
   other error is a broken setup. A criterion about content or configuration → a grep or read check.
   No test setup → a check script beside the code it checks; never build a test framework.
4. **Implement** — task by task in the project's patterns. A task's check is its criterion's check;
   unit tests cover only what that cannot reach. A check that touches user files → a temp home
   folder. A design that does not fit, or a change needed outside the task's files → stop with the
   gap, never deviate silently. A check that fails twice → stop with what failed, what was tried and
   two ways forward. A check is loosened, skipped or deleted only with a `D` that says why.
5. **Record** — per finished task, its check run and passing. Spec mode: its row done in the plan
   (blocked: with the reason), the plan's Progress line and the step's `progress`, and its
   criterion's command in the spec's `Check` cell, marked done.
6. **Report** — the tasks with their status and check results. `Open:` tasks not done, and gaps.
