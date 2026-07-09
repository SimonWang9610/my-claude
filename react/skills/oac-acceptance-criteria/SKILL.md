---
name: oac-acceptance-criteria
description: >
  Authors a feature's requirements.md (React 19 + TS): Example Mapping discovery + a domain
  glossary → EARS functional requirements → user stories and acceptance criteria with stable IDs
  (AC-<story>.<n>, NFR-<n>) in observable Given/When/Then form, each ID wired to the front of a
  Vitest describe so coverage is a grep query. Rejects implementation-step phrasing ("shall call
  X()", "shall set isPending"). Use when writing, extending, or hardening the acceptance criteria,
  user stories, or NFRs for a feature — or turning a scope (or figma map) into a testable spec.
---

# oac-acceptance-criteria

Author a feature's requirements document: user stories, EARS functional requirements,
acceptance criteria (`AC-<story>.<n>`), and NFRs (`NFR-<n>`) — every criterion phrased as an
observable outcome, its ID embedded at the front of a Vitest `describe` name. These IDs are
the spine every later artifact (task list, tests, coverage check) anchors to, so they must be
unique, stable, and greppable.

- **Given:** a feature scope, plus any figma component map the caller hands you.
- **Produce:** `requirements.md` with a Glossary, EARS FRs, ID'd user stories, ACs, NFRs, and an
  `## Open questions` section holding every Example-Mapping question you couldn't answer
  (surfaced for the caller to settle during clarification).

## Procedure

1. **Example Mapping discovery** — per user story (`US-<n>`), surface the business rules, make
   each concrete with happy / edge / counter examples, and capture open questions. Don't guess
   past a question; surface it to the caller. → `references/discovery.md`.
2. **Glossary** — record each domain term once in a `Glossary` section; then use those exact
   words verbatim in every AC, NFR, and test name. → `references/discovery.md` §4.
3. **EARS functional requirements** — write the system-level outcomes in EARS; they stay
   alongside the per-story ACs, they don't replace them. → `references/ac-format.md` §1.
4. **ACs from examples** — turn each discovery example into ≥1 `AC-<story>.<n>` in observable
   Given/When/Then form. For behaviour that varies only by data, write one Examples-table AC
   instead of many near-duplicates. → `references/ac-format.md` §3, `references/discovery.md` §5.
   Anti-patterns to avoid (spy-on-call, mock-call, render-it-back tautology, one-shot ban),
   each with a corrected form → `references/examples.md`.
5. **NFRs** — assign each a unique `NFR-<n>` under the same observable phrasing contract; a
   pattern-ban NFR must name itself an enduring CI guard, not a one-shot grep. → `references/ac-format.md` §3.
6. **Assign + verify IDs** — unique, stable, append-only (never renumber). Confirm each ID sits
   at the front of a Vitest `describe` name so `grep -r "AC-2.1" src/` finds the test.
   → `references/traceability.md`.
7. **Authoring checklist** — run the hard checks (below) over everything before handoff.

Why the ID + observable-phrasing discipline matters → `references/rationale.md`.

## Hard checks — an authored criterion fails if any are true

- No `AC-<story>.<n>` / `NFR-<n>` ID, or the ID duplicates another.
- Not in Given/When/Then form, or the Then clause isn't observable.
- Describes an internal call, state, or mechanism (`shall call X()`, `shall set isPending`,
  `shall dispatch to store`) — verifiable only by spying on a function or reading internals.
- A story with zero ACs, or an NFR with no ID.

Fix every failing criterion in `requirements.md` before handoff. When a criterion is ambiguous,
contested, or untestable in a way rewriting can't settle, rank the open items by Impact ×
Uncertainty and settle them with the caller (one question at a time, each with a recommended
answer); then rephrase to an observable form, or record it under `## Open questions`.

## References

- [references/ac-format.md](references/ac-format.md) — ID scheme, EARS patterns, the full
  observable-phrasing contract (reject/require examples), the authoring checklist.
- [references/discovery.md](references/discovery.md) — Example Mapping (rules / examples /
  questions), the domain glossary, and the Examples-table AC form for data-varying behaviour.
- [references/examples.md](references/examples.md) — Before/after for the four most common AC
  anti-patterns, each with its corrected form and a test-name skeleton.
- [references/traceability.md](references/traceability.md) — How an AC ID flows into Vitest
  describe/it names (and optional `--tags-filter` tags) so coverage is a query.
- [references/rationale.md](references/rationale.md) — Why stable IDs + observable phrasing
  exist: the passing-test-that-misses-behaviour failure they prevent.
