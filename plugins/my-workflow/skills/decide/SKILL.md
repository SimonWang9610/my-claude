---
name: decide
description: >-
  Designs what a task needs before building: the approach or the stack (options, one recommendation)
  and only the parts it needs (product, project structure, components, contracts and data, UI state),
  checked against the stack's limits, as one design. Use for a new project, an open approach or on
  "which approach", "which stack", "how should we structure this". Not for reviewing a design (use
  my-workflow:critique).
argument-hint: "[question or requirements]"
---

# decide

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md` and
`shared/principles.md`.

1. **Input** — the requirements: a spec in the session or a file the user names, else the request when
   it is a self-contained question.
2. **Parts** — only what the task needs (`shared/kinds.md` § Design must answer, for its kind). A part
   whose decision the requirements already hold as a `D` is designed from it, with no options:
   - approach — an open choice, the stack included when it is neither given nor detectable: 2–3
     realistic options weighed on the limits, the team's familiarity, ecosystem and running cost; one
     recommendation.
   - product — several systems or deployables: `templates/design.md` § Product.
   - structure — a new project or area, or code with no home →
     `/my-workflow:scaffold-project-structure`.
   - components — ≥2 units that depend on each other, or a new unit's interface no existing pattern
     covers → `/my-workflow:design-component`.
   - contracts and data — an API, schema, file format or stored data changes → § Contracts and data:
     shape and version, errors and failure per boundary, the data's owner, migration steps each
     shippable alone with a rollback.
   - UI state — screens whose state outlives one interaction → `/my-workflow:analyze-ui-state`.
3. **Ground** — `/my-workflow:audit-truth` on what the parts touch. The existing patterns are the
   default design; deviating takes a `D` with the reason.
4. **Design** — in order: approach → structure → components → contracts and data → UI state; each
   follows the recommendation. Run each part's skill with the requirements, the facts and the next
   free ids; each returns its section. Reconcile once: every fact has one owner, components fit the
   structure, each shared state unit has one owning component. Each section answers what kinds.md
   lists for its kind and no more; a diagram only where its table leaves the structure or flow
   unclear.
5. **Finalize** — ask the conventions' Knowledge sources for the limits that shape structure, state,
   concurrency and lifecycle; map each part's roles to the stack; a stack limit that breaks a part →
   revise it with a `D`. § Quality: one line per axis the limits name, saying how the design meets it.
6. **Write** — return the design in `templates/design.md`'s shape. When options ran, the first new `Q`
   is the pick, defaulting to the recommendation. A requirement the design shows must change → a `Q`,
   never a silent adjustment. `Open:` the questions and any requirement that must change.
