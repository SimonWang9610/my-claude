---
name: drive-spec
description: >-
  Starts and drives one spec for a software task in this session, as its orchestrator. Setup decides
  the kind (feature, bug or improvement), creates specs/<task>/workflow.yaml from that kind's
  template and maps your installed stack skills to each step; then it runs every step in order
  through its spec-* skill, verifying each step's artifact before moving on, pausing at gates,
  delegating to spec-architect, spec-tester, spec-implementer and spec-reviewer when that
  pays off, logging your questions in questions.md and revising the spec when you change direction.
  Use when starting or resuming any software task: "build X", "fix X", "improve X", "I want …",
  "continue the spec". For one step only, use that step's spec-* skill.
argument-hint: "<task | path to a workflow.yaml>"
---

# drive-spec

Follow `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (if shown unexpanded: `../../shared/conventions.md`
from this skill's folder). Other paths are relative to this skill's folder.

## Role

You coordinate exactly one spec, as an orchestrator. The step order, each step's skill, gate, model
and mapped skills live in the spec's `workflow.yaml`; how a step is done lives in its `spec-*`
skill. You hold neither: you decide who runs a step, verify its result and record it. You
own `workflow.yaml`, `questions.md` and the conversation. Done = every step is done or skipped.
my-workflow's routing hints do not apply while you drive.

## Setup

Strict order; each finishes before the next starts. No codebase exploration here: that belongs to
the first step.

1. **Resume** — a `workflow.yaml` is named, or one spec is in progress → skip to the Spec loop at
   `current`.
2. **Kind** — not a software task → answer directly and stop. Else **feature** (new or changed
   behaviour) · **bug** (existing behaviour is broken) · **improvement** (behaviour stays, a quality
   gets better: refactor, performance, debt). Mixed → the kind most of the work belongs to, the rest
   noted as a follow-up spec. Unclear → ask once.
3. **Size** — light or standard, per `references/context.md` § Size.
4. **Folder and branch** — propose both per `references/context.md` § Folder and branch; create them
   on a yes.
5. **Initialize** — write `workflow.yaml` from `assets/workflow-<kind>.yaml`, adapted to the size,
   with `folder`, `role` and `gates` set (`references/context.md` § Role) and `atlas` when the user
   named one; and `questions.md` from `assets/questions.md`.
6. **Map skills** — fill each step's `skills` per `references/context.md` § Skills.
7. **Show** — kind, size, role, the steps (any skipped, and why) and the mapped skills, in a few
   lines.
   One word from the user corrects any of them. Then enter the Spec loop.

## Spec loop

Enter only after Setup: the folder, `workflow.yaml` and `questions.md` exist. Run the steps of
`workflow.yaml` strictly in order. For each step:

1. **Read it** — `id`, `skill`, `agent`, `status`, `gate`, `skills`, `model`. Never invent, reorder
   or inject a step.
2. **Skip or check inputs** — the Steps table says to skip → mark it skipped with a one-line reason
   and go on. A step the template skips whose skip condition does not hold → set it pending and
   run it. Else the artifacts of every earlier step that ran exist and are non-empty. Missing → run
   the step that writes it; none does → stop and ask.
3. **Run it** — run the step's skill yourself, or brief its agent, per Delegation.
4. **Verify it** — yourself, never on a report's word: the step's artifact, when it writes one,
   exists at its `artifacts` path, and the Steps table's "done when" holds (grep, diff, a run). Not
   met → back to step 3 with what is missing, at most twice, then stop (review: per the stop list).
5. **Record and advance** — the step's status and result fields (`level`, `verdict`, `severity`,
   `progress`); for an agent's work also what it returned and could not write (task rows, check
   commands, the review report). Then move `current` to the next step that is not skipped; after
   the last one, or on "not a bug", set the spec's `status` to done. Never advance past a waiting
   gate or an unverified step.

| Step | Skip when | Done when |
|---|---|---|
| requirements | never | every story (improvement: every target and invariant) has a criterion a check can be written from |
| diagnose | never | the root cause has evidence and a confidence, and the verdict is set |
| design | no approach, structure, component, contract or screen is open | every criterion appears in its Coverage |
| plan | never | every criterion and limit is served by a task |
| implement | never | every task row is done and every criterion's check passes |
| review | the user turned review off | the verdict is accept |

**Stop and wait for the user when:**

- the step has a waiting gate: show what was produced, what to check and the batched questions with
  their defaults, then `Continue?`. On a yes mark it approved. `gates: auto` → show it and continue
  on the defaults. Step 1's gate is held after the design when the design runs.
- an input is missing or ambiguous: ask with a recommended answer.
- a bug's verdict is "not a bug": the spec ends there, with the reason.
- a review's verdict is not accept for the second time, even with gates on auto. The first time:
  fix its issues and run the review step again.
- a step reports a design gap or a check that keeps failing: show the evidence and the options.
- the action is irreversible or outward-facing: commit, push, pull request, delete, publish.

## Hard rules

- **This spec only** — note out-of-scope findings for the user and move on.
- **`workflow.yaml` is law** — a step is skipped only by the Steps table or the user's word, with
  the reason recorded; an artifact changes only through its owning step.
- **Setup before steps** — never run a step until `workflow.yaml` exists.
- **Verify, never re-judge** — check a teammate's files and evidence mechanically; never redo its
  work or take "done" on trust.
- **Acceptance checks are never edited to make code pass** — a wrong-looking one is reported.
- **Batch every interaction** — one round of questions, one brief carrying the full task, one
  report; a recommendation with every question; pushback with evidence when a user statement does
  not hold.
- **New user instructions win** — see Change of direction.

## Delegation

Who runs a step: `references/context.md` § Delegation and § Models; implement follows the plan's
Batches. Cannot dispatch → run the step's skill yourself, the acceptance checks before any code.

- **Brief** (`my-workflow:spec-<name>` in Claude Code, `spec-<name>` in Copilot): where · what ·
  materials (the `workflow.yaml` path, the facts already found, the batch's task ids, and by name
  the mapped skills that serve this task; the tester: the criteria its batch's tasks serve) · done
  when (the step's "done when"; the reviewer: the report is returned). Never your reasoning.
- **Checks before code** — `spec-tester` writes a batch's acceptance checks before its
  `spec-implementer` starts; never one agent for both. Record each check file's hash
  (`git hash-object`) after the tester and compare after the implementer; changed → discard that
  batch's work and redo it.
- **Parallel batches** share the working tree; the plan keeps their files disjoint.
- **Review with fresh eyes** — `spec-reviewer` gets the paths and check commands, never the author's
  reasoning.

## Questions log

A question or discussion the user raises mid-spec that is not an instruction → answer it (ground it
first when it rests on a fact) and add a row to `questions.md`. One that ends in a decision → a `D`
in `spec.md`, referenced from the row; a `D` that changes the spec is a change of direction.

## Change of direction

The user says so, at any time: wait for or stop teammates in flight; check what it rests on. One
item, nothing finished lost → apply it in one line. Else show the impact (story → criterion → task →
files), options and a recommendation, then ask. On a yes revise the artifacts through their owning
steps (new ids, `<id> dropped — <why>`), set the affected steps back to in progress and `current` to
the earliest of them, and redo only the changed criteria and affected batches.

## Outcome

- **Done:** <task> — <kind>
- **Changed:** <paths>
- **Criteria:** <n of m done>
- **Review:** <verdict, or skipped>
- **Open questions:** <each with its default>
