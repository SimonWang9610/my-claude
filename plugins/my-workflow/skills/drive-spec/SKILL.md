---
name: drive-spec
description: >-
  Use this skill whenever the user wants software work done end to end, or resumed: "build X", "fix
  X", "improve X", "refactor X", "I want …", "continue the spec", a pasted ticket or bug report with
  "do it", even when they never say "spec" or "workflow". Takes the task from requirements (or a bug
  diagnosis) through design, plan, implementation and review, stops for your approval of the
  requirements and the design, and proves every requirement with a test before calling the work done.
  Keeps progress in specs/<task>/ so the work can be resumed. For one step only, use that step's
  spec-* skill; for a question about existing code, use my-workflow:audit-truth.
argument-hint: "<task | path to a workflow.yaml>"
---

# drive-spec

Rules: `conventions.md` and `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (unexpanded → `../../shared/`).
Other paths are relative to this folder.

## Role

Orchestrate exactly one spec. Your strength is judgement, not labour: sequence the steps, hand off
precisely, verify every result by a run, know when to stop for the user. `workflow.yaml` holds the step order and each step's skill, gate, model
and mapped skills; each `spec-*` skill holds how its step is done. You decide who runs a step, verify
its result and record it. You own `workflow.yaml`, `history.md`, `coverage.md` and the
conversation. Done = every step is done or skipped. my-workflow's routing hints do not apply while
you drive.

## Setup

Strict order. No codebase exploration here: that belongs to the first step. § = a section of
`references/context.md`.

1. **Resume** — a `workflow.yaml` is named, or one spec is in progress → the Spec loop at `current`.
2. **Kind** — not a software task → answer directly and stop. Else **feature** (new or changed
   behaviour) · **bug** (existing behaviour is broken) · **improvement** (behaviour stays, a quality
   gets better). Mixed → the kind most of the work belongs to, the rest noted as a follow-up spec.
   Unclear → ask once.
3. **Size** — light or standard (§ Size).
4. **Folder and branch** — propose both (§ Folder and branch); create them on a yes.
5. **Initialize** — `workflow.yaml` from `assets/workflow-<kind>.yaml`, adapted to the size, with
   `folder`, `role` and `gates` set (§ Role) and `atlas` when the user named one.
6. **Map skills** — fill each step's `skills` (§ Skills).
7. **Show** — kind, size, role, the steps (any skipped, and why), the mapped skills, in a few lines.
   One word corrects any of them. Then the Spec loop.

## Spec loop

Run the steps of `workflow.yaml` strictly in order. Per step:

1. **Read** — `id`, `skill`, `agent`, `status`, `gate`, `skills`, `model`. Never invent, reorder or
   inject a step.
2. **Skip or check inputs** — the Steps table says skip → mark it skipped with a one-line reason. A
   step the template skips whose skip condition does not hold → set it pending and run it. Else the
   artifact of every earlier step that ran exists and is non-empty; missing → run the step that
   writes it; none does → stop and ask.
3. **Run** — the step's skill yourself, or brief its agent (On demand).
4. **Verify** — yourself, never on a report's word: the artifact exists at its `artifacts` path and
   "done when" holds, by running the named check. Read an artifact's body only to present a gate. Not
   met → back to 3 with the check's output, at most twice, then stop.
5. **Gate** — the step has a waiting gate → Gates.
6. **Record and advance** — the step's status and result fields (`level`, `verdict`, `severity`,
   `progress`); for an agent's work also what it returned and could not write (task rows, check
   commands, the review report). Move `current` to the next step not skipped; after the last one, set
   the spec's `status` to done. Never past a waiting gate or a failing check.

| Step | Skip when | Done when |
|---|---|---|
| requirements | never | `spec-check ids` passes |
| diagnose | never | the root cause has evidence and a confidence; the verdict is set; `spec-check ids` passes |
| design | no approach, structure, unit, contract or screen is open | `spec-check design` passes; standard size: a fresh-eyes design review accepts |
| plan | never | `spec-check plan` passes |
| implement | never | every task row is done; `spec-check coverage --run --write` passes |
| review | the user turned review off | `spec-check coverage --run --write` passes; the verdict is accept |

## Gates

The workflow leaves requirements (a bug: the diagnosis) and design only on approval.

- **Ask** — show a compact summary and the artifact's path (never its body), the check's result,
  the design review's verdict, the batched questions with defaults; then `Approve?`. Yes → mark the gate approved by the user.
- **Iterate** — any other answer → revise through the owning step, rerun its check (design: and its
  review), ask again.
- **`gates: auto`** — only when the user gave that permission in advance. The check passing (design:
  and the reviewer accepting) approves the gate as auto; show it and go on. It fails twice → stop.
- **Light size** — one gate, on the design step when it runs, else on the first step.
- **Plan** — the plan delegates → set its gate to waiting and implement's `agent`; ask before
  teammates start.

## Stop and wait for the user

- A step reports a workaround, a waiver or a design gap → show it per the spec rules' Workarounds
  and waivers, with options and a recommendation. Record the user's decision; `gates: auto` never
  decides these. It pauses only its task; independent tasks go on.
- A step's skill raises its own stop or questions → show them as raised; never answer for the user.
- The design step returns options → ask, log them in `history.md`, rerun the step with the pick.
- An input is missing or ambiguous → ask with a recommended answer.
- A bug's verdict is "not a bug" → mark the remaining steps skipped with that reason; the spec is
  done.
- A review's verdict is not accept for the second time, even on auto. The first time: fix its issues
  and run review again.
- A check keeps failing → show its output and the options.
- The action is irreversible or outward-facing: commit, push, pull request, delete, publish.

## Rules

- **This spec only** — note out-of-scope findings for the user and move on.
- **`workflow.yaml` is law** — a step is skipped only by the Steps table or the user's word, reason
  recorded; an artifact changes only through its owning step.
- **Earlier artifacts are authoritative** — ground every step and brief in them; deeper facts
  through `/my-workflow:audit-truth`, never a blind re-scan; one that looks wrong is raised, never
  silently diverged from.
- **Verify, never re-judge** — check a teammate's files with the script and a run; never redo its
  work or take "done" on trust.
- **Acceptance checks are never edited to make code pass** — a wrong-looking one is reported.
- **Batch every interaction** — one round of questions, one brief carrying the full task, one
  report; a recommendation with every question; pushback with evidence when a user statement does
  not hold.
- **New user instructions win** — `references/mid-spec.md`.

## On demand

| When | Read first |
|---|---|
| a step goes to an agent | `references/delegation.md` |
| mid-spec the user asks, challenges, offers an idea or changes direction | `references/mid-spec.md` |

Who runs a step: § Delegation and § Models; implement follows the plan's Batches. Cannot dispatch →
run the step's skill yourself, the acceptance checks before any code.

## Outcome

- **Done:** <task> — <kind>
- **Coverage:** <n of m ids ok, n waived> — `coverage.md` (passing: run by the script)
- **Workarounds:** <WA ids, each approved by you — or none>
- **Review:** <verdict, or skipped>
- **Changed:** <paths>
- **Yours to review:** the coverage report, the design's units and the workarounds, not every line.
- **Open questions:** <each with its default>
