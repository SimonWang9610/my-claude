# Spec rules

For drive-spec and the `spec-*` skills, on top of `conventions.md`.

## Mode

- **Spec mode** — a `workflow.yaml` is named, or one spec under `specs/` is in progress (several →
  the checked-out `branch`'s, else ask). Read its kind, size, `artifacts` and this step's `skills`.
  An earlier step neither done nor skipped → name it and ask. Mark this step in progress; when the
  work is complete save the artifact from the skill's `assets/` template at its `artifacts` path
  (light size: a section of `spec.md`), run the step's check, mark it done. Run without drive-spec
  → also move `current` on.
- **Standalone** — no `workflow.yaml`, or "no spec": work from the request; return the result; save
  nothing.
- **Who writes** — drive-spec and the step skills write spec files; an agent writes only what its
  definition names and returns the rest.
- **Where files go** — only product code and tests in the project's own test setup go outside the
  spec folder. Everything else a spec produces stays inside it: check scripts → `checks/`; probes,
  one-off scripts, measurements, logs → `scratch/`. Standalone → a temp folder.
- **Status** — pending · in progress · done · skipped · blocked; a gate: waiting · approved (user |
  auto). Spec files show them as the symbols in `workflow.yaml`'s legend.

## Ids

| Defined in | Ids |
|---|---|
| spec | `US-<n>` story · `AC-<n>.<m>` criterion of `US-<n>` (`AC-<n>`: standalone) · `FN-<n>` functionality (Serves `—`: standalone) · `R-<n>` limit · `WA-<n>` workaround |
| design | `UNIT-<n>` unit (`UNIT-<n>.<m>`: a unit inside it) |
| plan · review | `T-<n>` task · `I-<n>` issue |

- One definition each: a table row with the id first, or a heading that starts with the id over
  `**Label:** value` lines. Everything else refers to it.
- Unique per spec; never reused or renumbered; dropped → it stays, marked `dropped — <why>`.

## Checks

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/spec-check.py" <ids|design|plan|coverage> <workflow.yaml> [--run] [--write]
```

Unexpanded: `../scripts/` from this folder. Run from the project root.

| Check | Passes when |
|---|---|
| `ids` | every id is defined once, in its file, with its fields · each `AC-<n>.<m>` has its `US` |
| `design` | each unit states responsibility, input, output, boundary · the diagrams together match the unit list, at most 6 units each, no cycle |
| `plan` | every `AC`, `FN`, `R` and changed `UNIT` is served by a task |
| `coverage` | every `AC` and `FN` is planned, implemented, tested and passing, or waived. `--run` runs the checks; `--write` saves `coverage.md` |

- Tested = a file in a task's Files, its path containing `test`, `spec`, `check` or `e2e`, holds the
  literal id.
- `design` and `coverage` also fail on an unapproved `WA`.
- The script outranks judgement: cite its result; never call a step done while it fails. Cannot run
  it → check by hand and label the result "judged".

## Workarounds and waivers

Only the user approves; `gates: auto` never does. Inside an agent → return it as a gap.

- **Workaround** — anything that sidesteps a gap instead of solving it, a suppressed lint or check
  included. Stop; show the gap · why no proper fix · what it does · when it can go.
- **Waiver** — an `AC` or `FN` that cannot be tested or made to pass. Ask.

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
| AC-1.2 | untested · failing | <why> | <who>, <yyyy-mm-dd> |
```

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
