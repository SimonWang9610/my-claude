# my-workflow

A spec-driven software workflow for Claude Code and GitHub Copilot, for any language or framework.
Use it three ways: let **drive-spec** lead a task end to end, run one **step skill** at a time, or
ground unfamiliar code first with **code-auditor**.

## Install

```bash
python3 setup.py install --tools claude,copilot --plugins my-workflow
```

Run it from a clone of this repo. Needs Claude Code 2.1.219 or later.

## 1 · Drive a task: `/my-workflow:drive-spec`

```text
/my-workflow:drive-spec add rate limiting to the upload API
```

drive-spec decides the kind of task, creates the spec folder and runs that kind's steps:

| Step | Skill | Feature | Bug | Improvement |
|---|---|---|---|---|
| 1 | `spec-requirements` · `spec-diagnose` | user stories and acceptance criteria, clarified with you first | reproduce, root cause, fix options | current vs target with a measure; what must not change |
| 2 | `spec-design` | module, component or system level | only when the fix leaves a design choice open | only when it leaves a design choice open |
| 3 | `spec-plan` | tasks, batches, delegation | reproduction test, then the fix | steps each shippable alone |
| 4 | `spec-implement` | acceptance checks first, then the code | failing reproduction first | checks green before and after |
| 5 | `spec-review` | tests, validation per criterion, code review | reproduction re-run, regression | behaviour preserved, target measured |

You answer at most two gates: after step 1 (with the design when it runs), and before agents start
building. A small task is sized light: one `spec.md` plus `tasks.md`, no gate.

### The spec folder

`specs/<task>/` (git-ignored unless you want it committed, or under a location you name):

| File | Written by | Holds |
|---|---|---|
| `workflow.yaml` | drive-spec, then each step | kind, size, branch, artifact paths, each step's status, model and mapped skills |
| `spec.md` | step 1 | stories, acceptance criteria, limits, decisions (a bug: the diagnosis) |
| `clarifications.md` | step 1, optional | what was vague or in conflict, and the answers |
| `design.md` | `spec-design` | the design at its level, with diagrams and wireframes |
| `tasks.md` | `spec-plan`, always | tasks, batches, coverage, progress |
| `review.md` | `spec-review`, only when not accepted | checks, criteria, issues |
| `questions.md` | drive-spec | a sidebar log of what you asked mid-spec and how it was resolved |

Statuses show as symbols, with the legend at the top of `workflow.yaml`. A question that ends in a
decision is saved in `spec.md` and referenced from `questions.md`. To change direction, just say so;
drive-spec checks the impact, offers options and revises the spec. To resume, run drive-spec again.

## 2 · Run one step

Every `spec-*` skill picks its mode itself. With a `workflow.yaml` it checks that it is the current
step, uses the skills mapped to it, saves its artifact and updates its status. Without one it runs the
same procedure on your request and returns the result in the session.

```text
/my-workflow:spec-diagnose uploads fail with a 500 after the second retry
/my-workflow:spec-review the diff on this branch
/my-workflow:spec-design which approach for offline sync?
```

## 3 · Standalone skills

They work without a spec and never save a spec file. The step skills use the last four as companions.

| Skill | Use it to |
|---|---|
| `rephrase <prompt>` | Put the main objective of a long prompt, or of the conversation so far, first. |
| `discuss <topic>` | Talk a problem through and draft a direction a later session can spec. |
| `audit-truth <question>` | Find out how something works, where it lives, or whether a claim is true. |
| `scaffold-project-structure` | Lay out a project by its kind, or fit new code into an existing layout. |
| `design-component` | Design components by the decision each hides. |
| `analyze-ui-state` | Decide where each piece of UI state lives and how it changes. |

## 4 · Ground unfamiliar code first: `code-auditor`

```bash
claude --agent my-workflow:code-auditor "billing, to add refunds"
```

It maps the area into an atlas (an index plus a note per flow and structure, anchored to the source)
and ends with a line to paste into a new session: `Atlas: <path>/INDEX.md — read it before the
source.`

## Your stack's skills

my-workflow names no language or framework. When a spec starts, drive-spec detects the stack and maps
the skills you have installed to the steps they can help, in `workflow.yaml`:

```yaml
- id: implement
  skill: spec-implement
  skills:
    - { name: <your React components skill>, why: React components in scope }
```

A mapped skill is available, not mandatory: a step uses it only where it serves the step's goal, and
drive-spec names the relevant ones in each agent's brief. Add or remove one by saying so. Rules come
from, first match: your project's rules (CLAUDE.md, AGENTS.md, `.claude/rules`, ADRs), the mapped
skills, built-in knowledge. API facts come from a documentation tool at your stack's version, else
official docs.

To write a skill drive-spec will map, name the stack and the job (design, implement, test, review)
in its description.

## Agents

| Agent | Owns | Writes | Model · effort |
|---|---|---|---|
| `spec-architect` | the design step | `design.md` | opus · high |
| `spec-tester` | the acceptance checks | acceptance test files | set per batch by the plan |
| `spec-implementer` | one batch of tasks | its batch's files | set per batch by the plan |
| `spec-reviewer` | the verdict | nothing | opus · high |
| `code-auditor` | a codebase atlas; runs on its own | the atlas | opus · medium |

drive-spec dispatches the first four. The tester and implementer have no preset model: a batch the
plan marks complex runs on the stronger model, the rest on the standard one.
Copilot ignores the model names and runs agents on your session model.

## How it adapts

- **Your instructions come first.** A decision you state is kept, a path you name is read, "quick" or
  "deep" sets the size, and "just do it" skips the stops.
- **Role fills the gaps.** drive-spec infers senior or junior from how you write. Say "as junior", or
  put `my-workflow role: junior` in CLAUDE.md, to change it.
- **Claims are checked.** A statement the work rests on is verified first; a wrong one is corrected
  with evidence.
- **Steps and limits are defaults.** The model skips, merges or exceeds them when a task calls for
  it, and says why.

## Changes in 2.0

- drive-spec works by task kind (feature, bug, improvement) and starts every spec with a
  `workflow.yaml`; the fast and full tracks are now the light and standard sizes.
- Step skills are renamed and write their own artifacts: `decide` → `spec-design`, `build` →
  `spec-plan` and `spec-implement`, `verify` and `critique` → `spec-review` (acceptance checks are
  written in `spec-implement`). New: `spec-requirements`, `spec-diagnose`.
- Requirements are user stories with given/when/then acceptance criteria (`US`, `AC`); `R` is kept
  for limits.
- New `questions.md`, `clarifications.md` and `tasks.md`; the plan no longer lives in `spec.md`.
- Templates moved into each skill's `assets/`; `shared/kinds.md` and `shared/principles.md` moved
  into the skills that use them.
- Agents state what they own, their inputs, a procedure and when to escalate.
- Installed stack skills are mapped per step and may be run, not only read for rules.
