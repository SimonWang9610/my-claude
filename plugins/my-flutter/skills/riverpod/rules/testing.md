---
title: "Riverpod: Test Override and Container Discipline"
impact: HIGH
impactDescription: overriding the unit under test instead of its deps proves nothing; bare reads on autoDispose providers cause immediate disposal
tags: state, riverpod, testing, override, ProviderContainer, autoDispose, mocktail, fakeAsync
---

## Riverpod: Test Override and Container Discipline

<!-- TOC -->
1. [Override deps, not the unit](#1-override-deps-not-the-unit)
2. [Notifier fakes — 3.0 form](#2-notifier-fakes--30-form)
3. [Listen before reading an autoDispose provider](#3-listen-before-reading-an-autodispose-provider)
4. [Widget tests — tester.container()](#4-widget-tests--testercontainer)
5. [Invalidate upstream when verifying call counts](#5-invalidate-upstream-when-verifying-call-counts)
6. [Mocktail rules](#6-mocktail-rules)
7. [pump vs pumpAndSettle](#7-pump-vs-pumpandsettle)
8. [fakeAsync for timers](#8-fakeasync-for-timers)
9. [Stream assertions](#9-stream-assertions)
<!-- /TOC -->

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

---

### 6. Mocktail rules

The project uses **Mocktail** (not mockito). Three rules prevent runtime failures:

**6a. registerFallbackValue for custom types used with `any()`.**
`any()` requires a registered fallback when the argument type is a custom class:

```dart
// setUpAll — run once before all tests in the group
setUpAll(() {
  registerFallbackValue(FakeAlarm());
});

// FakeAlarm is a minimal concrete stand-in — just needs a no-arg constructor
class FakeAlarm extends Fake implements Alarm {}
```

Omitting `registerFallbackValue` causes a `StateError` at the first `any()` call on that
type. Primitives (`int`, `String`, `bool`) and `null` do not need registration.

**6b. `Mock` mixin, not extension.**
Mocktail mocks use `extends Mock implements Foo` — no code generation required:

```dart
class MockAlarmRepository extends Mock implements AlarmRepository {}
```

**6c. `when(...).thenAnswer((_) async => value)` for async stubs.**
Use `thenAnswer` (not `thenReturn`) for `Future`- and `Stream`-returning methods:

```dart
when(() => mockRepo.getAlarms()).thenAnswer((_) async => [Alarm.fixture()]);
```

---

### 7. pump vs pumpAndSettle

- `tester.pump()` — advances by one frame; use for discrete state transitions where no
  animation is involved.
- `tester.pumpAndSettle()` — repeatedly pumps until no more frames are scheduled; use
  **only** when an animation (route transition, `AnimationController`) must fully settle.

Prefer `pump()`. Reaching for `pumpAndSettle()` when there is no animation is a test-speed
smell and can hide timing bugs.

```dart
// ✅ one frame is enough for a state change with no animation
await tester.pump();
expect(find.text('0 alarms'), findsOneWidget);

// ✅ pumpAndSettle only when a transition animation must complete
await tester.pumpAndSettle();
expect(find.byType(DetailScreen), findsOneWidget);
```

---

### 8. fakeAsync for timers

Never use `Future.delayed` or `sleep` in tests. Use `fakeAsync` and call
`async.elapse(duration)` on the `FakeAsync` instance the callback receives so timers fire
synchronously without real wall-clock time:

```dart
import 'package:fake_async/fake_async.dart';

test('retries after 500 ms backoff', () {
  fakeAsync((async) {
    // arrange: set up provider / service that uses a Timer

    async.elapse(const Duration(milliseconds: 500));

    // assert: timer has fired, state has updated
    expect(container.read(alarmListProvider), isA<AsyncData<List<Alarm>>>());
  });
});
```

`fakeAsync` blocks the `Zone` clock; `async.flushTimers()` drains all pending timers at once.

---

### 9. Stream assertions

An `AsyncNotifierProvider` exposes no `.stream`, so accumulate its `AsyncValue` transitions
through `container.listen` (`fireImmediately` captures the initial state), drive the source
stream, then assert the sequence:

```dart
test('emits loading then data', () async {
  final controller = StreamController<List<Alarm>>();
  when(() => mockRepo.alarmsStream()).thenAnswer((_) => controller.stream);

  final states = <AsyncValue<List<Alarm>>>[];
  container.listen(
    alarmListProvider,
    (_, next) => states.add(next),
    fireImmediately: true,
  );

  controller.add([Alarm.fixture()]);
  await container.read(alarmListProvider.future); // resolves once data arrives

  expect(states.first, isA<AsyncLoading<List<Alarm>>>());
  expect(states.last, isA<AsyncData<List<Alarm>>>());

  await controller.close();
});
```

Assert observable output (`state`, rendered widgets, emitted values) — never inspect
internal notifier fields directly.
