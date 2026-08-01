# False-positive signal catalogue + mutation-test protocol

On-sight signals let you flag a likely false positive before running a mutation. A signal is a
*suspicion*; the mutation confirms the test cannot fail. Pair every blocking finding with at least one
confirmed mutation or a mechanically-verifiable fact.

---

## On-sight signals

### Assertion-level

- **No `expect` or `expectLater` in the block.** Arrange-act-no-assert. Always a confirmed false positive. *(high)*
- **`expect()` of a value the test supplied.** `find.text(label)` where `label` is the literal just passed
  to the widget constructor; `expect(result, equals(input))` against the exact value just built. A tautology. *(high)*
- **`verify`-only block.** `verify(() => mock.foo()).called(1)` with no rendered-output assertion. Tests that
  a method was invoked, not that the system produced the correct behavior. *(high)*
- **`expect(finder, findsWidgets)` with no count bound.** Passes even if zero matching widgets render,
  because `findsWidgets` accepts ≥0; use `findsOneWidget` or `findsNWidgets(n)`. *(high)*
- **`expect(finder, isNotNull)`.** A `Finder` object is always non-null; the assertion is a no-op. *(high)*

### Mock / fixture

- **Every collaborator mocked (`when(repo.load()).thenReturn(...)`) with no real SUT code path.**
  The test validates mock configuration, not application behavior. Prefer in-memory fakes implementing
  the real interface. *(high)*
- **Loose `Map<String, dynamic>` fixture instead of domain type.** Free to drift; a branch on an omitted
  field never runs. *(medium; high once you confirm the source branches on the omitted field)*
- **`when(mock.foo()).thenReturn(x)` where the test then asserts `expect(result, equals(x))`.** The test
  proves the stub returns what it was configured to return — a tautology. *(high)*
- **Entire widget/provider under test mocked.** `when(mockFeatureWidget.build()).thenReturn(...)` — the
  test covers only wiring and bypasses the criterion's behavior. *(high)*

### Async / timing

- **`pumpAndSettle()` in a test with a real `Future.delayed`, live HTTP, or an animation with no end.**
  Will time out at 30 s or silently succeed while frames are still dirty. *(high)*
- **Real `Future.delayed` / `sleep` / `http.get` in test body.** Flaky; clock-dependent. Should use
  `fakeAsync` + `elapse`, a `MockClient`, or a fake stream. *(high)*
- **`expectLater` matcher registered AFTER the trigger that emits.** The emission fires before the
  subscription is set up; the test passes vacuously. *(high)*
- **No `timeout` on a `stream.first` / `expectLater` assertion.** A hung stream makes the test hang
  rather than fail with a clear message. *(medium)*

### State / lifecycle

- **Shared `ProviderContainer` or global `Map`/`List` singleton across `test(...)` blocks without
  `addTearDown`.** State from test N seeds test N+1; order-dependent pass/fail. *(medium; high once
  you confirm a test passes only because a prior test seeded state)*
- **Async-state transitions incomplete.** An `AsyncNotifier` whose `build()` returns a `Future`
  (Riverpod automatically sets `AsyncLoading` while pending, then `AsyncData` on success or
  `AsyncError` on failure) where only the happy path (`AsyncData`) is asserted; `AsyncError` and
  `AsyncLoading` states have no criterion-mapped test. *(medium)*
- **In-test comment admitting a limitation** ("TODO: use real repo", "fake stream only"). Written
  admission the test does not test what it claims. *(high)*

---

## The mutation-test protocol (confirmation)

**Mental form (every criterion-mapped test):**

1. Open the production code the test claims to cover; find the deciding branch, `await`, state transition,
   or stream emission.
2. Mentally invert or delete it: `if (state is AsyncError)` → `if (state is AsyncData)`; remove the
   `emit(ErrorState(...))` call; drop a `throw` in the repository; silence a stream event.
3. Would this test now fail? **No → false positive.**

**Executed form (high-risk criteria — auth, data write, error recovery):**

```bash
# 1. apply the mutation in the production file (invert/comment the deciding branch)
# 2. run only the mapped test file
flutter test test/path/to/feature_test.dart --reporter=expanded
# 3. if it still passes → confirmed false positive (Critical when criterion-mapped)
# 4. REVERT the mutation immediately
```

Keep executed mutations scoped to one file and one mutation; revert before moving on. Record the exact
mutation in the finding so the fix is unambiguous and the reviewer can reproduce it.

Cap executed mutations at the high-risk criteria set for the spec under review. For the rest, the mental
form plus an on-sight signal is sufficient.

---

## From signal to fix

| Signal / form | Fix direction |
|---|---|
| No `expect`/`expectLater` / tautology | Add a failing-capable assertion; assert derived outcome, not supplied input |
| `verify`-only | Add a rendered-output assertion (`find.text`, `find.byType`) after the action |
| Over-mocking / SUT bypassed | Replace mocks with in-memory fakes implementing the real interface |
| Widget tests asserting internal state | Use `find.text` / `find.byType` / `find.byKey` on rendered output |
| `pumpAndSettle` with live timer/network | Switch to `fakeAsync` + `pump(Duration)` |
| Real `Future.delayed` / real HTTP | Use `fakeAsync`/`elapse`, `MockClient`, or fake stream |
| `expectLater` after trigger / no timeout | Register matcher BEFORE trigger; add `.timeout(Duration)` |
| Shared container / global state | Add `addTearDown(container.dispose)` or reset in `setUp`/`tearDown` |
| Loose `Map` fixture | Build from domain type (`MyModel(...)`) so field drift is a compile error |
