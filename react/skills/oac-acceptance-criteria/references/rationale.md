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
them. EARS functional requirements stay; each story's ACs gain IDs and the Given/When/Then
phrasing contract.

## Discovery before criteria

Criteria are only as good as the examples behind them. Before numbering ACs, run **Example
Mapping** (→ `references/discovery.md`): per story, surface the business rules, make each
concrete with happy / edge / counter examples, and capture open questions. Examples become ACs;
questions are surfaced to the caller; a small glossary holds one vocabulary across all downstream artifacts. This finds
edge and negative cases at authoring time instead of deferring them downstream.

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

```
requirements.md  →  AC-14.3       (this skill — authoring)
       │
       ▼
tasks.md         →  test task: cover AC-14.3     (task breakdown)
       │
       ▼
*.test.tsx       →  describe('AC-14.3: ...')     (test-contract: clause→test mapping)
       │
       ▼
coverage gate    →  count(AC IDs in reqs) == count(AC IDs in green tests)
```

Success: **unmapped-AC count → 0** when the coverage gate is run.
