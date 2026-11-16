# Spec rules

What drive-spec and the `spec-*` skills share, on top of `conventions.md`.

## Spec mode

A `spec-*` skill picks its mode and says which in one line. Its steps are the same in both.

- **Spec mode** — a `workflow.yaml` is named, or exactly one spec under `specs/` is in progress
  (several → the one whose `branch` is checked out, else ask):
  1. Read it: kind, size, `folder`, `artifacts`, this step's `skills` and `model`.
  2. Stage check: every earlier step is done or skipped, and this step is `current` or is being run
     again. Else name the expected step and ask.
  3. Mark the step in progress and `current`. Work complete → save the artifact from the skill's
     `assets/` template at its `artifacts` path (size light → a section of `spec.md`; the plan always
     in its own file), run the step's check (§ Checks), mark the step done, set `updated`. Moving
     `current` on is drive-spec's job; run alone, set it to the next step not skipped.
- **Standalone** — no `workflow.yaml`, or the user says "no spec": the input is the request, earlier
  results in the session, or named files (several versions → the latest). Return the result in the
  session; save nothing.

Who writes: drive-spec and the step skills write spec files; every other skill returns its result
(audit-truth: its atlas folder only). An agent writes only the files its definition names and returns
the rest, status and rows included. Code, tests and scaffolding go where they belong.

## Status

pending · in progress · done · skipped · blocked, for the spec, its steps and task rows; a gate is
waiting or approved (by the user, or auto). Spec artifacts show each as the symbol in the legend at the
top of `workflow.yaml`; write the word everywhere else.

## Ids

| Id | Is | Defined in |
|---|---|---|
| `US-<n>` | user story | spec |
| `AC-<n>.<m>` | acceptance criterion of `US-<n>` · `AC-<n>`: standalone, no story owns it | spec |
| `FN-<n>` | functionality: one thing the system does; serves criteria, or standalone (Serves `—`) | spec |
| `R-<n>` | limit | spec |
| `WA-<n>` | approved workaround | spec |
| `UNIT-<n>` | design unit (`UNIT-<n>.<m>`: a unit inside it) | design |
| `T-<n>` | task | plan |
| `I-<n>` | issue | review |

- One definition per id: its row, id in the first cell, in the table that defines it. Everything else
  refers to it.
- Unique within a spec. Assigned once; never reused or renumbered. Dropped → the row stays, its second
  cell `dropped — <why>`. Continue from the highest id in the spec.

## Checks

`spec-check` decides a step's gate where a script can:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/spec-check.py" <ids|design|plan|coverage> <workflow.yaml> [--run] [--write]
```

Unexpanded: `scripts/spec-check.py` beside this file's folder. Run from the project root.

| Check | Passes when |
|---|---|
| `ids` | templates valid · one definition per id, in its file · each `AC-<n>.<m>` has its `US` · each id an `FN` serves exists · no undefined id |
| `design` | each unit states responsibility, input, output, boundary · the Mermaid diagram matches the unit list · no cycle · every `WA` approved |
| `plan` | every `AC`, `FN`, `R` and changed `UNIT` is served by a task |
| `coverage` | every `AC` and `FN` is planned, implemented (files tracked), tested and passing, or waived · every `WA` approved. `--run` runs each criterion's check (a standalone `FN`: its tasks' checks); `--write` saves `coverage.md` |

- Tested = a file listed in a task's Files, its path containing `test`, `spec`, `check` or `e2e`,
  holds the literal id (`AC-1.2`).
- Its result outranks an agent's judgement. Cite its output as the evidence.
- Never report a step done while its check fails.
- Cannot run it → do the same checks by hand and label the result "judged, not checked". Label any
  result that rests on judgement, not a run, as judged.

## Workarounds and waivers

Only the user approves these; `gates: auto` never does.

- **Workaround** — code or design that sidesteps a gap instead of solving it, a suppressed lint or
  check included. Needed → stop. Show: the gap · why no proper fix · what the workaround does · when it
  can go. The user steers the design to avoid it, or approves. Never adopt one unapproved.
- **Waiver** — an `AC` or `FN` that cannot be tested or made to pass. Ask. Never self-approve.
- Inside an agent or another skill → return it as a gap. Standalone → ask it as a question.

Approved → a row in the spec, the section added on first use:

```markdown
## Workarounds
| Id | Gap | Why no proper fix | Workaround | Where | Approved | Remove when |
|---|---|---|---|---|---|---|
| WA-1 | <design vs codebase> | <why> | <what it does> | `path` | <who>, <yyyy-mm-dd> | <condition> |

## Waivers
| Id | Waived | Why | Approved |
|---|---|---|---|
| AC-1.2 | untested · failing | <why> | <who>, <yyyy-mm-dd> |
```

## History

Spec artifacts hold final decisions and outcomes only. The trail behind them goes to the spec's
`history.md`: a question, challenge or idea from the user · options weighed and the ones rejected ·
a clarification round. Created on the first entry; nothing to record → no file. Standalone → nothing
saved.

```markdown
# History — <title>

| # | Date | At step | Type | What came up | Considered | Outcome |
|---|---|---|---|---|---|---|
| 1 | <yyyy-mm-dd> | <step id> | question · challenge · idea · option · clarification | <the user's words, or the choice that was open> | <facts found, options weighed; rejected: <option> — <why>> | answered: <answer> · decided → D-<n> · rejected · parked: <until what> |
```

A decision is written in its artifact as a `D` and only referenced here.
