# Agent prompt template

Every delegation is this prompt, in this order. The agent's definition holds its craft; the prompt
holds this run. One format for every stage, so the user can read any of them. A stage is a
delegated step, or the design review.

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
- <each bullet of `spec-rules.md` written for this agent whose condition holds>
- <the spec's binding decisions, limits and approved workarounds; what the user constrained>

## Skills
- `<skill>` — <when in this run to use it>

## Verification
- **Done when:** <observable condition: command → expected result>
- **Deliver:** <the exact items to record, in a fixed shape>. Nothing else.
```

## Filling

- **Embed or point** — what must hold and what to do is embedded (Rules, Tasks, copied with their
  ids); what to consult is a path (artifacts), from the project root.
- **Rules** — a `spec-rules.md` bullet is copied verbatim, without its `→` part; never paraphrased.
  Never a project rule the agent loads itself (CLAUDE.md, `.claude/rules`).
- **Facts** — only what you established, anchored; never your reasoning. Commands are written
  resolved: `spec-check` with its full path.
- **Skills** — the step's `skills` in `workflow.yaml` and those the conversation named since; each
  with its when. `atlas` set → `my-workflow:audit-truth query <question>` — a fact not under Facts.
- Nothing of the role's craft: the agent's definition holds it. An empty section is omitted.
- Written once, straight into the agent call; never printed first.
- **Follow-up** — a continued agent gets Goal, Tasks, Verification and any section that changed. A
  new agent gets every section, the earlier artifact named under Facts.

## Per stage

### test — `spec-tester`

- **Tasks:** one line per `AC`, its sentence copied from `spec.md`.
- **Read first:** the criteria in `spec.md`; the design's Interface and contracts, where it has
  them; a bug: the Reproduction.
- **Facts:** the test runner, its command, where tests live, a test to copy.
- **Done when:** every `AC` a test can reach has one, run: failing for missing behaviour, passing
  for what must not change.
- **Deliver:** per `AC`: test file · command · its result line; an `AC` no test can reach: the
  evidence kind that fits. Then gaps with their evidence, `Q`s.

### implement — `spec-implementer`

- **Tasks:** the `T` rows in order, copied from `tasks.md`; a fix round: the review's issues.
- **Read first:** the criteria served in `spec.md`; the design files of the units touched.
- **Facts:** the acceptance tests and their failing run, or that none exist; the pattern to copy;
  the format, lint and type-check commands.
- **Done when:** the tasks' tests, lint and type-check pass, each as its command and result.
- **Deliver:** per `T`: files touched; per `AC` served: evidence command → result, or
  `observed: <what was done and seen>`; a fix round: per `I`, the files touched and the `T` they
  belong to. Then gaps with their evidence, `Q`s.

### design review — `spec-design-reviewer`

- **Tasks:** review `design.md` and `design/` against `spec.md`.
- **Read first:** `spec.md`, `design.md`, `design/`; the answers file,
  `../../spec-design/references/answers.md` from this folder, resolved.
- **Facts:** the `spec-check design` command and its last result.
- **Done when:** every finding carries an anchor; a verdict is set.
- **Deliver:** verdict · issues, most severe first, each `I-<n>` · severity · anchor · problem ·
  fix · `Q`s.

### review — `spec-code-reviewer`

- **Tasks:** review the change: the working tree against `<base>`, untracked files included (no
  git: the files `tasks.md` lists); check each task `tasks.md` marks done.
- **Read first:** `spec.md`, the design, `tasks.md`.
- **Facts:** the evidence, lint and test commands; the `spec-check coverage --run` command; second
  round: the earlier `I` ids.
- **Done when:** the checks rerun; every finding reproduced or marked "read, not run"; a verdict
  set.
- **Deliver:** the report in your template.
