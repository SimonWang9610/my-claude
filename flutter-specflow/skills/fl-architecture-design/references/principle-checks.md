# Principle checks — P1–P8 violation signals and bundled-rule crosswalk

Use when reviewing against a single principle: the signals are grep/read patterns that reveal a
violation; the crosswalk points at the bundled rule file with right/wrong examples. All crosswalk
paths are relative to this `references/` directory. Never cite a rule from memory — read the file.

---

## P1 — Four-layer boundary; dependencies point one way only

**Signals**
- A widget file with a direct `import '…/repositories/…'` or `import '…/services/…'` statement.
- A repository class with an `import '…/notifiers/…'` or `import '…/providers/…'` import (reverse dependency).
- A `FutureBuilder` or `StreamBuilder` inside a widget calling `_repo.fetchX()` directly.
- A service class that imports a holder or widget.

**Crosswalk:** `core/layering-and-structure.md`.

---

## P2 — Service layer: one stateless service per source; returns raw DTOs; maps transport errors

**Signals**
- A service method that constructs a domain model (`Device(id: …)`) rather than a DTO.
- A `List<…>`, `Map<String, …>`, or `Stream<…>` cache field on a service class.
- A `catch` block on a service method that swallows `DioException` / `SocketException` / a transport exception without converting to a typed error.
- Two service classes wrapping the same underlying source (duplicate `ApiClient`).
- A service method that calls another service method (chaining instead of repository orchestration).

**Crosswalk:** `core/service-isolation.md`.

---

## P3 — Repository is the SSOT per type; DTO→domain; owns caching/retry

**Signals**
- A holder field (`final List<Device> _devices = []`) holding the same entity type the repository streams.
- A holder calling `_api.fetchDevices()` or a stream source directly — skipping the repository.
- A `DeviceDto` reference in a widget, holder, or anywhere above the data layer.
- Two separate `watchAll()` streams subscribed by different holders for the same entity type (dual owner).
- Retry/exponential-backoff logic in a holder rather than the repository.

**Crosswalk:** `core/repository-ssot.md`,
`core/domain-models-immutable.md`.

---

## P4 — Provider layer: holder receives repos by constructor injection; package-agnostic seam

**Signals**
- A holder that contains both data-fetching logic and UI-state fields (God-notifier mixing concerns).
- Two holders both owning the same entity (dual-owner at the provider layer).
- A `useEffect`-style init block in a holder that mirrors repository data into a local field
  instead of subscribing to the repository's stream.
- Widget code that directly reads a `ChangeNotifier` field without going through a `ListenableBuilder`
  or equivalent, coupling the widget to the package's API.
- A holder with a method that performs a write AND updates local state directly (should invalidate
  via repository instead).

**Crosswalk:** `core/state-placement.md`,
`core/state-flow-and-async.md`,
`core/state-boundary-and-lifecycle.md`,
`core/dependency-injection.md`.

---

## P5 — State at the right level: ephemeral local; shared in provider

**Signals**
- A shared provider (notifier/bloc) holding ephemeral UI state: hover, focus, animation progress,
  field text that belongs to a single form widget.
- A `StatefulWidget` managing state that is also read by a sibling widget
  (should be lifted to a shared provider).
- A `StatefulWidget` managing state that must survive navigation
  (should be lifted to a provider with appropriate scope).
- A provider dependency graph where ephemeral UI preferences (scroll position, panel open/closed)
  are persisted alongside server-derived data.
- Page-local state (a wizard draft, a per-screen selection) either prop-drilled through many
  constructors or pushed into a global provider that survives after the page is popped — it should be
  scoped to the subtree with an `InheritedWidget` (or a subtree-scoped provider) instead.

**Crosswalk:** `core/state-ownership-decision.md`, `core/state-placement.md`,
`core/widget-composition.md`.

---

## P6 — Widgets compose and render; `build` is pure; const; theme tokens; mounted check

**Signals**
- A `Widget _buildX(…)` helper method that could be a `const StatelessWidget` class.
- A hard-coded hex color (`Color(0xFF…)` or `Colors.green`) in a widget `build()` rather than
  `Theme.of(context).colorScheme.*`.
