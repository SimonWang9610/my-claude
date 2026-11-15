---
name: analyze-ui-state
description: >-
  Designs a UI's state per screen, framework-agnostic: origin, owner, lifecycle, sharing, derivation,
  transitions and animation, as a navigation map, state tables and diagrams. Use on "where should this
  state live", "should this be global", "what survives back or reload", "does this need a state
  machine". Not for component boundaries (use my-workflow:design-component).
argument-hint: "[screens, feature or requirement]"
---

# analyze-ui-state

Follow `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (if shown unexpanded: `../../shared/conventions.md`
from this skill's folder). Other paths are relative to this skill's folder.

1. **Screens** — the navigation map: shells, screens, tabs, modal routes, multi-step flows; per screen
   the facts it shows or edits. Existing code → `/my-workflow:audit-truth` on its routes and state
   owners first.
2. **Units** — group the facts into units: facts that change together form one unit; units refer to
   each other by id. Then per unit, only the questions an existing pattern does not already answer
   (cite the pattern instead):
   1. Origin — derived · server data · URL · draft (a local copy being edited) · device or live stream
      · client data with business meaning · UI-only (open, hovered, scrolled).
   2. Placement — the lowest view or screen all its readers share; app-wide only with a reason
      (distant readers, survives navigation, persisted).
   3. Lifecycle — created when, reset by which key, what survives back, reload and sign-out, destroyed
      when.
   4. Sharing — pass down → compose → scoped injection → app store: the lowest rung that works.
   5. Derivation — computed from its sources where it is read; never stored.
   6. Transitions — events named by intent and what each changes; a state diagram when a unit has ≥3
      states with different allowed events; animations (enter, exit, update; interruptible?); where
      focus goes.
3. **Map** — per unit its mechanism, from the project's patterns, then the conventions' Knowledge
   sources.
4. **Write** — § UI state: the navigation `flowchart`; per screen, plus `App-wide` for units above
   every screen, a table (unit · origin · owner · lifecycle · shared via · maps to) and a `Derived:`
   list; a `stateDiagram-v2` where 2.6 calls for one; a `sequenceDiagram` per optimistic write or
   server push. `Open:` the questions and the units with no owner yet.

Check before writing: every line of `references/checks.md` holds.
