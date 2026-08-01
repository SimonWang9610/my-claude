# Flutter / Dart detection heuristics — Pass 3 forms (false-positive)

Grep/read recipes and before→after examples for Pass 3. Targets Flutter + `flutter_test` +
Mocktail + Riverpod (code-gen, `@riverpod` / `Notifier` / `AsyncNotifier`) + `fakeAsync`. Grep
commands narrow where to read — confirm every hit by reading the file.

Examples use a neutral "device list + detail" feature (`DeviceListPage`, `DeviceNotifier`,
`DeviceRepository`); substitute your own surfaces.

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
