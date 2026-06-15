---
paths: ["**/*_test.dart", "**/integration_test/**", "**/test/**"]
---

# Test quality

Apply when writing or editing a Dart/Flutter test. A test that passes without exercising the real
behavior is worse than no test — it hides the gap.

- **Assert observable outcomes, not implementation.** Check rendered widgets (`find.text`,
  `find.byType`, enabled/disabled, visible/absent), returned state, and emitted states — not that an
  internal method ran or a mock was called a certain number of times. Reserve `verify(...)` for a
  fire-and-forget side effect (navigation, analytics) that has no other observable.
  Ref: https://docs.flutter.dev/cookbook/testing/widget/introduction
- **Map each test to an acceptance-criterion ID.** Every AC behavior has a named test; every test names
  the AC it covers — embed the `AC-<story>.<n>` / `NFR-<n>` ID in the `group(...)` description so a
  coverage gap is a grep query, not a guess.
- **Build fixtures from the production domain type, not hand-written maps.** A fixture typed as the real
  domain model (or built by its constructor / `freezed` copy) breaks loudly when the model changes; a
  loose `Map<String, dynamic>` or ad-hoc literal silently drifts and tests a shape that no longer exists.
- **No tautologies; prefer fakes over mocks.** Don't assert a mock returns what you stubbed it to return
  — that exercises the mock, not the unit. Use an in-memory fake that implements the real interface so
  interacting methods are genuinely exercised; if a wholesale mock bypasses the behavior under test, the
  test is a false positive — decompose the unit instead (see architecture-principles P8).
- **Use real async/stream machinery when the AC depends on async behavior.** Test loading→data→error
  ordering and throttle/debounce timing with a real `StreamController`/`ProviderContainer`/`Bloc` and
  `expectLater(..., emitsInOrder([...]))`, driving time with `fakeAsync`/`elapse` — never a real
  `Future.delayed`. Never call `pumpAndSettle()` while a live network call or infinite timer is pending
  (it hangs to a 30 s timeout); advance with `pump(Duration)` instead.
- **Turn one-shot greps into CI guards.** A ban verified once at review time (no hard-coded hex, no
  `Widget _buildX()` helper, no service import in a widget, no business logic in `build`) must become an
  enduring `flutter analyze` lint, `custom_lint`/DCM rule, or test — or it regresses unseen.
