---
name: audit
description: >
  Turns existing or legacy code (any language) into a tiered, queryable atlas — a flow
  index over per-flow GIVEN/WHEN/THEN/HOW notes, plus architecture notes for cross-cutting
  structure, all anchored to path:symbol — then answers
  questions from it, healing itself on a miss by reading exactly the missing spot instead
  of re-scanning; a curated external atlas can be distilled into the local one as a fast
  quick-start. Use when work depends on understanding code you didn't write: before
  designing against or migrating from it, to locate the flows a change touches, to answer
  "where does this data come from" or "who else writes this fact", or to dive into a
  specific unit. Not for authoring the spec or design (use my-react:requirements,
  my-react:design) or judging a diff (use my-react:review). Output: atlas/
  (flow index + per-flow notes).
argument-hint: "[build | query | distill]"
---

# audit

Answer **what problem the code solves and how its data flows** — never how it is written.
Disclosure is tiered: `atlas/INDEX.md` (tiny, load first) → the note files it indexes
(opened per need, matched by frontmatter `keywords`/`outline`; nested folders allowed) →
source (via `path:symbol` anchors).
Build once per scope; afterwards phases **query** instead of re-scanning — a query answers
from the atlas and, on a miss, heals itself by reading exactly the missing spot and folding it
back, so the atlas deepens instead of evaporating in one agent's context.

## Modes

- **build** `<entry points> · purpose · kind: existing|legacy` — **Locate → Walk →
  Organize** the code into `atlas/`: grep the entry by keyword, walk the definition graph
  outward on-purpose, organize the walked hops into notes — feature flows (`F<n>`), and
  architecture notes (`A<n>`) for cross-cutting structure. Bounded during the walk, so the
  read can't run away. **ONE agent audits everything**: couplings, hubs, and the whole-flow
  sense only emerge in a single context — skip off-purpose flows instead of splitting;
  parallel subagents only when the caller explicitly designates them. Procedure:
  [references/build.md](./references/build.md) · artifact contracts + Format check:
  [references/formats.md](./references/formats.md) — load ONLY for this mode.
- **query** `"<question>" | <pointer>` — a **question** is answered from the atlas (scan
  frontmatter → open the matching flow bodies → widen → heal on a miss); a bare **pointer** just
  deepens that spot. The only mode that reads source after build. Procedure: [references/query.md](./references/query.md).
- **distill** `<external atlas path> · purpose` — a fast quick-start when a curated external
  atlas exists: cherry-pick its purpose-relevant flows into local flows (marked
  external-derived), no source read. Procedure: [references/distill.md](./references/distill.md).
