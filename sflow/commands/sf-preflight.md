---
description: Scan for reusable surfaces and shared-unit impact before requirements (decomposing a design source if present).
---
# sf:preflight

Find what already implements (or partly implements) the feature and classify shared-unit
adoption — before any requirement exists. Writes `preflight.md` (+ `references/design-units.md`
when a design source is decomposed) under `.specflow/specs/<name>/`. Requires `.meta.yaml`
(run `/sf-init` if missing); steering as context; the target repo is read, never written.

**Steps.**

1. Design source in `.meta.yaml` `design_links` → decompose it into a unit map
   (EXISTING / PARTIAL / NEW) → `references/design-units.md`; none → skip.
2. Survey existing surfaces related to the feature — per surface: path, what it
   implements, completeness; reconcile with the unit map when present.
3. Verdict: Exists / Partially exists / Does not exist.
4. Shared Unit Impact — per shared unit, check adoption (external importers) → table
   `Unit | ADOPTED/UNADOPTED | External Importers | Action` (Action: Reuse as-is · Copy
   and customize · Modify unadopted · No interaction).

**Exit.** `preflight.md` records the verdict + a Shared Unit Impact row for every shared unit
the feature may touch.
