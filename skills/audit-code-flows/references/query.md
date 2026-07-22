# query — answer from the atlas, heal on a miss

Answer a question from the **local** atlas reading as little as possible: match on the tiny
frontmatter first, open only the flows that earn it, widen if needed, and heal from source only
what the atlas still can't answer. A bare pointer skips straight to **Heal** on that spot.

**Scan the frontmatter** — the cheap routing tier; never read a whole flow just to route:

```
grep -HE '^(id|title|keywords|outline):' atlas/*.md
```

gives every flow's `title` / `keywords` / `outline` next to its file — one command, the whole
atlas, no bodies read. `index.md` adds structure (entry anchors, Couples-with) when the question
needs a blast radius.

## Steps

1. **Index the relevant flows** — from `index.md` + the frontmatter scan, pick the flows whose
   `keywords` / `outline` is relevant to the question; open the **body** of the on-purpose ones only.
2. **Answer** — in ≤ 20 lines from the opened bodies: the fields that answer (fact + `path:symbol`
   anchor, verbatim), then a **`Dive:`** line listing the `path:symbol` pointers the caller can
   grep/read to ground deeper detail; pull the blast radius from `index.md`'s Couples-with when
   the question asks for it.
3. **Widen** — not answered → check the frontmatter of the flows you skipped; open any whose
   `keywords` / `outline` now look relevant, and answer from them.
4. **Heal** — still missing (no matching flow, or the matched body lacks the fact) → declare a
   reveal budget (default 3), then loop: read source for exactly that spot (build.md § Walk
   boundary), chain a revealed on-path pointer, fold each delta into the local atlas (best-effort
   — a read-only caller keeps it in the answer only), until answered or budget spent. A disclosed
   sub-flow becomes its own note + index row; deeper facts fold into the covered flow. Name what
   was read (`healed via F3 §HOW`). Budget spent, or the question spans many unaudited flows →
   return the best partial + the gap + a build suggestion. Never re-scan blindly, never guess.
