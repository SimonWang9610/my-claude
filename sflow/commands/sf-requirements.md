---
description: Author user stories and acceptance criteria with stable IDs and observable Given/When/Then phrasing.
---
# sf:requirements

Produce the source of truth for all downstream phases: intent bound to stable, testable AC
IDs at authoring time. Writes `requirements.md` under `.specflow/specs/<name>/`. Requires
`.meta.yaml`; optional `preflight.md` + `references/design-units.md` (ground UI stories in
real units); steering as context.

**Steps.**

1. **First principles** — name the problem behind the ask (a requested solution is one
   candidate, never the requirement); check the request's assumptions against preflight
   notes and system fundamentals — a wrong or unverifiable one becomes a question, never a
   silent AC.
2. **Extract** — one US-<n> per user goal; per story, AC-<story>.<n> as observable
   Given/When/Then outcomes (never implementation steps); constraints as NFR-<n>; one
   glossary term per fact, used verbatim. Classify each AC's verification level
   (unit / journey / manual) so journey candidates surface now — design reconciles it.
3. **Ask ONE batched question round** — every ambiguity and challenged assumption, each
   with a recommended answer; fold answers in; record Q→A under `## Clarifications`,
   unanswered as OPEN (they feed the clarify phase).

**Exit.** Every story has ≥1 AC; every AC/NFR carries a unique stable ID
(`AC-<story#>.<n>` / `NFR-<n>`) phrased as an observable Given/When/Then outcome; IDs never
renumber.
