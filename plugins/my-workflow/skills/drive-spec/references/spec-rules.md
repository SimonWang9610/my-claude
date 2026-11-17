# Spec rules

For drive-spec and the `spec-*` skills, on top of `conventions.md`.

A bullet ending in a tag is also an agent's rule: drive-spec copies it into the prompt of each
tagged stage whose bracketed condition holds (`agent-prompt-template.md`). `T` tester ·
`I` implementer · `D` design reviewer · `C` code reviewer.

## Mode

- **Spec mode** — a `workflow.yaml` is named, or one spec under `specs/` is in progress (several →
  the checked-out `branch`'s, else ask). Read its kind, size and `artifacts`.
  An earlier step neither done nor skipped → name it and ask. Mark this step in progress; when the
  work is complete save the artifact from the skill's `assets/` template at its `artifacts` path
  (light size: a section of `spec.md`), run the step's check, mark it done. Run without drive-spec
  → also move `current` on.
- **Standalone** — no `workflow.yaml`, or "no spec": work from the request; return the result; save
  nothing. Its probes go to a temp folder.
- **Status** — pending · in progress · done · skipped · blocked; a gate: waiting · approved (user |
  auto). Spec files show them as the symbols in `workflow.yaml`'s legend.

## Files

- drive-spec and the step skills write the spec files.
- Never edit a spec file (`workflow.yaml`, `spec.md`, the design, `tasks.md`); deliver what should be recorded. `T I D C`
- Only product code and tests in the project's own suite go outside the spec folder; probes, measurements and logs go to its `scratch/`, output or screenshots an observation cites to its `evidence/`. `T I D C`

## Ids

| Defined in | Ids |
|---|---|
| spec | `US-<n>` story · `AC-<n>.<m>` criterion of `US-<n>` (`AC-<n>`: standalone) · `FN-<n>` functionality, optional, serving ≥1 `AC` · `R-<n>` limit · `WA-<n>` workaround |
| design | `UNIT-<n>` unit (`UNIT-<n>.<m>`: a unit inside it) |
| plan · review | `T-<n>` task · `I-<n>` issue |

- One definition each: a table row with the id first, or a heading that starts with the id over
  `**Label:** value` lines. Everything else refers to it.
- Unique per spec; never reused or renumbered; dropped → it stays, marked `dropped — <why>`.

## Checks

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/spec-check.py" <ids|design|plan|coverage> <workflow.yaml> [--run] [--write]
```

Unexpanded: `../../../scripts/` from this folder. Run from the project root.

| Check | Passes when |
|---|---|
| `ids` | every id is defined once, in its file · each `AC-<n>.<m>` has its `US` · each `FN` serves an `AC` |
| `design` | every unit has a responsibility · the diagrams together match the unit list, at most 6 units each, no cycle · (feature) every `AC` is delivered by a unit |
| `plan` | every `AC`, `R` and changed `UNIT` is served by a task |
| `coverage` | every `AC` is built (its tasks done, their files in the repo) and evidenced, or waived. `--run` runs the evidence commands; `--write` saves `coverage.md` |

- `design` and `coverage` also fail on an unapproved `WA`.
- The script outranks judgement: cite its result; never call a step done while it fails. Cannot run
  it → check by hand and label the result "judged".

## Evidence

Verification adds evidence about behaviour.

- Each `AC` carries one `Evidence` line, the strongest kind that fits: (1) a test in the project's own suite, by the command that runs it; (2) an existing project command whose result shows it; (3) `observed: <what was done and seen>`, only when 1 and 2 cannot reach it. `T I C`
- Never write a script to check a criterion. `T I C`
- A kind-1 test stays in the codebase; an observation is the user's to judge. Seen failing before
  the code and passing after: ⬜ → ✅.

## Workarounds and waivers

Only the user approves; `gates: auto` never does.

- A workaround (anything that sidesteps a gap instead of solving it, a suppressed lint or loosened test included) or a criterion that cannot be evidenced or made to pass: stop that task and deliver it as a gap with its evidence; never decide it. `T I`
- **Workaround** — stop; show the gap · why no proper fix · what it does · when it can go.
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

## Independence

- Never read the plan, the implementation or anyone's reasoning about them; the criteria and the design's contracts are your only sources. `T`
- Never edit the acceptance tests the tester wrote; one that looks wrong is a gap. `I` [a tester ran]
- Never read the author's reasoning, commit messages or `discussions.md`; judge the files and what a run shows. `D C`

## Atlas

- The atlas is a snapshot of the code as audited; never build one. Query it first; fold in only facts about files this spec has not changed; never rewrite an entry. `T I` [`atlas` set]
- The atlas is a snapshot of the code as audited; never build one. Query it first and keep new facts in your delivery. `D C` [`atlas` set]

## Discussions

`discussions.md` exists only once the user has actually discussed something with you: a question, a
challenge, an idea, a choice between options. Log only what no spec file holds: what was weighed and
why the rest lost. Never what was done or which step ran (`workflow.yaml` tracks that), never what an
artifact already states. Newest last; an entry still open is also asked under **Needs you**.

```markdown
## <n> · <yyyy-mm-dd> · <step> · question | challenge | idea | option

**What came up:** <the user's words, or the choice that was open>

**Considered:** <facts with anchors; options; rejected: <option> — <why>>

**Outcome:** answered: <answer> · decided → D-<n> · rejected · parked: <until what> · open
```
