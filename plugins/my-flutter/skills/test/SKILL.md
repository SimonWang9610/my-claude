---
name: test
description: >-
  Use this skill when writing or fixing tests for Flutter and Dart code: "write a widget test",
  "test this notifier, repository or service", "an acceptance test for this screen", "this test is
  flaky or hangs", with flutter_test, Mocktail and fakeAsync. Gives the rules that make a test able
  to fail: observable outcomes over verify, production-typed fixtures, fakes over mocks, real async
  and stream machinery, bans turned into CI guards, and the assertions each kind of unit needs.
  Knowledge only: it runs no process (with my-workflow, the spec-tester and spec-implementer agents
  do). Not for Riverpod test overrides (use my-flutter:riverpod).
---

# test

Flutter testing rules. Which behaviour to test comes from the task; these are the rules for how. A
test that passes without exercising the real behaviour is worse than no test: it hides the gap.

- A test runs a unit through its **seam**, which the design names (see `my-flutter:design`): a
  widget through `pumpWidget` with injected fakes; a holder, repository or service in pure
  `dart test` with constructor-injected fakes. A unit that can only be tested by mocking its host
  is a design finding: raise it as a gap, never work around it.
- **Name a test by the behaviour it proves.**
- A failing test is fixed in the code, never by weakening the test.

## Rules

| Card | Read when |
|---|---|
| [flutter-tests.md](./rules/flutter-tests.md) | every new or edited test file: nine rules, each with a wrong and right note and a check |
