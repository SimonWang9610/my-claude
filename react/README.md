# react — sflow React profile

This is the **React profile** of the unified sflow bundle. See [../sflow/README.md](../sflow/README.md) for the full process documentation.

**Stack:** React 19 + Vite + TypeScript + Zustand + TanStack Query + MUI + Vitest.

This profile provides:

- The workflow **generators** live at the repo root and are React-specific:
  [`../skills/sf-react-workflow`](../skills/sf-react-workflow/SKILL.md) (this bundle's `/sf-*`
  flow) and [`../skills/spec-react-workflow`](../skills/spec-react-workflow/SKILL.md) (company
  specflow `/spec-*` projects) — each generates the spec's `workflow.yaml`, binding a template's
  phases directly to concrete `oac-*` skills (design-link / legacy-port / E2E
  conditionals) plus the React exitWhen notes, reading the templates from the project's vendored
  specflow (`specflow/src/workflows/`, with `.specflow/workflows/` as override). Another stack
  would ship its own parallel `*-<tech>-workflow` generator.
- `skills/` — one per phase concern: `oac-figma-decompose` (reuse/decompose a design source),
  `oac-analyze` (root-cause + failing repro test for a defect, or change-surface/impact map for an
  in-place change), `oac-acceptance-criteria` (author the requirements doc — Example Mapping →
  EARS → observable ACs/NFRs, and harden ambiguous criteria), `oac-architecture-design` (owns the
  22-rule corpus + runs the verifiable-unit gate), `oac-journey-plan` (E2E journey scoping + human
  approval gate), `oac-task-design` (design + contracts → dependency-ordered tasks.md with a test
  task per AC), `oac-implementation` (contract-conforming correctness + React 19 idioms behind a
  fixed contract) paired with `oac-implementation-review` (detect-side perf-corpus + architecture-
  boundary review, run as the implement exit gate; findings loop back to the implementer),
  `oac-journey-tests` (author E2E tests from the approved plan), `oac-qa-report` (branch audit →
  sign-off report), and the paired `oac-test-contract` (authoring-time prevention) /
  `oac-test-forensics` (audit-time detection) whose findings map to each other's rules.
- `rules/` — `architecture-principles.md` (P1–P8, paths-gated to `**/*.ts(x)`), `test-quality.md`
  (paths-gated to `**/*.test.*` / `**/*.spec.*`). The shared `engineering-discipline.md` and
  `preferences.md` live only at the repo root [`../rules/`](../rules/) (real files, not
  mirrored here).

This profile ships no `agents/` — the unified driver agents (`sflow-driver`, `specflow-driver`)
live at the repo root [`../agents/`](../agents/).

The generic process commands live in [../sflow/commands/](../sflow/commands/) and are invoked
as `/sf-*`; the workflow phase machines come from the project's vendored specflow templates.
