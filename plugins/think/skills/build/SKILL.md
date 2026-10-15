---
name: build
description: >-
  The coding workflow from an agreed code spec: plan ordered subtasks, implement them (delegating
  independent ones, or handing them to the project's own driver when it has one), track progress,
  handle roadblocks and requirement changes, verify against the spec's done-when, and run a
  fresh-eyes review only when the user turns it on. Gates after every stage. Use for developing a
  feature or module, fixing a bug, refactoring, or any change to code, config, or tests. Input: the
  code spec already in the session; the argument is optional extra requirements.
argument-hint: [requirements]
---

# build

Uses: skill `think:prompt` when no spec exists, skill `think:explore` for facts; agent `reviewer` for
review (Claude Code `think:reviewer`).

**Input.** The latest code spec in the session (with any design decisions agreed after it) is the task.
An argument adds or changes requirements: fold them into the spec as `must` or `limits` lines and say so
in one line. No spec in the session → invoke the `prompt` skill first, with the argument as the raw
request. Stages, each ending in a gate:

1. **Plan.** Ordered subtasks: `T<n> — what — files — check that proves it — depends on`. Split until
   each subtask has one check. Read the files named in `context`/`touch` first (the `explore` skill for
   anything wider). Gate.
2. **Execute.** Subtask by subtask; independent ones may run in parallel subagents. A project driver
   or workflow already exists for this kind of work (an agent or skill set in the repo or installed) →
   hand it the subtasks instead. Track status in the session's task list.
   - Roadblock (a check fails twice, a fact contradicts the spec): stop, report the failing check, what
     was tried, the suspected cause, two ways forward. Gate.
   - Requirement change: update the spec, mark the affected subtasks, re-plan only those. Gate.
3. **Verify.** Run the spec's `verify` commands; map each `must` line to its evidence (test name,
   output, diff). Report: done / not done per line, with the evidence. Gate.
4. **Review** — only when the spec says `review: on` or the user asks: hand the `reviewer` agent the
   spec, the diff, and the verify commands; relay its findings. Gate.

Gate = at most three critical questions (with defaults) or "Continue to <next stage>?". Never start the
next stage without the user's permission unless the spec says `gates: auto`. Intermediate plans and
reports stay in chat; save files only when the user asks.
