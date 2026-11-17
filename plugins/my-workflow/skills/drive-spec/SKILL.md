---
name: drive-spec
description: >-
  Use this skill whenever the user wants software work done end to end or resumed: "build X", "fix
  X", "improve X", "refactor X", "continue the spec", a pasted ticket with "do it", even if they
  never say "spec". Settles the requirements (or a bug's diagnosis), the design and the plan with
  you, then delegates tests, code and review to agents, stopping for your approval and backing each
  requirement with a test or recorded evidence. For one step only, use that step's spec-* skill.
argument-hint: "<task | path to a workflow.yaml>"
---

# drive-spec

Rules: `conventions.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (else `../../shared/`) and
`references/spec-rules.md`. They and every other `references/` file are read once per conversation,
when first needed. § = a section of `references/context.md`.

Drive one spec from a task to accepted code. You and the user decide: requirements, design, plan.
Agents build and judge: tests, code, review. You own `workflow.yaml`, `discussions.md` and
`coverage.md`, and record what agents deliver. Done = every step done or skipped.

## Flow

`workflow.yaml` holds this spec's steps, strictly in this order; never invent or reorder one.

| Step | Run by | Done when | Skip when |
|---|---|---|---|
| requirements | you · `spec-requirements` | `spec-check ids` passes · gate | never |
| diagnose (bug) | you · `spec-diagnose` | cause with evidence; verdict set; `spec-check ids` passes · gate | never |
| design | you · `spec-design` | `spec-check design` passes · gate | nothing is open: approach, structure, unit, contract, screen |
| plan | you · `spec-plan` | `spec-check plan` passes | never |
| test | `spec-tester` | every `AC` in scope has a test seen failing | light size · no test suite |
| implement | `spec-implementer` | every task done; `spec-check coverage --run --write` passes | never |
| review | `spec-code-reviewer` | the same check passes; verdict accept | the user turned it off |

## Setup

In order; no code exploration yet.

1. **Resume** — a `workflow.yaml` is named, or a spec is in progress → Each step, at `current`.
2. **Kind** — feature (new or changed behaviour) · bug (behaviour is broken) · improvement
   (behaviour stays, a quality improves). Mixed → the main one, the rest a follow-up spec. Not
   software → answer and stop.
3. **Size, folder, branch** — § Size, § Folder and branch.
4. **Initialize** — `workflow.yaml` from `assets/workflow.yaml`, fitted to the kind and size; per
   delegated step, the installed skills that name this stack and step → its `skills`. Show kind,
   size and steps in one line.

## Each step

1. **Skip?** — per the table, with a one-line reason.
2. **Run** — a step you run: its skill. A delegated step: Delegate, below.
3. **Verify** — run the step's check yourself; an agent's "done" is a claim. Read an artifact's
   body only to present a gate. Fails twice → stop.
4. **Settle** — put to the user under **Needs you** what the step left for them: open `Q`s with
   their defaults · options to choose between · a conflict with what they said · a gap an agent
   delivered (a workaround, a waiver, a design that does not fit; it pauses only its task). Answers
   go back through the step, then recheck.
5. **Gate** — requirements (a bug: the diagnosis) and design: Gates, below.
6. **Record** — the step's status and result fields; what the agent delivered (task rows, files
   touched, `Evidence` lines, `progress`, `verdict`); move `current`.

## Gates

A compact summary, the artifact's path, the check's result, then `Approve, or tell me what to
change?`. Any answer but yes → revise through the step, recheck, ask again. Never pass a waiting
gate or a failing check.

- **Design review** — the design gate adds one line: `Design review: recommended — <why>` when the
  design is heavy (§ Heavy design), else `not needed — <why>`. Run `spec-design-reviewer` only on a
  yes; show its findings; ask the gate again.
- **`gates: auto`** (granted in advance) — a passing check approves. A heavy design → run the
  design review; its verdict decides; not accepted → revise and rerun once.

## Delegate

The test, implement and review steps, and the design review: always their agent, one at a time.
You write no test and no review yourself, and product code only as a trivial fix: a few lines in
one file with no new behaviour to test. Say so in one line and run the same checks.

1. **Prompt** — `references/agent-prompt-template.md`, filled from the step's entry in
   `workflow.yaml` (`agent`, `skills`), the template's entry for this stage, and the tasks in scope.
2. **Start or continue** — a step's first run starts its agent. A follow-up in the same step
   continues that agent, with only the sections that changed. Its context is spent, or it failed
   twice → a new agent, the full template.
3. **Receive** — a delivery is claims and gaps: verify, record, settle. Never hand one agent's
   prose to another.

- **test** — before any code exists. Skipped → the implementer writes each failing test first.
- **implement** — one implementer, the tasks in order. A plan too large for one context →
  consecutive batches, cut where no task depends across; never two at once.
- **review** — not accept → its issues are the implementer's next Tasks, then the same reviewer's
  second round. Save its report to `review.md` only when the verdict is not accept.

## Stop

- "Not a bug" → skip the remaining steps with that reason.
- A review, of the design or the code, not accepted twice · a check that keeps failing · a missing
  or ambiguous input.
- Anything irreversible: commit, push, pull request, delete.

## Rules

- This spec only; note out-of-scope findings.
- A step is skipped only by the table or the user; an artifact changes only through its step.
- Earlier artifacts are authoritative: ground in them first, then per the conventions' Grounding;
  an atlas built here → `atlas` in `workflow.yaml`. One that looks wrong is raised, never silently
  diverged from.
- One round of questions, one report; push back with evidence.
- The user asks, challenges or redirects mid-spec → `references/steering.md`.

## Outcome

**Done** <task, kind> · **Coverage** <n of m ok, n observed, n waived> · **Workarounds** <ids — or
none> · **Review** <verdict> · **Changed** <paths> · **Yours to review:** `coverage.md` (observed
criteria first), the units, the workarounds.
