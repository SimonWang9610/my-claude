---
name: oac-workflow
description: >
  Generate workflow.yaml for an OAC specflow spec: maps each specflow phase to its /spec-<id>
  command with a prompt that invokes the OAC React skills (build-acceptance-criteria,
  design-react-architecture, plan-react-tasks, implement-react-code), and writes
  <spec-dir>/workflow.yaml. Usage: /oac-workflow $SPEC_DIR.
argument-hint: $SPEC_DIR
---

# oac-workflow

Generate a `workflow.yaml` under the specflow `$SPEC_DIR` — a YAML representation of the phases:
commands, prompts, inputs, outputs, gates, exit conditions. Skills are invoked through each
phase's `prompt` (the extra prompt appended to the command), not a separate field. The spec dir
and `.meta.yaml` are owned by `/spec-init`: this skill writes **only** `$SPEC_DIR/workflow.yaml`.

## Instructions

1. **Collect required phases** — Read `$SPEC_DIR/.meta.yaml` for the `workflow:` variant and the
   `phase_status` keys. `.meta.yaml` missing → **STOP**, ask the user to run `/spec-init` first.
   A variant other than `feature` is deprecated — warn but allow.
2. **Emit one entry per phase** from the [Phase Mapping](#phase-mapping) below, in
   `phase_status` order — ids verbatim (they ARE the `phase_status` keys); never invent or
   inject a phase.
3. **Verify, then write** — the generated `workflow:` equals `.meta.yaml`'s and the phase ids
   match its `phase_status` keys in order; mismatch → STOP and report. Every phase's `outputs`
   must exist non-empty before the driver advances past it. Write `$SPEC_DIR/workflow.yaml` —
   nothing else.

### Workflow Template

```yaml
workflow: <workflow> # copy from .meta.yaml
phases:
  - id: <phase-id> # MUST match the .meta.yaml phase_status keys
    command: /spec-<id>
    prompt: <extra prompt appended when invoking the command: `/spec-<id> <prompt>`> # optional
    inputs: [<input1>]
    outputs: [<output1>]
    gate: <human | auto>
    exitWhen: <exit-condition>
```

## Phase Mapping

> ? for optional

1. **preflight**
   - command: `/spec-preflight`
   - prompt: use `/scan-resource` if relevant references or resources are given; use
     `/oac-figma-decompose` if design links are provided
   - inputs: none · outputs: `preflight.md` · gate: human
   - exitWhen: preflight.md records the reuse verdict and shared-unit impact

2. **analysis**
   - command: `/oac-analyze`
   - inputs: none · outputs: `analysis.md` · gate: human
   - exitWhen: bugfix: named, deterministic, FAILING reproduction test asserts the bug's AC;
     brownfield: change surface + shared-unit impact mapped in analysis.md

3. **requirements**
   - command: `/spec-requirements`
   - prompt: run `/build-acceptance-criteria` to author requirements.md (Glossary, EARS FRs,
     US/AC/NFR with stable IDs in observable Given/When/Then form); never guess past an open
     question — record it under `## Open questions`
   - inputs: `preflight.md`, ?`references/*` · outputs: `requirements.md` · gate: human
   - exitWhen: Glossary + EARS FRs present; every US/AC/NFR carries a stable unique ID in
     observable Given/When/Then form

4. **clarify**
   - command: `/spec-clarify`
   - prompt: settle the open questions in `requirements.md`, ranked
     by Impact × Uncertainty, each with a recommended answer
   - inputs: `requirements.md`, ?`references/*`? · outputs: `clarify.md` · gate: human
   - exitWhen: top ambiguities resolved; every untestable AC rephrased to observable form or
     recorded under `## Open questions`

5. **design**
   - command: `/spec-design`
   - prompt: run `/design-react-architecture` to produce design.md + contracts/ (including the
     AC → Verification table); challenge the draft (checks C1–C8) with fresh eyes — a subagent
     given only the draft tables and contracts;
   - inputs: `requirements.md`, ?`clarify.md`, ?`references/*` · outputs: `design.md`, `contracts/` · gate: human
   - exitWhen: one `contracts/<unit>.md` per MODIFY/NEW unit in the index; every AC/NFR has an
     AC → Verification row; C1–C8 hand-off criteria met (no open CRITICAL; HIGH passed or
     justified; MEDIUM passed or debt-recorded)

6. **tasks**
   - command: `/spec-tasks`
   - prompt: run `/plan-react-tasks` to produce tasks.md + the parallel-wave plan — transcribe
     from the design (dependencies from the unit index, test plan from AC → Verification), never
     re-derive
   - inputs: `design.md`, `contracts/` · outputs: `tasks.md` · gate: auto
   - exitWhen: count check holds (MODIFY/NEW units + AC → Verification rows + edge cases); every
     task carries the four fields; parallel-wave plan present; test tasks ordered before impl tasks

7. **implement**
   - command: `/spec-implement`
   - inputs: `tasks.md`, `contracts/`, ?`references/*` · outputs: code, `test-manifest.md` · gate: human
   - exitWhen: every task Status → completed with its Gate passing; no test edited to make code
     pass; design gaps resolved or human-dispositioned; test-manifest.md written

8. **spec-qa**
   - command: `/spec-qa`
   - prompt: run `/spec-validate` first and report its results in chat (a check, not a phase);
     if E2E coverage is wanted, author the journey tests with `/build-react-e2e` before the audit
     (it consumes the approved `qa-journey-plan.md` when present, otherwise generates one and
     stops for approval); then produce qa-report.md and save it at `<spec-dir>/qa-report.md`;
   - inputs: `requirements.md`, `design.md`, `tasks.md`, ?`test-manifest.md`, code diff · outputs:
     `qa-report.md` · gate: human
   - exitWhen: `/spec-validate` PASSES; findings dispositioned by the reviewer (sign-off); suite
     green via a single eslint + vitest run
