# Ground truth (step 1) — construct · audit · reconcile

The flows are the ground truth every later decision is checked against: contracts realize
them, the self-check walks them. Build them from requirements/ACs — the audit
refines them, never originates them.

## Construct (1a)

**User flows** — one per story/journey: trigger → interaction steps → observable outcome.
Each step cites the AC it realizes. Give mermaid diagrams and a table:

| # | Step (actor + action) | Observable outcome | AC |
|---|-----------------------|--------------------|-----|
| 1 | user opens Devices page | list renders sorted A→Z | AC-1.1 |

**Data flows** — one row per **fact** (a named piece of data with one eventual owner):
origin → transforms → sinks. Give mermaid diagrams and a table:

| Fact | Origin (server · user input · device · derived) | Transforms | Sinks (render · persist · emit) | ACs |
|------|--------------------------------------------------|------------|--------------------------------|-----|

**Scope & blast radius** — from the flows: the screens/features touched, and every existing
unit on a flow path (the audit entry points).

**Coverage guard (blocking):** every AC appears on at least one flow; a flow step citing no
AC is invented scope — cut it or flag it to the caller.

## Audit (1b)

Goal: understand the business logic the sources carry so the design can reuse or wire into
it. Two source kinds, used differently:

- **Existing implementation** — live code on the blast radius or relevant code pointed out by the user. Its notes feed Reconcile: verdicts, attachment points, importers.
- **Legacy code references** — read-only material consulted for behavior only. Its notes
  are a behavioral spec: flows and cases the design preserves or deliberately drops. Never
  wired, never tagged.

Getting the facts — `/my-react:audit`, never ad-hoc scanning; greenfield (no sources)
→ skip. Design **queries only** — the query heals itself on a miss; bulk auditing is the
caller's preflight:

- `/my-react:audit query "which flows touch DeviceTable and the selection fact? —
  purpose: <the decision needing it>"` — covered → answered from the atlas; on a miss it
  reads exactly the missing spot (one flow at a time) and folds it back, never re-auditing
  a flow the atlas already answers.

## Reconcile (1c — after the audit)

Refine the flows with the audit notes, in order:

1. **WHERE is the new** — mark each flow segment NEW vs existing. The atlas index's
   Couples-with column / interaction map widens the blast radius: a flow coupled to a
   touched flow (shared fact, trigger, invalidation) is on the radius even when no
   requirement names it.
2. **WHICH legacy flows survive** — name the surviving segments and the exact
   **attachment point** (the existing unit) where a new segment joins each one. Legacy
   references contribute cases to preserve here, not attachment points.
3. **WHICH existing units get which tag:**
   - **REUSE** — does the job as-is; read-only.
   - **MODIFY** — near fit, bounded change, often in place (a bugfix edits the unit where
     it stands). List its external importers now — the self-check rejects an unmapped one.
   - **REPLACE** — only when the unit becomes **useless** once the new lands (name the
     removal), or **refactoring it demonstrably benefits the architecture** (name the
     payoff; scope to one unit/interface). Anything else is MODIFY. A refactor judged
     valuable beyond that scope becomes a **gate proposal** (SKILL.md § Refactor
     proposals), never a silent rewrite.
4. **HOW each attachment point is wired** — the mechanism per hop (props, shared query key,
   store selector, context, service event, callback), per the picker in
   [design.md](./design.md).

5. **VERIFY every named symbol** — each existing unit/symbol the design will reference
   gets `verified <path:line>` (a grep/read hit) in the unit inventory; behavior relied
   on but not read is marked `ASSUMED` and routed to Open items.    evaluation's G axis — a remembered symbol is not a grounded one.
6. **LEDGER the inherited defects** — every existing-scope violation of `rules/` on the
   blast radius (dual writer, cycle, God unit…) gets a verdict: `INHERIT <cost>` ·
   `FIX-NOW <refactor proposal>` · `QUARANTINE <containment boundary>`. Feeds the
   evaluation's T axis; a FIX-NOW becomes a gate proposal (SKILL.md § Refactor proposals).

**Output:** updated flow diagrams and tables (segments tagged NEW/existing) + a unit inventory — every
unit tagged REUSE / MODIFY / REPLACE / NEW with its `verified` marks + the inherited-defect
ledger. Contracts are written for MODIFY and NEW only; a REPLACE pairs a NEW contract with
the old unit's migration note.
