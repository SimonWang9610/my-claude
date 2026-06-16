---
description: Scaffold a new spec directory and .meta.yaml phase status for the chosen workflow.
---
# spec:init

Scaffold a new spec directory and `.meta.yaml` phase status from the selected workflow.

---

**Purpose.** Stand up the spec folder and the phase ledger so every later stage has a known home and a status to advance. This is the entry point — no requirements, code, or tests exist yet.

## Spec Artifacts

Create the spec's artifact directory `.specflow/specs/<feature-name>/` and write `.meta.yaml` there; every later command reads and writes its artifacts in this directory.
- **Required:** a feature description (from the caller); the chosen workflow YAML `specflow/src/workflows/<workflow>.yaml` — source of the phase IDs.
- **Optional:** `design_links` (a list of design source URLs) in `.meta.yaml` when the feature is UI-related.
- **Additional:** steering `.specflow/steering/*`.

## Gate / exit

Exits when `.meta.yaml` exists, lists every phase ID read from the workflow YAML (never hardcoded), sets `current_phase` to the first phase, and marks every phase `pending`.

## Steps

1. **Pick the workflow** — gauge complexity; suggest `feature` / `quickfix` / `bugfix` / `brownfield`.
2. **Capture design links (if UI)** — If the feature/fix involves UI (a new or changed screen, unit, or visual surface), ask the user for any related design source links and record them. If it's not UI-related, or the user has none, skip — the field stays absent.
3. **Scaffold the spec dir** — create `.specflow/specs/<feature-name>/`; scaffold only what the workflow declares.
4. **Read the phase list** — extract phase IDs from the workflow YAML's `phases`; never hardcode them.
5. **Write `.meta.yaml`** — `name`, `workflow`, `created_at`/`updated_at`, `current_phase` (first phase), `phase_status` (every phase `pending`), `checksums: {}`; and `design_links` (a list of design source URLs) when captured above.
6. **Report** — what was created + suggested next steps.
