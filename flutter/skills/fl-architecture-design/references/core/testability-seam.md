---
title: Every Unit Is Independently Verifiable
impact: CRITICAL
tags: testability, isolation, fakes, seam, unit-test, widget-test, build-method, buildcontext
---

## Every Unit Is Independently Verifiable

Every class — widget, notifier, repository, service — must be exercisable without real network, real databases, or sibling classes. Abstract interfaces at every layer boundary let fakes substitute at the constructor; constructor injection lets tests wire those fakes. Without this seam a fast, deterministic test suite is impossible.

- **Widget tests via `pumpWidget` with injected fakes** — supply a fake notifier/holder; never hit real I/O from a widget test.
- **Holder/repo/service tests as pure `dart test`** — no Flutter dependency; use a `ProviderContainer` with `overrides` to wire fakes into Riverpod notifiers, or construct non-Riverpod classes directly with fake collaborators passed through the constructor.
- **Keep `build()` free of I/O and business logic** — `build()` runs on every frame; derivation requiring I/O or significant CPU belongs in the state holder or `initState`, not the build method.
- **Never pass `BuildContext` below the provider layer** — resolve context-dependent values (locale, theme) in the widget, then pass plain Dart values down; lower layers must not require a widget tree to be tested.
- **No test-shaped production code** — production code that exists only to make a test convenient means the test was wrong or the design needs a real seam; don't reach for `@visibleForTesting` instead of a proper interface.
- **TDD seam-selection heuristic** — unsure which layer to test? Start at the widget — it fails at the lowest missing seam and points you down to where the abstraction belongs.
- **Never:** embed an HTTP call or JSON parse in `build()`; accept `BuildContext` in a service or repository; mock the class under test's own host instead of its dependencies.

```dart
// Pure Dart unit test — no Flutter import needed
class FakeAuthRepository implements AuthRepository {
  bool shouldSucceed;
  FakeAuthRepository({this.shouldSucceed = true});

  @override
  Future<User> login(String email, String password) async =>
      shouldSucceed ? User(id: '1', email: email) : throw AuthException.invalid;
}

void main() {
  test('login success stores user', () async {
    final container = ProviderContainer(
      overrides: [
        authRepositoryProvider.overrideWithValue(FakeAuthRepository()),
      ],
    );
    addTearDown(container.dispose);

    await container.read(loginNotifierProvider.notifier).login('a@b.com', 'secret');
    expect(
      container.read(loginNotifierProvider).value?.email,
      'a@b.com',
    );
  });
}

// Widget test — supply the same fake via ProviderScope overrides
await tester.pumpWidget(
  ProviderScope(
    overrides: [
      authRepositoryProvider.overrideWithValue(FakeAuthRepository(shouldSucceed: false)),
    ],
    child: const LoginScreen(),
  ),
);
```

Ref: https://docs.flutter.dev/app-architecture/case-study/testing | https://docs.flutter.dev/perf/best-practices | https://dcm.dev/blog/2025/07/30/navigating-hard-parts-testing-flutter-developers/
