# react — sflow React profile

This is the **React profile** of the unified sflow bundle. See [../sflow/README.md](../sflow/README.md) for the full process documentation.

**Stack:** React 19 + Vite + TypeScript + Zustand + TanStack Query + MUI + Vitest.

This profile provides:

- `agents/` — the orchestrators: `oac-{feature,brownfield,bugfix,quickfix}-workflow.md`. Each driver
  starts via `/sf-workflow-startup react <variant>` (which binds through `/pick-react-workflow`),
  drives the phases, enforces the gates, and delegates phase work to subagents.
- The profile's **binding skill** lives at the repo root: [`../skills/pick-react-workflow`](../skills/pick-react-workflow/SKILL.md)
  — it converts a workflow template's capability roles into concrete `oac-*` skills (resolving
  design-link / legacy-port / Jira conditionals) plus the React stage notes, reading the
  templates from the sibling `../sflow/workflows/`.
- `skills/` — `oac-acceptance-criteria`, `oac-architecture-design` (owns the full rule corpus +
  runs the verifiable-unit gate at phase exit — design-time authoring and verification in one
  skill), `oac-figma-decompose`, `oac-journey-tests`, `oac-qa-report`, `oac-test-contract`,
  `oac-test-forensics`.
- `rules/` — `architecture-principles.md` (P1–P7, paths-gated to `**/*.ts(x)`), `test-quality.md`
  (paths-gated to `**/*.test.*` / `**/*.spec.*`), plus symlinks to the top-level canonical
  `engineering-discipline.md` and `preferences.md`.
- `commands/` — `_oac-jira-status-automation.md`: the per-project issue-tracker adaptation point
  (the `tracker-sync?` role). Rewrite for your tracker, or delete if you have none.

The generic process commands live in [../sflow/commands/](../sflow/commands/) and are invoked
as `/sf-*`; the workflow phase machines live in [../sflow/workflows/](../sflow/workflows/).
