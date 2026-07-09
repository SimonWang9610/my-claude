---
name: sf-react-workflow
description: >
  React-only generator for the spec's workflow.yaml, from the project-hosted specflow workflow
  template (feature | brownfield | bugfix | quickfix): maps each template phase to its /sf-*
  command, binds React `oac-*` skills DIRECTLY to phases (references/phase-map.md), resolves
  conditional bindings against the actual spec/project (design links, legacy port, E2E coverage),
  verifies against the spec's .meta.yaml, and WRITES workflow.yaml into the spec dir.
  Usage: /sf-react-workflow <variant> [spec-dir]. Run AFTER /sf-init (which owns the spec dir
  and .meta.yaml) and before the driver's Drive Loop.
argument-hint: "<variant> [spec-dir]"
---

# sf-react-workflow

Convert the project's specflow workflow template into the spec's generated `workflow.yaml` and
write it. This generator is **React-only** — it binds `oac-*` skills directly to phases; another
stack would use its own parallel `*-<tech>-workflow` generator. `/sf-init` owns the spec dir and
`.meta.yaml`; this skill is the sole writer of `workflow.yaml`.

`<variant>` is `feature` | `brownfield` | `bugfix` | `quickfix`. (A specflow-managed project uses
`/spec-react-workflow` instead.)

**Target spec** — the spec being planned under `.specflow/specs/` (just scaffolded by `/sf-init`:
`.meta.yaml` present, no `workflow.yaml` yet); pass `[spec-dir]` to target one explicitly, else
ask if ambiguous. Spec dir missing → tell the caller to run `/sf-init` first. Re-running against
an existing `workflow.yaml` (e.g. escalating to a larger variant) overwrites it.

## Procedure

### Step 1 — Locate the template

The bundle ships no templates. Read the project-hosted specflow template for `<variant>`, in
this order:

1. `specflow/src/workflows/<variant>.yaml` — the specflow repo vendored in the target project.
2. `.specflow/workflows/<variant>.yaml` — project override.

Neither found → STOP and report that the project must vendor specflow, or ask the user for the
template path. `brownfield`/`bugfix`/`quickfix` are deprecated upstream — WARN but allow.

Never invent phases: generate exactly what the template declares, ids verbatim (`spec-qa`
stays `spec-qa`). Per phase the template carries `id`, `approval` (`human|auto|skip`),
`required`, `inputs`, `outputs` — plus `generator`/`executor` hints, `validators`, and `hooks`,
which this skill ignores.

### Step 2 — Map phases to commands and skills

Read `references/phase-map.md` (under this skill's own dir) for each phase's React `oac-*` skill
bindings and its `exitWhen` line. Command mapping to the `/sf-*` set:

| Template phase     | Command                                |
| ------------------ | -------------------------------------- |
| preflight          | `/sf-preflight`                        |
| requirements       | `/sf-requirements`                     |
| clarify            | `/sf-clarify`                          |
| design             | `/sf-design`                           |
| tasks              | `/sf-tasks`                            |
| implement          | `/sf-implement`                        |
| spec-qa            | `/sf-qa`                               |
| analysis, describe | _(none — driver-led; omit `command:`)_ |

`taskstoissues` is dropped from the React flow — if a vendored template still declares it, emit
`skills: []`, `gate: auto`, `exitWhen: taskstoissues unused — record skipped in .meta.yaml`.

**The flow's validate command is `/sf-validate`** — it gates `spec-qa`'s `exitWhen` and is
never a phase. `/sf-drift` is an optional post-merge follow-up, also never a phase.

### Step 3 — Resolve conditional bindings (`?`)

Each `?`-marked skill in the phase map is conditional. Check its trigger against the actual
spec/project and **decide now** where possible — keep or drop per the decision table in
`references/phase-map.md` (design links, legacy/port scan, E2E coverage). A
trigger that can't be decided yet stays in the output with its condition attached.

### Step 4 — Emit the generated schema

Emit exactly this shape — nothing else:

```yaml
workflow: feature | brownfield | bugfix | quickfix # MUST match .meta.yaml `workflow:`
description: <workflow-description>
phases:
  - id: <phase-id> # MUST match the .meta.yaml phase_status keys
    command: <phase-command>
    inputs:
      - <input-name>
    outputs:
      - <output-name>
    skills:
      - <skill-name>
    gate: human | auto
    exitWhen: <exit-condition>
```

Emission rules:

- `id`, `inputs`, `outputs` — verbatim from the template.
- `command` — per the Step 2 mapping; absent for driver-led phases.
- `skills` — the phase map's bindings for that phase; an undecided conditional keeps its
  condition in parentheses.
- `gate` — `approval: human` → `human`; `auto`/`skip` → `auto`; `implement` is always `human`
  (the bundle's post-implement code check).
- `exitWhen` — the phase map's `exitWhen` line for that phase (one line).
- **Drop** everything else — `required`, `validators`, `hooks`, `generator`/`executor`. Global
  disciplines live in the driver's Hard Rules; escalation lives in the driver's Drive Loop.

Example phase after generation (feature):

```yaml
workflow: feature
description: specflow feature lifecycle driven via the /sf-* command set
phases:
  # …
  - id: spec-qa
    command: /sf-qa
    skills:
      [
        "/oac-qa-report",
        "/oac-test-forensics",
        "/oac-journey-tests (only if E2E coverage wanted; requires the approved journey plan)",
      ]
    inputs: [requirements.md, design.md, tasks.md]
    outputs: [qa-report.md]
    gate: human
    exitWhen: enters only after /sf-validate PASSES (static checks, reported in chat — never a ledger phase); suite green via a single eslint + vitest run; findings dispositioned by the reviewer (sign-off)
```

### Step 5 — Verify against `.meta.yaml`, then write

Read the spec's `.meta.yaml` (created by `/sf-init`): the generated `workflow:` MUST equal its
`workflow:`, and the generated phase ids MUST exactly match its `phase_status` keys, in order.
Mismatch → STOP and report (wrong variant, or a stale `.meta.yaml` — re-run `/sf-init`).
Then write the generated YAML to `.specflow/specs/<name>/workflow.yaml`.
