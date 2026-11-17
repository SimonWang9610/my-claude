---
name: review
description: >-
  Use this skill when reviewing Flutter and Dart code or its tests: "review this Flutter diff", "is
  this widget or notifier right", "are these tests honest", "why does this test never fail". Gives
  the architecture rules that apply to each kind of unit, the three structural defects that block a
  change, and how to spot a test that passes but misses the behaviour or cannot fail at all.
  Knowledge only: the verdict, severity scale and report belong to the reviewer (with my-workflow,
  the spec-code-reviewer agent). Not for writing the fix (use my-flutter:implement).
---

# review

Flutter review checks. Scope, severity and the report's shape belong to the reviewer; these say
what to look for in Flutter code and how to prove it. Open a rule card before citing it; never cite
from memory. Report only what you are confident of, with its evidence.

## By kind of unit

Classify each changed Dart file, then sketch the data flow: where each fact lives, who writes it,
who reads it.

| Unit | Typical paths | Check against |
|---|---|---|
| Widget | `screens/`, `widgets/`, `_screen.dart`, `_page.dart` | P6 · widget-composition · testability-seam · implement's build-discipline and theming |
| State holder | `providers/`, `_notifier.dart`, `_bloc.dart`, `_cubit.dart`, `_controller.dart` | P4, P5, P7 · state-ownership-decision · state-placement · state-flow-and-async · state-boundary-and-lifecycle |
| Repository | `_repository.dart` | P3 · repository-ssot · domain-models-immutable |
| Service | `_service.dart`, `_client.dart`, `_api.dart` | P2 · service-isolation |
| Domain model, DTO | `models/` | P3 · domain-models-immutable |
| Composition root | `main.dart`, `app.dart`, `injection.dart` | P1 · dependency-injection |
| Test | `test/`, `_test.dart`, `integration_test/` | `../test/rules/flutter-tests.md` and the cards below |

The cards are in `../design/rules/` and `../implement/rules/`.

## In order

1. **Structure** — the three defects under "A design is not ready while" in `my-flutter:design`:
   a god-widget or logic in `build`, a layer violation or two sources of truth, a missing
   testability seam. These are the most severe findings a Flutter change can carry.
2. **State and data** — the right state tier; one owner per fact; sealed async state consumed
   exhaustively; everything the unit created is disposed (a listenable passed in is its owner's to
   dispose); raw DTOs stay below the repository.
3. **Tests** — the cards below.
4. **Performance, only on a visible hazard** — a long list without `.builder`, expensive work in
   `build`, an image decoded at the wrong size, an animation without `child:`. Advisory unless
   measured. Cards: `../implement/rules/perf-*.md`.
5. **Riverpod**, when the diff touches providers or `ref` → `my-flutter:riverpod`. A legacy
   provider (`StateNotifier`, `StateProvider`, `ChangeNotifierProvider`) in new code is a finding;
   in a file already full of them, a note.

## Rules

| Card | Read when |
|---|---|
| [tests-missing-behavior.md](./rules/tests-missing-behavior.md) | a test whose name claims more than its body proves: four shapes with grep recipes |
| [false-positive-tests.md](./rules/false-positive-tests.md) | a test that may pass whether or not the code works: eight forms with grep recipes |
| [false-positive-signals.md](./rules/false-positive-signals.md) | the signals to spot on sight, and the mutation check that confirms one |
