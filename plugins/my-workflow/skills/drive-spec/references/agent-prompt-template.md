# Agent prompt template

One prompt per delegation, written as you would brief a teammate who knows the craft: who they are
here, why the work matters, what is theirs, what you already know, and what you need back. The
agent's definition holds its craft; the prompt holds this run. A stage is a delegated step, or the
design review.

## Template

```markdown
# <stage> — <spec title> · <batch>

## Role
You are a <level> <discipline> <title> working in <tools>, <job>. Your concerns: <concerns>.

## Goal
<Why this matters, the outcome that ends this run, and what is easy to get wrong.>

## The work
- <id> <what to do> — serves <ids> · <files>
Not yours: <what to leave alone> · Your call: <what you may decide> · Bring back: <what you must not decide>

## What I know
- Spec: `<folder>/workflow.yaml` — <kind> · <size> · <stack>
- Read: <artifact paths>
- Code: `<branch>` against `<base>` · Atlas: `<path>/INDEX.md`
- <fact> — <anchor>
- <decision or limit that binds here> — <why>

## Skills
- `<skill>` — <when to use it>

## Done
- **Done when:** <command → expected result>
- **Send back:** <items, in a fixed shape>. Nothing else.
```

## Role

| Part | From |
|---|---|
| level | the work's reach, below |
| discipline | the row of the batch's domain in `domains.md` (`../../../shared/` from this folder) |
| title · job | the agent's row, below |
| tools | the batch's Domain cell in `tasks.md`, versions from the spec's `stack` |
| concerns | the few the work touches: the design and limits first, the row's examples second |

No batch (a review, a fix round) → the domains and tools of the files under work; a review names
each discipline.

| Agent | Title | Job |
|---|---|---|
| `spec-tester` | test engineer | writing acceptance tests for these criteria |
| `spec-implementer` | engineer | building these tasks |
| `spec-design-reviewer` | architect | reviewing this design |
| `spec-code-reviewer` | code reviewer | reviewing this change |

| Level | The work | Your call |
|---|---|---|
| senior | sits inside units the design specifies; the default | how each task is built |
| staff | spans 3 or more units, changes a contract others depend on, or improves existing units | also choices the design leaves open inside its units |
| lead | spans domains | also how its units work together, within their contracts |

- A review: staff; lead when the design is heavy or the change spans domains.
- At every level the task list, a unit's boundary and a contract are never the agent's call: they
  come back as gaps.

## Every stage

- **Title** — `· <batch>` only when the work is a batch.
- **Goal** — two or three sentences: the spec's Goal (a bug: what is expected, and the root cause),
  the outcome of this batch or review, and the one trap in it, from what the design weighed, an
  earlier batch's gap or a review issue. No trap known → leave it out.
- **The work** — after the items:
  - Not yours: what the work sits beside and must leave alone;
  - Your call: the level's row above; a test batch or a review → leave it out;
  - Bring back: a choice this work may surface that only the user makes. None known → leave it out.
- **What I know** — paths from the project root; then:
  - facts you established, anchored, with commands resolved: `spec-check` by its full path;
  - the spec's binding decisions, limits and approved workarounds, and what the user constrained,
    each with its reason, so the agent can apply it to a case it did not foresee.
- **Skills** — those of the step's `skills` in `workflow.yaml` that fit the work's tools, and those
  the conversation named since.

## Per stage

Read and Facts fill What I know.

### test — `spec-tester`

- **The work:** one line per `AC` of the batch, its sentence copied from `spec.md`
- **Read:** the criteria · the design's Interface and contracts · a bug: the Reproduction
- **Facts:** the test runner and its command · where tests live · a test to copy · earlier batches'
  test files
- **Done when:** every `AC` a test can reach has one, run: failing for missing behaviour, passing
  for what must not change
- **Send back:**
  - per `AC`: test file · command · its result line;
  - an `AC` no test can reach: the evidence kind that fits;
  - gaps with their evidence · `Q`s.

### implement — `spec-implementer`

- **The work:** the batch's `T` rows in order, copied from `tasks.md`
- **Read:** the criteria served · the design files of the units touched
- **Facts:** the acceptance tests and their failing run, or that none exist · the pattern to copy ·
  the format, lint and type-check commands · the files earlier batches touched
- **Done when:** the tasks' tests, lint and type-check pass, each as command → result
- **Send back:**
  - per `T`: files touched;
  - per `AC` served: evidence command → result, or `observed: <what was done and seen>`;
  - gaps with their evidence · `Q`s.
- **Fix round:**
  - The work: the review's `I` ids, one line each;
  - Read: `review.md`;
  - Send back, per `I`: files touched and the `T` they belong to.

### design review — `spec-design-reviewer`

- **The work:** review `design.md` and `design/` against `spec.md`
- **Read:** `spec.md` · `design.md` · `design/`
- **Facts:** the `spec-check design` command and its last result
- **Done when:** every finding carries an anchor · a verdict is set
- **Send back:** the verdict · issues, most severe first, each `I-<n>` · severity · anchor ·
  problem · fix · `Q`s

### review — `spec-code-reviewer`

- **The work:**
  - review the working tree against `<base>`, untracked files included; no git → the files
    `tasks.md` lists;
  - check each task `tasks.md` marks done.
- **Read:** `spec.md` · the design · `tasks.md`
- **Facts:** the evidence, lint and test commands · the `spec-check coverage --run` command
- **Done when:** the checks rerun · every finding reproduced or marked "read, not run" · a verdict
  set
- **Send back:** the report in your template
- **Second round:** Facts add the earlier `I` ids.

## Writing it

- Size each section to the work: a one-issue fix has a one-line Goal and one item. Role, the Spec
  line and Done always stay.
- Embed what must hold and what to do; give a path for what to consult.
- Never include: your reasoning about how to build it · the role's craft or standing rules, which
  the agent's definition holds · a rule the agent loads itself (CLAUDE.md, `.claude/rules`).
- Omit an empty section.
- Write it once, straight into the agent call; never print it first.
- A continued agent gets Goal, The work, Done and any section that changed.
- A new agent gets every section; earlier agents' work is listed under What I know, as files.
