# flutter — sflow Flutter profile

This is the **Flutter profile** of the unified sflow bundle. See [../sflow/README.md](../sflow/README.md) for the full process documentation.

**Stack:** Flutter/Dart. State-management-package agnostic — core rules cover four-layer architecture,
SSOT, sealed async, and disposal. Package-specific idioms (Riverpod, Bloc, Provider…) live in a
dedicated package skill loaded by the driver agent.

This profile provides:

- The workflow **generators** are per-stack and currently ship for React only
  (`sf-react-workflow` / `spec-react-workflow`, which bind `oac-*` skills directly to phases). A
  Flutter spec needs a parallel `sf-flutter-workflow` / `spec-flutter-workflow` generator — not
  yet built — that would read the project's vendored specflow templates
  (`specflow/src/workflows/`, with `.specflow/workflows/` as override) and bind the `fl-*` skills
  below directly to each phase (appending `/fl-riverpod` when Riverpod is in `pubspec.yaml`,
  resolving design-link / legacy-port conditionals). Until then this profile ships only its
  `fl-*` skills and rules.
- `skills/` — `fl-acceptance-criteria`, `fl-architecture-design` (owns the rule corpus + runs the
  verifiable-unit gate at phase exit — design-time authoring and verification in one skill),
  `fl-implementation` (Flutter performance and widget-build idioms while coding inside a unit
  behind a fixed contract), `fl-pr-review`, `fl-riverpod`, `fl-task-design` (turns an approved
  design.md + contracts/ into a dependency-ordered tasks.md with a test task per AC),
  `fl-test-contract`, `fl-test-forensics`.
- `rules/` — `architecture-principles.md` (P1–P8, four-layer model, paths-gated to `**/*.dart`),
  `test-quality.md` (paths-gated to `*_test.dart`). The shared `engineering-discipline.md` and
  `preferences.md` live only at the repo root [`../rules/`](../rules/) (real files, not
  mirrored here).

This profile ships no `agents/` — the unified driver agents (`sflow-driver`, `specflow-driver`)
live at the repo root [`../agents/`](../agents/).

The Flutter profile has no `commands/` subdir. The generic process commands live in
[../sflow/commands/](../sflow/commands/) and are invoked as `/sf-*`; the workflow phase
machines come from the project's vendored specflow templates.
