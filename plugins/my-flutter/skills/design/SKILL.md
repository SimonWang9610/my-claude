---
name: design
description: >-
  Use this skill when designing Flutter and Dart units or reviewing such a design: "how should this
  feature be layered", "where does this state live", "setState, InheritedWidget or a provider",
  "what should this repository or notifier expose", "is this widget testable", or the design step
  of a Flutter app. Gives the eight architecture principles (four layers, one source of truth,
  state at the right level, sealed async state, disposal, a testability seam for every unit), a
  rule card per decision, and the signals of a violation. Knowledge only: it writes no design file
  and runs no process (with my-workflow, spec-design does). Not for widget build and performance
  idioms (use my-flutter:implement) or Riverpod APIs (use my-flutter:riverpod).
---

# design

Flutter architecture rules. The design's format and steps belong to whoever runs the design; this
skill says what a sound Flutter design decides. It is agnostic of the state-management package:
package idioms live in that package's skill, such as `my-flutter:riverpod`.

## The eight principles

Four layers, one dependency direction: UI → Provider → Data → Service. The reason behind each
principle: [rules/principles.md](./rules/principles.md).

- **P1** Respect the four-layer boundary; dependencies point one way only.
- **P2** The service layer isolates each raw data source and adds no business logic.
- **P3** One repository is the single source of truth per data type; it maps raw DTOs to immutable,
  pure-Dart domain models.
- **P4** The provider layer owns observable UI state; widgets hold no business logic.
- **P5** Place state at the right level: local `setState` → `InheritedWidget` scope → provider.
- **P6** Widgets compose and render; `build` is a pure function of its inputs.
- **P7** Dispose every listener, controller and subscription; model async as a sealed
  loading / data / error type; never swallow errors.
- **P8** Every unit is independently verifiable in isolation.

## Per feature, in order

1. **Layers** — list every unit with its layer and role (`*Screen`, `*Widget`, `*Notifier`,
   `*Repository`, `*ApiClient`), and domain models apart from DTOs. An arrow that skips or reverses
   a layer is redesigned first.
2. **State tier** — per piece of state, the narrowest that works: local `setState` (one widget,
   dies with it) · `InheritedWidget` scope (a subtree on one page, no navigation crossing) ·
   provider (crosses pages, survives navigation, or app-wide). One owner per fact; derive the rest.
3. **Data path** — service: stateless, raw DTOs or a raw stream, transport errors mapped at the
   boundary. Repository: one per domain type, DTO → domain model, owns caching, retry and throttle;
   no DTO escapes it. Domain models: immutable, pure Dart, value-equal.
4. **Holders and widgets** — a holder exposes a sealed `loading | data | error` state and named
   commands, receives repositories by constructor, and disposes what it creates. Widgets are small
   named `const StatelessWidget` classes with a pure `build`.
5. **Seam per unit** — state how each unit runs in isolation: a widget through `pumpWidget` with
   an injected fake holder; a holder, repository or service in pure `dart test` with
   constructor-injected fakes; a domain model directly. A unit with no seam is a design defect: add
   an interface at the boundary and inject it.
6. **Shared widgets** — each one taken from `lib/core/` or another feature is reused as it is, or
   copied into this feature and adapted; never modified in place.

## A design is not ready while

Each of these needs a unit extracted or a boundary moved, not a note.

- **A god-widget, a god-holder, or logic in `build`** — a large `build` mixing concerns, business
  logic or IO in `build`, or a holder mixing data fetching, UI state and lifecycle effects with no
  seam. Check: can its behaviour run in an isolated test without pumping or mocking the whole host?
- **A layer violation or two sources of truth** — a widget calling a repository or service, server
  data cached in a holder field instead of read from the repository, or two owners of one fact.
  Check: is there one authoritative owner for every fact?
- **A missing testability seam** — a behaviour reachable only by mocking the parent, a singleton
  looked up inside a class body, or a `BuildContext` passed into a service or repository. Check:
  could each behaviour be exercised without the host?

## Rules

Read the card before deciding; never cite one from memory.

| Card | Read when |
|---|---|
| [principles.md](./rules/principles.md) | first: the eight principles with their reasons |
| [layering-and-structure.md](./rules/layering-and-structure.md) | assigning units to layers; feature folders |
| [state-ownership-decision.md](./rules/state-ownership-decision.md) · [state-placement.md](./rules/state-placement.md) | choosing the state tier; one owner per fact |
| [service-isolation.md](./rules/service-isolation.md) · [repository-ssot.md](./rules/repository-ssot.md) · [domain-models-immutable.md](./rules/domain-models-immutable.md) | the data path |
| [state-flow-and-async.md](./rules/state-flow-and-async.md) · [state-boundary-and-lifecycle.md](./rules/state-boundary-and-lifecycle.md) | a holder's state shape, async and disposal |
| [widget-composition.md](./rules/widget-composition.md) | cutting widgets |
| [dependency-injection.md](./rules/dependency-injection.md) · [testability-seam.md](./rules/testability-seam.md) | wiring collaborators; the seam per unit |
| [principle-checks.md](./rules/principle-checks.md) | checking a design or code against one principle: its violation signals and the card to open |
| [principle-examples.md](./rules/principle-examples.md) | a compact right and wrong sketch per principle |
