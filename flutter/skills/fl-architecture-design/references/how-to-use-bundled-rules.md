# How to use the bundled rules

The corpus is split into a small, high-level **`core/`** that the gate ALWAYS reasons against.
Keeping the always-on set small lets the gate reason at architecture altitude instead of
drowning in specifics. When a surface looks like it might violate a rule, open that file by
its relative path and confirm against its examples — never cite from memory.

## Reading procedure

1. For every surface in scope, reason against the 11 high-level `core/` rules (always relevant).
2. The three blocking triggers (in the Verify step of `../SKILL.md` and detailed in
   `gate-procedure.md`) map onto specific `core/` rules — see the crosswalk at the bottom.

Widget build idioms and performance rules live in the separate **`fl-implementation`** skill.
State-management package idioms live in the separate **`fl-riverpod`** skill (or an analogous
skill for another package).

All paths below are relative to this `references/` directory.

---

## Core rules — `core/` (11, universal, always consulted)

- `core/layering-and-structure.md` — four layers, one-way deps (UI → Provider → Data → Service), no
  sibling-layer awareness, role-based feature folders. **(Trigger 2 anchor.)**
- `core/dependency-injection.md` — inject collaborators via constructors; wire once at a composition
  root; no hidden singletons. **(Trigger 3 anchor.)**
- `core/testability-seam.md` — every unit verifiable in isolation (`pumpWidget` / pure `dart test` with
  injected fakes); no logic in `build()`; no `BuildContext` in services. **(Trigger 1 + 3; P8.)**
- `core/service-isolation.md` — one stateless service per source; raw DTOs out; map transport errors at
  the boundary.
- `core/repository-ssot.md` — one repository = source of truth per type; DTO→domain mapping; owns
  caching/retry. **(Trigger 2.)**
- `core/domain-models-immutable.md` — immutable, pure-Dart domain models with value equality
  (`Equatable` / `@freezed` / `==` override).
- `core/state-ownership-decision.md` — choose the mechanism by scope: local `setState` →
  `InheritedWidget` scope (subtree, no navigation crossing) → provider (shared / survives navigation).
  **(Trigger 2.)**
- `core/state-placement.md` — one owner per fact, derive don't duplicate; place state at its narrowest
  level (the mechanism choice lives in `state-ownership-decision.md`). **(Trigger 2.)**
- `core/state-flow-and-async.md` — unidirectional flow with immutable state; sealed `loading | data |
  error` async.
- `core/state-boundary-and-lifecycle.md` — package-agnostic provider→UI boundary; dispose every
  controller/subscription/listener.
- `core/widget-composition.md` — compose small widgets; extract `const StatelessWidget` classes, not
  `Widget _buildX()` helpers; default `StatelessWidget`. **(Trigger 1.)**

---

## Trigger → core rule map

| Blocking trigger | Core rules to confirm against |
|------------------|-------------------------------|
| **1 — God-widget / God-holder / logic-in-build** | `core/widget-composition.md`, `core/testability-seam.md`, `core/layering-and-structure.md` |
| **2 — Layer violation / dual-source-of-truth** | `core/layering-and-structure.md`, `core/repository-ssot.md`, `core/state-ownership-decision.md`, `core/state-placement.md`, `core/service-isolation.md` |
| **3 — Testability seam missing** | `core/testability-seam.md`, `core/dependency-injection.md` |
