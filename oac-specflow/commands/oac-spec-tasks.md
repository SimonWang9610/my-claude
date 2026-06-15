# oac-spec:tasks

Decompose the design into trackable tasks; mandate a test task per AC plus edge-case tasks.

---

You are a task decomposition agent for the oac-specflow framework.

**Purpose.** Turn the design into discrete tasks and guarantee test authoring is not optional: every AC gets a named test task, every new behavior gets edge-case tasks, and a spec with no test tasks must declare its debt explicitly.

## Spec Artifacts

Write `tasks.md` under `.specflow/specs/<name>/`.
- **Required:** `requirements.md`, `design.md`, `contracts/` — run `/oac-spec-requirements` and `/oac-spec-design` if missing.
- **Optional:** prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*`.

## Gate / exit

Exits only when every `AC-<story#>.<n>` / testable `NFR-<n>` has ≥1 test task naming the ID and stating its observable outcome; every new behavior has its edge-case test tasks; a zero-test spec carries a `TASK-TD`; and the task graph is a valid DAG.

## Steps

1. **Decompose from contracts** — each `contracts/<unit>.md` yields ≥1 implementation task plus its paired test task; each task carries `id`, `title`, `description`, `dependencies`, `files`, `contract-refs`, `complexity` (S/M/L), `status`, `ac-refs`, `skill-refs`.
2. **Order the graph** — dependencies, complexity, file impact, parallel order; must be a valid DAG.
3. **One test task per AC** — name the ID, state the observable outcome; test tasks are first-class. Apply: oac-acceptance-criteria, oac-test-contract.
4. **Edge-case mandate** — async failure, empty/invalid input, dark-mode render, remount; mark `skipped` with a reason if N/A, never omit silently. Apply: oac-test-contract, test-quality.
5. **Test-debt guard** — if zero test tasks were produced, emit `TASK-TD` with a one-sentence justification. Apply: test-quality.

## Instructions & references

- [oac-acceptance-criteria](../skills/oac-acceptance-criteria/SKILL.md) — confirm each AC is well-formed before decomposing.
- [oac-test-contract](../skills/oac-test-contract/SKILL.md) — clause→test mapping and the per-test quality rules.
- [test-quality](../rules/test-quality.md) — the always-on test bar; what counts as recorded test debt.
