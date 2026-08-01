# fl-test-contract — rule reference

Six core rules + four additional assertions that must pass before a test task is marked complete.

## Contents

- [§1 — Observable outcomes, not implementation](#1--observable-outcomes-not-implementation)
- [§2 — Clause→test mapping](#2--clausetest-mapping)
- [§3 — Production-shaped fixtures](#3--production-shaped-fixtures)
- [§4 — No tautologies; prefer fakes over mocks](#4--no-tautologies-prefer-fakes-over-mocks)
- [§5 — Real async/stream machinery for async ACs](#5--real-asyncstream-machinery-for-async-acs)
- [§6 — One-shot greps become enduring CI guards](#6--one-shot-greps-become-enduring-ci-guards)
- [§7 — Dual-assert for service tests](#7--dual-assert-for-service-tests)
- [§8 — Three-assert for state-holder/cache command tests](#8--three-assert-for-state-holdercache-command-tests)
- [§9 — Negative equality per field for model tests](#9--negative-equality-per-field-for-model-tests)
- [§10 — Error path is a first-class test](#10--error-path-is-a-first-class-test)

---

## §1 — Observable outcomes, not implementation

Assert `find.text`, `find.byType`, enabled/disabled state, or visible/absent presence. `verify(...)` is only acceptable for a fire-and-forget side effect (navigation, analytics) that has no other observable — and even then it must accompany a visible assertion.

Wrong → right: `verify(() => mockRepo.sort(...)).called(1)` alone → assert rendered list order with `find.text(...)`.

**Check.** Scan for bare `verify(...)` calls with no accompanying `find.*` / `expect(find.*, ...)`. Mutation mindset: "If I invert the sorted flag in production, does this test fail?"

---

## §2 — Clause→test mapping

Every `group(...)` description names the AC or NFR ID it covers. A green suite with unmapped tests is not a PASS for the ACs those tests could cover.

Wrong → right: `test('calls sort', ...)` → `group('AC-14.3: header tap sorts by column', () { ... })`.

**Check.** Grep the file for each AC ID the task covers; every ID must appear in at least one `group(...)` label and that test must be independently runnable and green.

---

## §3 — Production-shaped fixtures

Every fixture is constructed from the real domain model — not a loose `Map<String,dynamic>` or ad-hoc literal. A shape mismatch must be a compile error. Use `const` constructors and `final` fields for models; use `.copyWith(...)` (from `freezed` or hand-rolled) for variants. For state unions, use Dart 3 `sealed` classes with exhaustive switch expressions — not `if (x is T)` chains.

Wrong → right: `final d = {'id': '1', 'name': 'Front Door'}` → `final d = Device(id: '1', name: 'Front Door', status: DeviceStatus.online)`.

**Check.** No bare `Map<String,dynamic>` fixture literals. Adding a required field to the prod type must break the fixture at compile time.

---

## §4 — No tautologies; prefer fakes over mocks

Don't assert a mock returns what you stubbed it to return. Use an in-memory fake implementing the real interface so interacting methods are genuinely exercised. `mocktail` (no codegen) is the default; `verify` is used sparingly for side effects only.

Mocktail requires `registerFallbackValue(FakeX())` in `setUpAll` for any `any()` matcher on custom types. For Riverpod, inject fakes via `ProviderContainer(overrides: [repoProvider.overrideWithValue(fakeRepo)])` — never mutate a global provider in tests.

Wrong → right: `when(() => mock.getDevices()).thenAnswer(...); expect(await mock.getDevices(), ...)` → implement `FakeDeviceRepository` with real filter logic and assert the output.

**Check.** Grep for `test(`/`testWidgets(` blocks with no `expect`. For every `Mock` class, confirm at least one assertion is not a restatement of the stub. Confirm `registerFallbackValue` is called for every custom type passed to `any()`.

---

## §5 — Real async/stream machinery for async ACs

ACs that depend on async behavior use a real `StreamController` or `ProviderContainer` with `expectLater(..., emitsInOrder([...]))`. Drive time with `fakeAsync`/`elapse` — never real `Future.delayed`. Never call `pumpAndSettle()` while a live network call or infinite timer is pending (hangs to 30 s timeout); advance with `pump(Duration)` instead.

For Riverpod: create a `ProviderContainer` (or use `ProviderScope` in widget tests) and read the notifier directly. Use `container.listen(provider, ...)` to capture state emissions. (`AsyncNotifierProvider` exposes no `.stream`, so `expectLater(container.read(provider.stream), ...)` is a compile error — always use the `listen` pattern.)

Wrong → right:
```dart
// ✗ real delay, polls state directly
await Future.delayed(Duration(milliseconds: 100));
expect(container.read(deviceListProvider), isA<AsyncData<List<Device>>>());

// ✓ fakeAsync + listen captures every emission in order.
// Prime the container first so build()'s own loading→data cycle is
// settled before we attach the listener; otherwise states will contain
// the build() emissions (AsyncLoading, AsyncData) plus the load() ones.
fakeAsync((async) {
  final container = ProviderContainer(overrides: [...]);
  // Prime: let build() run to completion before attaching the listener.
  async.flushMicrotasks();
  final states = <AsyncValue<List<Device>>>[];
  container.listen(deviceListProvider, (_, next) => states.add(next));
  container.read(deviceListProvider.notifier).load();
  async.elapse(Duration(seconds: 1));
  // states now contains only the emissions from load(), not from build().
  expect(states, [isA<AsyncLoading<List<Device>>>(), isA<AsyncData<List<Device>>>()]);
});
```

**Check.** For every AC naming async behavior or timing: no `Future.delayed`; no `pumpAndSettle()` with a timer or polling loop; stream ordering asserted with `emitsInOrder` or captured via `container.listen`.

---

## §6 — One-shot greps become enduring CI guards

Any ban verified once at review time (no hard-coded hex, no `Widget _buildX()` helper, no service import in a widget, no business logic in `build`) must become an enduring `flutter analyze` lint, `custom_lint`/DCM rule, or checked-in test. A one-shot PR-review grep is not sufficient.

Wrong → right: reviewer runs `grep -r '#[0-9a-fA-F]' lib/` and moves on → add a checked-in `test/nfr/no_hardcoded_hex_test.dart` or a DCM rule in `analysis_options.yaml`.

**Check.** For every "no occurrences of X" NFR, a corresponding checked-in test file or `analysis_options.yaml` entry must exist.

---

## §7 — Dual-assert for service tests

Assert the return value AND the specific client endpoint + args. An over-general stub (`any()`) hides routing bugs.

Wrong → right: `expect(result, isNotNull)` alone → also `verify(() => client.get('/devices', params: {'status': 'online'})).called(1)`.

---

## §8 — Three-assert for state-holder/cache command tests

Assert resulting state + notify/emit count + the collaborator interaction. One missing leg hides a real failure mode.

For Riverpod `Notifier`/`AsyncNotifier`: capture emissions via `container.listen`, then assert the final state, the emission sequence length, and the repository call.

Wrong → right:
```dart
// ✗ only checks final state — misses double-emit and collaborator routing
await container.read(deviceListProvider.notifier).refresh();
expect(container.read(deviceListProvider).value, isNotEmpty);

// ✓ all three legs.
// Prime the container before attaching the listener so build()'s own
// loading→data emissions are not counted; only refresh()'s 2 emissions
// (AsyncLoading, AsyncData) are captured.
fakeAsync((async) {
  // Prime: let build() settle before listening.
  async.flushMicrotasks();
  final states = <AsyncValue<List<Device>>>[];
  container.listen(deviceListProvider, (_, s) => states.add(s));
  container.read(deviceListProvider.notifier).refresh();
  async.flushMicrotasks();
  expect(states.length, 2);                              // loading → data
  expect(states.last, isA<AsyncData<List<Device>>>());   // final state
  verify(() => mockRepo.fetchDevices()).called(1);        // collaborator
});
```

---

## §9 — Negative equality per field for model tests

Test that changing each field individually breaks equality. A missing field in `props`/`==` is invisible to the positive test alone.

Wrong → right: `expect(device, device.copyWith())` alone → also `expect(device, isNot(equals(device.copyWith(id: 'other'))))` for each field.

---

## §10 — Error path is a first-class test

If a test catches an error the production code silently swallows, fix the production code, not the test.

Wrong → right: wrapping `expect(...)` in a try-catch to avoid a thrown exception → surface the throw in the production path and assert the error state explicitly.
