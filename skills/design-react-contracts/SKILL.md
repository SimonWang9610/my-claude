---
name: design-react-contracts
description: >
  Design React contracts — public API, data flow, state design per unit — and the wiring
  architecture, from requirements/ACs grounded in audit notes. Produces design.md +
  grouped contract files; fast path yields a contract delta for bugfix-scale changes.
---

# design-react-contracts

Turn requirements into **contracts** — each unit's public surface, data flow, and state
design — plus one architecture view wiring them. Contracts only: name types, boundaries,
mechanisms; no code bodies. Design from first principles: units derive from what the
flows fundamentally require, never from the shape existing code happens to have — the
audit says what exists to wire into, not what the design should look like; structure
fighting the fundamentals → REPLACE or refactor proposal, never a design bent to fit.

## Inputs

- **Requirements & ACs** — observable outcomes; never invent scope beyond them.
- **Existing implementation** — live code to wire into or change; audited for verdicts,
  attachment points, importers.
- **Legacy code references** — read-only behavioral spec; never wired, never modified.
- **Audit notes / component map** (optional) — notes (`audit-code-flows` format) used
  first, gaps filled by invoking that skill; `decompose-figma` rows seed the unit inventory.
- **Direct instructions** — narrows the procedure, never waives the self-check.

## Output

To the caller-designated dir; templates in [references/design.md](./references/design.md):

- `design.md` — architecture diagram, per-flow unit sequence diagrams + step tables,
  ownership table, unit index, failure containment, test strategy, open items. Never
  restates a contract.
- `contracts/<group>.md` — contracts grouped by relation (units on the same flow/slice
  share a file; each unit in exactly one). Fast path → a single contract delta.

**Discipline:** terse, goal-accurate — AC/rule IDs, exact identifiers/paths, no filler.
Decisions, never reasoning ("why" = a one-line rule citation; unresolved → Open items).
Fixed shape: code only in the template's fenced blocks; all else one-line prose or table rows.

## Rules

Read the relevant file before deciding; cite it in design notes:

- [rules/state-ownership.md](./rules/state-ownership.md) — fact ownership, concrete state design, URL state, write semantics
- [rules/decompose-components.md](./rules/decompose-components.md) — cutting units, split/merge blast radius, perf boundaries
- [rules/services-and-boundaries.md](./rules/services-and-boundaries.md) — one-way deps, services, containment, schemas, races

## Full path (feature-scale)

Steps 1–3 → [references/ground-truth.md](./references/ground-truth.md); 4–5 →
[references/design.md](./references/design.md).

1. **Ground truth** — user & data flows from requirements/ACs alone; scope + blast radius.
2. **Audit** — provided notes first; `/audit-code-flows` for uncovered entry points; skip when unnecessary.
3. **Reconcile** — refine flows against the notes; tag units REUSE/MODIFY/REPLACE; name each attachment point's wiring.
4. **Design** — per MODIFY/NEW unit: data contract, state design, decomposition per `rules/` → design.md + contracts/.
5. **Self-check** — internal, ONE pass; findings → one re-design of the affected units.
6. **Resolve or finalize** — open items → pause with what was tried, wait for steering, resume; else hand back.

**Refactor proposals:** touched code fighting the requirements → name root friction,
restricted scope, payoff, cost delta; present at the gate beside the minimal design — the
caller chooses. Never silently expand scope; never withhold a clearly valuable refactor.

## Fast path — bugfix/tweak: ≤2 existing units, no new fact or flow segment

1. Locate the owning unit(s); trace only the affected fact/case.
2. **Contract delta** (template in design.md): case, surface change, must-not-change, importers.
3. Self-check: one owner per fact + blast radius closed. Anything more → full path.
