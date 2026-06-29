# Flutter / Dart detection heuristics — Pass 2 shapes (tests-pass-but-miss-behavior)

Grep/read recipes and before→after examples for Pass 2. Targets Flutter + `flutter_test` +
Mocktail + Riverpod (code-gen, `@riverpod` / `Notifier` / `AsyncNotifier`) + `fakeAsync`. Grep
commands narrow where to read — confirm every hit by reading the file.

Examples use a neutral "device list + detail" feature (`DeviceListPage`, `DeviceNotifier`,
`DeviceRepository`); substitute your own surfaces.

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
