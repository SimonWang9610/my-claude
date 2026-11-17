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
| diagnose (bug) | you · `spec-diagnose` | cause with evidence; diagnosis set; `spec-check ids` passes · gate | never |
| design | you · `spec-design` | `spec-check design` passes · gate | nothing is open: approach, structure, unit, contract, screen |
| plan | you · `spec-plan` | `spec-check plan` passes | never |
| test | `spec-tester` | each delivered test, rerun, fails for missing behaviour or passes for what must not change | light size · no test suite |
| implement | `spec-implementer` | every task done; `spec-check coverage --run --write` passes | never |
| review | `spec-code-reviewer` | the same check passes; verdict accept | the user turned it off |

## Setup

In order, reading no code beyond the manifests that name the stack.

1. **Resume** — a `workflow.yaml` is named, or a spec is in progress → Each step, at `current`.
2. **Kind** — feature (new or changed behaviour) · bug (behaviour is broken) · improvement
   (behaviour stays, a quality improves). Mixed → the main one, the rest a follow-up spec. Not
   software → answer and stop.
3. **Size, folder, branch** — § Size, § Folder and branch. The first step may correct the size.
4. **Initialize** — `workflow.yaml` from `assets/workflow.yaml`, fitted to the kind and size; per
   delegated step, the installed skills that name this stack and step → its `skills`. Show kind,
   size and steps in one line.

## Each step

1. **Skip?** — per the table, with a one-line reason.
2. **Run** — a step you run: its skill, which saves its own artifact. A delegated step: Delegate,
   below.
3. **Record** — what an agent delivered, as delivered, which only you write: task rows with the
   files touched, `Evidence` lines, `progress`.
4. **Verify** — run the step's check yourself; set back to ⬜ what it shows failing. Read an
   artifact's body only to present a gate. A failure a delivered gap explains → Settle. Any other →
   back through the step once, the failure as its task; fails again → stop.
5. **Settle** — put to the user under **Needs you** what the step left for them: `Q`s an agent delivered,
   with their defaults · options to choose between · a conflict with what they said · a gap an agent
   delivered (a workaround, a waiver, a design that does not fit; it pauses only its task). Answers
   go back through the step, then recheck.
6. **Gate** — a step with a `gate` in `workflow.yaml`, even when skipped: Gates, below.
7. **Close** — the step's `status`, `gate` and its `diagnosis`, `severity`, `design_review` or
   `verdict`; `updated`;
   move `current`. The last step → the spec's `status: ✅`.

## Gates

Ask under **Needs you**: `Approve, or tell me what to change?`, with a compact summary, the defaults
taken, the artifact's path and the check's result. Any answer but an approval → revise through the step,
recheck, ask again. Never pass a waiting gate or a failing check.

- **Design review** — the design gate also says `Design review: recommended — <why>` when the
  design is heavy (§ Heavy design), else `not needed — <why>`, and asks `Approve, review it first,
  or tell me what to change?`. "Review" → `spec-design-reviewer`; show its findings; ask again.
- **`gates: auto`** (granted in advance) — a passing check approves. A heavy design → run the
  design review; accept → approved; else revise and rerun it once.

## Delegate

The test, implement and review steps, and the design review: always their agent, one at a time.
You write no test and no review yourself, and product code only as a trivial fix: a few lines in
one file with no new behaviour to test. Say so in one line and run the same checks.

1. **Prompt** — `references/agent-prompt-template.md`.
2. **Start or continue** — an agent's first run starts it; a follow-up continues it; one that can
   no longer be continued → a new agent.
3. **Receive** — a delivery is claims and gaps, never proof. Never hand one agent's prose to
   another.

- **test** — before any code exists. Skipped → the implementer writes each failing test first.
- **implement** — one implementer, the tasks in order. A plan too large for one context →
  consecutive batches, cut where no task depends across; never two at once.
- **review** — not accept → continue the implementer with the issues as its Tasks, then the same
  reviewer for a second round; `current` stays on review. Once a round is not accept, save the
  latest report to `review.md`.

## Stop

- "Not a bug" → skip the remaining steps with that reason. "Needs reproduction" → stop for what is
  missing.
- A review, of the design or the code, not accepted twice · a missing or ambiguous input.
- Anything irreversible: commit, push, pull request, delete.

## Rules

- This spec only; note out-of-scope findings.
- A step is skipped only by the table or the user; an artifact changes only through its step.
- Earlier artifacts are authoritative: ground in them first, then per the conventions' Grounding;
  an atlas built or named here → `atlas` in `workflow.yaml`. One that looks wrong is raised, never
  silently diverged from.
- The user asks, challenges or redirects mid-spec → `references/steering.md`.

## Outcome

**Done** <task, kind> · **Coverage** <n of m ok, n observed, n waived> · **Workarounds** <ids — or
none> · **Review** <verdict> · **Changed** <paths> · **Yours to review:** `coverage.md` (observed
criteria first), the units, the workarounds.
