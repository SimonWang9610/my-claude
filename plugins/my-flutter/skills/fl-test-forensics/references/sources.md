# External sources

Cite these URLs when justifying a finding; paraphrase, never paste substantial text.

## General Flutter testing overview (all passes)

- Flutter — Testing Flutter apps (official overview of unit, widget, integration testing layers):
  https://docs.flutter.dev/testing/overview

## Pass 3 forms 1–3 — tautology, over-mocking, verify-only

- Randy Coulman — Tautological Tests (why tests that assert what they set up cannot fail):
  https://randycoulman.com/blog/2016/12/20/tautological-tests/
- DCM — Navigating the Hard Parts of Testing for Flutter Developers (over-mocking, verify-only, and
  common Flutter test anti-patterns):
  https://dcm.dev/blog/2025/07/30/navigating-hard-parts-testing-flutter-developers/

## Pass 3 forms 6–7 — real async, stream ordering, fakeAsync

- Andrea Bizzotto / CodeWithAndrea — Async Tests and Streams in Flutter (fakeAsync, expectLater ordering,
  stream matchers, timeout discipline):
  https://codewithandrea.com/articles/async-tests-streams-flutter/

## Pass 1 — spec coverage / AC traceability

- Very Good Ventures — Road to 100% Test Coverage (traceability, coverage gaps, and systematic coverage
  enforcement in Flutter projects):
  https://verygood.ventures/blog/road-to-100-test-coverage/

## Local-evidence notes

- **Form 4 (internal state vs rendered output):** the guidance to use `find.text`/`find.byType` over
  direct state field access follows Flutter's own widget test philosophy (test what the user sees). No
  single canonical blog post; confirm with the rendered widget tree before blocking.
- **Form 5 (`pumpAndSettle` with live network):** the 30 s default timeout is a Flutter test framework
  behavior documented in `flutter_test` source (`TestWidgetsFlutterBinding`). Confirm via framework
  behavior observation rather than a single external URL.
- **Mutation-test protocol:** general engineering practice adapted to Flutter/Dart test tooling. Run
  `flutter test <file> --reporter=expanded` to execute mutations; the reasoning is framework-agnostic.
