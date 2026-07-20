# build — procedure and artifact formats

Inputs: **entry points** · **purpose** (the caller's questions — gates every read) ·
**source kind** per entry: **existing** (live code — the note adds Dependents + a
REUSE/MODIFY/REPLACE proposal) · **legacy** (read-only reference — the note is a
behavioral spec: preserve vs drop).

## Boundary — declare before the first read

From the purpose fix: the flows in scope · a depth cap (default 2 hops past the entry
unit, extended only while on-purpose) · a read budget (~15 files/flow). Every read
answers a named open question — no curiosity reads. Stop a branch when: no on-purpose
fact (record the name) · already audited · a boundary or the cap hit · a hop adds nothing
new. A branch cut while still on-purpose becomes a **Self-audit pointer**. Budget spent →
stop and report notes + gaps; a gap list is a valid result, an overrun is not.

## Trace rules

- **Audit flows, not files** — follow each flow end-to-end (entry → handler → state →
  boundary); per hop: WHAT data · WHERE from · WHERE to · HOW (mechanism).
- **Record boundaries, not implementations** — name the exact surface (method + path +
  params + body/response shape · DB table · topic · storage key) and stop; never descend
  into the client/SDK/framework plumbing behind it.
- **Indirection: open the hops the purpose needs; box the rest.** Name the chain — config
  origin → interpreter → collector (+ data model) → submission. An opened hop is traced
  and anchored; a boxed hop records in/out shapes + a Self-audit pointer. The chain stays
  continuous — never collapsed to the mechanism's name.
- **Record cross-flow touch points as you trace** — a store/key/topic/table two flows
  touch = a coupling; write it (direction + shared fact) into `index.md`'s Couples-with
  cell and map the moment the second flow hits it. Couplings live only in `index.md`,
  never in flow notes; never assembled by a second scan.
- **Tag what you didn't read directly** — untagged = read from source · `(inferred)` =
  deduced · `(uncertain)` = must carry a Self-audit pointer.
- **Scan wide; note narrow** — facts, anchors, surfaces, shapes; no narration, nothing
  that doesn't affect a downstream decision.

## Artifact — `atlas/` in the caller-designated directory

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

`<flow-id>.md` — one per flow; each field a `####` subheading in this order, omit the
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
mechanism per hop

## Mechanism chain            <!-- indirection only -->
config origin → interpreter → collector → submission — each hop anchored, opened or boxed

## Dependents / Verdict       <!-- existing only -->
external importers · REUSE | MODIFY | REPLACE — one-line reason (a proposal; the caller
confirms)

## Preserve / drop            <!-- legacy only -->
behaviors kept vs deliberately dropped

## Self-audit pointers
`path:symbol` — what deeper detail lives there + which decision needs it

## Diagram                    <!-- non-linear flows only -->
mermaid sequence/flow of the hops, boundary surfaces labeled

## Audited files
exact paths
````
