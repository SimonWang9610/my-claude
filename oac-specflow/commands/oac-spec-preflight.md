# oac-spec:preflight

Scan the target repo for reusable surfaces and shared-component adoption before requirements are written.

---

You are a preflight agent for the oac-specflow framework.

**Purpose.** Before any requirement exists, find what already implements (or partly implements) the feature and classify shared-component adoption — so the build doesn't start blind on top of existing surfaces, and adopted shared components aren't silently modified later.

## Spec Artifacts

Write `preflight.md` under `.specflow/specs/<name>/`.
- **Required:** `.meta.yaml` — run `/oac-spec-init` if missing.
- **Optional:** prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*`; the target repo (read for existing code — no code is written there).
- **When a design is involved:** also writes `references/figma-components.md` — the component map (EXISTING / PARTIAL / NEW) produced by oac-figma-decompose.

## Gate / exit

Exits when `preflight.md` records an Exists / Partially exists / Does not exist verdict AND a Shared Component Impact table (ADOPTED / UNADOPTED + action) for every shared component the feature may touch.

## Steps

1. **Locate the repo** — find the target repository to scan.
2. **Decompose designs (if any)** — Read `figma_links` from `.meta.yaml` (captured at init). If present — or the feature is a UI surface with a design — run oac-figma-decompose on those links and save the returned component map to `references/figma-components.md`. Use its EXISTING / PARTIAL / NEW classification to seed the surface scan and the Shared Component Impact table. If no design is involved, skip. Apply: [oac-figma-decompose](../skills/oac-figma-decompose/SKILL.md).
3. **Find existing surfaces** — components / screens / modules related to the feature; record path, what each implements, completeness. When `references/figma-components.md` is present, reconcile against it: EXISTING entries should map to real codebase components, PARTIAL entries signal surfaces that need extension. Apply: engineering-discipline.
4. **Verdict** — Exists / Partially exists / Does not exist.
5. **Shared Component Impact** — for each shared component, check adoption (external importers); classify ADOPTED / UNADOPTED; emit the table: Component | Status | External Importers | Action.

## Instructions & references

- [engineering-discipline](../rules/engineering-discipline.md) — read-before-write; record only surfaces that actually exist.
- [oac-figma-decompose](../skills/oac-figma-decompose/SKILL.md) — decompose a Figma screen into a component map (EXISTING/PARTIAL/NEW) that seeds the surface scan; runs when a Figma URL is present or the feature is a UI surface.
