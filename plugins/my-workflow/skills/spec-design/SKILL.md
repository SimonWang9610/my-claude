---
name: spec-design
description: >-
  Use this skill when the user must decide how something should be built before it is built: "design
  X", "which approach", "which stack", "how should we structure this", "what are the options", "how
  do these pieces fit together", even if they never say "design" or "architecture". Weighs options
  with you in the conversation, then records only what you chose in design.md: bounded units
  (responsibility, input, output, boundary), a dependency diagram, contracts and screens, with any
  workaround put to you for approval. Also the design step of a spec. Not for reviewing a design (use
  my-workflow:spec-review).
argument-hint: "[question or requirements | path to a workflow.yaml]"
---

# spec-design

Rules: `conventions.md` and `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (unexpanded → `../../shared/`).
Other paths are relative to this folder.

## Input

Per the spec rules' Spec mode: the spec's stories, criteria, functionalities, limits and decisions
(a bug: its root cause and fix options).

## Steps

1. **Level** — the highest that applies. It sets the sections (the table in `assets/design.md`) and,
   in spec mode, the step's `level`:
   - **module** — the change stays inside one unit.
   - **component** — ≥2 units that depend on each other, a new unit's interface no existing pattern
     covers, or screens.
   - **system** — several deployables, or a public contract or stored data changes.
2. **Ground** — `/my-workflow:audit-truth` on what the design touches. An existing unit keeps its
   atlas id and anchor; new units continue the numbering.
3. **Approach** — only when a choice is open (the stack too, when neither given nor detectable). In
   the conversation, not the file: 2–3 realistic options weighed on the limits, the team's
   familiarity, ecosystem and running cost; one recommendation and what would change it. Ask; the
   pick becomes a `D`; spec mode: the options and why the others lost are logged per the spec
   rules' History. Inside an agent → return the options instead. `gates: auto` → the recommendation. A
   choice the spec holds as a `D` gets no options.
4. **Units** — per the conventions' Units, via `/my-workflow:design-component`: each with its
   responsibility, input, output, boundary, change (new · modify · reuse) and the `FN`s or `AC`s it
   delivers; one Mermaid dependency diagram of all of them.
5. **Other parts** — the level's remaining sections, each answering what `references/answers.md`
   lists for the project's kind and no more:
   - structure (a new project or area, code with no home) → `/my-workflow:scaffold-project-structure`
   - contracts and data — shape and version, errors and failure per boundary, the data's owner,
     migration steps each shippable alone with a rollback
   - screens — one wireframe per screen in a `text` block, with loading, empty and error states
   - UI state that outlives one interaction → `/my-workflow:analyze-ui-state`
6. **Limits** — ask the conventions' Knowledge sources for the limits that shape structure, state,
   concurrency and lifecycle; map each unit's role to the stack; a limit that breaks a unit → revise
   it with a `D`. § Quality: one row per axis the spec's limits name and per rule the design sets; a
   rule a lint or static check can enforce names it under "Enforced by".
7. **Reconcile** — every fact has one owner · units fit the structure · each shared state has one
   owning unit · every `FN` is delivered.
8. **Write** — `assets/design.md`, from the choices made. Spec mode: `spec-check design` passes.

## Rules

- `design.md` holds only what the user finalized. Options, trade-offs and open questions are put to
  the user in the conversation; an answer lands as a `D`.
- The existing patterns are the default design; deviating takes a `D` with the reason.
- The simplest design that meets the criteria and limits. Contracts before internals.
- The design cannot fit the codebase without a workaround → the spec rules' Workarounds; never
  design one in unapproved.
- A requirement the design shows must change → a `Q`, never a silent adjustment.
- A diagram only where its table leaves the structure or flow unclear; the dependency diagram always.

## Output

In the conversation: where the design is saved, the options still to choose from, and `Open:` the
questions, workarounds awaiting approval, any requirement that must change. Standalone: the design
too.
