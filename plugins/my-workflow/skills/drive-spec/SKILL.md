---
name: drive-spec
description: >-
  Use this skill whenever the user wants software work done end to end or resumed: "build X", "fix
  X", "improve X", "refactor X", "continue the spec", a pasted ticket with "do it", even if they
  never say "spec". Runs requirements (or a bug diagnosis), design, plan, implementation and review,
  stopping for your approval and backing each requirement with a test or recorded evidence. For one step only, use that
  step's spec-* skill.
argument-hint: "<task | path to a workflow.yaml>"
---

# drive-spec

Rules: `conventions.md`, `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (else `../../shared/`); they
and each `references/` file are read once per conversation. § = a section of `references/context.md`.

Orchestrate one spec: sequence the steps, hand off precisely, verify by a run, know when to stop.
`workflow.yaml` holds the steps; each `spec-*` skill holds how its step is done. You own
`workflow.yaml`, `discussions.md` and `coverage.md`. Done = every step done or skipped.

## Setup

In order; no code exploration yet.

1. **Resume** — a `workflow.yaml` is named, or a spec is in progress → the Loop at `current`.
2. **Kind** — feature (new or changed behaviour) · bug (behaviour is broken) · improvement (behaviour
   stays, a quality improves). Mixed → the main one, the rest a follow-up spec. Not software → answer
   and stop.
3. **Size, folder, branch** — § Size, § Folder and branch.
4. **Initialize** — `workflow.yaml` from `assets/workflow.yaml`, fitted to the kind and size; show
   kind, size and steps in one line.

## Loop

Per step of `workflow.yaml`, strictly in order; never invent or reorder one.

1. **Skip?** — per the table, with a one-line reason.
2. **Run** — its skill yourself, or its agent (§ Delegation, briefed per `references/delegation.md`).
3. **Verify** — yourself: run the step's check. Read an artifact's body only to present a gate. Fails
   twice → stop.
4. **Settle** — put to the user under **Needs you** what the step left for them: open `Q`s with
   their defaults · options to choose between (the design's: log the choice to `discussions.md`,
   rerun the step with the pick) · a conflict with what they said · a workaround, waiver or design
   gap (the spec rules; it pauses only its task). They may also steer. Answers go back through the
   step, then recheck.
5. **Gate** — requirements (a bug: the diagnosis) and design. A compact summary, the artifact's
   path, the check's result, then `Approve, or tell me what to change?`. Any answer but yes →
   revise through the step, recheck, ask again. Never pass a waiting gate or a failing check.
   - Design: the user reviews it; offer a second opinion from `spec-reviewer`, run only on a yes.
   - `gates: auto` (granted in advance): a passing check approves; a design you judge risky →
     `spec-reviewer` decides.
6. **Record** — the step's status and result fields, and what an agent returned but could not write;
   move `current`.

| Step | Skip when | Done when |
|---|---|---|
| requirements | never | `spec-check ids` passes |
| diagnose | never | cause with evidence and confidence; verdict set; `spec-check ids` passes |
| design | nothing is open: approach, structure, unit, contract, screen | `spec-check design` passes |
| plan | never | `spec-check plan` passes |
| implement | never | every task done; `spec-check coverage --run --write` passes |
| review | the user turned it off | the same check passes; verdict accept |

## Stop

- "Not a bug" → skip the remaining steps with that reason.
- A review not accepted twice (once: fix and rerun) · a check that keeps failing · a missing or
  ambiguous input.
- Anything irreversible: commit, push, pull request, delete.

## Rules

- This spec only; note out-of-scope findings.
- A step is skipped only by the table or the user; an artifact changes only through its step.
- Earlier artifacts are authoritative: ground in them; deeper facts through
  `/my-workflow:audit-truth`; one that looks wrong is raised, never silently diverged from.
- One round of questions, one brief, one report; push back with evidence.
- The user asks, challenges or redirects mid-spec → `references/mid-spec.md`.

## Outcome

**Done** <task, kind> · **Coverage** <n of m ok, n observed, n waived> · **Workarounds** <ids — or
none> · **Review** <verdict> · **Changed** <paths> · **Yours to review:** `coverage.md` (observed
criteria first), the units, the workarounds.
