---
name: audit-truth
description: >-
  Use this skill when the user, or a step, needs to understand existing code before acting on it: "how
  does X work", "where is X", "what depends on X", "who writes this", "what's our convention for X",
  "is it true that X", "map this area", or before designing, changing or debugging unfamiliar code,
  even if they never say "audit". Maps the code top-down as units (what each receives, solely owns
  and delivers) with a dependency graph and source anchors, saves it as an atlas, and answers later
  questions from the atlas by reading only the missing spot. Modes: build, query, distill. Never
  changes what it reads; not for judging quality (use my-workflow:spec-review).
argument-hint: "[build | query | distill] <scope, question or claim> [sources]"
---

# audit-truth

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (unexpanded → `../../shared/conventions.md`).
Other paths are relative to this folder.

## Goal

Show how existing code works together: which units exist, how they affect each other, what each
solely owns. Later steps then open a few units through the atlas instead of exploring the codebase
again.

## Atlas

Three tiers, cheapest first: `INDEX.md` (graph, unit table, flows) → unit entries (opened when their
keywords match) → source (through anchors). Format: `references/format.md`.

## Modes

Pick, first match: the argument names one · an external atlas is given to lift from → distill · an
atlas covers the scope → query · else build, scoped to the question, then answer it.

| Mode | Input | Does | Procedure |
|---|---|---|---|
| **build** | scope or entry points · purpose | Locate → Walk → Organize the scope into an atlas | `references/build.md` |
| **query** | question, claim or pointer | answer from the atlas; on a miss read exactly that spot and fold it back | `references/query.md` |
| **distill** | external atlas · purpose | lift its on-purpose units into the local atlas, no source read | `references/distill.md` |

Load only the chosen mode's procedure.

## Where the atlas lives

First match:

1. The user says not to save → return the result in the session; write nothing.
2. A spec's `workflow.yaml` already names an `atlas` → that folder.
3. A path the user gives.
4. A spec is in progress → `<spec folder>/atlas/`.
5. `.docs/atlas/<scope>/`.

Return the atlas path; the caller records it. A caller that may not write keeps new facts in its
answer.

## Rules

- Read-only on source. Never judge it.
- Top-down: high-level units first; reveal a smaller unit only when a question needs it.
- What a unit does and what crosses its boundary; never how it is written.
- One context builds the whole atlas: couplings only show up there. No subagents.
- Importance over coverage; a gap list is a valid result.

## Output

- **build** — atlas path · units and flows written · "Start here" · gaps.
- **query** — the facts with anchors · `Dive:` pointers · what was folded back.
- **distill** — units lifted · what was skipped.

`Open:` what stayed unread, and why.
