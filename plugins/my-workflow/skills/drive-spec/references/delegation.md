# Delegation

How drive-spec hands a step to an agent. Who and when: `context.md` § Delegation and § Models.

- **Fresh spawn every time** — never continue an earlier agent. A follow-up goes to a new one whose
  materials name the earlier artifact and the delta: the artifacts are the state, a transcript is
  not, and re-entering one re-sends all of it.
- **Route** — inline when the work is trivial, tightly sequential or is itself the decision; an agent
  for isolation, parallel batches (dispatched in one message) or fresh eyes.
- **Brief** (`my-workflow:spec-<name>` in Claude Code, `spec-<name>` in Copilot): where · what ·
  materials (the `workflow.yaml` path, the facts found, the batch's task ids, the mapped skills that
  serve it by name; the tester: the criteria its batch's tasks serve) · done when (architect: the
  step's "done when" · tester: each check returned, seen failing · implementer: its tasks' checks and
  lint pass · reviewer: the report is returned). Sliced paths, never the whole spec folder. Never your reasoning,
  and never what the agent's definition already gives (its limits, skills, return format).
- **Checks before code** — `spec-tester` writes a batch's acceptance checks before its
  `spec-implementer` starts; never one agent for both. Record each check file's hash
  (`git hash-object`) after the tester and compare after the implementer; changed → redo only the
  affected task with a fresh tester and implementer.
- **Parallel batches** share the working tree; the plan keeps their files disjoint.
- **Fresh eyes** — `spec-reviewer` gets paths and check commands, never the author's reasoning.
