# flutter — sflow Flutter profile

This is the **Flutter profile** of the unified sflow bundle. See [../sflow/README.md](../sflow/README.md) for the full process documentation.

**Stack:** Flutter/Dart. State-management-package agnostic — core rules cover four-layer architecture,
SSOT, sealed async, and disposal. Package-specific idioms (Riverpod, Bloc, Provider…) live in a
dedicated package skill loaded by the driver agent.

This profile provides:

- `agents/` — the orchestrators: `fl-{feature,brownfield,bugfix,quickfix}-workflow.md`. Each driver
  starts via `/sf-workflow-startup flutter <variant>` (which binds through `/pick-flutter-workflow`),
  drives the phases, enforces the gates, and delegates phase work to subagents.
- The profile's **binding skill** lives at the repo root: [`../skills/pick-flutter-workflow`](../skills/pick-flutter-workflow/SKILL.md)
  — it converts a workflow template's capability roles into concrete `fl-*` skills (appending
  `/fl-riverpod` when Riverpod is in `pubspec.yaml`, resolving design-link / legacy-port
  conditionals, marking unbound roles) plus the Flutter stage notes, reading the templates from
  the sibling `../sflow/workflows/`.
- `skills/` — `fl-acceptance-criteria`, `fl-architecture-design` (owns the rule corpus + runs the
  verifiable-unit gate at phase exit — design-time authoring and verification in one skill),
  `fl-pr-review`, `fl-riverpod`, `fl-test-contract`, `fl-test-forensics`.
- `rules/` — `architecture-principles.md` (P1–P8, four-layer model, paths-gated to `**/*.dart`),
  `test-quality.md` (paths-gated to `*_test.dart`), plus symlinks to the top-level canonical
  `engineering-discipline.md` and `preferences.md`.

The Flutter profile has no `commands/` subdir. The generic process commands live in
[../sflow/commands/](../sflow/commands/) and are invoked as `/sf-*`; the workflow phase
machines live in [../sflow/workflows/](../sflow/workflows/).
