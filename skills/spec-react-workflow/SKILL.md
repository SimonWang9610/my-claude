---
name: spec-react-workflow
description: >
  React-only generator for a specflow-managed spec's workflow.yaml (company specflow toolchain,
  /spec-* commands): reads the variant from the existing .meta.yaml, reads the project-hosted
  specflow workflow template, maps each phase to its /spec-<id> command, binds React `oac-*`
  skills DIRECTLY to phases (references/phase-map.md), and WRITES workflow.yaml into the existing
  spec dir (owned by the project's /spec-init; the project's .meta.yaml is never touched).
  Usage: /spec-react-workflow <variant> [spec-dir]. variant defaults to the .meta.yaml
  `workflow:` (feature recommended — the others are deprecated in specflow).
argument-hint: "<variant> [spec-dir]"
---

# spec-react-workflow

Convert the project's specflow workflow template into the spec's generated `workflow.yaml` and
write it. This generator is **React-only** — it binds `oac-*` skills directly to phases; another
stack would use its own parallel `*-<tech>-workflow` generator. The spec dir and `.meta.yaml`
are owned by the project's `/spec-init` — this skill writes ONLY `<spec-dir>/workflow.yaml`,
never creates the dir, never touches `.meta.yaml`. The drive rules and contract facts live in
`references/specflow-contract.md`.

**Target spec** — the spec being planned under `.specflow/specs/` (pass `[spec-dir]` to target
one explicitly, else ask if ambiguous). Spec dir **missing** → tell the caller to run the
project's `/spec-init` first; write nothing. Spec dir exists → write (or overwrite)
`<spec-dir>/workflow.yaml`.

## Procedure

### Step 1 — Resolve the variant

Read `workflow:` from the spec's existing `.meta.yaml`; default `feature`. The other specflow
variants (`brownfield`/`bugfix`/`quickfix`) are **deprecated** — WARN but allow.

### Step 2 — Locate the template

The bundle ships no templates. Read the project-hosted specflow template for the variant at:`specflow/src/workflows/<variant>.yaml` — the specflow repo vendored in the target project.

Neither found → STOP and report that the project must vendor specflow, or ask the user for the
template path.

Never invent phases: generate exactly what the template declares, ids verbatim (`spec-qa`
stays `spec-qa`) — the phase ids ARE the company `.meta.yaml` `phase_status` keys. Per phase
the template carries `id`, `approval` (`human|auto|skip`), `required`, `inputs`, `outputs` —
plus `generator`/`executor` hints, `validators`, and `hooks`, which this skill ignores.

### Step 3 — Map phases to commands and skills

Read `references/phase-map.md` (under this skill's own dir) for each phase's React `oac-*` skill
bindings and its `exitWhen` line. Command mapping: every phase's command is the project's
**`/spec-<id>`** (`preflight` → `/spec-preflight`, …, `spec-qa` → `/spec-qa`). Driver-led template
phases without a project command (`analysis`, `describe` on the deprecated variants) omit `command:`.
`taskstoissues` is dropped from the React flow — if a vendored template still declares it, emit
`skills: []`, `gate: auto`, `exitWhen: taskstoissues unused — record skipped in .meta.yaml`.

**The flow's validate command is `/spec-validate`** — it gates `spec-qa`'s `exitWhen` (run it,
report results in chat) and is never a phase; NO extra phases are ever injected — phase ids
must exactly match the company `.meta.yaml`. `/spec-drift` is an optional post-merge
follow-up, also never a phase.

### Step 4 — Resolve conditional bindings (`?`)

Each `?`-marked skill in the phase map is conditional. Check its trigger against the actual
spec/project and **decide now** where possible — keep or drop per the decision table in
`references/phase-map.md` (design links, legacy/port scan, E2E coverage). A
trigger that can't be decided yet stays in the output with its condition attached.

### Step 5 — Emit the generated schema

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
- `command` — `/spec-<id>`; absent for driver-led phases.
- `skills` — the phase map's bindings for that phase; an undecided conditional keeps its
  condition in parentheses.
- `gate` — `approval: human` → `human`; `auto`/`skip` → `auto`; `implement` is always `human`
  (the bundle's post-implement code check, additive discipline on top of the project's auto
  approval).
- `exitWhen` — the phase map's `exitWhen` line for that phase; append the specflow conventions
  the phase must honor (see `references/specflow-contract.md` — e.g. requirements: EARS FRs,
  `AC-<story>.<n>`; tasks: test tasks ordered before impl tasks; implement: every task Status →
  `completed`, `test-manifest.md` written), `;`-separated, one line.
- **Artifact completeness** — `outputs` are the artifacts that MUST exist (non-empty) before a phase advances; when an output is a collection (e.g. `contracts/`), fold the per-item rule into `exitWhen` (one `contracts/<unit>.md` per unit named in `design.md`) so the driver's verify catches a missing one.

Example phase after generation (feature):

```yaml
workflow: feature
description: specflow feature lifecycle driven via the project's /spec-* commands
phases:
  # …
  - id: spec-qa
    command: /spec-qa
    skills:
      [
        "/oac-qa-report",
        "/oac-test-forensics",
        "/oac-journey-tests (only if E2E coverage wanted; requires the approved journey plan)",
      ]
    inputs: [requirements.md, design.md, tasks.md, test-manifest.md]
    outputs: [qa-report.md]
    gate: human
    exitWhen: enters only after /spec-validate PASSES (static checks, reported in chat — never a ledger phase); suite green via a single eslint + vitest run; findings dispositioned by the reviewer (sign-off)
```

### Step 6 — Verify against `.meta.yaml`, then write

The generated `workflow:` MUST equal the `.meta.yaml` `workflow:`, and the generated phase ids
MUST exactly match its `phase_status` keys, in order. Mismatch → STOP and report (wrong
template, or the project's `/spec-init` scaffolded a different variant). Then write the
generated YAML to `<spec-dir>/workflow.yaml` — and nothing else.
