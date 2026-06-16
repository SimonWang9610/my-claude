---
paths: ["**/*.dart"]
---

# Architecture principles (P1–P8)

Apply when a spec adds a widget, state holder (notifier/bloc/cubit/controller),
repository, service, domain model, stream, theming token, or a piece of selection
state. Cite the principle ID (P3, P6…) in design notes and violation messages.

The architecture is four layers with a **single dependency direction**:

```
UI Layer        widgets: watch shared state, hold ephemeral private state, run methods, build sub-trees
   │ depends on
Provider Layer  state holders: expose observable state + commands (state-management-package AGNOSTIC)
   │ depends on
Data Layer      repositories: single source of truth; raw DTO → immutable domain model
   │ depends on
Service Layer   data sources: REST ApiClient and other raw sources; raw payloads, no business logic
```

- **P1 — Respect the four-layer boundary; dependencies point one way only (UI → Provider → Data → Service).**
  A widget never calls a repository or service directly; a repository never imports a provider; no
  layer reaches around its neighbour. Skipping or reversing a layer couples two layers so neither is
  testable in isolation and a change in one cascades into the other.
  Ref: https://docs.flutter.dev/app-architecture/guide
- **P2 — The Service layer isolates each raw data source and adds no business logic.**
  One stateless service per source (e.g. a REST `ApiClient`); it returns raw DTOs or a
  `Stream<RawPayload>` and maps transport exceptions (`SocketException`, an HTTP error) to typed errors
  at the boundary. No domain-model construction, no caching, no app state inside a service. Prevents the
  transport SDK leaking into every caller.
  Ref: https://docs.flutter.dev/app-architecture/case-study/data-layer
- **P3 — One repository is the single source of truth per data type; it maps raw DTOs to immutable, pure-Dart domain models.**
  Only the repository mutates its type's canonical state. It converts wire DTOs → domain models and owns
  caching/retry/throttle. Domain models are immutable and free of Flutter/JSON/DB imports; DTOs are
  separate classes. Prevents dual-source-of-truth and wire-format details bleeding up into widgets.
  Ref: https://docs.flutter.dev/app-architecture/concepts
- **P4 — The Provider layer owns observable UI state; widgets hold no business logic; the boundary is package-agnostic.**
  State holders receive repositories by constructor injection, expose observable state + named commands,
  and own one fact each (derive, don't duplicate). Whether the holder is a Riverpod `Notifier`, a Bloc/
  Cubit, or a `ChangeNotifier`, the UI sees only "observable state + commands" — package idioms stay in
  the package's own skill (e.g. `fl-riverpod`). Prevents God-notifiers and couples-the-whole-tree-to-one-package.
  Ref: https://docs.flutter.dev/app-architecture/guide
- **P5 — Place state at the right level: local `setState` → `InheritedWidget` scope → provider.**
  Single-widget, never-persisted, no sibling reads → `StatefulWidget`/local controller. Shared by a
  subtree on one page that must not cross a navigation boundary → scope it with an `InheritedWidget` (or
  a subtree-scoped provider). Read across pages, survives navigation, or app-wide → a provider (your
  state-management package, feature-scoped where possible). Don't put ephemeral UI state in a shared
  container, don't prop-drill page-local state, and don't let page-local state leak into a global store.
  Within whichever holder owns a fact, keep one owner and derive the rest. Prevents bloated global
  stores, prop-drilling, and state leaking across routes.
  Ref: https://docs.flutter.dev/data-and-backend/state-mgmt/ephemeral-vs-app
- **P6 — Widgets compose and render; `build` is a pure function of its inputs.**
  Compose small widgets; extract a `const StatelessWidget` class instead of a `Widget _buildX()` helper
  method; declare `const` constructors everywhere possible; keep `build` free of IO, business logic, and
  expensive work; never use a `BuildContext` across an `await` without a `mounted` check; add a `Key`
  only to reorder stateful siblings; read colors/typography from `Theme.of(context)` tokens, never
  hard-coded. Prevents wasted rebuilds, dark-mode regressions, and async-gap context crashes.
  Ref: https://docs.flutter.dev/perf/best-practices
- **P7 — Dispose every listener/controller/subscription; model async as a sealed loading/data/error type; never swallow errors.**
  Cancel `StreamSubscription`s and dispose `AnimationController`/`TextEditingController`/`ScrollController`/
  `ChangeNotifier` in `dispose()` (remove listeners first, then dispose). Represent every async operation
  as a three-state union (`loading | data | error`) so `isLoading == true && data != null` is
  unrepresentable, and route caught exceptions into the error state — never `catch (_) {}`. Prevents
  leaks, `setState() after dispose`, and silent write failures that pass green.
  Ref: https://docs.flutter.dev/app-architecture/recommendations
- **P8 — Every unit is independently verifiable in isolation (a testability seam).**
  Each acceptance-criterion behavior must be reachable as: a widget rendered via `pumpWidget` with
  injected fakes, or a state holder / repository / service invoked in pure `dart test` with
  constructor-injected fakes — **without mocking its host widget or holder**. A unit testable only by
  mocking its parent, by reaching a singleton, or because logic lives in `build`, fails P8.
  (P1–P7 underwrite P8: layer boundaries + constructor injection + logic-out-of-build are what create the seam.)
  Ref: https://docs.flutter.dev/app-architecture/case-study/testing

Worked right/wrong examples and per-principle checks: see
../skills/fl-architecture-design/references/principle-examples.md and principle-checks.md.
