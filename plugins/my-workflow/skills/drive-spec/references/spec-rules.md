# Spec rules

For drive-spec and the `spec-*` skills, on top of `conventions.md`.

## Mode

- **Spec mode** — a `workflow.yaml` is named, or one spec under `specs/` is in progress (several →
  the checked-out `branch`'s, else ask). Read its kind, size and `artifacts`.
  An earlier step neither done nor skipped → name it and ask. Mark this step in progress; when the
  work is complete save the artifact from the skill's `assets/` template at its `artifacts` path
  (a design whose path is `spec.md`: a `## Design` section of it, headings one level down), run the
  step's check, mark it done. Run without drive-spec → also ask the step's gate, when it has one,
  then move `current` on.
- **Questions first** — a step's questions are asked (conventions) before its artifact is saved; an
  answer, or a default taken, becomes a `D`. A spec file holds no open question.
- **Standalone** — no `workflow.yaml`, or "no spec": work from the request; return the result; save
  nothing. Its probes go to a temp folder.
- **Status** — pending · in progress · done · skipped · blocked; a gate: waiting · approved (user |
  auto). Spec files show them as the symbols in `workflow.yaml`'s legend.

## Files

- drive-spec and the step skills write the spec files.
- Only product code and tests in the project's own suite go outside the spec folder; probes,
  measurements and logs go to its `scratch/`, output or screenshots an observation cites to its
  `evidence/`.

## Ids

| Defined in | Ids |
|---|---|
| spec | `US-<n>` story · `AC-<n>.<m>` criterion of `US-<n>` (`AC-<n>`: standalone) · `FN-<n>` functionality, optional, serving ≥1 `AC` · `R-<n>` limit · `WA-<n>` workaround |
| design | `UNIT-<n>` unit (`UNIT-<n>.<m>`: a unit inside it) |
| plan | `T-<n>` task · `TB-<n>` test batch · `IB-<n>` implement batch |

- One definition each: a table row with the id first, or a heading that starts with the id over
  `**Label:** value` lines. Everything else refers to it.
- Unique per spec; never reused or renumbered; dropped → it stays, its title replaced by
  `dropped — <why>`.
- The script reads none of these: `D-<n>` decisions, numbered on across the spec's files; `Q-<n>`
  questions, which live in the conversation and in what an agent sends back; `I-<n>` issues, unique per
  review report.

## Checks

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/spec-check.py" <ids|design|plan|coverage> <workflow.yaml> [--run] [--write]
```

Unexpanded: `../../../scripts/` from this folder. Without git, run it from the project root.

| Check | Passes when |
|---|---|
| `ids` | every id is defined once, in its file · each `AC-<n>.<m>` has its `US` · each `FN` serves an `AC` |
| `design` | every unit has a responsibility · the diagrams together match the unit list, at most 6 units each, no cycle · (feature) every `AC` is delivered by a unit |
| `plan` | every `AC`, `R` and changed `UNIT` is served by a task · every task sits in exactly one implement batch |
| `coverage` | every `AC` is built (its tasks done, their files in the repo) and evidenced, or waived. `--run` runs the evidence commands; `--write` saves `coverage.md` |

- `design` and `coverage` also fail on an unapproved `WA`.
- The script outranks judgement: cite its result; never call a step done while it fails. Cannot run
  it → check by hand and label the result "judged".

## Evidence

- Each `AC` carries one `Evidence` line, the strongest kind that fits: (1) a test in the project's
  own suite, by the command that runs it; (2) an existing project command that fails when the
  criterion does not hold; (3) `observed: <what was done and seen>`, only when 1 and 2 cannot
  reach it.
- Never write a script to check a criterion.
- The line is marked ⬜ until its evidence passes, then ✅. A kind-1 test stays in the codebase; an
  observation is the user's to judge.

## Workarounds and waivers

Only the user approves; `gates: auto` never does.

- **Workaround** — anything that sidesteps a gap instead of solving it, a suppressed lint or
  loosened test included. Stop; show the gap · why no proper fix · what it does · when it can go.
- **Waiver** — an `AC` that cannot be evidenced or made to pass. Ask.

Approved → recorded in the spec:

```markdown
## Workarounds

### WA-1 <title>

- **Gap:** <design vs codebase>
- **Why no proper fix:** <why>
- **Workaround:** <what it does>
- **Where:** `path`
- **Approved:** <who>, <yyyy-mm-dd>
- **Remove when:** <condition>

## Waivers

| Id | Waived | Why | Approved |
|---|---|---|---|
| AC-1.2 | no evidence · failing | <why> | <who>, <yyyy-mm-dd> |
```

## Discussions

Whenever the user asks, challenges, proposes or picks between options, in a step, at a gate or
mid-spec, add an entry to `discussions.md`; a plain approval is not one, and the file exists only
once there is an entry. Log only what no spec file holds: what was weighed and
why the rest lost. Never what was done or which step ran (`workflow.yaml` tracks that), never what an
artifact already states. Newest last; an entry still open is also asked under **Needs you**.

```markdown
## <n> · <yyyy-mm-dd> · <step> · question | challenge | idea | option

**What came up:** <the user's words, or the choice that was open>

**Considered:** <facts with anchors; options; rejected: <option> — <why>>

**Outcome:** answered: <answer> · decided → D-<n> · rejected · parked: <until what> · open
```
