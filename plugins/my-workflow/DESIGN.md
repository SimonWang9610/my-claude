# my-workflow: a development workflow for trusting agent-written code

For install and commands see [README.md](README.md).

## Abstract

Coding agents now write software faster than people can review it. The person who used to trust
code because they wrote it must now trust code they did not write. my-workflow is a plugin for
Claude Code and GitHub Copilot that answers this with one claim: **trust should rest on evidence
about behaviour, and each rule should be enforced by the strongest thing able to enforce it.** The
plugin turns that claim into eight mechanisms: criteria backed by evidence, two human gates, a
script that decides each step's gate, a design made of bounded units, working slices built test
first, fresh-context agents, approved workarounds, and a map of existing code. This document
states the problem, explains each mechanism and why it has its shape, and names what the design
cannot do.

## 1. Introduction

Software work has a familiar shape: requirements, design, plan, implement, test, review. For decades
the developer who wrote the code could stand behind it, because writing it built the detailed
knowledge that made it trustworthy. Confidence was a by-product of authorship.

Agents can now do the implementing. That removes authorship as the source of confidence and moves
the developer's leverage upstream: clear requirements and a good design are how a person steers
what an agent builds.

| Stage | Before | With agents |
|---|---|---|
| Requirements | stakeholders, product managers | stakeholders, product managers, **developers** |
| Design | architect | architect, **developers** |
| Plan | project managers | developers with agents |
| Implement | developers | **agents** |
| Test | QA | agents, checked by script where possible |
| Review | architect, staff developers | humans, reading verification evidence |

The shift creates four risks:

| Id | Risk |
|---|---|
| R1 | Output arrives faster than humans can review it. |
| R2 | Nothing reliably confirms the output meets the requirements. |
| R3 | Code quality is hard to judge. |
| R4 | Humans can hardly continue the work if the models become unavailable. |

The goal is a workflow for any language whose results are verifiable, deterministic where possible
and maintainable, so a person can steer the direction and trust the outcome without reading every
line.

## 2. Approach

An agent saying "done" is not a reason to trust the work. Two things are.

The first is **evidence about behaviour**: something that can be run again, or something recorded
that a person can judge.

The second is **where a rule lives**. A rule is only as reliable as what enforces it. In order of
strength:

1. the project's own tools: tests, linter, type-checker;
2. one script that reads the spec files and decides each step's gate;
3. written instructions to the agent, kept for judgement no tool can make.

A rule belongs in the highest layer that can hold it. Each mechanism below applies one of these two
ideas to one or more of the risks.

| § | Mechanism | Risks |
|---|---|---|
| 3 | Criteria with evidence | R2 |
| 4 | Two human gates | R1 |
| 5 | A script decides the gates | R2, R3 |
| 6 | Bounded units and one diagram | R3, R4 |
| 7 | Working slices, test first | R1, R2 |
| 8 | Fresh eyes | R2, R3 |
| 9 | Approved workarounds | R3, R4 |
| 10 | An atlas of existing code | R4 |

## 3. Criteria with evidence

**Problem.** A requirement written as a paragraph cannot be checked. "It works" is whatever the
author says it is.

**Mechanism.** Each requirement becomes a one-sentence acceptance criterion, `When <trigger>,
<observable result>`, with a stable id such as `AC-1.2`. A criterion may belong to a user story
(`US-1`) or stand alone. Each carries exactly one evidence line, the strongest kind that fits:

1. a test in the project's own suite;
2. an existing project command whose result shows it, such as a build, type-check or benchmark;
3. an observation: the product was run, and what was seen is recorded.

Ids make the path from requirement to code traceable:

```mermaid
flowchart LR
  US["US- story"] --> AC["AC- criterion"]
  AC --> UNIT["UNIT- design unit"]
  UNIT --> T["T- task"]
  T --> CODE["code files"]
  AC --> EV["evidence"]
  CODE --> REPORT["coverage.md"]
  EV --> REPORT
```

**Rationale.** A test in the suite keeps guarding the behaviour after the spec is closed, and it
survives the agent's context being lost. A script written only to satisfy a spec would be thrown
away, so the workflow never writes one. Observation is allowed because some behaviour has no
harness; it is the weakest kind, and the report marks it "yours to judge".

**Limit.** Evidence shows a criterion holds. It cannot show the criterion was the right one to
write.

## 4. Two human gates

