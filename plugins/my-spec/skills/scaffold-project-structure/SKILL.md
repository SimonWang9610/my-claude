---
name: scaffold-project-structure
description: >-
  Lays out a project by its kind (UI app, backend service, CLI, library, pipeline, workspace): folders,
  where each kind of code goes, which may import which; scaffolds it on a yes, or fits new code into an
  existing layout. Use on "scaffold a new <kind> project", "where does this go", "by feature or by
  layer". Not for component APIs (use my-spec:design-component).
argument-hint: "[scope or question]"
---

# scaffold-project-structure

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Frame** — new project, new area, or existing code; per deployable its kind, from
   `skills/scaffold-project-structure/references/archetypes.md`; the stack and its conventions
   (explore: the tree, configured import rules, the project's rules).
2. **Existing code** — its structure is the default: place each new file beside its closest existing
   example. Propose a change only when the task cannot fit, each change shippable alone.
3. **New layout** — the archetype's containers, only those the requirements need; slices by feature,
   layers inside a slice only when it grows; one composition root per entry point; one home each for
   config, errors, logging, and auth when needed.
4. **Rules** — allowed imports, everything else denied: entry → features → core; a feature reaches a
   sibling only through its public entry; core imports no I/O or framework (ports named by purpose,
   adapters implement them); adapters import core only and are wired by the composition root, never
   imported by features; shared holds what ≥2 features use and no domain logic. Name the tool that
   enforces them in this stack; none known → a `Q`.
5. **Write** — § Structure: the tree (`text`, a `# role` comment per entry), the rules table (from ·
   may import · enforced by), and for existing code the changes in shipping order. Run on its own:
   gate (`Continue to scaffold?`).
6. **Scaffold** — new layouts only; run on its own: after that gate; inside a design: as build's T1.
   The folders, a stub per public entry and composition root (signatures and wiring only; behaviour is
   build's) and the enforcement config, through an installed skill that covers it, else the stack's
   generator. Done when the stubs compile, the entry starts (a CLI: its help runs) and the enforcement
   tool passes (not installed → give the command; never install).

Check before writing: one place per kind of file · no import cycle · every step 4 rule holds.
