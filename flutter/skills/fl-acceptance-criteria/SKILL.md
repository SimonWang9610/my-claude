---
name: fl-acceptance-criteria
description: >
  Authors and validates acceptance criteria for Flutter/Dart 3 + Riverpod features.
  Assigns stable IDs (AC-<story>.<n>, NFR-<n>), enforces observable Given/When/Then
  phrasing, rejects implementation-step criteria (no "shall call notifyListeners()",
  "shall set isLoading", "shall emit a LoadingState"), and defines how IDs flow into
  Flutter group/test/testWidgets names so coverage is a grep query or a
  `flutter test --plain-name` filter. Trigger: use when writing or reviewing acceptance
  criteria or NFRs for a Flutter spec, or when a criterion may be untestable,
  ill-formed, or missing an ID before design begins.
---

# fl-acceptance-criteria

Produce acceptance criteria that carry stable IDs, describe user-observable outcomes
instead of implementation steps, and flow one-to-one into test names. The IDs minted
here are the spine that test tasks, implementation, and validation all anchor to.

## When to use

- Writing acceptance criteria or NFRs for a new or existing Flutter spec.
- Reviewing criteria that may be untestable, ill-formed, or missing IDs.
- Checking that every story has ≥1 AC and every NFR carries an ID before design begins.

## Instructions

1. Read the feature scope and any existing criteria from the relevant requirements artifact
   (e.g. `requirements.md`). → read `references/ac-format.md` §1 for EARS pattern guidance.
2. Write EARS functional requirements for system-level outcomes.
3. If the criteria already exist and you are only reviewing, skip to step 5 (hard checks).
4. For every user story, write ≥1 AC with ID `AC-<story#>.<n>` in Given/When/Then form.
   → read `references/ac-format.md` §2–3 for ID rules and phrasing contract.
5. Run the hard checks against every criterion (→ `references/ac-format.md` §5 checklist):
   - ID is unique and stable; no renumbering.
   - Then clause is user-observable — no internal call, state, or mechanism.
   - Not a mock-call assertion or render-it-back tautology (→ `references/examples.md`).
6. For every NFR, assign a unique `NFR-<n>` ID using the same observable phrasing contract.
7. For each AC/NFR, confirm its ID embeds in the Flutter `group(...)` description.
   → read `references/traceability.md` §1 for naming convention and §2 for `--plain-name` filtering.
8. Flag any criterion failing a hard check as a blocking authoring condition — fix the
   source artifact before proceeding.

### Hard checks — a criterion fails if any are true

- No `AC-<story#>.<n>` or `NFR-<n>` ID, or the ID duplicates another.
- Describes an internal call, state, or mechanism (`shall call notifyListeners()`,
  `shall set isLoading`, `shall emit a LoadingState`).
- Then clause is only verifiable by reading a provider/notifier field directly or
  spying on an internal method — not by what a widget renders or a stream emits.

## References

- [references/ac-format.md](references/ac-format.md) — ID scheme, EARS patterns, full
  phrasing contract (reject/require examples), authoring checklist.
- [references/examples.md](references/examples.md) — Before/after for the five most
  common AC anti-patterns with Flutter test-name skeletons.
- [references/traceability.md](references/traceability.md) — How an AC ID flows into
  Flutter group/test/testWidgets names and `flutter test --plain-name`/`-N` filtering.
- [references/rationale.md](references/rationale.md) — Why this skill exists, the
  two-layer EARS + AC model, and the downstream coverage chain.
