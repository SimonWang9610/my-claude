# Why this skill exists — rationale

## The failure mode it prevents

The pervasive failure mode in spec-driven development is the **passing test that misses
the behaviour**: a test asserts an internal call or echoes its own input instead of
checking what the user observes. The structural defect is placement — nothing binds an
acceptance criterion to a named, observable test *at authoring time*. A requirements phase
with no ID format and no observable-phrasing contract leaves downstream phases with nothing
to anchor a traceability check to.

This skill is the upstream fix: criteria with stable IDs + observable phrasing make
coverage a runnable query, not a manual audit.

## Scope boundary

This skill sharpens EARS notation, user stories, and NFR sections — it does not replace
them. EARS functional requirements stay; each story's ACs gain IDs and the Given/When/Then
phrasing contract.

## Discovery before criteria

Criteria are only as good as the examples behind them. Before numbering ACs, run **Example
Mapping** (→ `references/discovery.md`): per story, surface the business rules, make each
concrete with happy / edge / counter examples, and capture open questions. Examples become ACs;
questions go to `/spec-clarify`; a small glossary holds one vocabulary across phases. This finds
edge and negative cases at authoring time instead of deferring them downstream.

## The two-layer model: EARS + AC IDs

- **EARS functional requirements** — system-level statements describing *what the system
  shall do*. Outcome-oriented but not individually test-anchored.
- **Acceptance criteria (`AC-<story>.<n>`)** — per-story, observable Given/When/Then
  clauses. Each is the testable, traceable atom a test names.
- **Non-functional requirements (`NFR-<n>`)** — observable system properties (performance,
  theming, pattern bans, platform constraints). Same ID-and-phrasing contract as ACs.

A requirements document is complete only when every story has ≥1 ID'd AC and every NFR
carries an ID.

## Flutter-specific observability model

In Flutter, "observable" means different things at different test layers:

**Widget tests** (`testWidgets`): observable outcomes are what `find.*` locates —
`find.text`, `find.byType`, `find.byIcon`, `find.bySemanticsLabel`, `find.byKey` — and
whether those finders resolve to `findsOneWidget`, `findsNothing`, `findsNWidgets(n)`.
An AC is observable at this layer when its Then clause can be expressed as a finder
assertion without reading any provider, notifier, or controller field directly.

**Unit tests** (`test`): observable outcomes for pure Dart logic are the return value of
a function, the sequence of `AsyncValue` states exposed by a Riverpod `AsyncNotifier`
(or `Notifier`), or the final state of a value exposed via a public getter. An AC about
async data flow (loading → data → error) is observable at this layer when the
`AsyncValue` sequence is asserted via `ProviderContainer` on the publicly exposed
provider, not on a private field or method spy.

A well-formed AC about async behavior typically maps to both layers:
- a unit test on the notifier/repository asserting the `AsyncValue` state sequence
- a widget test asserting the rendered outcome the user sees

Both test groups carry the AC ID so `flutter test --plain-name 'AC-X.Y'` exercises
both layers and the coverage gate finds both.

## Downstream chain

```
requirements.md  →  AC-14.3       (this skill — authoring)
       │
       ▼
tasks.md         →  test task: cover AC-14.3     (task-breakdown phase)
       │
       ▼
*_test.dart      →  group('AC-14.3: ...')        (test-contract: clause→test mapping)
       │
       ▼
validate gate    →  count(AC IDs in reqs) == count(AC IDs covered by green tests)
```

Success: **unmapped-AC count → 0** at the validation phase.
