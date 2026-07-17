---
name: audit-code-flows
description: >
  Distill code in any language into flow-focused audit notes — data models, boundary
  surfaces (API path/params/body), user flows, cases covered — so downstream phases read
  notes instead of source. Use before designing against or migrating from existing/legacy
  code; invoked by design-react-contracts to fill audit gaps.
---

# audit-code-flows

Answer **what problem the code solves and how its data flows** — never how it is written.
Language-agnostic: the notes are what another agent reads instead of the source. Notes are
the index, source is the appendix — every recorded fact anchored `path:symbol`, one jump
from its evidence — so depth discloses gradually: later phases self-audit the pointed
spots when a decision needs more, never re-scan.

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

**Scan wide; note narrow and terse.** Read as much relevant source as the boundary allows;
notes record flows, boundaries, and cases — never code style, line-by-line narration, or
detail that doesn't affect a downstream decision.

## Note format — one per audited flow/area

```markdown
### <flow or area> — existing | legacy

- **Problem & approach:** what it solves and the solution shape, 1–2 sentences
- **Data model:** the facts it handles and the field shapes that matter downstream
- **Data flow:** per fact — origin (endpoint + response shape · user input · cache ·
  config/default) → transforms/validation → destination (method + path + query + body ·
  store · storage · emitted event)
- **User flow:** trigger → steps → observable outcome, for each interaction it serves
- **Mechanism chain** (indirection only): config origin → interpreter → collector
  (+ data model) → submission — each hop `path:symbol`-anchored and marked opened, or
  boxed (in/out shapes + Self-audit pointer)
- **Cases covered:** each distinct case/branch (happy · error · empty · races · permissions)
  with its observable outcome
- **State:** facts held · where (local state, store, service) · change triggers · propagation
- **Dependents** (existing only): external importers
- **Verdict** (existing only): REUSE | MODIFY | REPLACE — one-line reason (a proposal; the
  caller confirms)
- **Preserve / drop** (legacy only): behaviors to keep vs deliberately leave behind
- **Self-audit pointers:** `path:symbol` — one line on what deeper detail lives there and
  which decision would need it; a later phase reads exactly that spot on demand
- **Diagram** (when the flow is non-linear — branches, multiple sources/sinks, async hops):
  a mermaid sequence/flow diagram of the hops, boundary surfaces labeled
- **Audited files:** the original files read for this note, exact paths
```

Omit lines that don't apply.

## Output

Notes + the gap list (what wasn't audited, and why). Concise and goal-accurate: every
line must serve the stated purpose.
