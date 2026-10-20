---
name: decide
description: >-
  Designs what a task needs before building: the approach (options, one recommendation) and only the
  parts it needs (product, project structure, components, UI state) in one design.md. Use when a spec
  routes to decide, for a new project, or on "which approach", "how should we structure this". Not for
  reviewing a design (use my-spec:critique).
argument-hint: "[question or requirements]"
---

# decide

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Input** — the spec (an argument adds to it); no spec and the argument is not a self-contained
   question → `/my-spec:start` first.
2. **Parts** — pick only what the task needs:
   - approach — an open choice: 2–3 realistic options, one recommendation.
   - product — several systems or deployables: `templates/design.md` § Product.
   - structure — a new project or area, or code with no home → `/my-spec:scaffold-project-structure`.
   - components — ≥2 units that depend on each other, or a new unit's interface no existing pattern
     covers → `/my-spec:design-component`.
   - UI state — screens whose state outlives one interaction → `/my-spec:analyze-ui-state`.

   ≥2 of structure, components and UI state, or a new project, you are not the `designer` and you can
   spawn → hand this stage to the `designer` agent and gate on its report.
3. **Ground** — `/my-spec:explore` on what the chosen parts touch. The existing patterns are the
   default design; deviating takes a `D` line with the reason.
4. **Design** — approach first; the parts follow the recommendation. Run each part's skill with the
   spec, the facts and the next free ids; each returns its section. Reconcile once: every fact has one
   owner, components fit the structure, each shared state unit has one owning component.
5. **Write** — `design.md` per `templates/design.md`; save per the conventions; gate (when options
   ran, the first new `Q` is the pick, defaulting to the recommendation). Next: the spec's route.
