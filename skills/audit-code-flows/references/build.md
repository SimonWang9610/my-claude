# build — procedure and artifact formats

Inputs: **entry points** · **purpose** (the caller's questions — gates every read) ·
**source kind** per entry: **existing** (live code — the note adds Dependents + a
REUSE/MODIFY/REPLACE proposal) · **legacy** (read-only reference — the note is a
behavioral spec: preserve vs drop).

Explore the way you would by hand — **Locate → Walk → Organize** — bounding depth *during* the
walk (jump only where a purpose question is still open), so the off-purpose graph is never
built and the read can't run away.

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

## 3. Organize — the walked hops into flows

Turn the walked hops into each flow's note + the couplings index.

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
- **Deepen, don't duplicate** — a flow already in the atlas (e.g. a distilled one) is updated
  in place; verifying a `source: distilled` field from source drops that mark. Never a second
  note for the same flow.
- **Tag what you didn't read directly** — untagged = read from source · `(inferred)` =
  deduced · `(uncertain)` = must carry a Self-audit pointer.
- **Scan wide; note narrow** — facts, anchors, surfaces, shapes; no narration, nothing
  that doesn't affect a downstream decision.

## Artifact — `atlas/` in the caller-designated directory

The walk fills the mechanical parts (units, call edges, `path:symbol` anchors); organizing
fills the frontmatter `outline` + GIVEN/WHEN/THEN/HOW — judgment authors, search verifies.

`index.md` — the always-loaded tier:

````markdown
# Atlas
<scope>
<purpose — one or two lines>

## Index
| Flow | Kind | Entry anchor | Units touched | Couples with |
|------|------|--------------|---------------|--------------|
| F1 <name> | existing | `path:symbol` | <units> | → F3 (invalidates <fact>) |

## interaction map
<mermaid: nodes = flows, labeled edges = coupling + direction; hub units several flows
couple through flagged — widest change radius. Omit under 2 interacting flows.>

## Gaps
<what wasn't audited, and why, each one line; e.g. "F2: no entry found", "F4: out of scope,
only a legacy reference">
````

`<flow-id>.md` — one per flow; frontmatter routes the query, body carries the facts (omit an
inapplicable section; bodies are facts in the fewest lines that carry them):

````markdown
---
id: F<n>
title: F<n> <flow>
keywords: <query keywords, 2-3 words each, comma-separated>
outline: <what it solves + solution shape, when it is useful, what it is not, 1-3 sentences>
source: <omit if audited from source; `distilled from <path>` if from an external atlas>
---

## GIVEN
per fact: origin (surface + shape) · preconditions (auth · flag · prior flow) · initial state
## WHEN
trigger (user action · timer · external event · state change) + guards
## THEN
per case (happy · error · empty · race · permission): outcome · state changed + where · propagation
## HOW
transforms per hop · side effects (exact surface: method+path+body · storage key · event) ·
mechanism per hop; for indirection, name the full chain (config origin → interpreter →
collector → submission), each hop anchored, opened or boxed
## Dependents / Verdict       <!-- existing only -->
external importers · REUSE | MODIFY | REPLACE — one-line reason (a proposal; the caller confirms)
## Preserve / drop            <!-- legacy only -->
behaviors kept vs deliberately dropped
## Self-audit pointers
`path:symbol` — what deeper detail lives there + which decision needs it
````
