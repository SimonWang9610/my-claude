---
name: build
description: >-
  Builds from a spec and its design: a short plan, the change in the project's own patterns, and each
  requirement verified with evidence; on the fast track, straight to the change. Use when a spec routes
  to build, or on "implement this", "fix this bug", "refactor X", "add X". Not for choosing an
  approach (use my-spec:decide).
argument-hint: "[requirements]"
---

# build

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Input** — the spec, and `design.md` when there is one; an argument adds requirements (fold them
   in and say so). No spec → `/my-spec:start`.
2. **Context** — the spec's `context`, the files the design names, and what start already found;
   anything else through `/my-spec:explore` (the patterns to copy, the tests to extend).
3. **Plan** — fast track: no plan; the spec's `done` is the check. Full track: tasks in order, each
   `T<n> what — files — the check that proves it`; a new layout in the design → T1 is its scaffold
   (`/my-spec:scaffold-project-structure` step 6); gate.
4. **Implement** — task by task, each check seen failing before the change (a no-regression check:
   seen passing; no test setup → a check script beside the saved spec, else in a temp dir, its command
   added to `verify`; a check that touches user files → a temp HOME); names and code per the
   conventions' Stack order; independent tasks may run in parallel subagents. A check that fails
   twice, or a fact that contradicts the spec → stop with what failed, what was tried and two ways
   forward.
5. **Verify** — run the spec's `verify` commands; per `R<n>`: done, not done, or unverifiable — <what
   would show it>, with evidence (test name, command output); a proxy check is evidence, not done.
6. **Review** — `review on` → `/my-spec:critique code` on the diff; a non-accept verdict → fix its `I`
   lines and review once more; a second non-accept stops at the gate even under `gates auto`. Else
   offer it. Full track: gate.
