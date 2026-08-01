# fl-test-contract — external sources

Cite as links when justifying a rule; paraphrase, never paste substantial text.

## Rule 1 — Observable outcomes, not implementation

- Flutter Docs — An introduction to widget testing (query widgets by type/text/key, assert the rendered tree):
  https://docs.flutter.dev/cookbook/testing/widget/introduction
- Very Good Ventures — Guide to Flutter testing (outcomes over internals; when verify is appropriate):
  https://verygood.ventures/blog/guide-to-flutter-testing/
- DCM Blog — Navigating the hard parts of testing for Flutter developers (implementation-detail traps):
  https://dcm.dev/blog/2025/07/30/navigating-hard-parts-testing-flutter-developers/

## Rule 2 — Clause→test mapping

- Flutter Docs — An introduction to widget testing (structuring tests so coverage gaps are queryable):
  https://docs.flutter.dev/cookbook/testing/widget/introduction
- Very Good Ventures — Guide to Flutter testing (group/test naming conventions and AC traceability):
  https://verygood.ventures/blog/guide-to-flutter-testing/

## Rule 3 — Production-shaped fixtures

- Flutter Docs — An introduction to widget testing (constructing widget trees from real domain objects):
  https://docs.flutter.dev/cookbook/testing/widget/introduction
- DCM Blog — Navigating the hard parts of testing for Flutter developers (fixture drift and typed models):
  https://dcm.dev/blog/2025/07/30/navigating-hard-parts-testing-flutter-developers/

## Rule 4 — No tautologies; prefer fakes over mocks

- pub.dev — mocktail (no-codegen mocking library for Dart; use sparingly, prefer fakes):
  https://pub.dev/packages/mocktail
- Flutter Docs — Mock dependencies using Mockito / mocktail (when mocks are appropriate vs. fakes):
  https://docs.flutter.dev/cookbook/testing/unit/mocking
- DCM Blog — Navigating the hard parts of testing for Flutter developers (false-positive tautologies):
  https://dcm.dev/blog/2025/07/30/navigating-hard-parts-testing-flutter-developers/

## Rule 5 — Real async/stream machinery for async ACs

- Andrea Bizzotto — Async tests and streams in Flutter (StreamController, expectLater, emitsInOrder):
  https://codewithandrea.com/articles/async-tests-streams-flutter/
- Dart API — fakeAsync (drive time deterministically; elapse vs. flushMicrotasks):
  https://api.flutter.dev/flutter/package-fake_async_fake_async/fakeAsync.html
- Very Good Ventures — Guide to Flutter testing (pump vs. pumpAndSettle; infinite-timer pitfalls):
  https://verygood.ventures/blog/guide-to-flutter-testing/
- DCM Blog — Navigating the hard parts of testing for Flutter developers (pumpAndSettle timeout trap):
  https://dcm.dev/blog/2025/07/30/navigating-hard-parts-testing-flutter-developers/

## Rule 6 — One-shot greps become enduring CI guards

- DCM Blog — Navigating the hard parts of testing for Flutter developers (custom_lint/DCM as CI enforcement):
  https://dcm.dev/blog/2025/07/30/navigating-hard-parts-testing-flutter-developers/
- Very Good Ventures — Guide to Flutter testing (analysis_options.yaml and lint-driven bans):
  https://verygood.ventures/blog/guide-to-flutter-testing/
