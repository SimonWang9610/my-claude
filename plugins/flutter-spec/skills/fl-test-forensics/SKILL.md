---
name: fl-test-forensics
description: >
  Audits a Flutter/Dart test suite for three gap classes: (1) behaviors exhibited with no governing
  acceptance criterion (no-spec-coverage), (2) green tests whose bodies assert a weaker proxy than
  the named behavior (tests-pass-but-miss-behavior), and (3) tests that pass regardless of whether
  production code works (false-positive). Uses a mutation-test mindset with Flutter-specific
  heuristics for flutter_test, Mocktail, Riverpod code-gen (Notifier/AsyncNotifier), fakeAsync,
  and streams. Trigger when auditing an existing Flutter test suite for false positives, tautologies,
  over-mocked tests, verify-only tests, or uncovered AC clauses — especially after implementation
  lands, when a green suite lacks confidence, or at drift review time.
---

# fl-test-forensics

Given a feature's surfaces and their tests, determine whether every exhibited behavior is governed by an
acceptance criterion and whether every criterion has a test that actually fails when the behavior breaks.

## Instructions

1. **Enumerate behaviors for each surface.** List widget props, interaction handlers, rendered branches,
   async-state transitions (loading → data → error), side-effects, and stream emissions.
   → read `references/heuristics-behavior-enumeration.md` (behavior enumeration grep recipes, AC traceability shortcut, async-state coverage check)

2. **Pass 1 — no-spec-coverage.** Map each behavior to a requirement ID and each requirement to a test.
   Record behaviors with no requirement as *improvised*; requirements with no test as *uncovered clauses*.
   → read `references/gap-classes.md` (Pass 1 procedure + finding format)
   If a surface has no tests at all, that is a Pass 1 finding — record it and skip Passes 2–3 for that surface.

3. **Pass 2 — tests-pass-but-miss-behavior.** For each requirement-mapped test, read the name as a
   behavioral claim, then read the body. Flag if the triggering action never fires, the assertion checks
   internal state instead of rendered output, or a mock is configured but never exercised by the SUT.
   → read `references/gap-classes.md` (Pass 2 procedure + finding format)
   → read `references/heuristics-pass2-shapes.md` (shapes A–D with before/after examples)

4. **Pass 3 — false-positive.** Scan for on-sight signals (no `expect`/`expectLater`, tautology,
   verify-only, over-mocking, pumpAndSettle with live timers, real async in tests). Confirm with the
   mutation-test mindset: invert or delete the deciding production branch — does the test still pass?
   Yes → false positive.
   → read `references/gap-classes.md` (Pass 3 procedure + finding format)
   → read `references/heuristics-pass3-forms.md` (forms 1–8 grep recipes + before/after examples)
   → read `references/false-positive-signals.md` (on-sight signal catalogue + mutation protocol)

5. **Tag confidence.** Mark every finding high/medium/low. Block on high and medium; surface low as
   advisory. A false positive mapped to a requirement is always Critical.
   → read `references/gap-classes.md` (confidence calibration table)

6. **Cite sources.** When justifying a finding with an external reference (Flutter testing docs, DCM blog,
   CodeWithAndrea, Very Good Ventures, Randy Coulman), look up the URL.
   → read `references/sources.md`

## References

- `references/gap-classes.md` — full detection procedure, finding formats, confidence calibration, reporting table.
- `references/heuristics-behavior-enumeration.md` — Pass 1 grep recipes (widget/notifier/repo enumeration, AC traceability shortcut, async-state coverage check).
- `references/heuristics-pass2-shapes.md` — Pass 2 shapes A–D grep recipes and before/after examples.
- `references/heuristics-pass3-forms.md` — Pass 3 forms 1–8 grep recipes and before/after examples.
- `references/false-positive-signals.md` — on-sight signal catalogue and mutation-test protocol.
- `references/sources.md` — external citations grouped by pass.
