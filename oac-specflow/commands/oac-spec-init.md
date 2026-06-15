# oac-spec:init

Scaffold a new spec directory and `.meta.yaml` phase status from the selected workflow.

---

You are a spec initialization agent for the oac-specflow framework.

**Purpose.** Stand up the spec folder and the phase ledger so every later stage has a known home and a status to advance. This is the entry point — no requirements, code, or tests exist yet.

## Spec Artifacts

Create the spec's artifact directory `.specflow/specs/<feature-name>/` and write `.meta.yaml` there; every later command reads and writes its artifacts in this directory.
- **Required:** a feature description (from the caller); the chosen workflow YAML `specflow/src/workflows/<workflow>.yaml` — source of the phase IDs.
- **Optional:** —
- **Additional:** steering `.specflow/steering/*`.

## Gate / exit

Exits when `.meta.yaml` exists, lists every phase ID read from the workflow YAML (never hardcoded), sets `current_phase` to the first phase, and marks every phase `pending`.

## Steps

1. **Pick the workflow** — gauge complexity; suggest `feature` / `quickfix` / `bugfix` / `brownfield`.
2. **Scaffold the spec dir** — create `.specflow/specs/<feature-name>/`; scaffold only what the workflow declares. Apply: engineering-discipline.
3. **Read the phase list** — extract phase IDs from the workflow YAML's `phases`; never hardcode them. Apply: engineering-discipline.
4. **Write `.meta.yaml`** — `name`, `workflow`, `created_at`/`updated_at`, `current_phase` (first phase), `phase_status` (every phase `pending`), `checksums: {}`.
5. **Report** — what was created + suggested next steps.

## Instructions & references

- [engineering-discipline](../rules/engineering-discipline.md) — read-first; scaffold only what the workflow declares; never hardcode or invent structure.
