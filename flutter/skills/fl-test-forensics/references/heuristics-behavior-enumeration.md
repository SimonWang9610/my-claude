# Flutter / Dart detection heuristics — behavior enumeration (Pass 1 input)

Grep/read recipes and before→after examples for Pass 1. Targets Flutter + `flutter_test` +
Mocktail + Riverpod (code-gen, `@riverpod` / `Notifier` / `AsyncNotifier`) + `fakeAsync`. Grep
commands narrow where to read — confirm every hit by reading the file.

Examples use a neutral "device list + detail" feature (`DeviceListPage`, `DeviceNotifier`,
`DeviceRepository`); substitute your own surfaces.

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
