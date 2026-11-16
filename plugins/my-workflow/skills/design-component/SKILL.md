---
name: design-component
description: >-
  Use this skill when the user is deciding how to split a system into parts or where a boundary goes:
  "what components do we need", "should these be one", "which way should this dependency point", "how
  do I split this module", "this class does too much", even if they never say "component". Designs
  units (packages, services, modules, UI components) by the decision each hides: responsibility,
  input, output, boundary, dependencies and where likely changes land; or one unit's inside. Not for
  folder layout (use my-workflow:scaffold-project-structure).
argument-hint: "[scope or unit]"
---

# design-component

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (unexpanded → `../../shared/conventions.md`).

## Input

The requirements; the Structure section when the design has one.

## Steps

1. **Ground** — existing units and their imports: `/my-workflow:audit-truth` on how the area is
   organised.
2. **Changes** — up to 5 changes the requirements make likely (a new variant, a swapped external
   system, a changed rule, a new consumer), each anchored to a requirement or a past commit. Fewer is
   fine; never invent one. None anchored → skip step 5 and keep the units minimal.
3. **Units** — per the conventions' Units. Each hides one decision likely to change behind an
   interface simpler than what it hides, or wraps an external system as a port named by purpose.
   State per unit: responsibility (one sentence, and what it solely owns) · input and from whom ·
   output and to whom · boundary (what it never does or exposes).
4. **Edges** — direction and kind (call · event · implements). Depend on what changes less; only
   names and types cross a boundary. A cycle → invert one edge through an interface its consumer
   declares, or extract the shared part.
5. **Walk** — each change from step 2 should touch one unit, plus the consumers of what it adds. More
   → merge, split or move a responsibility once, else a `Q`.
6. **One unit's inside**, when that is the ask — what it does and does not do; interface (operations,
   errors, invariants); the state it owns and how it is disposed; failure (report, retry, degrade);
   contract tests and the fakes for its ports.
7. **Write** — § Units: the table (unit · anchor · responsibility · input · output · boundary ·
   change · delivers). § Dependencies: one Mermaid `flowchart`, every unit a node, every edge
   labelled. The walk (change → units touched).

## Check before writing

- one hidden decision per unit
- each change touches one unit, plus its new consumers
- no cycle · no reach into another unit's internals
- no pass-through layer · no split by execution order · no unit smaller than a human needs to
  understand it

## Output

§ Units and § Dependencies. `Open:` the questions, any change the walk could not contain.
