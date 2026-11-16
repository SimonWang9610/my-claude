---
name: scaffold-project-structure
description: >-
  Use this skill when the user asks where code should live or how a project should be laid out:
  "scaffold a new <kind> project", "set up the repo", "where does this go", "by feature or by layer",
  "how should I organise this", "which folder may import which", even if they never say "structure".
  Lays out folders by project kind (UI app, backend service, CLI, library, pipeline, workspace) with
  import rules and the tool that enforces them, fits new code into an existing layout, and scaffolds
  on a yes. Not for component APIs (use my-workflow:design-component).
argument-hint: "[scope or question]"
---

# scaffold-project-structure

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (unexpanded → `../../shared/conventions.md`).
Other paths are relative to this folder.

## Input

A new project, a new area, or existing code.

## Steps

1. **Frame** — per deployable its kind, from `references/layouts.md`; the stack and its conventions
   (`/my-workflow:audit-truth`: the tree, configured import rules, the project's rules).
2. **Place** —
   - Existing code: its structure is the default. Put each new file beside its closest existing
     example. Propose a change only when the task cannot fit, each change shippable alone.
   - New layout: the archetype's containers, only those the requirements need; slices by feature,
     layers inside a slice only when it grows; one composition root per entry point; one home each
     for config, errors, logging, and auth when needed.
3. **Rules** — existing code: its configured or observed import rules, plus only what the task needs.
   New layout: the import rules in `references/layouts.md`. Name the tool that enforces them in this
   stack (the conventions' Knowledge sources); none known → a `Q`.
4. **Write** — § Structure: the tree (`text`, a `# role` comment per entry) · the rules table (from ·
   may import · enforced by) · for existing code, the changes in shipping order.
5. **Scaffold** — new layouts only, after a yes to `Scaffold this layout?` or when asked for alone
   (inside another skill or agent: return § Structure instead). Write the folders, a stub per public
   entry and composition root (signatures and wiring only) and the enforcement config, through the
   conventions' Knowledge sources, else the stack's generator.

## Done when (scaffold)

The stubs compile · the entry starts (a CLI: its help runs) · the enforcement tool passes (not
installed → give the command; never install).

## Check before writing

One place per kind of file · no import cycle · every step 3 rule holds.

## Output

§ Structure. `Open:` the questions, the changes still to ship, the behaviour the stubs still need.
