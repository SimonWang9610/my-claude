# requirements

Produce the source of truth for all downstream phases: intent bound to stable, testable AC IDs at
authoring time.

**Writes** `requirements.md` · **Reads** `.meta.yaml` · optional `preflight.md` + caller materials
(a design decomposition, to ground UI stories in real units).

**Steps**
1. **First principles** — name the problem behind the ask (a requested solution is one candidate,
   never the requirement); check its assumptions against preflight notes + system fundamentals — a
   wrong or unverifiable one becomes a question, never a silent AC.
2. **Extract** — one `US-<n>` per user goal; per story `AC-<story>.<n>` as observable
   Given/When/Then outcomes (never implementation steps); constraints as `NFR-<n>`; one glossary
   term per fact, used verbatim. Classify each AC's level (unit / journey / manual).
3. **One batched question round** — every ambiguity + challenged assumption, each with a recommended
   answer; fold answers in; record Q→A under `## Clarifications`, unanswered as OPEN.

**Exit** — every story ≥1 AC; every AC/NFR a unique stable ID (`AC-<story#>.<n>` / `NFR-<n>`) phrased
as an observable Given/When/Then outcome; IDs never renumber.
