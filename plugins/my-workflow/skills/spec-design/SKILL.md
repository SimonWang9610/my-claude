---
name: spec-design
description: >-
  Designs what a spec needs before building, at the level the change calls for: module (one unit's
  interface and inside), component (several units, their interfaces, interactions and screens, with
  wireframes) or system (several deployables, contracts, data and migration), with options and one
  recommendation where the approach is open, diagrams and mockups to match, checked against the
  stack's limits, as design.md. Use as the design step of a spec, or on "which approach", "which
  stack", "how should we structure this", "design X". Not for reviewing a design (use
  my-workflow:spec-review).
argument-hint: "[question or requirements | path to a workflow.yaml]"
---

# spec-design

Follow `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (if shown unexpanded: `../../shared/conventions.md`
from this skill's folder). Other paths are relative to this skill's folder.

1. **Context** — per the conventions' Spec mode; the input is the spec (stories, criteria, limits,
   decisions; a bug: its root cause and fix options).
2. **Level** — the highest that applies; it sets the sections and their detail (the table in
   `assets/design.md`), and in spec mode the step's `level`:
   - **module** — the change stays inside one unit.
   - **component** — ≥2 units that depend on each other, a new unit's interface no existing pattern
     covers, or screens.
   - **system** — several deployables, or a public contract or stored data changes.
3. **Ground** — `/my-workflow:audit-truth` on what the design touches. The existing patterns are the
   default design; deviating takes a `D` with the reason.
4. **Approach** — only when a choice is open (the stack included, when neither given nor
   detectable): 2–3 realistic options weighed on the limits, the team's familiarity, ecosystem and
   running cost; one recommendation and what would change it. A choice the spec holds as a `D` is
   designed from it, with no options.
5. **Parts** — the level's sections, in the template's order, each answering what
   `references/answers.md` lists for the project's kind and no more:
   - structure (a new project or area, or code with no home) →
     `/my-workflow:scaffold-project-structure`
   - components → `/my-workflow:design-component`
   - contracts and data — shape and version, errors and failure per boundary, the data's owner,
     migration steps each shippable alone with a rollback
   - screens — one wireframe per screen in a `text` block, with its loading, empty and error states
   - UI state (state that outlives one interaction) → `/my-workflow:analyze-ui-state`

   Reconcile once: every fact has one owner, components fit the structure, each shared state unit has
   one owning component. A diagram only where its table leaves the structure or flow unclear.
6. **Limits** — ask the conventions' Knowledge sources for the limits that shape structure, state,
   concurrency and lifecycle; map each part's roles to the stack; a limit that breaks a part → revise
   it with a `D`. § Quality: one line per axis the spec's limits name.
7. **Write** — `assets/design.md`, with § Coverage showing where each story or criterion is met. When
   options ran, the first new `Q` is the pick, defaulting to the recommendation. A requirement the
   design shows must change → a `Q`, never a silent adjustment. `Open:` the questions and any
   requirement that must change.
