---
description: Scaffold a new spec directory and .meta.yaml phase status for the chosen workflow.
---
# sf:init

Scaffold a new spec directory and `.meta.yaml` phase status from the selected workflow.

---

**Purpose.** Stand up the spec folder and the phase ledger so every later stage has a known home and a status to advance. This is the entry point — no requirements, code, or tests exist yet.

## Spec Artifacts

Create the spec's artifact directory `.specflow/specs/<feature-name>/` and write `.meta.yaml` plus the `workflow.yaml` there; every later command reads and writes its artifacts in this directory.
- **Required:** a feature description and the `workflow.yaml` to install — both supplied by the caller.
- **Optional:** `design_links` (a list of design source URLs) in `.meta.yaml` when the feature is UI-related.
- **Additional:** steering `.specflow/steering/*`.

## Gate / exit

Exits when `workflow.yaml` is snapshotted into the spec dir and `.meta.yaml` exists with a `phase_status` map listing every phase read from the snapshot (never hardcoded) as `pending`, and `current_phase` set to the first phase.

## `.meta.yaml` shape

```yaml
# Example — a `feature` spec just scaffolded (phases read from the bound workflow.yaml):
name: <feature-name>
workflow: feature
jira_issues: []              # tracker keys; the tracker-sync step fills it — omit if no tracker
created_at: <ISO 8601 timestamp>
updated_at: <ISO 8601 timestamp>
current_phase: preflight     # the first phase in the snapshot
phase_status:                # one entry per phase in workflow.yaml, all pending at init
  preflight: pending
  requirements: pending
  clarify: pending
  design: pending
  tasks: pending
  implement: pending
  validate: pending
  qa: pending
  drift: pending
design_links: []             # present only for UI work (captured at Step 2)
checksums: {}                # reserved for the project's tooling
```

`phase_status` carries only the status; a phase's `gate` and `required` live in the
`workflow.yaml` snapshot (one source of truth — never copy them here). Later commands update a
phase's value to `complete` / `skipped` and advance `current_phase`.

## Steps

1. **Capture design links (if UI)** — If the feature/fix involves UI (a new or changed screen, unit, or visual surface), ask the user for any related design source links and record them. If it's not UI-related, or the user has none, skip — the field stays absent.
2. **Scaffold the spec dir** — create `.specflow/specs/<feature-name>/`; this command is the sole writer of it.
3. **Write `workflow.yaml`** — save the caller's `workflow.yaml` into the spec dir verbatim; every later command reads this file.
4. **Read the phase list** — extract each phase `id` from `workflow.yaml`'s `phases`, in order; never hardcode them (`init` is not among them — this command is the scaffold step).
5. **Write `.meta.yaml`** — per the shape above: `name`, `workflow`, `jira_issues` (when a tracker is used), `created_at`/`updated_at`, `current_phase` (the first phase), `phase_status` (every phase `pending`), `design_links` (when captured above), `checksums: {}`.
6. **Report** — what was created + suggested next steps.
