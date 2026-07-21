# distill — cherry-pick an external atlas into the local one

A fast quick-start: when a caller supplies a read-only **external atlas** (curated for shared
or stable code), lift its purpose-relevant flows into the local atlas instead of auditing that
code from source. Lightweight — a rephrase, not a source read. `build` and `query` know nothing
of this; the result is ordinary local flows, so the local atlas stays intact and self-contained.

Inputs: the **external atlas path** · the **purpose** (which flows matter).

1. **Cherry-pick** — read the external `index.md`; select only the flows on-purpose for this
   scope, skip the rest. A handful, not the whole atlas.
2. **Rephrase to local** — for each, write a local `<flow>.md` in the build.md flow-note shape:
   keep the anchors, trim to what this purpose needs, refit `outline` + `keywords` to your
   questions. Mark provenance with frontmatter `source: distilled from <path>` — so it reads as
   external-derived, not source-verified this run.
3. **Index them** — add each to the local `index.md` (row + couplings), same as any flow.

Distilled flows are first-class local flows: `query` reads them like any other and **heals**
them against source on demand (a heal that reads source drops the `source` mark for the verified
fields). Depth you can't defer → run `build` on that flow. Never write the external atlas.
