# Review report

One block; a line marked `(…)` only where it applies, `open` and `recommend` only when non-empty, one
`verify` line per command.

```text
Critique — <code | design | doc> · <target> · spec: <path | none> · verdict: accept | accept with fixes | rework
verify  <command> → exit <n> | unverifiable — <reason>                    (when the spec has verify)
spec    R<n> → met | not met → I<n> | unverifiable — <evidence>           (one per R, when a spec exists)
I<n>    blocker | major | minor · <path:line> — <defect> — breaks when: <input or state> — evidence: <run | read, not run> — fix: <direction>
open    Q<n> <question> — default: <answer>
recommend <≤3 lines: fix order, a missing test or check>
pre-existing <n>                                                          (diffs)
next    /my-spec:decide | build | write (the skill that made the target) — fix I<n>…   (rework, accept with fixes)
```