**Problem.** A person cannot review everything, and correcting direction after the code exists is
the expensive moment to do it.

**Mechanism.** The person approves two things before any code is written: the requirements (for a
bug, the diagnosis) and the design. Before each gate the agent settles what is open: questions with
their defaults, options to choose between, conflicts with what the person said. Design options are
weighed in conversation; the design file records only what was chosen. Anything that needs an
answer leads the reply under a **Needs you** line, because a file can record a question but cannot
ask it.

**Rationale.** These are the two cheapest places to change direction, and the two steps where the
person's judgement cannot be replaced. After them the criteria define "right", so the remaining
steps are gated by the script alone. A person may grant the gates in advance ("just do it"), in
which case a passing check approves.

**Limit.** A gate is only as good as the attention given to it. Keeping the artifacts short is the
design's main defence.

## 5. A script decides the gates

**Problem.** An agent that judges its own step complete will sometimes be wrong, and will sound the
same either way.

**Mechanism.** `scripts/spec-check.py` reads the spec files and exits non-zero when something is
missing. No step is done while it fails.

| After | It fails when |
|---|---|
| requirements | an id is defined twice or never; a story has no criterion |
| design | a unit has no responsibility; the diagram and the unit list disagree; a diagram shows more than six units; there is a dependency cycle; a criterion is delivered by no unit |
| plan | a criterion or changed unit is served by no task |
| implement, review | a criterion is not built (its tasks done, their files in the repo) or its evidence does not pass |

It also writes `coverage.md`, the report the person reviews: per criterion, whether it is built and
what evidence backs it.

**Rationale.** An exit code cannot be argued with. The script checks only what a script can
decide and leaves the rest labelled as judgement.

**Limit.** It confirms that evidence exists and passes. It does not judge whether a test truly
proves its criterion or whether a design is good.

## 6. Bounded units and one diagram

**Problem.** Code nobody understands cannot be judged or taken over.

**Mechanism.** The design is a short table of units. Each unit has one responsibility it solely
owns, an anchor in the code, and the criteria it delivers. One dependency diagram shows what
depends on what, with at most six units; a larger design splits into groups. Further detail, such
as a boundary or an interface, is written only for the units that need it.

**Rationale.** Someone taking the work over needs three answers: what exists, what each part owns,
and what depends on what. Dependencies are stated once, in the diagram, so no two documents have to
be kept in agreement. Six units is the point past which a diagram stops being read.

**Limit.** The script checks the shape of a design, not its quality. That remains the person's
judgement at the design gate.

## 7. Working slices, test first

**Problem.** A large change is hard to review and hard to stop halfway.

**Mechanism.** The plan is a list of tasks. Each task makes at least one criterion's evidence pass
and leaves the project working. Inside a task the test comes first:

```mermaid
flowchart LR
  CHECK["Write the criterion's test<br/>in the project's suite"] --> RED{"Fails for the<br/>missing behaviour?"}
  RED -->|"no: fix the test"| CHECK
  RED -->|"yes"| CODE["Write the code<br/>per the design's units"]
  CODE --> LINT{"Format, lint and<br/>the test all pass?"}
  LINT -->|"no"| CODE
  LINT -->|"yes"| ROW["Mark the task done,<br/>record the files touched"]
  CODE -.->|"design does not fit, or a<br/>test must be loosened"| ASK{{"Stop: you decide"}}
```

**Rationale.** A slice that works on its own is small enough to review and safe to stop after. A
test seen failing first proves the test can fail. The task list doubles as the map from each
criterion to the files that realize it.

**Limit.** "It failed first" is a written rule. Nothing scripted proves it.

## 8. Fresh eyes

**Problem.** An author's tests can pass for the wrong reason, and an author's review inherits the
author's blind spots.

**Mechanism.** Two agents work without the author's reasoning. `spec-tester` writes the acceptance
tests from the criteria alone, before the code. `spec-reviewer` reruns the evidence, repeats each
observation, reproduces every finding before reporting it, looks for tests weakened after they were
written, and names what would prevent each issue's class: a lint rule, a type or a test. At the
design gate the person may ask the reviewer for a second opinion.

