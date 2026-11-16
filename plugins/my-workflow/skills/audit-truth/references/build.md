# build — Locate → Walk → Organize

Inputs: the scope or entry points · the purpose (the questions the atlas must answer). The purpose
gates every read.

Sources other than code (docs, notes, a summary): read first, only what matches the purpose. A fact
taken from them is marked (from <file>) until checked against source.

## 1. Locate

- Grep the purpose's keywords (names, routes, fields, keys, synonyms); glob the layout.
- List the entry modules' exported surface.
- Name the scope's top-level units, about 3–9: entry points, modules, services. They are the graph's
  nodes.

## 2. Walk — top-down, one hop at a time

Per unit, from its entry:

- **Input** — what it receives, and who hands it over (grep the callers).
- **Unit** — the facts it reads or writes, the decisions it makes; which of them no other unit has.
- **Output** — what it returns, emits or writes, and who receives it.

Go one level down only where a purpose question is still open. Stop a branch when it is:

- understood, or already walked;
- off-purpose → record its name under Gaps;
- at a boundary → name the exact surface (endpoint, table, key, event) and stop; never descend into
  the client, SDK or framework behind it.

Budget, declared before the first read: a claim or location ≤5 files · a mechanism ≤15 per flow · an
area's organisation ≤12 · docs ≤6 pages. Spent → stop. A branch cut while on-purpose becomes a Dive
pointer.

## 3. Organize

Per `format.md`:

- Graph and unit table first; then one entry per unit the purpose needed opened.
- "Owns solely" is logic found in this unit only. Shared logic → name its owner instead.
- One flow line per trigger the purpose names, as a chain of units.
- Keep a fact only if it changes what the reader does next: a file to touch, a decision, a risk, a rule.
- Indirection: name the whole chain; open the hops the purpose needs, leave the rest as one-line
  sub-units.
- Deepen an existing entry in place; never a second entry for one unit. Checking a distilled entry
  against source drops its `source` mark.
- Record the audited commit. Run the Format check.
