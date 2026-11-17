---
name: audit-truth
description: >-
  Use this skill when existing code must be understood as a whole before acting: "how does X work",
  "what depends on X", "what breaks if I change X", "map this area", or before designing on or
  improving unfamiliar code, even if they never say "audit". Maps code as units and their
  dependencies into an atlas and answers from it. Never changes or judges what it reads. Not for
  one location or one claim when no atlas exists: read the code.
argument-hint: "[build | query | distill] <scope, question or claim> [sources]"
---

# audit-truth

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (else `../../shared/`), read once per
conversation. Other paths: this folder.

Show how existing code works together (which units exist, what each depends on, solely owns and
provides) so later steps open a few units instead of exploring again.

The atlas has three tiers: `INDEX.md` (graph, units, flows) → unit entries → source. Format:
`references/format.md`.

| Mode | When | Procedure |
|---|---|---|
| build `<scope> · <purpose>` | no atlas exists for the work | `references/build.md` |
| query `<question, claim or pointer>` | an atlas exists | `references/query.md` |
| distill `<external atlas> · <purpose>` | one is given to lift from | `references/distill.md` |

Load only the chosen mode's procedure.

**Saves to**, first match: "don't save" → nowhere · a path the user or the project's context files
give · a spec's: the `atlas` its `workflow.yaml` names, else `<spec folder>/atlas/` · inferred: an
atlas already in the project, or where it keeps such documents, said in one line · none → ask;
cannot ask (inside a skill or an agent) → nowhere. Return the path. A caller that may not write
keeps new facts in its answer.

## Rules

- Read-only on source; never judge it.
- Top-down: reveal a smaller unit only when a question needs it.
- What crosses a unit's boundary, never how it is written.
- A snapshot of the code as audited: an atlas grows (entries, units inside, edges, deeper facts)
  and is never rewritten to follow later changes. Only a fact wrong at the audited commit is
  corrected.
- One context, no subagents; a gap list is a valid result.
