# Flutter / Dart detection heuristics

Grep/read recipes and before→after examples for each detection pass. Targets Flutter + `flutter_test` +
Mocktail + Riverpod (code-gen, `@riverpod` / `Notifier` / `AsyncNotifier`) + `fakeAsync`. Grep
commands narrow where to read — confirm every hit by reading the file.

Examples use a neutral "device list + detail" feature (`DeviceListPage`, `DeviceNotifier`,
`DeviceRepository`); substitute your own surfaces.

---

## Contents

- [Behavior enumeration (Pass 1 input)](#behavior-enumeration-pass-1-input)
- [Pass 2 shapes — tests-pass-but-miss-behavior](#pass-2-shapes--tests-pass-but-miss-behavior)
  - [Shape A — widget pumped without triggering the action](#shape-a--widget-pumped-without-triggering-the-action)
  - [Shape B — verify-only; named behavior is a side-effect, not an outcome](#shape-b--verify-only-named-behavior-is-a-side-effect-not-an-outcome)
  - [Shape C — async-state transitions partially covered](#shape-c--async-state-transitions-partially-covered)
  - [Shape D — pumpAndSettle masking a timing requirement](#shape-d--pumpandsettle-masking-a-timing-requirement)
- [Pass 3 forms — false-positive](#pass-3-forms--false-positive)
  - [Form 1 — Tautology / arrange-act-no-assert](#form-1--tautology--arrange-act-no-assert)
  - [Form 2 — Over-mocking that bypasses the SUT](#form-2--over-mocking-that-bypasses-the-sut)
  - [Form 3 — verify-only (no rendered-outcome assertion)](#form-3--verify-only-no-rendered-outcome-assertion)
  - [Form 4 — Widget tests asserting internal state instead of rendered output](#form-4--widget-tests-asserting-internal-state-instead-of-rendered-output)
  - [Form 5 — pumpAndSettle with live network / infinite timer](#form-5--pumpandsettle-with-live-network--infinite-timer)
  - [Form 6 — Real Future.delayed / sleep / real network in tests](#form-6--real-futuredelayed--sleep--real-network-in-tests)
  - [Form 7 — Stream/async assertion ordering](#form-7--streamasync-assertion-ordering)
  - [Form 8 — Shared ProviderContainer / global state between tests](#form-8--shared-providercontainer--global-state-between-tests)
- [AC traceability check (Pass 1 shortcut)](#ac-traceability-check-pass-1-shortcut)
- [Async-state coverage check (Pass 1 / Pass 2 support)](#async-state-coverage-check-pass-1--pass-2-support)

---

## Behavior enumeration (Pass 1 input)

**Widget** — open the file and enumerate:

```bash
# conditional branches: ternaries, if-guards, switch on state
grep -nE 'if \(|switch \(|\? |?? ' <Widget>.dart | grep -vE '^\s*//'
# interaction handlers
grep -nE 'onTap|onPressed|onChanged|onSubmitted|GestureDetector|InkWell' <Widget>.dart
# async state checks — Riverpod code-gen uses switch expressions on AsyncValue
grep -nE 'AsyncLoading|AsyncError|AsyncData|switch \(.*state\b|\.when\(|\.maybeWhen\(' <Widget>.dart
```

Note: Riverpod code-gen (`@riverpod`) builds state as `AsyncValue<T>`; widgets typically switch on it
with an exhaustive `switch` expression (Dart 3). Legacy `.when()`/`.maybeWhen()` calls are also common
in older code — both patterns produce the same branches to enumerate.

**Notifier / AsyncNotifier** — state transitions and public surface:

```bash
# state assignments (Notifier: state = ...; AsyncNotifier: state = AsyncData/AsyncError/AsyncLoading)
grep -nE 'state =|AsyncLoading\(\)|AsyncError\(|AsyncData\(' <notifier>.dart
# public event methods (exclude the mandatory build())
grep -nE 'Future<|Stream<|void ' <notifier>.dart | grep -vE 'build\(\)'
```

`emit(` is a Cubit/BLoC pattern, not Riverpod. For Riverpod code-gen notifiers, state mutation is
`state = <newValue>` (Notifier) or `state = AsyncData(value)` (AsyncNotifier).

**Service / Repository** — exported contracts and error paths:

```bash
grep -nE '^  Future<|^  Stream<|^  \w+ \w+\(' <repo>.dart | grep -vE '^\s*//'
grep -nE 'throw |catch \(|on \w+Exception' <repo>.dart
```

A behavior that appears here with no criterion ID (`AC-<story>.<n>` / `NFR-<n>`) in `requirements.md` is
a `no-spec-coverage` (improvised) finding.

---

## Pass 2 shapes — `tests-pass-but-miss-behavior`

### Shape A — widget pumped without triggering the action

```bash
# locate test/group blocks
grep -nE "test\('|testWidgets\('|group\('" <file>_test.dart
# check action present (tap, drag, enterText)
grep -nE 'tester\.tap|tester\.drag|tester\.enterText|tester\.pump' <file>_test.dart
# flag blocks that have pumpWidget + find but no interaction call
```

```dart
// MISS — names an error behavior, never triggers a failed load, checks a structural proxy
testWidgets('shows error message when load fails', (tester) async {
  await tester.pumpWidget(DeviceListPage());
  expect(find.byType(DeviceListPage), findsOneWidget);
});

// FIXED — trigger the error, assert the rendered outcome
testWidgets('AC-3.2: shows error banner when load fails', (tester) async {
  when(() => mockRepo.fetchDevices()).thenThrow(Exception('network'));
  await tester.pumpWidget(ProviderScope(
    overrides: [
      // code-gen: overrideWith replaces the factory; overrideWithValue is for simple providers
      deviceRepoProvider.overrideWith((ref) => mockRepo),
    ],
    child: const DeviceListPage(),
  ));
  await tester.pump(); // let the notifier emit
  expect(find.text('Failed to load devices'), findsOneWidget);
  expect(find.byType(RetryButton), findsOneWidget);
});
```

### Shape B — `verify`-only; named behavior is a side-effect, not an outcome

The test asserts that a method was called but not what the user sees or what state changed.

```bash
grep -nE 'verify\(\(\) =>' <file>_test.dart
# flag blocks where verify is the ONLY assertion
```

```dart
// MISS — asserts the repo method was called; the criterion's behavior (navigation) is never checked
verify(() => mockRepo.saveDevice(device)).called(1);

// FIXED — assert the observable outcome (navigation + rendered content)
verify(() => mockRepo.saveDevice(device)).called(1);
expect(find.byType(DeviceDetailPage), findsOneWidget); // also assert the navigation happened
```

### Shape C — async-state transitions partially covered

```bash
grep -nE 'AsyncLoading|AsyncError|AsyncData' <notifier>.dart
grep -nE 'AsyncLoading|AsyncError|isLoading|hasError' <file>_test.dart
# if loading and error states have no test hits → lifecycle gap
```

```dart
// MISS — only happy path tested; loading → error path has no criterion-mapped test
test('AC-2.1: returns device list on success', () async {
  when(() => mockRepo.fetchDevices()).thenAnswer((_) async => [device]);
  // code-gen: test via ProviderContainer, not by constructing the notifier directly
  final container = ProviderContainer(
    overrides: [deviceRepoProvider.overrideWith((ref) => mockRepo)],
  );
  addTearDown(container.dispose);
  expect(await container.read(deviceNotifierProvider.future), [device]);
});
// AC-2.2 (shows loading indicator) → 0 tests
// AC-2.3 (shows error + retry on failure) → 0 tests
```

### Shape D — `pumpAndSettle()` masking a timing requirement

`pumpAndSettle()` drives frames until stable; it hides whether a delay/animation criterion is met.

```dart
// MASKING — pumpAndSettle hides whether the 300 ms debounce NFR is enforced
await tester.pumpAndSettle();
expect(find.byType(SearchResultList), findsOneWidget);

// FIXED — use fakeAsync + pump(Duration) to assert timing explicitly
testWidgets('NFR-4: 300 ms debounce is enforced', (tester) async {
  fakeAsync((fake) {
    tester.pumpWidget(const SearchPage());
    tester.enterText(find.byType(TextField), 'foo');
    fake.elapse(const Duration(milliseconds: 200));
    expect(find.byType(SearchResultList), findsNothing); // NFR: debounce not yet fired
    fake.elapse(const Duration(milliseconds: 100));
    tester.pump();
    expect(find.byType(SearchResultList), findsOneWidget); // NFR-4: 300 ms debounce
  });
});
```

---

## Pass 3 forms — `false-positive`

### Form 1 — Tautology / arrange-act-no-assert

```bash
# blocks with no expect or expectLater
grep -nE "test\('|testWidgets\('" <file>_test.dart   # collect test block starts
grep -nE 'expect\(|expectLater\(' <file>_test.dart   # check assertions present
# also catch: asserts the literal just passed in
grep -nE "find\.text\(['\"]?\w+['\"]?\)" <file>_test.dart
```

```dart
// TAUTOLOGY — asserts the label prop passed in; cannot fail
testWidgets('shows device name', (tester) async {
  await tester.pumpWidget(DeviceTile(name: 'Front Door'));
  expect(find.text('Front Door'), findsOneWidget); // we supplied 'Front Door'; this always passes
});

// FIXED — assert a derived outcome the widget is responsible for computing
testWidgets('AC-5.1: offline device shows grey icon', (tester) async {
  await tester.pumpWidget(DeviceTile(device: device.copyWith(online: false)));
  expect(
    tester.widget<Icon>(find.byType(Icon)).color,
    equals(Colors.grey),
  );
});
```

### Form 2 — Over-mocking that bypasses the SUT

```bash
grep -nE 'when\(\(\) =>' <file>_test.dart | wc -l   # count stubs
grep -nE 'class Mock\w+ extends Mock' <file>_test.dart | wc -l  # count mock classes
# if every collaborator is mocked AND no real widget tree is pumped → SUT is not exercised
```

```dart
// OVER-MOCKED — only mock wiring validated; DeviceNotifier logic never runs
when(() => mockNotifier.state).thenReturn(AsyncData([device]));
testWidgets('shows device list', (tester) async {
  await tester.pumpWidget(ProviderScope(
    overrides: [deviceNotifierProvider.overrideWith((_) => mockNotifier)],
    child: const DeviceListPage(),
  ));
  expect(find.byType(DeviceTile), findsWidgets);
});

// BETTER — override the repository with an in-memory fake; let the real notifier run
final fakeRepo = FakeDeviceRepository(devices: [device]);
await tester.pumpWidget(ProviderScope(
  overrides: [
    // code-gen: overrideWith((ref) => ...) for providers with dependencies
    deviceRepoProvider.overrideWith((ref) => fakeRepo),
  ],
  child: const DeviceListPage(),
));
await tester.pump();
expect(find.byType(DeviceTile), findsOneWidget);
```

### Form 3 — `verify`-only (no rendered-outcome assertion)

```bash
grep -nE 'verify\(\(\) =>' <file>_test.dart
# flag blocks where the ONLY assertion is a verify call
awk '/test\(|testWidgets\(/{n=$0;v="";e=""} /verify\(/{v="y"} /expect\(/{e="y"} /\}\);/{if(n && v && !e) print FILENAME": "n; n=""}' <file>_test.dart
```

```dart
// VERIFY-ONLY — tests method call, not behavior
test('AC-6.1: saves device on confirm', () async {
  await notifier.confirmSave(device);
  verify(() => mockRepo.saveDevice(device)).called(1);
  // nothing asserts the state the user sees after save
});

// FIXED — drive notifier through a ProviderContainer; assert via container.read(provider)
test('AC-6.1: saves device and navigates to list on confirm', () async {
  final container = ProviderContainer(overrides: [deviceRepoProvider.overrideWith((ref) => fakeRepo)]);
  addTearDown(container.dispose);
  await container.read(deviceNotifierProvider.notifier).confirmSave(device);
  verify(() => fakeRepo.saveDevice(device)).called(1);
  expect(container.read(deviceNotifierProvider), isA<AsyncData<void>>());
  // + widget test: expect(find.byType(DeviceListPage), findsOneWidget)
});
```

### Form 4 — Widget tests asserting internal state instead of rendered output

```bash
# accessing State fields directly or by position index
grep -nE '\.state\.' <file>_test.dart | grep -vE 'AsyncData|AsyncError|AsyncLoading'
grep -nE 'find\.byIndex\|tester\.firstWidget' <file>_test.dart
```

```dart
// BRITTLE — accesses internal field; breaks on refactor
final state = tester.state<DeviceListState>(find.byType(DeviceListPage));
expect(state.isLoading, isFalse);

// FIXED — assert what the user sees
expect(find.byType(CircularProgressIndicator), findsNothing);
expect(find.byType(DeviceTile), findsNWidgets(3));
```

### Form 5 — `pumpAndSettle()` with live network / infinite timer

```bash
grep -nE 'pumpAndSettle\(\)' <file>_test.dart
# cross-reference with real http/Dio/network calls in the widget tree (no mock)
grep -nE 'http\.|Dio\(\)|Uri\.https\|Uri\.http' <source>.dart
# or with AnimationController that has no .stop() / forward() call in test
grep -nE 'AnimationController\|AnimatedBuilder' <source>.dart
```

```dart
// HANGS — real HTTP under pumpAndSettle; 30 s timeout
await tester.pumpAndSettle();

// FIXED — inject a MockClient; pump(Duration) to drive frames
final client = MockClient((req) async => http.Response(json.encode([deviceJson]), 200));
await tester.pumpWidget(DeviceListPage(client: client));
await tester.pump(); // initial load
await tester.pump(const Duration(milliseconds: 100)); // settle transition
expect(find.byType(DeviceTile), findsOneWidget);
```

### Form 6 — Real `Future.delayed` / `sleep` / real network in tests

```bash
grep -nE 'Future\.delayed|sleep\(|await Future\.value\(Duration' <file>_test.dart
grep -nE 'http\.get\|http\.post\|Dio\(\)' <file>_test.dart
grep -nE 'Stream\.periodic' <source>.dart   # live-clock stream that never terminates
```

```dart
// FLAKY — real sleep; timing-sensitive
await Future.delayed(const Duration(seconds: 1));
expect(find.byType(Snackbar), findsOneWidget);

// FIXED — fakeAsync + elapse inside testWidgets; callback must NOT be async
testWidgets('shows SnackBar after save', (tester) async {
  final container = ProviderContainer(overrides: [deviceRepoProvider.overrideWith((ref) => fakeRepo)]);
  addTearDown(container.dispose);
  fakeAsync((fake) {
    tester.pumpWidget(const SavePage());
    container.read(deviceNotifierProvider.notifier).save(device);
    fake.elapse(const Duration(milliseconds: 500));
    tester.pump();
    expect(find.byType(SnackBar), findsOneWidget);
  });
});
```

### Form 7 — Stream/async assertion ordering

```bash
# expectLater AFTER the trigger that emits
grep -n 'expectLater\|\.listen\|controller\.add\|sink\.add\|state =' <file>_test.dart
# visually check: does the trigger line come BEFORE expectLater?
grep -nE 'controller\.add|sink\.add' <file>_test.dart
```

```dart
// MISS-ORDER — emission fires before expectLater subscribes; passes vacuously
controller.add(device);
await expectLater(stream, emitsInOrder([device]));

// FIXED — register the matcher BEFORE triggering
final expectation = expectLater(stream, emitsInOrder([device]));
controller.add(device);
await expectation;
```

```dart
// MISSING TIMEOUT — hangs if stream never emits
await expectLater(stream, emitsInOrder([device]));

// FIXED — add a short timeout so the test fails clearly
await expectLater(stream, emitsInOrder([device]))
    .timeout(const Duration(seconds: 2));
```

### Form 8 — Shared `ProviderContainer` / global state between tests

```bash
grep -nE 'ProviderContainer\(\)' <file>_test.dart
# check whether it is created in setUp and disposed in addTearDown / tearDown
grep -nE 'addTearDown|tearDown|container\.dispose' <file>_test.dart
# if container is declared at top-level or in group scope without dispose → leak
```

```dart
// LEAK — shared container; test N+1 inherits state from test N
final container = ProviderContainer();

test('AC-7.1: initial state is loading', () {
  expect(container.read(deviceProvider), isA<AsyncLoading>());
});

test('AC-7.2: state is data after load', () async {
  await container.read(deviceProvider.future);
  expect(container.read(deviceProvider), isA<AsyncData>());
});

// FIXED — fresh container per test, disposed in addTearDown
late ProviderContainer container;

setUp(() {
  container = ProviderContainer(overrides: [
    // code-gen: overrideWith((ref) => ...) for providers generated with @riverpod
    deviceRepoProvider.overrideWith((ref) => FakeDeviceRepository()),
  ]);
  addTearDown(container.dispose);
});
```

---

## AC traceability check (Pass 1 shortcut)

```bash
# find all AC IDs mentioned in requirements
grep -nE 'AC-[0-9]+\.[0-9]+' requirements.md | grep -oE 'AC-[0-9]+\.[0-9]+' | sort -u

# find all AC IDs referenced in tests
grep -rE 'AC-[0-9]+\.[0-9]+' test/ | grep -oE 'AC-[0-9]+\.[0-9]+' | sort -u

# diff to find uncovered clauses
comm -23 <(grep -oE 'AC-[0-9]+\.[0-9]+' requirements.md | sort -u) \
         <(grep -rE 'AC-[0-9]+\.[0-9]+' test/ | grep -oE 'AC-[0-9]+\.[0-9]+' | sort -u)
```

Any ID appearing only in the first list is an **uncovered clause** (Pass 1 finding, high confidence).

---

## Async-state coverage check (Pass 1 / Pass 2 support)

For every Riverpod `AsyncNotifier` (code-gen: `@riverpod` + `build()` returns `Future<T>` or
`Stream<T>`), enumerate `AsyncValue` variants and check coverage:

```bash
# find all AsyncValue states set in the notifier
grep -nE 'AsyncLoading\(\)|AsyncError\(|AsyncData\(' <notifier>.dart

# find which states are asserted in tests
grep -nE 'AsyncLoading|AsyncError|AsyncData|isLoading|hasError' test/<notifier>_test.dart
```

A state variant that appears in production but not in any criterion-mapped test is a
`no-spec-coverage (uncovered clause)` or `tests-pass-but-miss-behavior` finding.
