---
name: fl-architecture-design
description: >
  Design-time skill: applies the flutter-specflow architecture rules — four-layer layering
  (UI → Provider → Data → Service), the three-tier state-ownership decision (setState →
  InheritedWidget scope → provider), SSOT repository, immutable + Equatable domain models,
  the testability seam (P8), and package idioms — *while authoring* design.md and contracts/.
  Carries the full rule corpus under references/. The companion fl-architecture-gate verifies
  the result at phase exit. Triggers on the fl-spec-design stage, on "design this feature's
  architecture", or whenever you are structuring widgets, state holders, repositories,
  services, or domain models for a feature.
---

# fl-architecture-design

**Design AGAINST the rules proactively, so the gate rarely has to block.**

Author `design.md` and `contracts/<unit>.md` such that when `fl-architecture-gate` runs at
phase exit, each blocking trigger is already a non-issue: no god-widgets, no layer violations,
no unit lacking a testability seam.

---

## Purpose

Apply architecture principles P1–P8 as a *design-time authoring discipline* — not a retroactive
reviewer. You are building structure on paper before any Dart is written. A seam missing from
the design cannot be tested in the implementation; catch it here.

---

## When to use

- The `fl-spec-design` command stage (primary trigger).
- Structuring a feature's units from scratch: widgets, state holders, repositories, services, models.
- Revisiting or extending `design.md` to add new units or change ownership decisions.

---

## Instructions

### 1. Load the rule index first

Open `references/how-to-use-bundled-rules.md` — it lists all 13 `core/` rules (always applied)
and the three `conditional/` packs. Keep it at hand throughout.

### 2. Follow the design procedure

Open `references/design-procedure.md` and work through all 8 steps in order.

### 3. Key decisions

- **Layer assignment** — `references/core/layering-and-structure.md`
- **State-ownership tier** (setState / InheritedWidget / provider) — `references/core/state-ownership-decision.md`
- **One owner per fact, derive the rest** — `references/core/state-placement.md`
- **Service returns raw DTOs only** — `references/core/service-isolation.md`
- **Repository = SSOT; DTO→domain; cache/retry here** — `references/core/repository-ssot.md`
- **Domain models immutable + value-equal** — `references/core/domain-models-immutable.md`
- **Holders: sealed async + dispose every controller** — `references/core/state-flow-and-async.md`, `references/core/state-boundary-and-lifecycle.md`
- **Widgets: compose, const, build is pure** — `references/core/widget-composition.md`, `references/core/widget-build-discipline.md`
- **Colors/typography from Theme tokens** — `references/core/widget-theming.md`
- **Inject collaborators via constructors** — `references/core/dependency-injection.md`
- **Every unit independently verifiable (P8)** — `references/core/testability-seam.md`

### 4. Conditional packs — open only when the scenario applies

- `references/conditional/performance/` — concrete performance hazard surfaced (advisory, non-blocking).
- For Riverpod package idioms, load the separate **`fl-riverpod`** skill (`../fl-riverpod/SKILL.md`). Use an analogous skill for other state-management packages.

### 5. Gate hand-off

At design exit, run `../fl-architecture-gate/SKILL.md`. It verifies P8 and the three blocking
triggers. If this skill was applied correctly, the gate should PASS with no justifications.

---

## References

| Resource | Path |
|----------|------|
| Rule index (read first) | `references/how-to-use-bundled-rules.md` |
| Step-by-step design procedure | `references/design-procedure.md` |
| Core rules (13, universal) | `references/core/` |
| Conditional packs | `references/conditional/` |
| Right/wrong principle sketches | `references/principle-examples.md` |
| Per-principle violation signals | `references/principle-checks.md` |
| Gate skill | `../fl-architecture-gate/SKILL.md` |
