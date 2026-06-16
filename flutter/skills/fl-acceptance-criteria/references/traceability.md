# AC → test traceability — making coverage a runnable query

Stable AC IDs flow from `requirements.md` into Flutter test names so "is AC-X.Y covered?"
is a grep or a `flutter test --plain-name` filter, not a manual audit. No BDD framework
needed — the discipline is in the naming.

## 1. Naming convention

Embed the AC ID at the start of the `group(...)` string; mirror the criterion's
Given/When/Then so the description reads as the behaviour. The `test(...)` or
`testWidgets(...)` name states the specific observable outcome being asserted.

```dart
// requirements.md:
//   AC-14.3: Given the table is rendered, when the user taps a column header,
//            then rows sort by that column and the header shows the sort direction.

// device_table_test.dart:
group('AC-14.3: tapping a column header sorts rows by that column', () {
  testWidgets('sorts ascending and marks header with ascending semantics on first tap',
      (tester) async {
    // act then observable assertion
  });
});
```

The ID at the front of the `group` description makes coverage greppable: a CI step can
scan for `AC-14.3` across the test tree and find exactly the test(s) that claim to cover it.

**Placement rules:**
- The AC/NFR ID belongs in the `group(...)` description, not buried in the `testWidgets` name.
- A single `group` may contain multiple `testWidgets` if they all assert different facets of
  the same criterion (e.g. positive path + negative path for AC-1.1).
- A criterion that has both a holder/unit-test layer and a widget-test layer should carry the
  AC ID in the `group` description of **both** test files.

## 2. `flutter test --plain-name` filtering

Flutter's test runner supports `--plain-name` (`-N`) to filter by a substring of the
full test description (group name + test name concatenated).

```bash
# Does any test claim to cover AC-14.3?
flutter test --plain-name 'AC-14.3'

# Run every test for story 14 before merging a change to that feature
flutter test --plain-name 'AC-14.'

# Run all NFR guards
flutter test --plain-name 'NFR-'
```

`--plain-name` matches a literal substring across the concatenated group+test description,
so `AC-14.` catches `AC-14.1`, `AC-14.2`, `AC-14.3`, etc.

For CI pipelines that run a feature branch, a targeted step can be:
```bash
flutter test --plain-name 'AC-14.' test/
```

This is equivalent to Vitest's `--tags-filter` pattern — no extra tooling required.

## 3. Optional: tags for machine-queryable filtering

If the team wants structured metadata alongside the human-readable description, add a
comment tag convention (or use a test helper) that encodes the AC ID separately.
A lightweight approach:

```dart
group('AC-14.3: tapping a column header sorts rows by that column', () {
  // tags: AC-14.3
  testWidgets('sorts ascending on first tap', (tester) async {
    // ...
  });
});
```

A CI grep then finds both the comment tag and the group description:
```bash
grep -r 'AC-14.3' test/
```

This is optional — the `group` description convention alone is sufficient. Adopt tags
consistently within a spec if you use them; mixing styles inside one spec is worse than
either approach alone.

## 4. Two-layer test coverage for async ACs

An AC that describes async or stream behaviour (e.g. loading → data → error) should be
covered at two layers, both carrying the AC ID:

| Layer | Test type | File pattern | What it asserts |
|---|---|---|---|
| Holder/repository | `test(...)` unit test | `*_test.dart` under `test/unit/` | The publicly observable stream/value sequence |
| Widget | `testWidgets(...)` | `*_test.dart` under `test/widget/` | The rendered outcome the user sees |

Both `group` descriptions must carry the AC ID so a `flutter test --plain-name 'AC-7.1'`
run exercises both layers.

## 5. Downstream gate

The task-breakdown phase generates one test task per AC ID. The test-contract rule
requires every `group`/`test`/`testWidgets` in a new or modified test file to name the
AC or NFR ID it covers. The validation phase then counts AC IDs in `requirements.md`
against AC IDs in passing test names — any AC with no mapped passing test is a blocking FAIL.

```
requirements.md  →  AC-14.3
      │
      ▼
tasks.md         →  "test task: cover AC-14.3"
      │
      ▼
device_table_test.dart  →  group('AC-14.3: ...')
      │
      ▼
validate gate    →  count(AC IDs in reqs) == count(AC IDs covered by green tests)
```

Success signal: **unmapped-AC count → 0 at the validation phase.**
