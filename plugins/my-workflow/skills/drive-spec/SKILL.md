---
name: drive-spec
description: >-
  Use this skill whenever the user wants software work done end to end or resumed: "build X", "fix
  X", "improve X", "refactor X", "continue the spec", a pasted ticket with "do it", even if they
  never say "spec". Runs requirements (or a bug diagnosis), design, plan, implementation and review,
  stopping for your approval and proving each requirement with a test. For one step only, use that
  step's spec-* skill.
argument-hint: "<task | path to a workflow.yaml>"
---

# drive-spec

Rules: `conventions.md` and `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (unexpanded →
`../../shared/`); already loaded in this conversation → do not read them again; the same for every `references/` file. § = a section of `references/context.md`.

Orchestrate one spec: sequence the steps, hand off precisely, verify by a run, know when to stop.
`workflow.yaml` holds the steps; each `spec-*` skill holds how its step is done. You own
`workflow.yaml`, `discussions.md` and `coverage.md`. Done = every step done or skipped.

## Setup

In order; no code exploration yet.

1. **Resume** — a `workflow.yaml` is named, or a spec is in progress → the Loop at `current`.
2. **Kind** — feature (new or changed behaviour) · bug (behaviour is broken) · improvement (behaviour
   stays, a quality improves). Mixed → the main one, the rest a follow-up spec. Not software → answer
   and stop.
3. **Size, folder, branch, role** — § Size, § Folder and branch, § Role.
4. **Initialize** — `workflow.yaml` from `assets/workflow-<kind>.yaml`, fitted to the size; map the
   installed skills (§ Skills).
5. **Show** — kind, size, role, steps and mapped skills in a few lines; one word corrects any.

## Loop

Per step of `workflow.yaml`, strictly in order; never invent or reorder one.

1. **Skip?** — per the table, with a one-line reason. A step the template skips whose condition does
   not hold → run it.
2. **Run** — its skill yourself, or its agent (§ Delegation, briefed per `references/delegation.md`).
   Cannot dispatch → yourself, acceptance checks before code.
3. **Verify** — yourself: the artifact exists and "done when" holds, by running the check. Read an
   artifact's body only to present a gate. Fails twice → stop.
4. **Settle** — before any gate, put to the user under **Needs you** what the step left for them:
   open `Q`s with their defaults · options to choose between · a conflict with what they said · a
   workaround or waiver. They may also steer. Answers go back through the step, then recheck.
   Nothing open → go on.
5. **Gate** — waiting → Gates.
6. **Record** — the step's status and result fields, and what an agent returned but could not write;
   move `current`; after the last step the spec is done.

| Step | Skip when | Done when |
|---|---|---|
| requirements | never | `spec-check ids` passes |
| diagnose | never | cause with evidence and confidence; verdict set; `spec-check ids` passes |
| design | nothing is open: approach, structure, unit, contract, screen | `spec-check design` passes |
| plan | never | `spec-check plan` passes |
| implement | never | every task done; `spec-check coverage --run --write` passes |
| review | the user turned it off | the same check passes; verdict accept |

## Gates

Requirements (a bug: the diagnosis) and design need approval. Never pass a waiting gate or a failing
check.

- **Ask** — once the step's open points are settled: a compact summary, the artifact's path, the
  check's result, then `Approve, or tell me what to change?`. Any answer but yes → revise through the
  step, recheck, ask again.
- **Design** — the user reviews it. Offer a second opinion from `spec-reviewer`; run it only on a yes.
- **`gates: auto`** (granted in advance) — a passing check approves; for a design you judge risky,
  `spec-reviewer` decides.
- **Plan** — it delegates → set its gate to waiting and implement's `agent`; ask before agents start.

## Stop for the user

- A workaround, waiver or design gap (spec rules) → show it with options and a recommendation. It
  pauses only its task.
- A step's own stop or questions → show them as raised.
- The design step returns options → ask, log the choice to `discussions.md`, rerun it with the pick.
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

**Done** <task, kind> · **Coverage** <n of m ok, n waived> · **Workarounds** <ids — or none> ·
**Review** <verdict> · **Changed** <paths> · **Yours to review:** `coverage.md`, the units, the
workarounds.
