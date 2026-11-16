---
name: design-component
description: >-
  Use this skill when the user is splitting a system into parts or placing a boundary: "what
  components do we need", "should these be one", "which way should this dependency point", "this
  class does too much", even if they never say "component". Designs units by the decision each
  hides: responsibility, input, output, boundary, dependencies. Not for folder layout (use
  my-workflow:scaffold-project-structure).
argument-hint: "[scope or unit]"
---

# design-component

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (else `../../shared/`), read once per
conversation. Other paths: this folder.

## Steps

1. **Ground** — existing units and imports (`/my-workflow:audit-truth`).
2. **Changes** — up to 5 the requirements make likely, each anchored; never invent one.
3. **Units** — each hides one decision likely to change behind an interface simpler than what it
   hides, or wraps an external system as a port. Per unit: responsibility · input · output ·
   boundary.
4. **Edges** — direction and kind (call · event · implements); depend on what changes less. A cycle
   → invert an edge through an interface its consumer declares, or extract the shared part.
5. **Walk** — each change should touch one unit plus its new consumers; more → merge, split or move
   once, else a `Q`.
6. **One unit's inside**, when asked — interface (operations, errors, invariants), state and its
   disposal, failure, contract tests and fakes.
7. **Write** — § Units (unit · anchor · responsibility · input · output · boundary · change ·
   delivers), § Dependencies (flowcharts, edges labelled), the walk.

## Check before writing

One hidden decision per unit · no cycle · no reach into internals · no pass-through layer, split by
execution order, or unit smaller than a human needs.
