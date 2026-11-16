# Delegation

- **A fresh agent every time**; a follow-up names the earlier artifact and the delta. Parallel
  batches go out in one message.
- **Brief** (`my-workflow:spec-<name>`; Copilot: `spec-<name>`): where · what · materials (the
  `workflow.yaml` path, facts found, task ids, the skills to use; sliced paths) · done when (tester:
  checks returned, seen failing · implementer: its checks and lint pass · reviewer: the report).
  Never your reasoning, nor what the agent's definition already says.
- **Checks before code** — the tester writes a batch's checks before its implementer starts. Record
  each check file's `git hash-object`; changed after the implementer → redo that task with fresh
  agents.
- Batches share the working tree; their files do not overlap.
