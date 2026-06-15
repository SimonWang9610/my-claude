---
title: "Riverpod: Test Override and Container Discipline"
impact: HIGH
impactDescription: overriding the unit under test instead of its deps proves nothing; bare reads on autoDispose providers cause immediate disposal
tags: state, riverpod, testing, override, ProviderContainer, autoDispose
---

## Riverpod: Test Override and Container Discipline

Riverpod's test seam is `ProviderContainer.test(overrides: […])` for unit/notifier tests
and `ProviderScope(overrides: […])` for widget tests. Providers under test are declared
with `@riverpod` codegen; overrides target the **generated** provider variable
(`alarmListProvider`, `alarmRepositoryProvider`, etc.). Apply these rules consistently.

**Auto-retry is active in tests** — if a test should not retry on failure, disable it:
`ProviderContainer.test(retry: (count, error) => null)`.

### 1. Override deps, not the unit

Override the unit's **dependencies** — never the unit itself. Overriding `alarmListProvider`
(the generated provider) tests only the override, not the `AlarmList` notifier.

```dart
// ✅ correct: override the repo dep, exercise the real @riverpod notifier
final container = ProviderContainer.test(
  overrides: [
    alarmRepositoryProvider.overrideWithValue(FakeAlarmRepository()),
  ],
);
```

### 2. Notifier fakes — 3.0 form

Use `extends _$Foo with Mock implements Foo` (mockito pattern) and override via
`fooProvider.overrideWith(FakeFoo.new)`. Implementing `_$Foo` alone throws at runtime.

```dart
// ✅ 3.0 fake: mixin Mock, implement the @riverpod class interface
class FakeAlarmList extends _$AlarmList with Mock implements AlarmList {
  @override
  Future<List<Alarm>> build() async => const [];
}

// ✅ override in test
final container = ProviderContainer.test(
  overrides: [alarmListProvider.overrideWith(FakeAlarmList.new)],
);
```

Seed state without replacing methods using `overrideWithBuild`:
```dart
alarmListProvider.overrideWithBuild((ref) => [Alarm.fixture()])
```

### 3. Listen before reading an autoDispose provider

A bare `container.read(p)` on an autoDispose async provider triggers immediate disposal
before the future resolves. Attach a listener first to hold the subscription.

```dart
// ❌ wrong — autoDispose provider (default with @riverpod) disposes before future resolves
final result = await container.read(alarmListProvider.future);

// ✅ correct — listener keeps the subscription alive
container.listen(alarmListProvider, (_, __) {});
final alarms = await container.read(alarmListProvider.future);
```

### 4. Widget tests — tester.container()

In widget tests, retrieve the `ProviderContainer` from the tester after pumping:
```dart
await tester.pumpWidget(ProviderScope(overrides: [...], child: const App()));
final container = tester.container(); // extension from riverpod_test
```

### 5. Invalidate upstream when verifying call counts

`verify(mock.method()).called(N)` can under-count because Riverpod pauses and resumes an
upstream provider without re-running `build()`. Force re-execution with
`container.invalidate(upstream)` between acts when verifying call counts.

```dart
// between act 1 and act 2:
container.invalidate(alarmRepositoryProvider);
// now act 2 triggers a fresh build(), and the verify count is accurate
```

Review heuristic: any `overrides: [alarmListProvider.overrideWith(…)]` in a test for
`AlarmList` (or any `@riverpod` notifier) is testing the override — move the override to
its dependency instead.

Ref: https://riverpod.dev/docs/how_to/testing  
Ref: https://riverpod.dev/docs/migration/from_riverpod_2_0_0_to_3_0_0
