# Altitudes — pick the one the question needs

| Altitude | Question sounds like | Read | Bound | Output shape |
|---|---|---|---|---|
| **map** | "how is X organised", "architecture of", "what are the parts", "how does data flow between" | manifests and entry points, top-level folders, module boundaries, the seams (APIs, queues, stores, workers), one representative flow end to end | breadth first, ≤2 hops into any unit | component diagram with labelled edges; per component: role, owns which data, talks to whom; the 2–3 structural decisions visible in the code and why |
| **mechanism** | "how does X work", "what happens when", "why does X do Y", "trace" | the entry point, then the call chain one hop at a time in both directions (calls / called by), the state it reads and writes, its side effects at boundaries | depth first along one path, ≤15 files | sequence or flow diagram; numbered steps `path:symbol — what — data in/out`; invariants and edge cases found; the why |
| **onboarding** | "help me understand this repo", "where do I start", "what should I read first" | README and docs, manifests, the build/run/test commands, the main entry points, one representative feature end to end | ≤12 files, prefer docs and entry points | glossary of 5–10 domain terms with anchors; reading order of ≤8 files with one line each; the conventions a newcomer must know; the first safe change to try |
| **locate** | "where is X", "who writes X", "which module owns X", "is there already a Y" | grep by name and by concept synonyms, then the enclosing unit | ≤5 files | list of `path:symbol — role` ordered by relevance; owner and dependents; one-line answer |

Rules at every altitude: read only what an open question needs; stop at the budget and name the gaps;
facts you did not read are `(inferred)`; never modify the code.
