---
name: pick-react-workflow
description: >
  Binds an sflow workflow template (feature | brownfield | bugfix | quickfix) to the React
  profile: resolves each phase's capability roles to concrete oac-* skills, resolves conditional
  roles against the actual spec/project (design links, legacy port, Jira tracking), attaches the
  React stage notes, and returns the bound workflow the driver agent orchestrates from.
  Usage: /pick-react-workflow <variant> [spec-dir]. Run BEFORE /sf-init when starting a spec — it
  returns the bound workflow for /sf-init to write; pass a spec-dir only to RE-BIND an existing
  spec whose workflow.yaml still carries unbound roles.
---

# pick-react-workflow

Convert a workflow template into the **bound** phase machine for a React spec. Pure binder — it
scaffolds nothing; `/sf-init` owns the spec dir. Two modes:

- **Fresh bind** (default — no spec dir exists yet): `/pick-react-workflow <variant>` — return
  the bound workflow to the caller, who passes it to `/sf-init`.
- **Re-bind**: `/pick-react-workflow <variant> <spec-dir>` — the spec's `workflow.yaml` exists
  but still carries unbound `roles:`; rewrite it in place.

`<variant>` is `feature` | `brownfield` | `bugfix` | `quickfix`.

## Procedure

### Step 1 — Locate the template

- **Re-bind mode** — the template is the existing `<spec-dir>/workflow.yaml`.
- **Fresh mode** — the bundle's template for `<variant>`, located **relative to this skill**:
  from this skill's own directory (`skills/pick-react-workflow/`, resolve its real path first
  since it is symlinked into `.claude/`), the template is `../../sflow/workflows/<variant>.yaml`.
  Never read templates from the project's own `.specflow/` tree — that belongs to the project's
  tooling.

Never invent phases: bind exactly what the template declares.

### Step 2 — Resolve conditional roles (`"role?"`)

Check each trigger against the actual spec/project and **decide now** where possible:

| Conditional role | Keep when | Drop when |
|---|---|---|
| `design-decompose?` | the caller reports design links (or `.meta.yaml` records them, when re-binding) | no design links |
| `resource-scan?` | legacy/cross-stack port, or a large existing subsystem to audit | greenfield, small scope |
| `tracker-sync?` | the project tracks issues in Jira (playbook present) | no tracker |
| `tracker-align?` | the spec is JIRA-tracked | not tracked |
| `journey-tests?` | E2E coverage is wanted (keep with its approval condition) | project has no E2E layer |
| `architecture-design?` (quickfix validate) | keep with its condition — decidable only after implement | — |

A trigger that can't be decided yet stays in the output with its condition attached.

### Step 3 — Bind roles to skills

| Role | React binding |
|---|---|
| acceptance-criteria | `/oac-acceptance-criteria` |
| architecture-design | `/oac-architecture-design` |
| task-design | `/oac-task-design` |
| implementation | `/oac-implementation` |
| test-contract | `/oac-test-contract` |
| qa-report | `/oac-qa-report` |
| test-forensics | `/oac-test-forensics` |
| journey-tests | `/oac-journey-tests` — only if E2E coverage is wanted; the journey plan needs human approval |
| design-decompose | `/oac-figma-decompose` |
| resource-scan | `/scan-resource` — parallel subagents, one per legacy folder |
| tracker-sync | the `_oac-jira-status-automation` playbook (not a skill — follow the file) |
| tracker-align | `/jira-ac-align` — confirm-first before any ticket edit |

### Step 4 — Attach the React stage notes

Add a `notes:` line to these phases (verbatim):

- **preflight** (brownfield): `impact analysis — map the shared-component adoption table (ADOPTED units + external importers); never plan a modification to an adopted shared component without explicit approval`
- **implement**: `run only the changed tests + lint changed files, never the full suite; adopted shared components are read-only (copy, never modify); stop for the human code check before validate/qa`
- **qa**: `run eslint + vitest run exactly once — a single, non-parallel run; no duplicate runs, no extra coverage/type-check passes`
- **validate**: `static only, runs no tests or build; blocking: modified adopted shared component, PR closing keyword, incomplete required phase`

### Step 5 — Emit the bound workflow

Rewrite each phase's `roles:` as `skills:` (bound entries; an undecided conditional keeps its
condition in parentheses), keep every other field (`id`, `command`, `inputs`, `outputs`, `gate`,
`required`, `exit`, top-level `escalate`) untouched, and add `bound: react` at the top level.
**Fresh mode**: return the full bound YAML to the caller — do not write any file. **Re-bind
mode**: overwrite `<spec-dir>/workflow.yaml`. Example phase after binding:

```yaml
  - id: qa
    command: /sf-qa
    skills: ["/oac-qa-report", "/oac-test-forensics", "/oac-test-contract",
             "/oac-journey-tests (only if E2E coverage wanted; plan needs human approval)"]
    inputs: [requirements.md, design.md, tasks.md]
    outputs: [qa-report.md]
    gate: human
    required: true
    exit: enters only after validate PASS; build + suite green; findings dispositioned by the reviewer (sign-off)
    notes: run eslint + vitest run exactly once — a single, non-parallel run; no duplicate runs, no extra coverage/type-check passes
```

### Step 6 — Report

Return to the caller: the bound workflow (fresh mode) or the rewritten file path (re-bind mode),
which conditional roles were kept/dropped and why, and any role left undecided.
