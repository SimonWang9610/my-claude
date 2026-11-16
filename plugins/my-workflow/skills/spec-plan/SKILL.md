---
name: spec-plan
description: >-
  Use this skill when the user wants work broken down before building: "plan this", "break this into
  tasks", "what order do we build this in", "who should build what", or whenever a spec or design is
  ready and code comes next, even if they never say "plan". Produces tasks.md: ordered tasks tied to
  the requirement and unit ids they deliver, their files and checks, batches that can run in
  parallel, and whether to hand batches to agents. Also the plan step of a spec. Not for choosing an
  approach (use my-workflow:spec-design).
argument-hint: "[requirements | path to a workflow.yaml]"
---

# spec-plan

Rules: `conventions.md` and `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (unexpanded → `../../shared/`).
Other paths are relative to this folder.

## Input

Per the spec rules' Spec mode: the spec and, when there is one, the design. The spec's `Open:` or the
design step leaves an approach, structure or contract undecided → take a small one as a stated `D`, or stop and say a
design is needed.

## Steps

1. **Tasks** — in build order, about 8 (more → the design is too coarse, or split the spec). Each:
   what it does · the ids it serves (`AC`, `FN`, `R`, `UNIT`) · its files · the check that proves it ·
   the tasks it depends on. By kind:
   - feature — a batch's acceptance checks come before its code; a new layout → `T-1` is its
     scaffold, a prerequisite of every other task.
   - bug — `T-1` the failing reproduction as a test, then the fix, then the neighbours' checks.
   - improvement — `T-1` the must-not-change checks seen passing and the baseline measured; every
     later task shippable alone with those checks still passing.
   A design rule marked "Enforced by" a lint → a task that encodes it.
2. **Size** — complex: a new contract, concurrency, a security or data-migration path, or no existing
   example to copy; else normal.
3. **Batches** — group tasks whose file sets do not overlap; keep each criterion within one batch.
   Delegate when ≥2 batches are independent, or independent acceptance checks pay off (several
   behavioural criteria); else the session builds it. Per batch: the owner, the model (strong when it
   holds a complex task, else standard), the installed skills its work needs (spec mode: from the
   implement step's `skills`).
4. **Write** — `assets/tasks.md`. Spec mode: `spec-check plan` passes.

## Rules

- Every `AC`, `FN`, `R` and changed `UNIT` is served by a task; one that is not is flagged, never
  dropped.
- A task serves at least one id; work that serves none is out of scope.

## Output

The plan per its template. `Open:` ids no task serves, undecided points.