```mermaid
sequenceDiagram
  participant U as You
  participant D as drive-spec
  participant A as spec-architect
  participant R as spec-reviewer
  participant T as spec-tester
  U->>D: task
  D->>U: requirements (gate)
  U-->>D: approve
  D->>A: design
  A-->>D: design.md
  D->>U: design (gate)
  opt you ask for a second opinion
    D->>R: review the design
    R-->>D: verdict
    D->>U: verdict
  end
  U-->>D: approve
  D->>T: write the acceptance tests
  T-->>D: failing tests
  D->>D: implement against them
  D->>R: review the work
  R-->>D: report
  D->>U: coverage.md, verdict
```

**Rationale.** Independence is the cheapest check on an author. While this plugin was being built,
a fresh-context review found 20 inconsistencies the authoring context had missed.

**Limit.** A reviewer is still a model. Its findings count only when reproduced.

## 9. Approved workarounds

**Problem.** When a design does not fit the code, the easy path is a quiet shortcut: a suppressed
lint, a loosened test, a special case. The next agent copies whatever the codebase contains, so the
shortcut becomes the pattern.

**Mechanism.** When the design cannot be built as written, or a test or lint would have to be
loosened, the agent stops and asks. An approved workaround is recorded with its reason and the
condition for removing it. A criterion that cannot be evidenced needs a waiver, approved the same
way. The script fails while either is unapproved, and granting the gates in advance never covers
them.

**Rationale.** A few recorded exceptions are maintainable. Unrecorded ones are how a design decays.

**Limit.** The agent must recognise that it is taking a shortcut. That is judgement, backed by the
reviewer.

## 10. An atlas of existing code

**Problem.** A design made against code that was guessed at often cannot be built.

**Mechanism.** `audit-truth` maps existing code as units, each described as what it receives, what
it solely owns and what it delivers, with a dependency graph. The map is saved and read in three
tiers: an index, then unit entries, then the source through their anchors. Later steps open only
the units they need.

| Mode | Does |
|---|---|
| `build` | maps a scope top-down; smaller units are revealed only where a question needs them |
| `query` | answers from the atlas; on a miss reads exactly that spot and adds it |
| `distill` | lifts the relevant units from another atlas, with no source read |

**Rationale.** Every step grounds itself in the same map instead of exploring again, and the map
is something a person can read.

**Limit.** This is the least proven mechanism. Nothing yet measures how much exploration it saves.

## 11. The workflow as a whole

`drive-spec` decides the kind of task (feature, bug or improvement), creates the spec folder and
runs the steps in order. Each step skill also works on its own, without a spec.

```mermaid
flowchart TD
  START["Your task"] --> SETUP["Setup: kind, size, folder, workflow.yaml"]
  SETUP --> REQ["1 Requirements<br/>(bug: diagnose)"]
  REQ --> C1{"spec-check ids"}
  C1 -->|"fail"| REQ
  C1 -->|"pass"| G1{{"You approve?"}}
  G1 -->|"revise"| REQ
  G1 -->|"yes"| DES["2 Design<br/>options weighed with you"]
  DES --> C2{"spec-check design"}
  C2 -->|"fail"| DES
  C2 -->|"pass"| G2{{"You approve?"}}
  G2 -->|"revise"| DES
  G2 -->|"yes"| PLAN["3 Plan"]
  PLAN --> C3{"spec-check plan"}
  C3 -->|"fail"| PLAN
  C3 -->|"pass"| IMPL["4 Implement"]
  IMPL --> C4{"spec-check coverage"}
  C4 -->|"fail"| IMPL
  C4 -->|"pass"| REV["5 Review"]
  REV --> C5{"coverage passes,<br/>verdict accept"}
  C5 -->|"fixes"| IMPL
  C5 -->|"yes"| DONE["Done: you review coverage.md,<br/>the units and the workarounds"]
```

| Step | Skill | Feature | Bug | Improvement |
|---|---|---|---|---|
| 1 | `spec-requirements` · `spec-diagnose` | stories and criteria, clarified first | reproduce, root cause, fix options | current vs target; what must not change |
| 2 | `spec-design` | units and their diagram | only when a choice is open | only when a choice is open |
| 3 | `spec-plan` | tasks, each a working slice | reproduction test, then the fix | steps each shippable alone |
| 4 | `spec-implement` | test first, then the code | failing reproduction first | tests green before and after |
| 5 | `spec-review` | evidence rerun, code review | reproduction rerun, regression | behaviour preserved, target measured |

