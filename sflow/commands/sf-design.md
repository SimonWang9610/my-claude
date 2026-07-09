---
description: Produce the technical design and per-unit contracts, then pass the architecture gate.
---
# sf:design

Produce the technical design plus the contract artifacts (interfaces, data models, APIs), then run the architecture gate before the phase closes.

---

**Purpose.** Decide the structure before any code is written and capture it as concrete, referenceable **contracts** — one per unit (module, data model, API/service) — so the next phase decomposes tasks against real interfaces, not prose. Technology-agnostic: the concrete principles and verifiable-unit checks live in the skills the spec's `workflow.yaml` lists for this phase, so the flow retargets to another stack by swapping those.

## Spec Artifacts

Read inputs and write outputs (`design.md`, `contracts/`) under `.specflow/specs/<name>/`.
- **Required:** `requirements.md` — run `/sf-requirements` if missing.
- **Optional:** `clarify.md`; `preflight.md`; `references/design-units.md` (the design unit map).
- **Additional:** steering `.specflow/steering/*`; prior-phase `references/`; the target repo (read to design against existing code — no code is written there).

## Gate / exit

Exits only when: every `AC-<story#>.<n>` / testable `NFR-<n>` is covered by ≥1 contract; a `contracts/<unit>.md` exists per introduced unit, each tracing to its AC-IDs and stating its testability seam; `design.md` indexes them and carries a Shared Unit Plan (Reuse-or-Copy; never modify an adopted unit); and the architecture gate returns PASS or every trigger has a recorded justification in `design.md`.

## Steps

1. **Map the units and their architecture layers per the project's architecture** — units, data flow, state ownership, error and testing strategy; diagram where it clarifies.
2. **Author each unit to the project's architecture rules** and the independently-verifiable-unit question, following the design procedure.
3. **Draft the contracts** — one `contracts/<unit>.md` per unit (kind, interface, data shapes, ownership, AC-IDs, testability seam, dependencies); every AC covered by ≥1 contract.
4. **Plan shared units** — classify each referenced shared unit Reuse or Copy; never modify an adopted unit — when `references/design-units.md` is present, reconcile each UI unit with its EXISTING (reuse) / PARTIAL (extend) / NEW (build) classification.
5. **Run the architecture gate (verify)** — the lightweight gate confirms each unit is independently verifiable; PASS, or record an extraction plan / justification under `## Architecture Gate — Justifications`.
