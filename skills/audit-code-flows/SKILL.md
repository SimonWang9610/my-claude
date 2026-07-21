---
name: audit-code-flows
description: >
  Turns existing or legacy code (any language) into a tiered, queryable atlas — a flow
  index over per-flow GIVEN/WHEN/THEN/HOW notes anchored to path:symbol — then answers
  questions from it, healing itself on a miss by reading exactly the missing spot instead
  of re-scanning. Use when work depends on understanding code you didn't write: before
  designing against or migrating from it, to locate the flows a change touches, to answer
  "where does this data come from" or "who else writes this fact", or to dive into a
  specific unit. Not for authoring the spec or design (use build-requirements,
  design-react-contracts) or judging a diff (use review-react-changes). Output: atlas/
  (flow index + per-flow notes).
argument-hint: "[build | query]"
---

# audit-code-flows

Answer **what problem the code solves and how its data flows** — never how it is written.
Disclosure is tiered: `atlas/index.md` (tiny, load first) → `atlas/<flow>.md` (open per
need) → source (via `path:symbol` anchors). Build once per scope; afterwards phases
**query** instead of re-scanning — a query answers from the atlas and, on a miss, heals
itself by reading exactly the missing spot and folding it back, so the atlas deepens
instead of evaporating in one agent's context.

## Modes

- **build** `<entry points> · purpose · kind: existing|legacy` — **Locate → Walk →
  Organize** the code into `atlas/`: locate the entry by keyword, walk the definition graph
  outward on-purpose (go-to-definition style), organize the walked hops into flows. Bounded
  during the walk, so the read can't run away. **ONE agent audits everything**: couplings,
  hubs, and the whole-flow sense only emerge in a single context — skip off-purpose flows
  instead of splitting; parallel subagents only when the caller explicitly designates them.
  Procedure + artifact formats: [references/build.md](./references/build.md) — load it ONLY
  for this mode.
- **query** `"<question>" | <pointer>` — a **question** is answered from the atlas, healing
  on a miss; a bare **pointer** just deepens that spot and returns the delta. The only mode
  that reads source after build.

## query — answer, healing on a miss

1. **Atlas answers** — match the question against `atlas/index.md`; open ONLY the matching
   flow notes. Answer in ≤ 20 lines: index rows hit · the note fields that answer (field +
   fact + anchor, verbatim) · `Dive:` pointers (`atlas/<flow>.md § <field>` · `path:symbol`).
2. **Scoped miss → heal** — the question maps to a clear pointer / one uncovered flow.
   Declare a reveal budget first (default: 3 acquisitions), then loop: acquire the nearest
   fundable gap (below), re-check, follow a revealed on-path pointer, repeat until answered
   or budget spent. Answer from the union and **name what was read** (`healed via F3 §HOW,
   F7 §GIVEN`) so the source reads + atlas growth are visible.
3. **Broad miss / budget spent** — no atlas, the question spans many unaudited flows, or the
   loop capped → don't run away: return the best partial + the remaining gap + a build
   suggestion. Never re-scan blindly, never guess.

**Acquire** (each loop step, and a bare-pointer query) — read source only for that spot,
under [references/build.md](./references/build.md)'s Walk boundary; fold the delta back
**best-effort** (persist to `atlas/` when the caller can write; a read-only caller keeps the
facts in its answer only). A disclosed sub-flow is promoted to its own note + index row
(coupled to its parent); deeper facts on a covered flow fold into that note's fields
(tagged). Report only the delta lines.
