---
name: spec-plan
description: >-
  Use this skill when work must be broken down before building: "plan this", "break this into
  tasks", "what order", "who builds what", or when a spec or design is ready and code comes next,
  even if they never say "plan". Writes ordered tasks, each a working slice tied to the
  criteria it proves and the files it touches. Not for choosing an approach (use my-workflow:spec-design).
argument-hint: "[requirements | path to a workflow.yaml]"
---

# spec-plan

Rules: `conventions.md`, `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (else `../../shared/`), read
once per conversation. Mode per the spec rules. Other paths: this folder.
Input: the spec and the design. An approach still open → a small stated `D`, or say a design is
needed.

## Steps

1. **Tasks** — vertical slices in build order, about 8: each makes at least one criterion's evidence
   pass and leaves the project working. Per task: what · the ids served (`AC`, `R`, `UNIT`) ·
   files, tests included · depends on.
   - feature — a new layout → `T-1` scaffolds it.
   - bug — `T-1` the failing reproduction as a test, then the fix, then the neighbours.
   - improvement — `T-1` the invariants passing and the baseline measured; each later task
     shippable alone.
   - a design rule a lint enforces → a task that encodes it.
2. **Write** — `assets/tasks.md`. Spec mode: `spec-check plan`.

## Rules

- A task serves at least one id; an id no task serves is flagged, never dropped.
