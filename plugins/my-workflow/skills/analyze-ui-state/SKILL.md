---
name: analyze-ui-state
description: >-
  Use this skill when the user is deciding where UI state lives or how it changes: "where should
  this state live", "should this be global", "what survives reload", "does this need a state
  machine", "why is this out of sync", for any UI framework. Decides each state's origin, owner,
  lifecycle, sharing and transitions. Not for component boundaries (use
  my-workflow:design-component).
argument-hint: "[screens, feature or requirement]"
---

# analyze-ui-state

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (else `../../shared/`), read once per
conversation. Other paths: this folder.

## Steps

1. **Screens** — the navigation map; per screen the facts it shows or edits. Existing code →
   `/my-workflow:audit-truth` on its routes and state owners first.
2. **State units** — facts that change together form one.
3. **Decide** per unit, only what no existing pattern answers:
   - Origin — derived · server · URL · draft · device or stream · client data with meaning · UI-only.
   - Placement — the lowest view all its readers share; app-wide only with a reason.
   - Lifecycle — created when, reset by which key, what survives back, reload and sign-out.
   - Sharing — pass down → compose → scoped injection → store: the lowest that works.
   - Derivation — computed where read, never stored.
   - Transitions — events named by intent; animations; where focus goes.
4. **Write** — § UI state: the navigation `flowchart`; per screen (and `App-wide`) a table (unit ·
   origin · owner · lifecycle · shared via · maps to) and a `Derived:` list; a `stateDiagram-v2` per
   unit with ≥3 states; a `sequenceDiagram` per optimistic write or server push.

## Check before writing

Every line of `references/checks.md` holds.
