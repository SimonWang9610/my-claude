---
name: oac-workflow
description: >
  Generate workflow.yaml for an OAC specflow spec: for each phase, emit the skills it invokes (the
  /spec-<id> command included as the first skill) and a self-contained prompt that weaves those
  skills — binding the OAC React skills (build-acceptance-criteria, design-react-architecture,
  plan-react-tasks, implement-react-code) — then writes <spec-dir>/workflow.yaml.
  Usage: /oac-workflow $SPEC_DIR.
argument-hint: $SPEC_DIR
---

# oac-workflow

Generate a `workflow.yaml` under the specflow `$SPEC_DIR` — a YAML representation of each phase: the
`skills` it invokes, a self-contained `prompt`, `inputs`, `outputs`, `gate`, and `exitWhen`. There
is **no** `command` field — a phase's specflow command (`/spec-preflight`, …) is just the first
entry in its `skills`, woven verbatim into the `prompt`; the driver runs the `prompt` directly. Each
phase is defined in [`references/<id>.md`](references/); this skill assembles them and writes
**only** `$SPEC_DIR/workflow.yaml` (the spec dir and `.meta.yaml` are owned by `/spec-init`).

## Instructions

1. **Collect required phases** — Read `$SPEC_DIR/.meta.yaml` for the `workflow:` variant and the
   `phase_status` keys. `.meta.yaml` missing → **STOP**, ask the user to run `/spec-init` first.
   A variant other than `feature` is deprecated — warn but allow.
2. **Emit one entry per phase** — phase ids and order come from `.meta.yaml`'s `phase_status` (they
   ARE its keys); never invent, reorder, or drop a phase. For each id, read `references/<id>.md` and
   build its entry per [Building a phase entry](#building-a-phase-entry).
3. **Verify, then write** — the generated `workflow:` equals `.meta.yaml`'s and the phase ids match
   its `phase_status` keys in order; every entry carries a resolved `skills` list, a `prompt` that
   explicitly invokes each of those skills by its exact slash name, `inputs`, `outputs`, `gate`, and
   `exitWhen`; mismatch → STOP and report. Write `$SPEC_DIR/workflow.yaml` — nothing else.

## Workflow Template

```yaml
workflow: <workflow> # copy from .meta.yaml
phases:
  - id: <phase-id> # MUST match a .meta.yaml phase_status key, in order
    skills: [<skill>, ...] # every skill the phase invokes, verbatim; the /spec-* command is first
    prompt: <text> # self-contained; explicitly invokes each skill above by exact slash name
    inputs: [<input>, ...] # ? marks optional
    outputs: [<output>, ...]
    gate: <human | auto>
    exitWhen: <exit-condition>
```

## Building a phase entry

1. read the phase's `references/<id>.md` for its `skills`, `prompt`, `inputs`, `outputs`, `gate`,
   and `exitWhen`.

2. emit one entry per the [template](#workflow-template), applying:
   - **Prompt rule.** Adapt the sample `prompt`; every applicable skill (post-condition) MUST appear as
     an explicit `run /skill` / `using /skill` invocation — exact slash name, never paraphrased or
     described. Self-contained; restate no skill know-how.
   - **Conditions.** A `skills` entry tagged `# if <cond>` is kept — in `skills` and `prompt` — only
     when `<cond>` holds. Resolve from `.meta.yaml` where knowable (design links → `/oac-figma-decompose`;
     references/legacy → `/scan-resource`; variant → analysis); a runtime-only cond (e.g. E2E wanted)
     stays an annotated `skills` entry + a conditional clause in the prompt.
   - **inputs / outputs** verbatim, `?` = optional; never invent them;
