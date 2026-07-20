---
name: audit-code-flows
description: >
  Audit code references (existing or legacy, any language) into a tiered, queryable
  atlas/ — a greppable flow index over per-flow GIVEN/WHEN/THEN/HOW notes anchored
  path:symbol — and serve later phases on demand: query answers from the atlas without
  re-scanning source; extend acquires exactly what the atlas lacks (funds a pointer, or
  builds the one uncovered flow) and folds it back in. Use before designing against or
  migrating from existing/legacy code, and whenever a phase needs to locate or dive into
  audited flows.
argument-hint: "[build | query | extend]"
---

# audit-code-flows

Answer **what problem the code solves and how its data flows** — never how it is written.
Disclosure is tiered: `atlas/index.md` (tiny, load first) → `atlas/<flow>.md` (open per
need) → source (via `path:symbol` anchors). Build once per scope; afterwards phases
**query** and **extend** instead of re-scanning — a dive folds back into the atlas, so it
deepens instead of evaporating in one agent's context.

## Modes

- **build** `<entry points> · purpose · kind: existing|legacy` — audit the references
  into `atlas/`. **ONE agent audits everything**: couplings, hubs, and the whole-flow
  sense only emerge in a single context — skip off-purpose flows instead of splitting;
  parallel subagents only when the caller explicitly designates them. Procedure +
  artifact formats: [references/build.md](./references/build.md) — load it ONLY for this
  mode.
- **query** `"<question>"` — answer from the atlas: pointers + minimal facts.
- **extend** `<pointer | gap | uncovered reference>` — get what the atlas lacks: fund a
  pointer, or build just the uncovered flow. The only mode that reads source after build.

## query

1. Match the question against `atlas/index.md` (flows, units, facts); open ONLY the
   matching flow notes.
2. Answer in ≤ 20 lines: index rows hit · the note fields that answer (field + fact +
   anchor, verbatim) · `Dive:` pointers (`atlas/<flow>.md § <field>` · `path:symbol`) —
   the caller decides whether to open them.
3. The atlas can't answer → say so + the nearest flows + an extend suggestion. Never scan
   source, never guess.

## extend

The scoped acquirer — reads source only for exactly what was asked, under
[references/build.md](./references/build.md)'s boundary rules. Two cases:

- **New flow** — the pointer/question/reference covers a flow the atlas lacks (a query
  miss, no atlas yet, or a pointed spot that discloses a coherent sub-flow of an existing
  flow) → **build** that flow alone: its own note + index row; a sub-flow is promoted, never
  inlined — couple it to its parent in `index.md`.
- **More facts on an existing flow** — the disclosure deepens what a note already covers
  → fold the facts into that note's fields (tagged); refresh its index row when
  units/couplings changed.

Report only the delta lines.
