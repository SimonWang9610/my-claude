---
name: fl-architecture-design
description: >
  Applies the Flutter specflow architecture rules — four-layer layering (UI → Provider → Data
  → Service), the three-tier state-ownership decision (setState → InheritedWidget scope →
  provider), SSOT repository, immutable + Equatable domain models, the testability seam (P8),
  and package idioms — *while authoring* design.md and contracts/. At phase exit, also verifies
  that each unit is independently verifiable (the verifiable-unit gate, P8): checks the three
  blocking triggers and writes PASS or records an extraction plan / justification.
  Carries the full rule corpus and gate procedure under references/.
  Triggers on the spec-design stage, on "design this feature's architecture", or whenever you
  are structuring widgets, state holders, repositories, services, or domain models for a feature.
---

# fl-architecture-design

**Design AGAINST the rules proactively, so the verify step rarely has to block.**

Author `design.md` and `contracts/<unit>.md` such that at phase exit, each blocking trigger
is already a non-issue: no god-widgets, no layer violations, no unit lacking a testability seam.
This skill both authors the design and runs the verifiable-unit gate (P8) at phase exit.

---

## Purpose

Apply architecture principles P1–P8 as a *design-time authoring discipline* — not a retroactive
reviewer. You are building structure on paper before any Dart is written. A seam missing from
the design cannot be tested in the implementation; catch it here.

---

## When to use

- The `spec-design` command stage (primary trigger).
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

### 5. Verify — the verifiable-unit gate (P8)

At design exit (and again at validate), confirm the gate QUESTION and check the THREE BLOCKING
TRIGGERS. Read `references/gate-procedure.md` for the full procedure and report formats (this
is a lightweight read — do NOT re-open the full corpus under `core/` at this step).

**Gate question:** Does each spec behavior map onto an independently verifiable unit — a widget
renderable via `pumpWidget` with injected fakes, or a state holder / repository / service
invocable in pure `dart test` with constructor-injected fakes — without mocking its host?

**Blocking trigger 1 — God-widget / God-holder / logic-in-build:** A widget with a very large
`build()` mixing multiple concerns, business logic or IO inside `build()`, or a state holder
mixing data-fetching + UI-state + lifecycle side-effects with no isolation seam.

**Blocking trigger 2 — Layer violation / dual-source-of-truth:** A widget calling a repository
or service directly (P1 break), server data cached in a holder field instead of read from the
repository SSOT (P3 break), or two owners for the same fact.

**Blocking trigger 3 — Testability seam missing:** A behavior reachable only by mocking the
entire parent widget or holder; a hidden singleton (`Service.instance` looked up inside a class);
or a `BuildContext` passed into a service or repository.

Write PASS, or record an extraction plan / justification per `references/gate-procedure.md`.
If this skill was applied correctly throughout Steps 1–4, the gate should PASS with no
justifications.

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
| Verification procedure + report formats | `references/gate-procedure.md` |
