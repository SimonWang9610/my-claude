---
description: Scan for reusable surfaces and shared-unit impact before requirements (decomposing a design source if present).
---
# spec:preflight

Scan the target repo for reusable surfaces and shared-unit adoption before requirements are written.

---

**Purpose.** Before any requirement exists, find what already implements (or partly implements) the feature and classify shared-unit adoption — so the build doesn't start blind on top of existing surfaces, and adopted shared units aren't silently modified later.

## Spec Artifacts

Write `preflight.md` under `.specflow/specs/<name>/`.
- **Required:** `.meta.yaml` — run `/spec-init` if missing.
- **Optional:** prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*`; the target repo (read for existing code — no code is written there).
- **When a design is involved:** also writes `references/design-units.md` — the unit map (EXISTING / PARTIAL / NEW) produced by decomposing the design source.

## Gate / exit

Exits when `preflight.md` records an Exists / Partially exists / Does not exist verdict AND a Shared Unit Impact table (ADOPTED / UNADOPTED + action) for every shared unit the feature may touch.

## Steps

1. **Locate the repo** — find the target repository to scan.
2. **Decompose designs (if any)** — Read `design_links` from `.meta.yaml` (captured at init). If the project provides a design source, decompose it into a unit map and save the returned unit map (EXISTING / PARTIAL / NEW) to `references/design-units.md`. Use its classification to seed the surface scan and the Shared Unit Impact table. If no design is involved, skip.
3. **Find existing surfaces** — units / screens / modules related to the feature; record path, what each implements, completeness. When `references/design-units.md` is present (the unit/design map, if produced), reconcile against it: EXISTING entries should map to real codebase units, PARTIAL entries signal surfaces that need extension.
4. **Verdict** — Exists / Partially exists / Does not exist.
5. **Shared Unit Impact** — for each shared unit, check adoption (external importers); classify ADOPTED / UNADOPTED; emit the table: Unit | Status | External Importers | Action.
