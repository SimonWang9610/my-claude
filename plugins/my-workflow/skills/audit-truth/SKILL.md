---
name: audit-truth
description: >-
  Use this skill when existing code must be understood before acting: "how does X work", "where is
  X", "what depends on X", "is it true that X", "map this area", or before designing, changing or
  debugging unfamiliar code, even if they never say "audit". Maps code as units with a dependency
  graph into an atlas and answers from it. Never changes or judges what it reads.
argument-hint: "[build | query | distill] <scope, question or claim> [sources]"
---

# audit-truth

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (else `../../shared/`), read once per
conversation. Other paths: this folder.

Show how existing code works together (which units exist, how they affect each other, what each
solely owns) so later steps open a few units instead of exploring again.

The atlas has three tiers: `INDEX.md` (graph, units, flows) → unit entries → source. Format:
`references/format.md`.

| Mode | When | Procedure |
|---|---|---|
| build `<scope> · <purpose>` | no atlas covers the scope | `references/build.md` |
| query `<question, claim or pointer>` | an atlas covers it | `references/query.md` |
| distill `<external atlas> · <purpose>` | one is given to lift from | `references/distill.md` |

Load only the chosen mode's procedure.

**Saves to**, first match: "don't save" → nowhere · the `atlas` a spec's `workflow.yaml` names · a
path given · `<spec folder>/atlas/` · `.docs/atlas/<scope>/`. Return the path. A caller that may not
write keeps new facts in its answer.

## Rules

- Read-only on source; never judge it.
- Top-down: reveal a smaller unit only when a question needs it.
- What crosses a unit's boundary, never how it is written.
- One context, no subagents; a gap list is a valid result.
