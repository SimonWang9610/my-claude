---
description: Decompose the design into ordered tasks with a test task per acceptance criterion plus edge cases.
---
# sf:tasks

Decompose the design into trackable tasks; mandate a test task per AC plus edge-case tasks.

---

**Purpose.** Turn the design into discrete tasks and guarantee test authoring is not optional: every AC gets a named test task, every new behavior gets edge-case tasks, and a spec with no test tasks must declare its debt explicitly.

## Spec Artifacts

Write `tasks.md` under `.specflow/specs/<name>/`.
- **Required:** the upstream artifacts the workflow declares — `requirements.md` + `design.md` + `contracts/` on feature/brownfield (run `/sf-requirements` / `/sf-design` if missing), or `analysis.md` on bugfix.
- **Optional:** prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*`.

## Gate / exit

Exits only when every `AC-<story#>.<n>` / testable `NFR-<n>` has ≥1 test task naming the ID and stating its observable outcome; every new behavior has its edge-case test tasks; a zero-test spec carries a `TASK-TD`; and the task graph is a valid DAG grouped into parallel waves.

## Steps

1. **Decompose from contracts** — each `contracts/<unit>.md` yields ≥1 implementation task plus its paired test task; each task carries `id`, `title`, `description`, `dependencies`, `files`, `contract-refs`, `complexity` (S/M/L), `status`, `ac-refs`, `skill-refs`.
2. **Order the graph + wave it** — dependencies, complexity, file impact; must be a valid DAG. Group independent units into parallel **waves** (Wave 1 = no-dependency units; Wave *n* = units whose dependencies completed in earlier waves) so `/sf-implement` runs each wave concurrently.
3. **One test task per AC** — name the ID, state the observable outcome; test tasks are first-class.
4. **Edge-case mandate** — async failure, empty/invalid input, boundary conditions, remount/reload; mark `skipped` with a reason if N/A, never omit silently.
5. **Test-debt guard** — if zero test tasks were produced, emit `TASK-TD` with a one-sentence justification.
