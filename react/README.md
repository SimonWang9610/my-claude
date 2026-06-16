# react — specflow React profile

This is the **React profile** of the unified specflow bundle. See [../specflow/README.md](../specflow/README.md) for the full process documentation.

**Stack:** React 19 + Vite + TypeScript + Zustand + TanStack Query + MUI + Vitest.

This profile provides:

- `agents/` — the binding layer: `oac-{feature,brownfield,bugfix,quickfix}-workflow.md`. Each driver
  loads the skills below, applies the rules, and binds the 12 generic `/spec-*` stage commands to
  concrete `oac-*` skills.
- `skills/` — `oac-acceptance-criteria`, `oac-architecture-design` (owns the full rule corpus +
  runs the verifiable-unit gate at phase exit — design-time authoring and verification in one
  skill), `oac-figma-decompose`, `oac-journey-tests`, `oac-qa-report`, `oac-test-contract`,
  `oac-test-forensics`.
- `rules/` — `architecture-principles.md` (P1–P7, paths-gated to `**/*.ts(x)`), `test-quality.md`
  (paths-gated to `**/*.test.*` / `**/*.spec.*`), plus symlinks to the top-level canonical
  `engineering-discipline.md` and `preferences.md`.
- `commands/` — `_oac-jira-status-automation.md`: the per-project issue-tracker adaptation point.
  Rewrite for your tracker, or delete if you have none.

The generic process commands live in [../specflow/commands/](../specflow/commands/) and are invoked
as `/spec-*`.
