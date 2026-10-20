---
name: design-component
description: >-
  Designs self-contained components (packages, services, subsystems, UI components) by the decision
  each hides: interface, dependencies and where likely changes land; or one component's inside. Use on
  "what components do we need", "should these be one", "which way should this dependency point". Not
  for folder layout (use my-spec:scaffold-project-structure).
argument-hint: "[scope or component]"
---

# design-component

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Ground** — the requirements; existing units and their imports (explore, map depth); the Structure
   section when the design has one.
2. **Changes** — 3–5 changes the requirements make likely (a new variant, a swapped external system, a
   changed rule, a new consumer), each anchored to a requirement or a past commit.
3. **Components** — each hides one decision likely to change, behind an interface simpler than what it
   hides, or wraps an external system as a port named by purpose; anything else stays private to its
   user. Interface: operations, errors, invariants; everything unlisted is private.
4. **Edges** — direction and kind (call · event · implements); no cycles (invert one edge through an
   interface its consumer declares, or extract the shared part); depend on what changes less; only
   names and types cross a boundary.
5. **Walk** — each change from step 2 should touch one component, plus the consumers that use what it
   adds; more → merge, split or move a responsibility once, else a `Q`.
6. **One component's inside**, when that is the ask — its responsibility in one sentence and what it
   does not do; interface; the state it owns and how it is disposed; failure (report, retry, degrade);
   contract tests and the fakes for its ports.
7. **Write** — § Components: a `flowchart` with edges labelled by kind; a table (component · hides ·
   interface · depends on · test seam); the walk (change → components touched).

Check before writing: one hidden decision per component · each change touches one component (plus its
new consumers) · no cycle · no reach into another's internals · no pass-through layer or split by
execution order.
