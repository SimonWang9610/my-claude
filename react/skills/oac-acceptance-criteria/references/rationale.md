# Why this skill exists — rationale

## The failure mode it prevents

The pervasive failure mode in spec-driven development is the **passing test that misses
the behaviour**: a test asserts an internal call or echoes its own input instead of
checking what the user observes. The structural defect is placement — nothing binds an
acceptance criterion to a named, observable test *at authoring time*. A requirements document
with no ID format and no observable-phrasing contract leaves the downstream artifacts (task
list, tests, coverage check) with nothing to anchor a traceability check to.

This skill is the upstream fix: criteria with stable IDs + observable phrasing make
coverage a runnable query, not a manual audit.

## Scope boundary

This skill sharpens EARS notation, user stories, and NFR sections — it does not replace
them (EARS mechanics: `references/ac-format.md` §1).

## Discovery before criteria

Criteria are only as good as the examples behind them. Example Mapping (→
`references/discovery.md`) finds edge and negative cases at authoring time instead of
deferring them downstream.

## The two-layer model: EARS + AC IDs

- **EARS functional requirements** — system-level statements describing *what the system
  shall do*. Outcome-oriented but not individually test-anchored.
- **Acceptance criteria (`AC-<story>.<n>`)** — per-story, observable Given/When/Then
  clauses. Each is the testable, traceable atom a test names.
- **Non-functional requirements (`NFR-<n>`)** — observable system properties (performance,
  theming, query config, pattern bans). Same ID-and-phrasing contract as ACs.

A requirements document is complete only when every story has ≥1 ID'd AC and every NFR
carries an ID.

## Downstream chain

AC IDs flow from `requirements.md` through task-breakdown into test names and the coverage
gate — full chain and success signal in `references/traceability.md` §3.
