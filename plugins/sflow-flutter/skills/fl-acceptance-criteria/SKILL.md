---
name: fl-acceptance-criteria
description: >
  Authors and validates acceptance criteria for Flutter/Dart 3 + Riverpod features.
  Assigns stable IDs (AC-<story>.<n>, NFR-<n>), enforces observable Given/When/Then
  phrasing, rejects implementation-step criteria (no "shall call notifyListeners()",
  "shall set isLoading", "shall emit a LoadingState"), and defines how IDs flow into
  Flutter group/test/testWidgets names so coverage is a grep query or a
  `flutter test --plain-name` filter. Runs Example Mapping discovery (rules/examples/questions) and a domain glossary before authoring. Trigger: use when writing or reviewing acceptance
  criteria or NFRs for a Flutter spec, or when a criterion may be untestable,
  ill-formed, or missing an ID before design begins.
---

# fl-acceptance-criteria

Produce acceptance criteria that carry stable IDs, describe user-observable outcomes instead of implementation steps, and flow one-to-one into test names. The IDs minted here are the spine that test tasks, implementation, and validation all anchor to.

## Instructions

1. Read the feature scope and any existing criteria from the relevant requirements artifact
   (e.g. `requirements.md`). → read `references/ac-format.md` §1 for EARS pattern guidance.
2. Write EARS functional requirements for system-level outcomes.
3. **Run Example Mapping discovery** before writing ACs (→ `references/discovery.md`). Per user
   story, enumerate the business **rules**, then concrete observable **examples** for each
   (happy, edge, counter), and capture open **questions**. Record domain terms in a `Glossary`
   section of `requirements.md`; surface open questions back to the caller rather than guessing.
4. If the criteria already exist and you are only reviewing, skip to step 6 (hard checks).
5. Derive ACs from the discovery examples — each example becomes ≥1 AC with ID `AC-<story#>.<n>`
   in Given/When/Then form; for behaviour that varies only by data, use an Examples-table AC.
   → read `references/ac-format.md` §2–3 and `references/discovery.md` §5.
6. Run the hard checks against every criterion (→ `references/ac-format.md` §5 checklist):
   - ID is unique and stable; no renumbering.
   - Then clause is user-observable — no internal call, state, or mechanism.
   - Not a mock-call assertion or render-it-back tautology (→ `references/examples.md`).
7. For every NFR, assign a unique `NFR-<n>` ID using the same observable phrasing contract.
8. For each AC/NFR, confirm its ID embeds in the Flutter `group(...)` description.
   → read `references/traceability.md` §1 for naming convention and §2 for `--plain-name` filtering.
9. Flag any criterion failing a hard check as a blocking authoring condition — fix the
   source artifact before proceeding.
10. Write `requirements.md` terse — every later phase re-reads it: no filler or restated
    context; Glossary terms, IDs, and Given/When/Then facts exact; no invented abbreviations.

### Hard checks — a criterion fails if any are true

- No `AC-<story#>.<n>` or `NFR-<n>` ID, or the ID duplicates another.
- Describes an internal call, state, or mechanism (`shall call notifyListeners()`,
  `shall set isLoading`, `shall emit a LoadingState`).
- Then clause is only verifiable by reading a provider/notifier field directly or
  spying on an internal method — not by what a widget renders or a stream emits.

## References

- [references/ac-format.md](references/ac-format.md) — ID scheme, EARS patterns, full
  phrasing contract (reject/require examples), authoring checklist.
- [references/discovery.md](references/discovery.md) — Example Mapping (rules / examples /
  questions), the domain glossary, and the Examples-table AC form for data-varying behaviour.
- [references/examples.md](references/examples.md) — Before/after for the five most
  common AC anti-patterns with Flutter test-name skeletons.
- [references/traceability.md](references/traceability.md) — How an AC ID flows into
  Flutter group/test/testWidgets names and `flutter test --plain-name`/`-N` filtering.
- [references/rationale.md](references/rationale.md) — Why this skill exists, the
  two-layer EARS + AC model, and the downstream coverage chain.
