---
name: build
description: >-
  Builds from requirements and a design: a short plan of tasks linked to the requirements, the change
  in the project's own patterns with unit tests, then every requirement verified; a small change goes
  straight to the code. Also implements only the given tasks of an existing plan. Use on "implement
  this", "fix this bug", "refactor X", "add X". Not for choosing an approach (use
  my-workflow:decide).
argument-hint: "[requirements | T<n>… of a plan]"
---

# build

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md` and
`shared/principles.md`.

1. **Input** — the requirements (a spec in the session or a file the user names, else the request) and
   a design when there is one; an argument adds requirements (fold them in and say so). No spec →
   restate the request as `R1`… each with its check, then go on. The input's Open leaves an approach,
   structure or contract undecided → take a small one as a stated `D`, or stop and say a design is
   needed. Given `T` lines from a plan → implement only those tasks and their files (steps 2 and 4).
2. **Context** — the facts already given and the files the design names; anything else through
   `/my-workflow:audit-truth` (the patterns to copy, the tests to extend). The conventions' Knowledge
   sources for the idioms, APIs and pitfalls of the units being written.
3. **Plan** — a change of a few files with an obvious check: none; the done-when line is the check.
   Asked for the plan only → return it and stop. Else tasks in order, about 8 at most (more → group
   them into batches, or say the design is too coarse), each `T<n> <what> — R<n> — <files> — <the
   check that proves it>`; a requirement no task serves is flagged. A new layout in the design → T1 is
   its scaffold (`/my-workflow:scaffold-project-structure` step 6), a prerequisite of every other
   task. Mark batches whose file sets do not overlap as independent, and keep each requirement within
   one batch.
4. **Implement** — task by task in the project's patterns. A requirement with an acceptance check uses
   it as its task's check; unit tests cover only what that check cannot reach. Each check seen failing
   before the change (a no-regression check: seen passing). No test setup → a check script beside the
   code it checks, its command reported for its requirement's Done when line; a check that touches
   user files → a temp home folder. A design that does not fit → stop with the gap, never deviate
   silently. A check that fails twice → stop with what failed, what was tried and two ways forward.
5. **Verify** — `/my-workflow:verify` in run mode.
6. **Report** — the task lines with their status, then verify's table. `Open:` requirements not done,
   and gaps.