The workflow scales down. A small task with an existing pattern to follow runs "light": one spec
file, one gate, no agents. It also adapts: a decision the person states is kept, a claim the work
rests on is verified first, and steps and numeric limits are defaults the agent may skip or exceed
with a one-line reason. Rules worded "never" or "only with approval" are not defaults.

At the end the person reviews three things: `coverage.md`, the units with their diagram, and the
approved workarounds.

## 12. What was left out

Each of these was built or considered, then removed because nothing showed it helped:

- **A check script per spec.** Evidence belongs in the project's own suite.
- **Spec ids inside product tests.** They go stale once the spec is closed.
- **A required "functionality" layer** between criteria and units. It is optional (`FN-1`); most
  specs map criteria straight to units.
- **Input and output prose per unit.** It repeated the diagram's edges.
- **Parallel implementer agents.** Speeding up a loop that has not yet proven itself adds risk.
- **Design levels, a senior or junior role, per-step model and skill settings, a prompt-routing
  hook.** The model, the agent definitions and the skill descriptions already handle these.

## 13. Limitations

- The workflow cannot prove the requirements themselves are right.
- Whether a test truly proves its criterion, and whether a design is good, remain judgements made
  by the reviewer and the person.
- The mechanisms have been tested piece by piece, mainly the script on sample specs. **The workflow
  has not yet been run end to end on a real task**, so the claims in the rationale paragraphs are
  reasoned, not measured.

## 14. Conclusion

The plugin does not try to make agents trustworthy. It makes their output checkable: every
requirement is a criterion, every criterion has evidence, a script refuses to move on without it,
and a person approves the two decisions that set the direction. The design stays small by one rule
for adding anything:

1. If the project's tools can hold it, it belongs in the project, not here.
2. If the script can hold it, it goes in the script, with a helpful failure message.
3. Otherwise it is a written instruction, and it needs evidence: a failure it would have prevented,
   or a decision by the team.

## Appendix A. Ids

| Id | Is | Lives in |
|---|---|---|
| `US-1` | user story | `spec.md` |
| `AC-1.1` | acceptance criterion of `US-1` (`AC-7`: standalone, no story) | `spec.md` |
| `FN-1` | functionality, optional: one capability that serves several criteria | `spec.md` |
| `UNIT-1` | design unit | `design.md` |
| `T-1` | task | `tasks.md` |
| `WA-1` | approved workaround | `spec.md` |

## Appendix B. The spec folder

`specs/<task>/`, git-ignored unless you want it committed, or under a location you name.

| File | Written by | Holds |
|---|---|---|
| `workflow.yaml` | drive-spec, then each step | kind, size, branch, artifact paths, each step's status and gate |
| `spec.md` | step 1 | stories, criteria with their evidence, limits, decisions, approved workarounds and waivers |
| `design.md` | `spec-design` | the chosen approach, the units, the dependency diagram, decisions |
| `design/` | `spec-design` | only when needed: a file per group of units, plus contracts, screens and flows |
| `tasks.md` | `spec-plan` | tasks with the ids and files of each, progress |
| `coverage.md` | `spec-check` | per criterion: built, evidenced, the files |
| `review.md` | `spec-review`, only when not accepted | evidence results, coverage gaps, issues |
| `atlas/` | `audit-truth` | the existing code this spec touches, as units |
| `discussions.md` | only once you have discussed something | what was weighed and why the rest lost |
| `scratch/` · `evidence/` | the steps | probes and measurements; output an observation cites |

## Appendix C. The parts of the plugin

| Part | What it holds |
|---|---|
| `drive-spec` | the order of steps, the gates, when to stop |
| Six `spec-*` skills | how each step is done |
| `shared/` | rules every skill follows: ids, evidence, output, workarounds |
| Templates in each skill's `assets/` | the fixed file formats the script reads |
| `scripts/spec-check.py` | the gates |
| Standalone skills | `audit-truth`, `design-component`, `analyze-ui-state`, `scaffold-project-structure`, `discuss`, `rephrase` |

| Agent | Owns | Writes | Model · effort |
|---|---|---|---|
| `spec-architect` | the design step | `design.md`, the spec's atlas | opus · high |
| `spec-tester` | the acceptance tests, before any code | test files in your suite | session |
| `spec-reviewer` | the verdict, on a design or on code | nothing | opus · high |
| `code-auditor` | a codebase atlas; runs on its own | the atlas | opus · low |

Copilot ignores the model names and runs agents on the session model.
