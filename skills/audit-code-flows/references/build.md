# build — procedure and artifact formats

Inputs: **entry points** · **purpose** (the caller's questions — gates every read) ·
**source kind** per entry: **existing** (live code — the note adds Dependents + a
REUSE/MODIFY/REPLACE proposal) · **legacy** (read-only reference — the note is a
behavioral spec: preserve vs drop).

Build the way you'd explore by hand: **Locate** the entry → **Walk** the definition graph
outward on-purpose → **Organize** the walked hops into flows. Depth is bounded *during* the
walk — you jump only where a purpose question is still open — so the read can't run away and
the off-purpose graph is never built.

## 1. Locate — the entry, and the mode

**Pick the mode once, before any read:**

- `ast-grep --version` succeeds (or `npx --yes @ast-grep/cli --version`) → **ast-grep
  mode**: use the queries in [ast-grep-usage.md](./ast-grep-usage.md) for the walk.
- neither resolves → **grep/read mode**: walk with Grep + Glob + targeted Read, and tag the
  walked edges `(grep)` — candidates until a read confirms them.

Then locate fast: from the purpose's keywords + project structure, find the entry file(s) /
symbols and list the entry modules' exported surface (`outline`, or export/definition grep).
Cheap and wide — the starting point, not a full-graph sweep.

## 2. Walk — go-to-definition, on-purpose, one hop at a time

From each entry, follow the definition graph outward like go-to-definition — **only where a
purpose question is still open.** Per hop, both directions:

- **what it calls / who calls it** → the next hop's unit (`run -p '<sym>($$$)'` = call
  sites; `outline` / grep = where a symbol is defined).
- **fact touch points** → every site that reads or writes a store / key / field the purpose
  names → this is where couplings are found, as you walk, not by a later re-scan.

Stop a branch when it's understood, off-purpose (record the name), already walked, or a
boundary / cap is hit. A branch cut while still on-purpose becomes a **Self-audit pointer**.
Read budget ~15 files/flow; spent → stop and report notes + gaps. A gap list is a valid
result; an overrun is not.

## 3. Organize — the walked hops into flows

Turn the walked hops into each flow's note fields + the couplings index.

- **Audit flows, not files** — follow each flow end-to-end (entry → handler → state →
  boundary); per hop: WHAT data · WHERE from · WHERE to · HOW (mechanism).
- **Record boundaries, not implementations** — name the exact surface (method + path +
  params + body/response shape · DB table · topic · storage key) and stop; never descend
  into the client/SDK/framework plumbing behind it.
- **Indirection: annotate the hops the purpose needs; box the rest.** Name the chain —
  config origin → interpreter → collector (+ data model) → submission. An opened hop is
  traced and anchored; a boxed hop records in/out shapes + a Self-audit pointer. The chain
  stays continuous — never collapsed to the mechanism's name.
- **Couplings live in `index.md`** — the walk's fact-touch-points already found the sites;
  write each into `index.md`'s Couples-with cell (direction + shared fact) and map the
  moment the second flow hits it. Never in flow notes, never a second scan.
- **Tag what you didn't read directly** — untagged = read from source · `(inferred)` =
  deduced · `(uncertain)` = must carry a Self-audit pointer · `(grep)` = a walked edge
  found without ast-grep, a candidate until a read confirms it.
- **Scan wide; note narrow** — facts, anchors, surfaces, shapes; no narration, nothing
  that doesn't affect a downstream decision.

## Artifact — `atlas/` in the caller-designated directory

The walk fills the mechanical cells (index's Units touched + Entry anchor, the call edges,
the inline `path:symbol` anchors); organizing fills Problem + GIVEN/WHEN/THEN/HOW — judgment
authors, search verifies.

`index.md` — the always-loaded tier:

````markdown
# Atlas — <scope> · <purpose, one line>

| Flow | Kind | Entry anchor | Units touched | Couples with |
|------|------|--------------|---------------|--------------|
| F1 <name> | existing | `path:symbol` | <units> | → F3 (invalidates <fact>) |

## Interaction map
<mermaid: nodes = flows, labeled edges = coupling + direction; hub units several flows
couple through flagged — widest change radius. Omit under 2 interacting flows.>

## Gaps
<what wasn't audited, and why>
````

`<flow-id>.md` — one per flow; each field a `##` subheading in this order, omit the
inapplicable; bodies are facts in the fewest lines that carry them:

````markdown
# F<n> <flow> — existing | legacy

## Problem
what it solves + solution shape, 1–2 sentences

## GIVEN
per fact: origin (surface + shape) · preconditions (auth · flag · prior flow) · initial state

## WHEN
trigger (user action · timer · external event · state change) + guards

## THEN
per case (happy · error · empty · race · permission): outcome · state changed + where ·
propagation

## HOW
transforms per hop · side effects (exact surface: method+path+body · storage key · event) ·
mechanism per hop; for indirection, name the full chain (config origin → interpreter →
collector → submission), each hop anchored, opened or boxed

## Dependents / Verdict       <!-- existing only -->
external importers · REUSE | MODIFY | REPLACE — one-line reason (a proposal; the caller
confirms)

## Preserve / drop            <!-- legacy only -->
behaviors kept vs deliberately dropped

## Self-audit pointers
`path:symbol` — what deeper detail lives there + which decision needs it
````
