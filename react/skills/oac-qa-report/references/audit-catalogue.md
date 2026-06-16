# Audit catalogue

The build gate and the audit families QA runs before writing the report. Each check, when it fires,
becomes a finding flagged `⚠️ **<Label>:** <one-line>` and a row in the report's findings table.
General and stack-agnostic — substitute your project's commands and conventions (from the steering
files). Optional project extensions (visual/design fidelity, E2E journeys, API-contract compliance)
live at the adaptation point, not here.

---

## §0 — Build gate

Audit nothing on a red branch.

1. **Build** the branch with the project's build command. If it fails → STOP, report `❌ BUILD FAILED`
   with the error, write no further sections.
2. **Run the existing suite** with the project's test command. If pre-existing tests fail → STOP,
   report which tests regressed; the developer fixes regressions before QA proceeds.
3. Record the suite's pass/fail counts for the report's **Test Suite Results** section.

---

## §1 — Spec authenticity

The specs may describe the work inaccurately. Do not take them at face value.

- **Commit order** — were the spec docs committed *after* the implementation? If so, the spec may
  describe the work retroactively. `⚠️ Spec lifecycle violation`.
- **Baseline accuracy** — if the spec claims a "current behavior" or "bug" on the base branch, verify
  it against the base. A described baseline that never existed → `⚠️ Spec baseline mismatch` (a new
  feature mislabeled as a bugfix).
- **Workflow type** — does `.meta.yaml`'s `workflow` match the actual work (a `bugfix` must fix
  something demonstrably broken on the base; a `feature` adds new behavior)?
- **Phase/task honesty** — for each task marked `completed`, verify the deliverable exists
  (created files present, deleted files gone, modification sub-items actually landed). Flag
  `status: validated`/all-tasks-completed on a single spec+code commit (retroactive fiction), any
  `pending` phase under a `validated`/`complete` status, a `current_phase` that contradicts `status`,
  and a `name`/directory mismatch.
- **Requirement ↔ task consistency** — for each `FR-*`/`AC-*`, find the `TASK-*` that implements it;
  if they describe different behavior, the implementation can only match one. `⚠️ Spec internal
  contradiction` (Critical — the losing doc must be fixed and QA re-run).
- **Spec ↔ code value drift** — if the spec claims a value/field/shape was removed or changed, grep
  the code for the old value; if it survives → `⚠️ Spec ↔ code value drift`.

---

## §2 — Scope creep

A feature PR should contain only feature-related changes.

- **Governance files** — config/CI/ownership surfaces changed (`.github/`, CI workflows, lint/TS/
  bundler config, `.gitignore`, dotenv, the framework's own command/rule files) without the feature
  being a governance task → `⚠️ Scope creep — governance files` (Critical).
- **Steering placeholders** — steering docs rewritten to template placeholders (`[Describe …]`).
- **Project identity** — package renamed to a temp/placeholder name, or an unrelated entry point.
- **Unrelated dependencies** — new runtime deps not traceable to the design; test-only packages added
  to runtime deps.
- **Unrelated routes** — router changes not described in the spec.
- **CI changes** — workflow YAML modified by a feature PR → belongs in a separate infra PR.

---

## §3 — Coverage + false-positive

Detection mechanics live in the sibling skills — apply them and record the hits here:
- [`../../oac-test-forensics/SKILL.md`](../../oac-test-forensics/SKILL.md) — the three gap classes, mock-shape drift, matcher misuse, and the **mutation test** (invert/delete the deciding branch — does the test still pass? → false positive). A false positive mapped to an `AC-*` is **Critical** (the AC has no real verification).
- [`../../oac-test-contract/SKILL.md`](../../oac-test-contract/SKILL.md) — the six per-test rules.

QA-specific coverage checks not covered there:
- **Colocated tests** — every newly created unit has a colocated test; if not → `⚠️ Missing colocated test`.
- **Branch coverage of new code** — new props/conditionals have a case per branch; a green suite that
  never exercises the new branch → `⚠️ Test coverage gap` (green-but-hollow).
- **Type tightness on shared APIs** — a shared export whose value set is known uses a union, not a
  bare `string`/`number` → `⚠️ Weak types on shared API`.
- **Tests mirror production logic** — a test that re-implements a production helper instead of
  importing it stays green when the real code drifts → `⚠️ Test mirrors production logic`.
- **Dead/deprecated code** — a file the docs mark deprecated was modified (not deleted), or a
  deprecated module gains a new import (Critical).

---

## §4 — Silent failure

Error handling that hides failures from users and tests.

- **Swallowed errors** — a `catch` that only logs (or `catch(() => {})`) on a write/mutation, with no
  user-facing error surface → failures look like successes. `⚠️ Console-only / swallowed error`.
- **Stub returning fake success** — a function returns a hardcoded success value with a `TODO`
  instead of calling the real backend → tests pass against the stub. `⚠️ Stub API returning fake success`.
- **Ephemeral state shown as persisted** — user-visible state kept in a ref/in-memory map with no
  persistence, presented as saved → data lost on reload. `⚠️ Ephemeral state masquerading as persisted`.
- **Client-generated server IDs** — entity IDs minted client-side (`Date.now()`, random) that must be
  server-assigned → phantom records on sync. `⚠️ Client-generated ID`.

---

## §5 — Consumer + regression

- **Direct consumers** — for each consumer of a changed unit: imports resolve, no removed/renamed prop
  is still passed, no type error; run its tests if any.
- **Blast radius** — classify changes as unit-scoped, shared-dependency, or layout/ancestor. For a
  shared change, find every importer and run (or smoke-test) them. Run the suite for the files QA's own
  commits touched. Log regressions in their own report section, separate from feature findings.
