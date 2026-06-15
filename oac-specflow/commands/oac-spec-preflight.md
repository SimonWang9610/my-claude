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

## Gate / exit

Exits when `preflight.md` records an Exists / Partially exists / Does not exist verdict AND a Shared Component Impact table (ADOPTED / UNADOPTED + action) for every shared component the feature may touch.

## Steps

1. **Locate the repo** — find the target repository to scan.
2. **Find existing surfaces** — components / screens / modules related to the feature; record path, what each implements, completeness. Apply: engineering-discipline.
3. **Verdict** — Exists / Partially exists / Does not exist.
4. **Shared Component Impact** — for each shared component, check adoption (external importers); classify ADOPTED / UNADOPTED; emit the table: Component | Status | External Importers | Action.

## Instructions & references

- [engineering-discipline](../rules/engineering-discipline.md) — read-before-write; record only surfaces that actually exist.
