---
name: spec-plan
description: >-
  Use this skill when work must be broken down before building: "plan this", "break this into
  tasks", "what order", "who builds what", or when a spec or design is ready and code comes next,
  even if they never say "plan". Writes ordered tasks tied to the ids they deliver, with files,
  checks and parallel batches. Not for choosing an approach (use my-workflow:spec-design).
argument-hint: "[requirements | path to a workflow.yaml]"
---

# spec-plan

Rules: `conventions.md` and `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (unexpanded →
`../../shared/`); already loaded in this conversation → do not read them again. Mode per the spec rules. Other paths are relative to this folder.
Input: the spec and the design. An approach still open → a small stated `D`, or say a design is
needed.

## Steps

1. **Tasks** — in build order, about 8: what · the ids served (`AC`, `FN`, `R`, `UNIT`) · files ·
   check · depends on.
   - feature — a batch's acceptance checks before its code; a new layout → `T-1` scaffolds it.
   - bug — `T-1` the failing reproduction as a test, then the fix, then the neighbours.
   - improvement — `T-1` the invariants passing and the baseline measured; each later task
     shippable alone.
   - a design rule a lint enforces → a task that encodes it.
2. **Size** — complex: a new contract, concurrency, security, a data migration, or nothing to copy.
3. **Batches** — tasks whose files do not overlap; a criterion stays in one batch. Delegate when ≥2
   are independent or separate acceptance checks pay off. Per batch: owner, model (strong when
   complex), the skills it needs.
4. **Write** — `assets/tasks.md`. Spec mode: `spec-check plan`.

## Rules

- A task serves at least one id; an id no task serves is flagged, never dropped.
