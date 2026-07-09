---
description: Report the spec's phase status and artifacts.
---
# sf:status

Report spec progress, phase status, and blocking required phases.

---

**Purpose.** Give an at-a-glance picture of where every spec sits and what is gating completion. Observability only — this command changes nothing.

## Spec Artifacts

Read-only and cross-spec: read every spec's artifacts under `.specflow/specs/*/`; write nothing.
- **Required:** one or more spec directories under `.specflow/specs/`; each spec's generated `workflow.yaml` (phase-order cross-reference — a spec with only `.meta.yaml` is awaiting `/sf-react-workflow`; report it as such).
- **Optional:** each spec's `tasks.md`, `.meta.yaml`.
- **Additional:** —

## Gate / exit

None (read-only). Complete when every spec's phase status and blocking required phases are surfaced.

## Report

For every spec:

1. **Name + workflow.**
2. **Current phase + status.**
3. **Task progress** — including any `pending` test tasks or an open `TASK-TD`, so missing coverage is visible.
4. **Blocked / failed phases.**
5. **Blocking phases** — any phase in `phase_status` not yet `completed`, or `skipped` with a recorded reason (the spec can't complete until every phase ends in one of those two states).
