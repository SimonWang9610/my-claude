# The three gap classes — detection procedure

Three recurring classes of how Flutter/Dart tests pass while behavior is broken. They overlap — a surface
can exhibit all three simultaneously — so naming the class matters because each maps to a different fix.

---

## Contents

- [Pass 1 — no-spec-coverage](#pass-1--no-spec-coverage)
- [Pass 2 — tests-pass-but-miss-behavior](#pass-2--tests-pass-but-miss-behavior)
- [Pass 3 — false-positive](#pass-3--false-positive)
- [Reporting](#reporting)
- [Confidence calibration](#confidence-calibration)

---

## Pass 1 — `no-spec-coverage`

**Definition.** The code exhibits a behavior with no governing criterion, OR a criterion exists with zero
mapped tests. The behavior is trivially reversible by a later edit with no failing test.

### Procedure

1. Build the behavior inventory for each owned surface (see `heuristics-behavior-enumeration.md`):
   - **widget** — each constructor parameter that changes rendered output; each `GestureDetector`/
     `InkWell`/`onTap`/`onPressed` handler; each conditional render branch (loading / empty / error /
     success / permission-gated); each `AnimatedWidget`/`AnimationController` transition.
   - **Notifier / AsyncNotifier** (Riverpod code-gen) — each `AsyncValue` variant (`AsyncLoading`,
     `AsyncData`, `AsyncError`); each public method that mutates state; each side-effect path
     (repository call, navigation, stream subscription). `StateNotifier`, `StateProvider`, and
     `ChangeNotifierProvider` are legacy — flag their usage separately.
   - **service/repository** — each exported method's observable contract, including error/fallback branches
     and stream emissions.
2. Map each behavior to a governing criterion. Find a criterion ID (`AC-<story>.<n>` / `NFR-<n>`) whose
   Given/When/Then covers it. A behavior with no criterion owner is **improvised** → finding.
3. Map each criterion to a test. Grep test files for the criterion ID (`group('AC-1.2 …')`,
   `test('… AC-1.2 …')`). Zero hits → **uncovered clause** → finding.
4. If a spec has no test files touched at all, the whole spec is outstanding test debt → finding at spec level.

### Finding format

```
NO-SPEC-COVERAGE (improvised): <surface> exhibits "<behavior>" with no governing criterion.
  Confidence: <high|medium|low>
  Resolution: add a criterion to requirements.md and an outcome-asserting test,
  OR remove the behavior as out-of-scope.

NO-SPEC-COVERAGE (uncovered clause): <criterion-id> has 0 mapped tests in <test-dir>.
  Resolution: add a test naming <criterion-id> that asserts its observable outcome.
```

---

## Pass 2 — `tests-pass-but-miss-behavior`

**Definition.** A green test whose name describes a behavior but whose body asserts a weaker proxy. The
named behavior is unverified. This is typically the dominant class in a suite.

### Procedure

For each criterion-mapped test:

1. Read the test name as a behavioral claim (e.g. "shows error message when load fails").
2. Find the assertion that would prove that claim, and check that the test performs the triggering action
   before asserting. See `heuristics-pass2-shapes.md` for recurring Flutter/Dart shapes.
3. Classify the gap:
   - *no action performed* — widget pumped and finder asserted for presence; the criterion's behavior
     (tap, scroll, swipe, async trigger) never fires.
   - *wrong assertion depth* — asserts internal `State` fields or provider internals instead of rendered
     output (`find.text`, `find.byType`, `find.byKey`).
   - *mock declared, never called* — a `MockFoo` is set up with `when(...)` but the action that would
     invoke it never triggers.

### Finding format

```
MISS-BEHAVIOR: <test-file>:<line> "<test-name>" names "<behavior>" but asserts "<proxy>";
the named action is never <fired|exercised>.
  Confidence: <high|medium|low>
  Resolution: fire the action (tap, pump, stream event), then assert the observable output —
  rendered text, widget type, accessible label, returned value, or emitted stream event.
```

---

## Pass 3 — `false-positive`

**Definition.** A test that passes regardless of whether the code works — it exercises nothing that could
break it. Eight recurring Flutter/Dart forms.

### Procedure

For each criterion-mapped test, scan for on-sight signals (`false-positive-signals.md`), then apply the
mutation mindset: invert/delete the production branch the test claims to cover; if the test still passes,
it is a false positive. Grep/read recipes for each form are in `heuristics-pass3-forms.md`.

- **Form 1 — Tautology / no-assert.** `expect()` asserts a value the test supplied, or no `expect` at all.
- **Form 2 — Over-mocking that bypasses the SUT.** Every collaborator mocked so only mock configuration
  is validated; SUT logic never runs.
- **Form 3 — `verify`-only tests.** `verify(() => x.foo()).called(1)` as the sole assertion; tests
  that a method was called, not that the system behaved.
- **Form 4 — Widget tests asserting internal state.** Accessing `State` fields directly instead of
  rendered output; brittle finders by index.
- **Form 5 — `pumpAndSettle()` with live network / infinite timer.** Hangs to a 30 s timeout or masks
  an unfinished frame; `pump(Duration)` should be used instead.
- **Form 6 — Real async (Future.delayed / real network / sleep) in tests.** Tests become flaky; should
  use `fakeAsync`/`elapse`, `MockClient`, or fake streams.
- **Form 7 — Stream/async assertion ordering.** `expectLater` matcher placed after the trigger (misses
  emissions), or missing a short timeout, or using `expect` instead of `expectLater` for a future.
- **Form 8 — Shared container / global state between tests.** `ProviderContainer` not disposed between
  tests or global singletons causing order-dependence.

### Finding format

```
FALSE-POSITIVE (form <1-8>): <test-file>:<line> "<test-name>" passes even when <mutation/drift>.
<criterion-id> has no real verification.
  Confidence: <high|medium|low>   Severity: Critical when mapped to a criterion.
  Resolution: form 1 → add a failing-capable assertion; form 2/3 → assert rendered outcome;
  form 4 → use find.text/find.byType; form 5/6 → use fakeAsync/elapse; form 7 → fix ordering;
  form 8 → addTearDown(container.dispose).
```

---

## Reporting

Emit one table per surface:

```
| Class | Surface / Test | Behavior / Criterion | Confidence | Severity | Resolution |
|-------|----------------|----------------------|------------|----------|------------|
```

Block on any **high** or **medium** finding; surface **low** as advisory. A false positive mapped to a
criterion is always **Critical**.

---

## Confidence calibration

| Confidence | When to assign |
|---|---|
| **high** | Mechanically verifiable: no `expect`/`expectLater`, confirmed mutation leaves test green, fixture fails type check, criterion has zero grep hits in test files, `verify`-only with no rendered assertion. |
| **medium** | Strong structural signal but runtime outcome depends on data/config not yet executed: fixture looks shallow vs domain type but branch not confirmed; `pumpAndSettle` suspected to mask timing but network not confirmed live. |
| **low** | A hunch worth recording but not blocking: test name reads like a proxy but body not fully traced; possible stream-ordering gap. |
