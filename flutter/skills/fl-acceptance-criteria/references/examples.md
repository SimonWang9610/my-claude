# AC anti-patterns — before/after with Flutter test-name skeletons

<!-- TOC -->
- [1. The cache-invalidation no-op (spy-on-the-call AC)](#1-the-cache-invalidation-no-op-spy-on-the-call-ac)
- [2. The mock-call assertion (callback fired, nothing happened)](#2-the-mock-call-assertion-callback-fired-nothing-happened)
- [3. The render-it-back tautology](#3-the-render-it-back-tautology)
- [4. The one-shot ban that decays](#4-the-one-shot-ban-that-decays)
- [5. The stream-state tautology (Flutter-specific)](#5-the-stream-state-tautology-flutter-specific)
<!-- /TOC -->

Five recurring anti-patterns, each shown as the ill-formed criterion, the corrected
observable form, and the test-name skeleton it produces.

---

## 1. The cache-invalidation no-op (spy-on-the-call AC)

A feature triggers a repository refresh; the AC is written as "shall call
`repository.refresh()`". A spy fires even when the returned list is stale, so the test
stays green while nothing actually updates on screen.

**Reject:**
```
AC-9: When the user toggles "Include sub-sites", the system shall call repository.refresh().
```

**Require:**
```
AC-9.1: Given the device list has loaded for the parent site, when the user toggles
        "Include sub-sites" on, then the device list refetches and sub-site device
        rows appear in the list.

AC-9.2: Given sub-site rows are shown, when the user toggles "Include sub-sites" off,
        then those rows disappear and only parent-site devices remain.
```

**Test-name skeleton (widget test):**
```dart
group('AC-9.1: toggling "include sub-sites" on shows sub-site devices', () {
  testWidgets('renders sub-site device rows after the toggle', (tester) async {
    // act: tap the toggle
    // assert (observable): find.text('<sub-site device name>') findsOneWidget
  });
});

group('AC-9.2: toggling "include sub-sites" off hides sub-site devices', () {
  testWidgets('removes sub-site rows when toggle is off', (tester) async {
    // assert (observable): find.text('<sub-site device name>') findsNothing
  });
});
```

---

## 2. The mock-call assertion (callback fired, nothing happened)

An interactive control is specced as "the `onTap` callback shall be called with the
device id". The test asserts a mock fired but never checks that navigation occurred.
The durable assertion is on what the user observes — a new route appeared — not an
internal callback being invoked.

**Reject:**
```
AC-14: The onTap callback shall be called with the device id when a list row is tapped.
```

**Require:**
```
AC-14.3: Given the device list is rendered, when the user taps a device row, then the
         device detail screen for that device is shown.
```

**Test-name skeleton (widget test):**
```dart
group('AC-14.3: tapping a device row navigates to the device detail screen', () {
  testWidgets('shows device detail screen after row tap', (tester) async {
    // act: await tester.tap(find.text('<device name>'))
    // assert (observable): find.byType(DeviceDetailScreen) findsOneWidget
    // WARNING: asserting that a mock router received the device id does NOT
    //   substitute for the rendered-screen assertion above. The mock-call check
    //   may pass even when navigation is broken; the primary signal is always
    //   the rendered screen.
  });
});
```

---

## 3. The render-it-back tautology

A display widget is specced as "the notification message shall be displayed". A test
pumps a widget with a `message` parameter then calls `find.text(message)` using the
same variable — a mathematical identity that cannot fail regardless of layout, styling,
or accessibility semantics. The criterion is too loose, inviting a self-confirming assertion.

**Reject:**
```
AC-1: The notification message shall be displayed.
```

**Require:**
```
AC-1.1: Given an unread notification of type "alarm", when the notification card renders,
        then the alarm icon is visible and the card carries the semantics label "unread
        notification", alongside the notification's title text.

AC-1.2: Given a read notification, when the card renders, then the card does NOT carry
        the "unread notification" semantics label and the mark-as-read button is absent.
```

**Test-name skeleton (widget test):**
```dart
group('AC-1.1: unread alarm notification shows alarm icon and unread semantics', () {
  testWidgets('renders alarm icon and exposes unread semantics label', (tester) async {
    // assert (observable): find.byIcon(Icons.alarm) findsOneWidget
    //                      find.bySemanticsLabel('unread notification') findsOneWidget
  });
});

group('AC-1.2: read notification omits unread semantics and mark-as-read button', () {
  testWidgets('does not render the mark-as-read button once read', (tester) async {
    // assert (observable): find.byKey(const Key('mark_as_read_btn')) findsNothing
  });
});
```

---

## 4. The one-shot ban that decays

A pattern ban (no hardcoded Color literals) is "enforced" by a one-shot grep at review.
Once merged, nothing re-runs it. A check that runs only once decays to zero enforcement
— the durable form is a resident CI guard that runs on every change.

**Avoid:**
```
NFR-1: grep -r 'Color(0xff' lib/features returns zero matches.
```

**Require:**
```
NFR-1: Given the app is viewed in system dark-mode, when any screen in this feature
       renders, then every colour resolves through the design-token ThemeData chain —
       no hardcoded Color(0xff…) literal appears in feature source.
       (Enforce as an enduring CI guard, not a one-shot grep.)
```

**Test/guard skeleton:**
```dart
group('NFR-1: no hardcoded Color literals in feature source', () {
  test('feature lib files contain no Color(0xff…) literals', () {
    // resident source-scan guard — see the test-contract skill for implementation
    // e.g. scan lib/features/<name>/ for the pattern and fail if any match found
  });
});
```

---

## 5. The stream-state tautology (Flutter-specific)

An AC for async data loading is written as "shall emit LoadingState then DataState".
A unit test on a fake notifier asserts the fake emits what the fake was programmed to emit
— it tests the test double, not the notifier under test. The observable assertion is on
the sequence of values a real consumer (the widget, or an integration test) observes.

**Reject:**
```
AC-7: The devicesNotifier shall emit LoadingState followed by DataState when fetch succeeds.
```

**Require:**
```
AC-7.1: Given the device list screen is opened, when the repository fetch completes,
        then the loading indicator disappears and the device rows are visible.

AC-7.2: Given the device list screen is opened, when the repository fetch fails, then
        the loading indicator disappears and an error message "Could not load devices"
        is visible with a retry button.
```

**Test-name skeleton — two-layer approach:**

For the notifier/repository unit test (pure state logic, fast). With Riverpod code-gen,
the provider under test is an `AsyncNotifier`; override its repository dependency via
`ProviderContainer.overrideWithValue`:
```dart
group('AC-7.1: devicesNotifier transitions loading→data on successful fetch', () {
  test('exposes data state after repository returns', () async {
    final fakeRepo = FakeDeviceRepository();
    final container = ProviderContainer(
      overrides: [deviceRepositoryProvider.overrideWithValue(fakeRepo)],
    );
    addTearDown(container.dispose);
    // Assert the publicly exposed AsyncValue sequence via container.listen / container.read.
    // This is valid because we assert the publicly observable AsyncValue,
    // not a private field.
  });
});
```

For the widget integration test (observable UI):
```dart
group('AC-7.1: device list shows rows after fetch completes', () {
  testWidgets('renders device rows once loading finishes', (tester) async {
    // assert (observable): find.byType(CircularProgressIndicator) findsNothing
    //                      find.text('<device name>') findsOneWidget
  });
});
```

An AC about async behavior should map to a unit test on the notifier/repository
(loading→data→error `AsyncValue` sequence) AND, if the AC names a UI outcome, a widget
test. Both test names must carry the AC ID so coverage grep finds both layers.

---

See `ac-format.md` for the ID and phrasing rules. See `traceability.md` for how these
IDs flow into `group`/`test`/`testWidgets` names and `--plain-name` filtering.
