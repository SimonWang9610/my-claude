---
name: analyze-ui-state
description: >-
  Use this skill when the user is deciding where UI state lives or how it changes: "where should this
  state live", "should this be global", "what survives back or reload", "does this need a state
  machine", "why is this out of sync", "how do I share this between screens", even if they never say
  "state". Works for any UI framework. Decides per screen each state's origin, owner, lifecycle,
  sharing, derivation and transitions, as a navigation map, state tables and diagrams. Not for
  component boundaries (use my-workflow:design-component).
argument-hint: "[screens, feature or requirement]"
---

# analyze-ui-state

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (unexpanded → `../../shared/conventions.md`).
Other paths are relative to this folder.

## Input

The screens, feature or requirement. Existing code → `/my-workflow:audit-truth` on its routes and
state owners first.

## Steps

1. **Screens** — the navigation map: shells, screens, tabs, modal routes, multi-step flows; per
   screen the facts it shows or edits.
2. **State units** — facts that change together form one unit; units refer to each other by id.
3. **Decide** — per unit, only the questions an existing pattern does not already answer (cite the
   pattern instead):

   | Question | Answer |
   |---|---|
   | Origin | derived · server data · URL · draft (a local copy being edited) · device or live stream · client data with business meaning · UI-only (open, hovered, scrolled) |
   | Placement | the lowest view or screen all its readers share; app-wide only with a reason (distant readers, survives navigation, persisted) |
   | Lifecycle | created when · reset by which key · what survives back, reload and sign-out · destroyed when |
   | Sharing | pass down → compose → scoped injection → app store: the lowest rung that works |
   | Derivation | computed from its sources where it is read; never stored |
   | Transitions | events named by intent and what each changes; animations (enter, exit, update; interruptible?); where focus goes |

4. **Map** — per unit its mechanism, from the project's patterns, then the conventions' Knowledge
   sources.
5. **Write** — § UI state:
   - the navigation `flowchart`;
   - per screen, plus `App-wide` for units above every screen: a table (unit · origin · owner ·
     lifecycle · shared via · maps to) and a `Derived:` list;
   - a `stateDiagram-v2` per unit with ≥3 states that allow different events;
   - a `sequenceDiagram` per optimistic write or server push.

## Check before writing

Every line of `references/checks.md` holds.

## Output

§ UI state. `Open:` the questions, the units with no owner yet.
