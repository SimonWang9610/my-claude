---
description: Scaffold a new spec directory and .meta.yaml phase status for the chosen workflow.
---
# sf:init

Scaffold the spec directory and `.meta.yaml` phase ledger for the chosen workflow variant.

---

**Purpose.** Stand up the spec folder and the phase ledger so every later stage has a known home and a status to advance. This is the entry point — it runs at the driver's Setup, BEFORE `/sf-react-workflow` (which later writes the spec's `workflow.yaml`); no requirements, code, or tests exist yet.

## Spec Artifacts

Create the spec's artifact directory `.specflow/specs/<feature-name>/` and write `.meta.yaml` there — nothing else (no `workflow.yaml`; `/sf-react-workflow` writes that later). Every later command reads and writes its artifacts in this directory.
- **Required:** a feature description and the workflow variant (`feature | brownfield | bugfix | quickfix`) — both supplied by the caller.
- **Optional:** `design_links` (a list of design source URLs) in `.meta.yaml` when the feature is UI-related.
- **Additional:** steering `.specflow/steering/*`.

## Gate / exit

Exits when `.meta.yaml` exists with a `phase_status` map listing every phase read from the variant's project-hosted workflow template (never hardcoded) as `pending`, and `current_phase` set to the first phase.

## `.meta.yaml` shape

```yaml
# Example — a `feature` spec just scaffolded. The phase list below is illustrative for the
# feature workflow; the real list ALWAYS comes from the variant's template (Step 3).
name: <feature-name>
workflow: feature
created_at: <ISO 8601 timestamp>
updated_at: <ISO 8601 timestamp>
current_phase: preflight     # the first phase in the template
phase_status:                # one entry per phase in the template, all pending at init
  preflight: pending
  requirements: pending
  clarify: pending
  design: pending
  tasks: pending
  taskstoissues: pending
  implement: pending
  spec-qa: pending
design_links: []             # present only for UI work (captured at Step 1)
checksums: {}                # reserved for the project's tooling
```

`phase_status` carries only the status; a phase's `command`, `gate`, and `exitWhen` live in the
generated `workflow.yaml` (one source of truth — never copy them here). Phase status values are
`pending | in_progress | completed | skipped | failed`; later commands update a phase's value to
`completed` / `skipped` and advance `current_phase`.

## Steps

1. **Capture design links (if UI)** — If the feature/fix involves UI (a new or changed screen, unit, or visual surface), ask the user for any related design source links and record them. If it's not UI-related, or the user has none, skip — the field stays absent.
2. **Scaffold the spec dir** — create `.specflow/specs/<feature-name>/`; this command is the sole writer of it.
3. **Read the phase list** — locate the variant's project-hosted specflow template: `specflow/src/workflows/<variant>.yaml` (the vendored specflow repo), else `.specflow/workflows/<variant>.yaml` (project override); neither found → STOP and report that the project must vendor specflow, or ask the user for the template path. Extract each phase `id` from its `phases`, in order; never hardcode them (`init` is not among them — this command is the scaffold step).
4. **Write `.meta.yaml`** — per the shape above: `name`, `workflow` (the chosen variant), `created_at`/`updated_at`, `current_phase` (the first phase), `phase_status` (every phase `pending`), `design_links` (when captured above), `checksums: {}`.
5. **Report** — what was created + the next step: `/sf-react-workflow <variant>` writes the spec's `workflow.yaml`.
