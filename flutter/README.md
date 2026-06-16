# flutter — specflow Flutter profile

This is the **Flutter profile** of the unified specflow bundle. See [../specflow/README.md](../specflow/README.md) for the full process documentation.

**Stack:** Flutter/Dart. State-management-package agnostic — core rules cover four-layer architecture,
SSOT, sealed async, and disposal. Package-specific idioms (Riverpod, Bloc, Provider…) live in a
dedicated package skill loaded by the driver agent.

This profile provides:

- `agents/` — the binding layer: `fl-{feature,brownfield,bugfix,quickfix}-workflow.md`. Each driver
  loads the skills below, applies the rules, and binds the 12 generic `/spec-*` stage commands to
  concrete `fl-*` skills. The feature driver also loads the `fl-riverpod` skill when Riverpod is
  detected in `pubspec.yaml`.
- `skills/` — `fl-acceptance-criteria`, `fl-architecture-design` (owns the rule corpus + runs the
  verifiable-unit gate at phase exit — design-time authoring and verification in one skill),
  `fl-pr-review`, `fl-riverpod`, `fl-test-contract`, `fl-test-forensics`.
- `rules/` — `architecture-principles.md` (P1–P8, four-layer model, paths-gated to `**/*.dart`),
  `test-quality.md` (paths-gated to `*_test.dart`), plus symlinks to the top-level canonical
  `engineering-discipline.md` and `preferences.md`.

The Flutter profile has no `commands/` subdir. The generic process commands live in
[../specflow/commands/](../specflow/commands/) and are invoked as `/spec-*`.
