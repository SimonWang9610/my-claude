# Agent prompt template

Every delegation is this prompt, in this order. The agent's definition holds its craft; the prompt
holds this run. One format for every stage, so the user can read any of them.

## Template

```markdown
# <stage> — <spec title>

## Goal
<why the spec exists, one sentence> → <the outcome this run must reach>

## Tasks
- <id> <what to do> — serves <ids> · <files>
Not yours: <what to leave alone>

## Context
- Spec: `<folder>/workflow.yaml` — <kind> · <size> · <stack>
- Read first: <artifact paths, sliced to what the tasks touch>
- Code: `<branch>` against `<base>` · Atlas: `<path>/INDEX.md`

## Facts
- <what is already established> — <anchor>

## Rules
- Every fact you report carries an anchor: `path:line`, `path:symbol` or `run: <command> → <result>`; not read → (inferred).
- A question is delivered as `Q-<n> <question> — default: <answer>`, never asked.
- <each rule of `spec-rules.md` tagged for this stage whose condition holds>
- <the spec's binding `D`, `R` and approved `WA`; what the user constrained>

## Skills
- `<skill>` — <when in this run to use it>

## Verification
- **Done when:** <observable condition: command → expected result>
- **Deliver:** <the exact items to record, in a fixed shape>. Nothing else.
```

## Filling

- **Embed or point** — what must hold and what to do is embedded (Rules, Tasks, copied with their
  ids); what to consult is a path (artifacts), from the project root.
- **Rules** — tagged bullets are copied verbatim, without the tag; never paraphrased. Never a
  project rule the agent loads itself (CLAUDE.md, `.claude/rules`).
- **Facts** — only what you established, anchored; never your reasoning, never another agent's
  prose. Commands are written resolved: `spec-check` with its full path.
- **Skills** — the step's `skills` in `workflow.yaml`, the session's skills that name this stack
  and stage, and those the conversation named; each with its when. `atlas` set →
  `my-workflow:audit-truth query <question>` — a fact not under Facts.
- Nothing the agent's definition already says; an empty section is omitted.
- Written once, straight into the agent call; never printed first.
- **Follow-up** — a continued agent gets Goal, Tasks, Verification and any section that changed. A
  new agent gets every section, the earlier artifact named under Facts.

## Per stage

### test — `spec-tester`

- **Tasks:** one line per `AC` in scope, its sentence copied from `spec.md`.
- **Read first:** the criteria in `spec.md`; the design's contracts.
- **Facts:** the test runner, its command, where tests live, a test to copy.
- **Done when:** every `AC` in scope has a test, run and failing for the missing behaviour.
- **Deliver:** per `AC`: test file · command · the failure line. Then gaps with their evidence, `Q`s.

### implement — `spec-implementer`

- **Tasks:** the `T` rows in order, copied from `tasks.md`. Not yours: the acceptance tests.
- **Read first:** the criteria served in `spec.md`; the design files of the units touched.
- **Facts:** the acceptance tests and their failing run, or that none exist; the pattern to copy;
  the format, lint and type-check commands.
- **Done when:** each task's evidence, lint and type-check pass; then `spec-check coverage --run`
  exits 0.
- **Deliver:** per `T`: files touched · evidence command → result. Then gaps with their evidence,
  `Q`s.

### design review — `spec-design-reviewer`

- **Tasks:** review `design.md` and `design/` against `spec.md`.
- **Read first:** `spec.md`, `design.md`, `design/`; the answers file,
  `../../spec-design/references/answers.md` from this folder, resolved.
- **Facts:** the `spec-check design` command and its last result.
- **Done when:** every finding carries an anchor; a verdict is set.
- **Deliver:** verdict · issues, most severe first, each `I-<n>` · severity · anchor · problem ·
  fix · `Q`s.

### review — `spec-code-reviewer`

- **Tasks:** review the diff of `<branch>` against `<base>`; check each task `tasks.md` marks done.
- **Read first:** `spec.md`, the design, `tasks.md`.
- **Facts:** the evidence, lint and test commands; the `spec-check coverage --run` command; second
  round: the earlier `I` ids.
- **Done when:** the checks rerun; every finding reproduced or marked "read, not run"; a verdict
  set.
- **Deliver:** the report in your template.
