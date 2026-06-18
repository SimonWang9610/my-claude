---
name: oac-test-forensics
description: >
  Audits a React/TypeScript test suite for three gap classes: behaviors with no governing requirement
  (no-spec-coverage), green tests that never exercise the named behavior (tests-pass-but-miss-behavior),
  and false-positive tests that pass regardless of whether the code works. Uses a mutation-test mindset
  and stack-specific heuristics for RTL, Zustand, TanStack Query v5, and Vitest. Trigger after
  implementation lands, before a release, or whenever a green suite does not give confidence that a
  real regression would be caught. Keywords: test audit, false positive, tautology, mock-shape drift,
  proxy assertion, query-config NFR, mutation test, React Testing Library, TanStack Query, Zustand.
---

# oac-test-forensics

Given a feature's surfaces and their tests, determine whether every exhibited behavior is governed by an
acceptance criterion and whether every criterion has a test that actually fails when the behavior breaks.

## When to use

When auditing an existing or recently changed test suite for false-positive, tautological,
mock-shape-drift, proxy-assertion, or behavior-missing tests — especially after implementation lands or
when a green suite does not give confidence that a real regression would be caught.

## Instructions

1. **Enumerate behaviors for each surface.** List props, handlers, render branches, side-effects, and error paths.
   → read `references/react-ts-heuristics.md` (behavior enumeration grep recipes)

2. **Pass 1 — no-spec-coverage.** Map each behavior to a requirement ID and each requirement to a test. Record behaviors with no requirement as *improvised*; requirements with no test as *uncovered clauses*.
   → read `references/gap-classes.md` (Pass 1 procedure + finding format)
   If a surface has no tests at all, that is a Pass 1 finding — record it and skip Passes 2–3 for that surface.

3. **Pass 2 — tests-pass-but-miss-behavior.** For each requirement-mapped test, read the name as a behavioral claim, then read the body. Flag if the triggering action never fires, the assertion is at the wrong depth/owner, or the mock is declared but never called.
   → read `references/gap-classes.md` (Pass 2 procedure + finding format)
   → read `references/react-ts-heuristics.md` (shapes A–D with before/after examples)

4. **Pass 3 — false-positive.** Scan for on-sight signals (no `expect()`, tautology, mock-shape drift, un-awaited write, CSS-class-for-color, mocked QueryClient). Confirm with the mutation-test mindset: invert or delete the deciding production branch — does the test still pass? Yes → false positive.
   → read `references/gap-classes.md` (Pass 3 procedure + finding format)
   → read `references/react-ts-heuristics.md` (forms 1–5 grep recipes + before/after examples)
   → read `references/false-positive-signals.md` (on-sight signal catalogue + mutation protocol)

5. **Tag confidence.** Mark every finding high/medium/low. Block on high and medium; surface low as advisory. A false positive mapped to a requirement is always Critical.
   → read `references/gap-classes.md` (confidence calibration table)

6. **Cite sources.** When justifying a finding with an external reference (Kent C. Dodds, Testing Library, Cucumber, Vitest tags, MSW TypeScript, TkDodo), look up the URL.
   → read `references/sources.md`

## References

- `references/gap-classes.md` — full detection procedure, finding formats, confidence calibration, reporting table.
- `references/react-ts-heuristics.md` — grep/read recipes and before/after examples for all passes and forms.
- `references/false-positive-signals.md` — on-sight signal catalogue and mutation-test protocol.
- `references/sources.md` — external citations grouped by pass.
