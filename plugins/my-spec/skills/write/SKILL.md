---
name: write
description: >-
  Writes a non-code deliverable from its spec (document, plan, report, decision record, research
  write-up): an outline mapped to the requirements, the draft for its reader, and a done check. Use
  when a spec routes to write, or on "write the doc", "draft the plan", "write up the research". Not
  for choosing between approaches (use my-spec:decide).
argument-hint: "[requirements]"
---

# write

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Input** — the spec, and `design.md` when there is one; an argument adds requirements. No spec →
   `/my-spec:start`.
2. **Form** — the conventions' Stack order, applied to documents of this kind: the project's existing
   ones, an installed skill that covers the kind, the genre.
3. **Outline** — sections in order, each `R<n>` in exactly one, with its sources; missing facts →
   `/my-spec:explore`. Full track: gate.
4. **Draft** — for the spec's reader, in its length and format, saved where the spec names; claims
   carry their source; diagrams where structure or flow matters, tables for comparisons.
5. **Check** — each `done` item: met, or a gap with the section that fixes it.
6. **Review** — `review on` → `/my-spec:critique doc` on the draft; a non-accept verdict → fix its `I`
   lines and review once more; a second non-accept stops at the gate even under `gates auto`. Else
   offer it. Full track: gate.
