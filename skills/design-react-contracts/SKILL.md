---
name: design-react-contracts
description: >
  Design React contracts — public API, data flow, state design per unit — and the wiring
  architecture, from requirements/ACs grounded in audit notes. Produces design.md +
  grouped contract files; fast path yields a contract delta for bugfix-scale changes.
---

# design-react-contracts

Turn requirements into **contracts** — each unit's public surface, data flow, and state
design — plus one architecture view wiring them. Contracts only, never implementation:
name types, boundaries, mechanisms; no code bodies.

## Inputs

- **Requirements & ACs** — observable outcomes to achieve, never implementation steps. Do
  not invent scope beyond them.
- **Existing implementation** — live code the work wires into or changes. Audited for
  wiring: verdicts, attachment points, importers.
- **Legacy code references** — read-only material consulted for behavior only (old version,
  other repo, samples). A behavioral spec — never wired, never modified.
- **Audit notes** (optional) — pre-made notes in `audit-code-flows` format; used first,
  gaps filled by invoking that skill.
- **Component map** (optional) — a `decompose-figma` map; its EXISTING / PARTIAL / NEW
  rows seed the unit inventory as REUSE / MODIFY / NEW proposals.
- **Direct instructions** — caller steering: where to start, focus, avoid. They narrow the
  procedure, never waive the self-check.

## Output

Written to the caller-designated design directory:

- `design.md` — architecture diagram, AC-traced flows, ownership table, unit index linking
  each contract, failure containment, test strategy (AC → level → test location), open
  items. Never restates a contract.
- `contracts/<group>.md` — unit contracts grouped by relation (units collaborating on the
  same flow/feature slice share a file; each unit appears in exactly one). Templates in
  [references/design.md](./references/design.md).
- Fast path → a single contract delta instead.

**Output discipline:** every artifact concise, terse and goal-accurate — cite AC/rule IDs, exact
identifiers and paths, no restatement, no filler.

## Rules

`rules/` steers design decisions — concise rules with code samples. Read the relevant file
before deciding; cite it in design notes:

- [rules/state-ownership.md](./rules/state-ownership.md) — where a fact lives; its concrete
  state design (useState · custom hook · context provider · store · listenable service ·
  query hook); URL-addressable state; write semantics (invalidate vs optimistic + rollback)
- [rules/decompose-components.md](./rules/decompose-components.md) — how to cut units, and
  when not to (blast radius of splits/merges); performance boundaries (code-split,
  containment, virtualization)
- [rules/services-and-boundaries.md](./rules/services-and-boundaries.md) — one-way
  dependencies, side effects behind services, failure containment, boundary schemas +
  typed errors, race ownership

## Full path (feature-scale work)

1. **Ground truth** — user & data flows from requirements/ACs alone; scope and blast
   radius. → [references/ground-truth.md](./references/ground-truth.md)
2. **Audit** — use provided audit notes first; invoke `/audit-code-flows` for uncovered
   blast-radius entry points. Skip when unnecessary. → ground-truth.md § Audit
3. **Reconcile** — refine flows against the notes; tag existing units
   REUSE / MODIFY / REPLACE; name each attachment point's wiring.
   → ground-truth.md § Reconcile
4. **Design** — per MODIFY/NEW unit: data contract, state design, decomposition, applying
   `rules/`; consolidate into design.md + contracts/.
   → [references/design.md](./references/design.md)
5. **Self-check** — internal self-correction, never a user-facing report; blocking findings
   loop back to step 4 (max 2 loops). → design.md § Self-check
6. **Resolve or finalize** — open items remaining? **Pause**: present them to the caller
   with what was tried, wait for decisions or steering, resume the affected steps with that
   input. Otherwise hand back the artifacts.

**Propose refactors deliberately.** When the audit shows the touched code fights the
requirements — tangled ownership, missing seams, duplicated facts — judge whether a
bounded refactor pays off even though it expands scope: name the **root friction**, the
**restricted scope**, the **payoff** (this feature + near-term work), and the **cost
delta** (extra units/tasks). Present it at the gate as an explicit option beside the
minimal design — the caller chooses. Never silently expand scope; never withhold a
refactor you judge clearly valuable.

## Fast path (small bounded change)

Take it for a bugfix or tweak: ≤2 existing units, no new fact, no new flow segment. MODIFY
happens in place.

1. Locate the owning unit(s); trace only the affected fact/case.
2. Write a **contract delta** (template in design.md): case fixed, surface change (often
   none), must-not-change, importers checked.
3. Self-check only: one owner per fact + blast radius closed.

A new fact, new flow segment, or third unit → upgrade to the full path.
