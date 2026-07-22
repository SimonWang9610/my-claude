# preflight

Find what already implements (or partly implements) the feature and classify shared-unit adoption
— before any requirement exists.

**Writes** `preflight.md` · **Reads** `.meta.yaml` (`/sflow init` if missing) · optional caller
materials (a design decomposition — a unit map EXISTING/PARTIAL/NEW; prior audits of the code).

**Steps**
1. **Survey** existing surfaces related to the feature — per surface: path, what it implements,
   completeness; reconcile with a provided design decomposition when present.
2. **Verdict** — Exists / Partially exists / Does not exist.
3. **Shared-unit impact** — per shared unit, check adoption (external importers) → table
   `Unit | ADOPTED/UNADOPTED | External Importers | Action` (Reuse as-is · Copy and customize ·
   Modify unadopted · No interaction).

**Exit** — `preflight.md` records the verdict + a shared-unit-impact row for every shared unit the
feature may touch.
