# Ground truth — flows, audit, reconcile (steps 1–3)

The flows are the ground truth every later decision is checked against: contracts realize
them, the self-check walks them. Build them from requirements/ACs — the audit
refines them, never originates them.

## Construct (step 1)

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

## Audit (step 2)

Goal: understand the business logic the sources carry so the design can reuse or wire into
it. Two source kinds, used differently:

- **Existing implementation** — live code on the blast radius or relevant code pointed out by the user. Its notes feed Reconcile: verdicts, attachment points, importers.
- **Legacy code references** — read-only material consulted for behavior only. Its notes
  are a behavioral spec: flows and cases the design preserves or deliberately drops. Never
  wired, never tagged.

Getting the facts — `/audit-code-flows`, never ad-hoc scanning; greenfield (no sources)
→ skip:

1. `/audit-code-flows query "which flows touch DeviceTable and the selection fact?"`
2. Unanswered → `/audit-code-flows extend <pointer | uncovered reference> — purpose:
   <the decision needing it> — kind: existing|legacy` (extend builds what the atlas
   lacks); never re-audit a flow the atlas already answers.

## Reconcile (step 3 — after the audit)

Refine the flows with the audit notes, in order:

1. **WHERE is the new** — mark each flow segment NEW vs existing. The atlas index's
   Couples-with column / interaction map extends the blast radius: a flow coupled to a
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

**Output:** updated flow diagrams and tables (segments tagged NEW/existing) + a unit inventory — every
unit tagged REUSE / MODIFY / REPLACE / NEW. Contracts are written for MODIFY and NEW only;
a REPLACE pairs a NEW contract with the old unit's migration note.