- IO, a `Future.wait`, a sort/filter, or any `async` work inside `build()`.
- A `BuildContext` captured before an `await` and used after without a `mounted` check.
- A `StatelessWidget` or `StatefulWidget` constructor without `const` where it could have one.
- `Widget` helper methods on `State` classes that duplicate the pattern `const` widget extraction
  would solve (no rebuild isolation).

**Crosswalk:** `core/widget-composition.md`,
`core/widget-build-discipline.md`,
`core/widget-theming.md`,
`core/testability-seam.md`.

---

## P7 — Dispose every listener; async as sealed type; never swallow errors

**Signals**
- A `StreamSubscription` field with no `_sub?.cancel()` call in `dispose()`.
- An `AnimationController`, `TextEditingController`, or `ScrollController` declared but not
  disposed in `dispose()`.
- Two independent bool fields (`isLoading`, `hasData`) whose combination allows impossible states
  instead of a sealed `loading | data | error` type.
- `catch (e) { /* nothing */ }` or `catch (_) { print(e); }` with no error state update.
- A holder that calls `notifyListeners()` or emits state after the widget tree is unmounted
  (no lifecycle guard).

**Crosswalk:** `core/state-boundary-and-lifecycle.md`,
`core/state-flow-and-async.md`,
`core/widget-composition.md`.

---

## P8 — Every unit is independently verifiable in isolation (testability seam)

**Signals**
- A test that pumps the full `AppShell` or root widget to reach a feature behavior (host mocking).
- A holder that looks up `Service.instance` inside a method body rather than receiving it by
  constructor/ref injection.
- A repository or service that accepts a `BuildContext` parameter (context in service/repo = no
  isolation seam).
- A `dart test` for a holder that requires a running Flutter binding (`testWidgets`, not `test`).
- An AC behavior with no corresponding holder test or widget test that isolates exactly that behavior.
- Any `// TODO: test` comment beside an AC-named behavior with no test seam planned.

**Crosswalk:** `core/testability-seam.md`,
`core/dependency-injection.md`.

---

## Trigger → principle → bundled-rule map

| Blocking trigger | Principles | Primary bundled rules |
|------------------|------------|----------------------|
| **1 — God-widget / God-holder / logic-in-build** | P4, P6, P8 | `core/widget-build-discipline.md`, `core/widget-composition.md`, `core/testability-seam.md`, `core/layering-and-structure.md` |
| **2 — Layer violation / dual-source-of-truth** | P1, P3 | `core/layering-and-structure.md`, `core/repository-ssot.md`, `core/state-placement.md`, `core/service-isolation.md` |
| **3 — Testability seam missing** | P8 (underwritten by P1, P4, P6) | `core/testability-seam.md`, `core/dependency-injection.md` |

P2 (service layer isolation), P5 (ephemeral vs shared), and P7 (dispose / sealed async) are not
blocking triggers in themselves, but a violation surfaced during the gate is recorded as a finding
and resolved before phase exit.

---

## Quick decision: where does this fact live?

```
Is the value fetched from / owned by a remote source (REST / other data sources)?
├─ yes → Repository stream (P3). Only the repository owns and streams this type.
│         Holder subscribes to the stream; widget watches the holder.
└─ no  → Who reads it, and does it cross a navigation page? (P5 — state-ownership-decision)
         ├─ one widget, dies with it      → Local setState / controller.
         ├─ a subtree on ONE page reads shared data, no nav → InheritedWidget scope (data down, not callbacks).
         └─ across pages, survives nav, or the subtree must mutate it → Shared provider / notifier (P4).

Need server data AND a client selection (e.g. selectedId)?
└─ keep selectedId in the holder, derive the Device at read time (P4):
   state.devices.firstWhere((d) => d.id == state.selectedId)
   Never mirror the resolved entity into a second field.

Writing to the server?
└─ command on the holder → repository.save() → stream emits updated model → holder rebuilds (P1, P3, P4).
   Never let the widget call the repository directly (P1).
   Never swallow the error; surface it as an error state (P7).

Adding a color?
└─ Theme.of(context).colorScheme.* — never Color(0xFF…) (P6).

New widget or holder class?
└─ Can I test it in dart test / testWidgets with a fake injected by constructor?
   ├─ yes → Good — seam exists (P8).
   └─ no  → Extract until the answer is yes, or record a justification.
```
