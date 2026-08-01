# build — Locate → Walk → Organize

Inputs: **entry points** · **purpose** (the caller's questions — gates every read) ·
**source kind** per entry: **existing** (live code — the note adds Dependents + a
REUSE/MODIFY/REPLACE proposal) · **legacy** (read-only reference — the note is a
behavioral spec: preserve vs drop).

Explore the way you would by hand, bounding depth *during* the walk (jump only where a
purpose question is still open), so the off-purpose graph is never built and the read
can't run away.

## 1. Locate — narrow by keyword

Grep the purpose's keywords (symbol names, routes, store / field names) and glob the project
structure to find the candidate entry file(s) / symbols, and list the entry modules' exported
surface. Cheap and wide — the starting point, not a full-graph sweep.

**Warm start** — if you carry the project's conventions (where kinds of unit live, standard
boundaries, naming), check the conventional location first: a hint that biases order, never a
prune — the grep still runs and confirms.

## 2. Walk — go-to-definition, on-purpose, one hop at a time

From each located entry, follow the definition graph outward like go-to-definition — **only
where a purpose question is still open.** Per hop, both directions: what it calls / who calls
it (grep the symbol, read the enclosing unit), and the fact touch points it reads or writes
(a store / key / field the purpose names — the couplings surface here).

Stop a branch when it's understood, off-purpose (record the name), already walked, or a
boundary / cap is hit. A branch cut while still on-purpose becomes a **Self-audit pointer**.
Read budget ~15 files/flow; spent → stop and report notes + gaps. A gap list is a valid
result; an overrun is not.

## 3. Organize — the walked hops into notes

Turn the walked hops into notes + the couplings index, per the contracts in
[references/formats.md](./formats.md).

- **Audit flows, not files** — follow each flow end-to-end (entry → handler → state →
  boundary); per hop: WHAT data · WHERE from · WHERE to · HOW (mechanism).
- **Two note shapes, one envelope** — a coherent user/data flow → a **feature note**
  (`F<n>`, GIVEN/WHEN/THEN/HOW); a cross-cutting structure or mechanism the purpose needs
  (layering, routing setup, state-management organization, a DI/service pattern) → an
  **architecture note** (`A<n>`, STRUCTURE/MECHANISM/RULES). Content fitting neither body
  is a signal to split the note — never to abandon the envelope.
- **Record boundaries, not implementations** — name the exact surface (method + path +
  params + body/response shape · DB table · topic · storage key) and stop; never descend
  into the client/SDK/framework plumbing behind it.
- **Indirection: annotate the hops the purpose needs; box the rest.** An opened hop is
  traced and anchored; a boxed hop records in/out shapes + a Self-audit pointer. The chain
  stays continuous — never collapsed to the mechanism's name.
- **Couplings live in `INDEX.md`** — the walk's fact-touch-points already found the sites;
  write each into the Couples-with cell (direction + shared fact) and map the moment the
  second flow hits it. Never in note bodies, never a second scan.
- **Deepen, don't duplicate** — a note already in the atlas (e.g. a distilled one) is updated
  in place; verifying a `source: distilled` field from source drops that mark. Never a second
  note for the same flow.
- **Tag what you didn't read directly** — untagged = read from source · `(inferred)` =
  deduced · `(uncertain)` = must carry a Self-audit pointer.
- **Scan wide; note narrow** — facts, anchors, surfaces, shapes; no narration, nothing
  that doesn't affect a downstream decision.

The walk fills the mechanical parts (units, call edges, `path:symbol` anchors); organizing
fills the frontmatter `outline` + the body sections — judgment authors, search verifies.
Finish with formats.md's **Format check**.
