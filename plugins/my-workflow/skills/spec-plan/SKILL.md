---
name: spec-plan
description: >-
  Use this skill when work must be broken down before building: "plan this", "break this into
  tasks", "what order", "who builds what", or when a spec or design is ready and code comes next,
  even if they never say "plan". Writes ordered tasks, each tied to the criteria it proves and the
  files it touches, and groups the criteria and tasks into batches for the agents that test and
  build them. Not for choosing an approach (use my-workflow:spec-design).
argument-hint: "[requirements | path to a workflow.yaml]"
---

# spec-plan

Rules: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (else `../../shared/`) and
`../drive-spec/references/spec-rules.md`, read once per conversation. Mode per the spec rules. Other
paths: this folder.
Input: the spec and the design. An approach still open → a small stated `D`, or say a design is
needed.

## Steps

1. **Tasks** — vertical slices in build order, about 8: each slice makes at least one criterion's
   evidence pass and leaves the project working. A slice inside one domain
   (`domains.md`, beside the conventions) is one task; one that crosses domains, such as a UI app
   and its backend service, is a task per domain, the provider first: the provider serves its `UNIT` and
   is checked by its own tests, and the `AC` sits on the task that completes the slice. Per task: what · the ids served
   (`AC`, `R`, `UNIT`) · files, tests included · depends on.
   - feature — a new layout → `T-1` scaffolds it.
   - bug — the fix, serving `AC-1` and the neighbours it could break.
   - improvement — each task shippable alone, the invariants passing after it.
   - a design rule a lint enforces → a task that encodes it.
   - never a task that only writes tests: the test step writes them, else the implementer does,
     first in each task.
2. **Batches** — one new agent works each batch, so size a batch to what one agent can hold: one
   domain, work that belongs together, in order.
   - implement — consecutive tasks on the same units or depending on each other, about 3. Every
     task sits in exactly one.
   - test — only when the test step will run (standard size, a test suite): every criterion a test
     could reach, grouped by story, else by the surface they share, about 5. Each sits in exactly
     one; the tester reports any it cannot reach.
   - per batch: its domain with the tools the work touches (`<domain> · <tools>`), what it holds,
     the batches of its step it must come after.
3. **Write** — `assets/tasks.md`. Spec mode: `spec-check plan`.

## Rules

- A task serves at least one id; an id no task serves is flagged, never dropped.
- Split a batch before it mixes domains or passes its size; never split a task.
