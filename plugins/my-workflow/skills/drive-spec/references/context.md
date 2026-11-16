# Spec context

How drive-spec sets a spec up and staffs it.

## Folder and branch

- Folder: `specs/<task>/`, `<task>` a short kebab-case name. `specs/` sits under a location the user
  named, else one the project's context files name (CLAUDE.md, AGENTS.md, README), else the project
  root. Add a new `specs/` to `.gitignore` unless the user wants it committed.
- Branch: propose `<kind>/<task>` from the current base; create it on a yes. No git, or the user
  declines → `branch: none`.

## Size

- **Light** — a few files, no open approach, an existing pattern covers it. No teammate; the design
  and review live in `spec.md`. In `workflow.yaml`: every `agent` → `none`; one gate: on the design
  step when it runs (then the first step's `gate` → `none`), else on the first step; `artifacts.design` and `artifacts.review` → `spec.md`. A
  question with no safe default makes it standard.
- **Standard** — everything else: one file per step, the gates the template lists.

## Role

The user's instructions set the workflow first: "quick" or "deep" sets the size and the grounding ·
"just do it" sets `gates: auto`. What they leave open is grounded at the role's depth:

| | senior (includes staff) | junior |
|---|---|---|
| Grounding | the touched area's units and their callers | map, then units, then callers |
| Questions | default and why | plus a one-line consequence per option |
| Light size | as sized | only when an existing example to copy was found |

Role, first match: stated ("as junior") · a `my-workflow role:` line in CLAUDE.md or AGENTS.md ·
inferred (paths, symbols, decisions or a named area → senior; only an outcome → junior; unclear →
senior). Show it as stated or inferred, so one word corrects it.

## Skills

Map the user's installed skills to the steps they can help:

1. Detect the stack (manifests, lockfiles, the request). List the installed skills from the session's
   skill listing, this plugin's standalone design skills included.
2. Per step, add a skill whose description names this stack or kind of work and the step's job
   (design, implement, test, review): `- { name: <skill>, why: <one line> }`. No fit → `[]`. Never map
   `rephrase` or `discuss`; never a skill for another stack.
3. Remap when the stack or scope changes, or the user adds or removes one.

## Delegation

| Teammate | Bring in when |
|---|---|
| `spec-architect` | step 1 shows several dependent units, screens, several deployables or a new project |
| `spec-reviewer` (design mode) | a standard-size design is written, before its gate |
| `spec-tester` · `spec-implementer` | the plan's Batches name them (a scaffold task runs first) |
| `spec-reviewer` (code mode) | review runs at standard size |

Otherwise run the step's skill yourself.

## Models

`model` per step: `session` (you run it), `strong` or `standard`. Strong for design, review and a
diagnosis whose root cause is low-confidence. `spec-tester` and `spec-implementer` carry no model:
pass each batch's model from the plan. Claude Code: strong → `opus`, standard → `sonnet`, as the
dispatch's model. Copilot runs agents on the session model.
