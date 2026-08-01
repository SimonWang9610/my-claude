---
name: fl-architecture-design
description: >
  Authors design.md and contracts/ for Flutter features by applying architecture rules P1–P8:
  four-layer structure (UI → Provider → Data → Service), three-tier state-ownership
  (setState → InheritedWidget → Riverpod provider), SSOT repository with DTO→domain mapping,
  immutable domain models, and testability seams. At phase exit runs the verifiable-unit gate
  (P8): checks the three blocking triggers and writes PASS or records an extraction plan.
  Riverpod idioms use @riverpod code-gen with Notifier/AsyncNotifier; StateNotifier,
  StateProvider, and ChangeNotifierProvider are legacy. Full rule corpus and gate procedure
  are under references/.
  Trigger: "design this feature's architecture"; structuring widgets,
  Notifier/AsyncNotifier holders, repositories, services, or domain models for any feature.
---

# fl-architecture-design

**Design AGAINST the rules proactively, so the verify step rarely has to block.**

Author `design.md` and `contracts/<unit>.md` such that at phase exit, each blocking trigger is already a non-issue: no god-widgets, no layer violations, no unit lacking a testability seam. This skill both authors the design and runs the verifiable-unit gate (P8) at phase exit.

A seam missing from the design cannot be tested in the implementation; catch it here.

Write both artifacts terse — later phases re-read them each turn: terse prose, reference rule/AC
IDs instead of restating them; identifiers and paths exact; no invented abbreviations. Gate
verdicts and justifications are human-read: clear full sentences.

---

## Instructions

### 1. Load the rule index first

Open `references/how-to-use-bundled-rules.md` — it lists all 11 `core/` rules (always applied).
Keep it at hand throughout.

### 2. Follow the design procedure

Open `references/design-procedure.md` and work through all 8 steps in order.

### 3. Key decisions

- **Layer assignment** — `references/core/layering-and-structure.md`
- **State-ownership tier** (setState / InheritedWidget / provider) — `references/core/state-ownership-decision.md`
- **One owner per fact, derive the rest** — `references/core/state-placement.md`
- **Service returns raw DTOs only** — `references/core/service-isolation.md`
- **Repository = SSOT; DTO→domain; cache/retry here** — `references/core/repository-ssot.md`
- **Domain models immutable + value-equal** — `references/core/domain-models-immutable.md`
- **Holders: sealed async + dispose with ref.onDispose()** — `references/core/state-flow-and-async.md`, `references/core/state-boundary-and-lifecycle.md`
- **Widgets: compose small named classes** — `references/core/widget-composition.md`
- **Inject collaborators via constructors** — `references/core/dependency-injection.md`
- **Every unit independently verifiable (P8)** — `references/core/testability-seam.md`

For Riverpod package idioms, load the separate **`fl-riverpod`** skill. For widget build idioms
and performance, load the separate **`fl-implementation`** skill.

### 4. Verify — the verifiable-unit gate (P8)

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
If this skill was applied correctly throughout Steps 1–3, the gate should PASS with no
justifications.

---

## References

| Resource | Path |
|----------|------|
| Rule index (read first) | `references/how-to-use-bundled-rules.md` |
| Step-by-step design procedure | `references/design-procedure.md` |
| Core rules (11, universal) | `references/core/` |
| Right/wrong principle sketches | `references/principle-examples.md` |
| Per-principle violation signals | `references/principle-checks.md` |
| Verification procedure + report formats | `references/gate-procedure.md` |
