# distill — lift an external atlas into the local one

A quick start when a curated, read-only atlas already covers shared or stable code. No source read.

Inputs: the external atlas path · the purpose.

## Steps

1. **Pick** — read the external `INDEX.md`; select only the units the purpose needs.
2. **Rewrite** — per unit, a local entry per `format.md`: keep the anchors, trim to the purpose, refit
   `keywords` and `owns` to the questions, add `source: distilled from <path>`. Renumber into the
   local ids.
3. **Index** — add each to the local `INDEX.md`: graph node, edges, table row. Run the Format check.

## Rules

- Never write the external atlas.
- A distilled entry is an ordinary local entry: query reads it and heals it against source.
- Depth that cannot wait → build on that unit.
