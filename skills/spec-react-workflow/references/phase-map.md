# Phase map — React `oac-*` skill bindings + exitWhen

The project-hosted specflow template declares the phase order, `approval`, `required`,
`inputs`, `outputs` (its `generator`/`executor` hints, `validators`, and `hooks` are ignored).
This map binds each phase directly to its React `oac-*` skills and supplies the `exitWhen`
line. It is the union of all variants' phase ids — a variant uses only the phases its template
declares. A trailing `?` marks a conditional the generator resolves against the actual
spec/project (see the SKILL's decision table); `/scan-resource` is a shared skill, not `oac-*`.

Stack: React 19 + Vite + TypeScript + Zustand + TanStack Query v5 + MUI + Vitest.

| Phase | Skills | exitWhen |
|---|---|---|
| preflight | `/oac-figma-decompose`?, `/scan-resource`? | reuse verdict + shared-unit impact table (ADOPTED/UNADOPTED + action) |
| analysis | `/oac-analyze`, `/scan-resource`? | bugfix: named, deterministic, FAILING reproduction test asserts the bug's AC; brownfield: change surface + shared-unit impact mapped in analysis.md |
| describe | `/oac-acceptance-criteria` | exactly one AC with a stable ID + observable Given/When/Then phrasing |
| requirements | `/oac-acceptance-criteria` | every AC/NFR has a stable ID + observable Given/When/Then phrasing |
| clarify | `/oac-acceptance-criteria` | top ambiguities resolved; every untestable AC rephrased or recorded |
| design | `/oac-architecture-design`, `/oac-journey-plan`? | every AC covered by >=1 contract; architecture gate PASS or justified |
| tasks | `/oac-task-design`, `/oac-test-contract` | valid dependency order + a parallel-wave plan (independent units grouped into concurrency waves); >=1 test task per AC plus edge-case tasks |
| implement | `/oac-implementation`, `/oac-test-contract`, `/oac-implementation-review` | every task completed with a passing AC-traceable test, authored red-before-green by a separate test agent; branch passes `/oac-implementation-review` (no unresolved Critical/Major findings); human verifies the code before spec-qa |
| spec-qa | `/oac-qa-report`, `/oac-test-forensics`, `/oac-journey-tests`? | enters only after the flow's validate command PASSES (static checks, reported in chat — never a ledger phase); findings dispositioned by the reviewer (sign-off); suite green via a single eslint + vitest run |

## Conditionals the generator resolves (`?`)

| Conditional | Keep when | Drop when |
|---|---|---|
| `/oac-figma-decompose`? (preflight) | the caller reports design links, or the spec's `.meta.yaml` records them | no design links |
| `/scan-resource`? (preflight, analysis) | legacy/cross-stack port, or a large existing subsystem to audit | greenfield, small scope |
| `/oac-journey-plan`? (design) / `/oac-journey-tests`? (spec-qa) | E2E coverage is wanted — plan at design (blocking human approval), authoring at spec-qa from the approved plan | project has no E2E layer |

A conditional that can't be decided yet stays in the output with its condition attached.

Gate mapping: template `approval: human` → `gate: human`; `auto`/`skip` → `gate: auto`.
**Exception:** `implement` is always `gate: human` regardless of the template's approval — the
bundle's post-implement human code check.
