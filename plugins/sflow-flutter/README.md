# sflow-flutter — Flutter/Dart spec-driven skills

The **Flutter profile** of the my-claude marketplace, packaged as a self-contained Claude Code
plugin. Installs independently of `sflow-react`.

**Stack:** Flutter/Dart. State-management-package agnostic — core rules cover four-layer
architecture, SSOT, sealed async, and disposal; Riverpod idioms live in the dedicated
`fl-riverpod` skill.

## Contents

- `skills/` — `fl-acceptance-criteria`, `fl-architecture-design` (owns the rule corpus + the
  verifiable-unit gate), `fl-implementation`, `fl-pr-review`, `fl-riverpod`, `fl-task-design`,
  `fl-test-contract`, `fl-test-forensics`. Invoke as `/sflow-flutter:<skill>`.
- `rules/` — `architecture-principles.md` (P1–P8, four-layer model) and `test-quality.md`.
  These ship inside the plugin; skills that need the rule text Read them from
  `${CLAUDE_PLUGIN_ROOT}/rules/`.

This plugin ships no agents — a Flutter driver agent is not yet built; run the skills directly
or from your own orchestration.

## Install

```
/plugin marketplace add SimonWang9610/my-claude
/plugin install sflow-flutter@my-claude
```
