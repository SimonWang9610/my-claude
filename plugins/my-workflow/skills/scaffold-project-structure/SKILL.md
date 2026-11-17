---
name: scaffold-project-structure
description: >-
  Use this skill when the user asks where code should live or how to lay out a project: "scaffold a
  new <kind> project", "where does this go", "by feature or by layer", "which folder may import
  which", even if they never say "structure". Lays out folders and import rules by the project's domain,
  fits new code into an existing layout, scaffolds on a yes. Not for component APIs (use
  my-workflow:design-component).
argument-hint: "[scope or question]"
---

# scaffold-project-structure

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (else `../../shared/`), read once per
conversation. Other paths: this folder.

## Steps

1. **Frame** — per deployable its domain (`references/layouts.md`); the stack and its rules,
   per the conventions' Grounding.
2. **Place** — existing code: beside the closest example; change the layout only when the task
   cannot fit. New: the archetype's containers the requirements need; slices by feature; one
   composition root per entry; one home each for config, errors and logging.
3. **Rules** — the import rules (existing: observed; new: `references/layouts.md`) and the tool that
   enforces them; none known → a `Q`.
4. **Write** — § Structure: the tree (`text`, a `# role` per entry), the rules (from · may import ·
   enforced by), the changes in shipping order.
5. **Scaffold** — standalone only, new layouts, after a yes: folders, a stub per public entry, the enforcement
   config. Done when the stubs compile, the entry starts and the enforcer passes; never install.

## Check before writing

One place per kind of file · no import cycle.
