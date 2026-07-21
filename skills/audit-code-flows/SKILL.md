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
argument-hint: "[build | query | distill]"
---

# audit-code-flows

Answer **what problem the code solves and how its data flows** — never how it is written.
Disclosure is tiered: `atlas/index.md` (tiny, load first) → `atlas/<flow>.md` (opened per
need, matched by its frontmatter `keywords`/`outline`) → source (via `path:symbol` anchors).
Build once per scope; afterwards phases **query** instead of re-scanning — a query answers
from the atlas and, on a miss, heals itself by reading exactly the missing spot and folding it
back, so the atlas deepens instead of evaporating in one agent's context.

## Modes

- **build** `<entry points> · purpose · kind: existing|legacy` — **Locate → Walk →
  Organize** the code into `atlas/`: grep the entry by keyword, walk the definition graph
  outward on-purpose, organize the walked hops into flows. Bounded during the walk, so the
  read can't run away. **ONE agent audits everything**: couplings, hubs, and the whole-flow
  sense only emerge in a single context — skip off-purpose flows instead of splitting;
  parallel subagents only when the caller explicitly designates them. Procedure + artifact
  formats: [references/build.md](./references/build.md) — load it ONLY for this mode.
- **query** `"<question>" | <pointer>` — a **question** is answered from the atlas, healing on
  a miss; a bare **pointer** just deepens that spot and returns the delta. The only mode that
  reads source after build. Local atlas only — knows nothing of external atlases.
- **distill** `<external atlas path> · purpose` — a fast quick-start when a curated external
  atlas exists: cherry-pick its purpose-relevant flows into local flows (marked
  external-derived), no source read. Procedure: [references/distill.md](./references/distill.md).

## query — answer from the atlas, heal on a miss

1. **Find the flow(s)** — match the question against flow `keywords` + `outline` (grep the
   frontmatter across `atlas/*.md`, cross-checked with `index.md`); open the full note(s) of
   the best matches — reading a matched note whole beats chasing pointers. Nothing matches → 3.
2. **Answer** — in ≤ 20 lines from the opened note's fields (fact + `path:symbol` anchor,
   verbatim); pull blast radius from `index.md`'s Couples-with when the question needs it.
3. **Miss → heal** — no matching flow, or the note lacks the fact → declare a reveal budget
   (default 3), then loop: read source for exactly that spot (build.md § Walk boundary), chain
   a revealed on-path pointer, fold each delta into the atlas (best-effort — a read-only caller
   keeps it in the answer only), until answered or budget spent. A disclosed sub-flow becomes
   its own note + index row; deeper facts fold into the covered note. Name what was read
   (`healed via F3 §HOW`). Budget spent or the question spans many unaudited flows → return the
   gap + a build suggestion. Never re-scan blindly, never guess.
