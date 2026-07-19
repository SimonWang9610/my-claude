---
name: audit-code-flows
description: >
  Distill code in any language into flow-focused audit notes — each flow as a
  GIVEN/WHEN/THEN/HOW chain with entry/exit points and cross-flow interactions, boundary
  surfaces exact (API path/params/body) — so downstream phases read notes instead of
  source. Use before designing against or migrating from existing/legacy code; invoked by
  design-react-contracts to fill audit gaps.
---

# audit-code-flows

Answer **what problem the code solves and how its data flows** — never how it is written.
Language-agnostic: the notes are what another agent reads instead of the source. Each note
walks one fixed chain — entry/exit → GIVEN → WHEN → THEN → HOW → interactions — so
downstream phases can locate the flows a requirement touches and see how a change ripples.
Notes are the index, source is the appendix — every fact anchored `path:symbol`, one jump
from its evidence; later phases self-audit the pointed spots, never re-scan.

## Inputs

- **Entry points** — units/paths to audit.
- **Purpose** — the question(s) the caller needs answered; gates every read.
- **Source kind** per entry point: **existing** (live code — notes add dependents + a
  REUSE/MODIFY/REPLACE proposal) · **legacy** (read-only reference — the note is a
  behavioral spec: preserve vs deliberately drop).

## Boundary — declare it before the first read

An audit without a declared boundary scans forever. From the purpose, fix up front: the
flows in scope · a **depth cap** (default 2 hops past the entry unit, extended only while
the fact is still on-purpose) · a **read budget** per flow (default ~15 files). Then:

- **Every read answers a named open question** from the purpose — no curiosity reads.
- **Stop a branch when:** the unit carries no on-purpose fact (record the name, move on) ·
  already audited · a boundary is reached · the depth cap hits · a hop adds no new fact,
  boundary, or case (diminishing returns). A branch cut while still on-purpose becomes a
  **Self-audit pointer** in the note — never silently dropped.
- **Budget spent → stop and report:** notes so far + the gap list. A gap list is a valid
  result; an overrun is not — ask the caller to decide whether to fund a deeper trace.

## Trace rules

**Audit flows, not files.** Follow the flow across every file it traverses until it
completes end-to-end (entry → handler → state → boundary); a note covering one file with
the flow dangling is incomplete. Per hop: WHAT data · WHERE from · WHERE to · HOW
(mechanism).

**Record boundaries, not implementations.** Where data crosses a boundary, name the exact
surface — method + path + params + body/response shape, DB table, message topic, storage
key — and stop; never descend into the client code, SDK wiring, or framework plumbing
behind it.

**Indirection: open the hops the purpose needs; box the rest.** When a flow passes
through indirection — server-driven config, dynamic forms, registries, dispatch tables,
feature flags — name the chain's hops: **config origin** (surface + shape) →
**interpreter** (converts config to UI/behavior) → **collector** (runtime values + their
data model) → **submission** (target surface). Then trace selectively:

- an **opened hop** (on-purpose) is traced and anchored like any flow segment;
- a **boxed hop** (off-purpose) records only what enters and leaves it (surfaces + shapes)
  plus a Self-audit pointer, and the trace continues past it.
  The chain must stay **continuous** — every hop opened or boxed, so the note still guides
  later phases end-to-end. What's never acceptable is the chain collapsed to the
  mechanism's name with no hops at all.

**Record cross-flow touch points as you trace.** A store/cache key/event topic/table two
flows both touch is an interaction — note coupling + direction the moment the second flow
hits it; the interaction map is assembled from these, never from a second scan.

**Scan wide; note narrow and terse.** Read as much relevant source as the boundary allows;
notes record flows, boundaries, and cases — never code style, line-by-line narration, or
detail that doesn't affect a downstream decision.

## Note format — one per audited flow, one fixed chain

Each field a subheading, in this order; omit fields that don't apply. Bodies are facts —
anchors, surfaces, shapes — in the fewest lines that carry them; no narration, no
restating the field name's meaning.

````markdown
### <flow> — existing | legacy

#### Problem
what it solves + solution shape, 1–2 sentences

#### Entry / exit
entry (route · mount · exported call · event) → exit (render · navigation · persisted
write · emitted event), each `path:symbol`

#### GIVEN
per fact: origin (surface + shape) · preconditions (auth · flag · prior flow) · initial state

#### WHEN
trigger (user action · timer · external event · state change) + guards

#### THEN
per case (happy · error · empty · race · permission): outcome · state changed + where ·
propagation

#### HOW
transforms per hop · side effects (exact surface: method+path+body · storage key · event) ·
mechanism per hop

#### Interacts with
per flow, one line: coupling (shared fact/store/key · triggers · triggered by ·
invalidates · ordering) + direction

#### Mechanism chain            <!-- indirection only -->
config origin → interpreter → collector → submission — each hop anchored, opened or
boxed (in/out shapes + Self-audit pointer)

#### Dependents                 <!-- existing only -->
external importers

#### Verdict                    <!-- existing only -->
REUSE | MODIFY | REPLACE — one-line reason (a proposal; the caller confirms)

#### Preserve / drop            <!-- legacy only -->
behaviors kept vs deliberately dropped

#### Self-audit pointers
`path:symbol` — what deeper detail lives there + which decision needs it

#### Diagram                    <!-- non-linear flows only -->
mermaid sequence/flow of the hops, boundary surfaces labeled

#### Audited files
exact paths
````

## Output

1. **Notes** — one per flow, format above.
2. **Flow interaction map** (2+ interacting flows) — mermaid graph (nodes = flows, edges =
   coupling + direction) or a `flow → flow · coupling · effect` table; built from the
   Interacts-with lines only, no new facts.
3. **Gap list** — what wasn't audited, and why.

Every line must serve the stated purpose.
