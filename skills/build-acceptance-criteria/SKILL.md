---
name: build-acceptance-criteria
description: >
  Extract and formalize requirements from a user's instructions into user stories (US-<n>),
  acceptance criteria (AC-<story#>.<n>), and non-functional requirements (NFR-<n>) — each with a
  stable, unique ID and phrased as an observable Given/When/Then outcome, never an
  implementation step. Use when writing, extending, or
  hardening the acceptance criteria, user stories, or NFRs for a feature, or turning an
  ambiguous scope into a testable spec.
---

# Build Acceptance Criteria

Turn a user's request — often partial or ambiguous — into a single **requirements document**
that formalizes what to build. The document holds:

- **Glossary** — each domain term defined once.
- **EARS functional requirements** — system-level statements of what the system shall do, in EARS syntax.
- **User stories** — each with a unique `US-<n>` ID.
- **Acceptance criteria** — each with a unique `AC-<story#>.<n>` ID, phrased in observable Given/When/Then form.
- **Non-functional requirements** — each with a unique `NFR-<n>` ID, in the same observable form.
- **Open questions** — every gap discovery could not settle, surfaced for the caller.

## Instructions

1. **Discovery** — Follow [discovery](./discovery.md) to explore the requirements and examples to find edge cases, negative cases, and missing behaviour, surface the business rules, make each concrete with happy / edge / counter examples, and capture open questions. Don't guess past a question; surface it to the caller
2. **Glossary** — Record each domain term once in a `Glossary` section; then use those exact words verbatim across every user story, AC, and NFR (one word per concept, no synonyms) so nothing drifts between artifacts.
3. **Authoring** — Follow [ac-format](./ac-format.md) and [phrasing-contract](./phrasing-contract.md) to: write the system-level functional requirements in EARS syntax; then turn the discovery results into concrete user stories and acceptance criteria; assign unique IDs; phrase each criterion in observable Given/When/Then form; and avoid implementation-step phrasing.
4. **Verification** - Follow [Hard rules](#hard-rules) to check the authored criteria. If any fails, fix it before handoff. When a criterion is ambiguous, contested, or untestable in a way rewriting can't settle, rank the open items by Impact × Uncertainty and settle them with the caller (one question at a time, each with a recommended answer); then rephrase to an observable form, or record it under `## Open questions`.

### Hard rules

- **Unique IDs** — Ensure every user story, acceptance criterion, and non-functional requirement has a unique ID.
- **Observable Given/When/Then** — Verify that each acceptance criterion and non-functional requirement is phrased in observable Given/When/Then form.
- **Independent verifiability** — Check that each criterion can be independently verified without reaching into the implementation's internals.
