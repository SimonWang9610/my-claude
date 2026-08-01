# my-flutter — Flutter/Dart spec-driven skills (⚠️ work in progress — incomplete)

The **Flutter profile** of the my-claude marketplace, packaged as a self-contained Claude Code
plugin. Installs independently of `my-react`.

**Stack:** Flutter/Dart. State-management-package agnostic — core rules cover four-layer
architecture, SSOT, sealed async, and disposal; Riverpod idioms live in the dedicated
`riverpod` skill.

## Contents

- `skills/` — `acceptance-criteria`, `design` (owns the rule corpus + the
  verifiable-unit gate), `implement`, `review`, `riverpod`, `tasks`,
  `test-contract`, `test-forensics`. Invoke as `/my-flutter:<skill>`.
- `rules/` — `architecture-principles.md` (P1–P8, four-layer model) and `test-quality.md`.
  These ship inside the plugin; skills that need the rule text Read them from
  `${CLAUDE_PLUGIN_ROOT}/rules/`.

This plugin ships no agents — a Flutter driver agent is not yet built; run the skills directly
or from your own orchestration.

## Install

```
/plugin marketplace add SimonWang9610/my-claude
/plugin install my-flutter@my-claude
```
