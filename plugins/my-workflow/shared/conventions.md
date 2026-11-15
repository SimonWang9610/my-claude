# my-workflow conventions

The rules every skill shares. Steps are defaults, not a script: skip, merge or reorder any step the
task does not need, and say which in one line. Numbers in a skill (counts, budgets, caps) are defaults
too: go past one when the task needs it, with the reason in one line. Rules worded "never" or "only
with a `D`" are not defaults.

## Spec mode

A `spec-*` skill picks its mode itself and says which in one line. Its other steps are the same in
both modes.

- **Spec mode** — a `workflow.yaml` is named, or exactly one spec under `specs/` is in progress
  (several → the one whose `branch` is checked out, else ask):
  1. Read it: kind, size, `folder` and the artifact paths inside it, and this step's `skills` and
     `model`.
  2. Stage check: every earlier step is done or skipped, and this step is `current` or is being run
     again. Else name the expected step and ask before going on.
  3. Mark the step in progress and `current`. When its work is complete, save the artifact from the
     skill's `assets/` template at the path `artifacts` names (size light → as a section of
     `spec.md`; the plan always in its own file), mark the step done and set `updated`. Moving
     `current` on is drive-spec's job; run alone, set it to the next step that is not skipped.
- **Standalone** — no `workflow.yaml`, or the user says "no spec": the input is the request, earlier
  results in the session, or files the user names (several versions → the latest). Return the result
  in the session and save nothing.

Only drive-spec and the step skills write spec files; every other skill returns its result. Inside an
agent, write only the files its definition names and return the rest. Code, tests and scaffolding are
the work itself and go where they belong.

## Status

pending · in progress · done · skipped · blocked, for the spec, its steps and task rows; a gate is
waiting or approved. Spec artifacts show each as the symbol in the legend at the top of
`workflow.yaml`; write the symbol there, the word everywhere else.

## Ids and facts

- Ids only where a result will be referenced later; a small result uses plain bullets. `US<n>` story ·
  `AC<n.m>` acceptance criterion of `US<n>` (`AC<n>` when there are no stories) · `R<n>` limit ·
  `D<n> <decision> — <why>` · `Q<n> <question> — default: <answer>` · `T<n>` task · `I<n>` issue.
  Assigned once, never renumbered; a dropped one stays as `<id> dropped — <why>`. A choice still open
  is a `Q`, never also a `D`. Continue from the highest id already in the session or the spec's files.
- A fact carries its anchor: `path:line`, `doc §`, `url (date)` or `run: <command> → <result>`; not
  read → (inferred).

## Questions

At most 3 questions whose answers would change the result most, each with its default (any others
listed as defaults). An answered or defaulted `Q` becomes a `D` in place, keeping its id. Inside an
agent or another skill, return the questions instead of asking them.

## Output

Markdown with short headings, one-line bullets and tables; an id leads its bullet; the why follows an
em dash; empty sections omitted. End with `Open:` — what is still unresolved (questions, gaps,
criteria not done), or `Open: nothing`.

## Knowledge

Analysis and design name roles; a library or tool appears only where a step maps a role to it (an
option, a `D`, the tree, a "maps to" or "enforced by" column, the spec's Context). Names and code
follow the project's existing patterns first, then, for the question the step asks:

- Rules: the project's rules (CLAUDE.md, AGENTS.md, `.claude/rules`, ADRs) → installed skills (spec
  mode: this step's `skills` list, which is available, not mandatory; standalone: one whose
  description names the detected stack and this step) → built-in knowledge. Use an installed skill
  only where it serves this step's goal: apply its rules, or run it for a section or a check. The
  step keeps its own file, gates and questions.
- API facts: a documentation tool (MCP) at the detected version → official docs, dated → built-in,
  marked (built-in).
- Name the sources you used in the output.

## Diagrams

Mermaid `flowchart`, `sequenceDiagram` or `stateDiagram-v2` only; flowchart labels in double quotes,
ids `[A-Za-z0-9_]`. Directory trees and screen wireframes in a `text` block. A table beside each
diagram carries the meaning.
