# analysis

```yaml
skills:
  - /analyze-react
prompt: >
  run /analyze-react to produce analysis.md — bugfix: author a named, deterministic reproduction
  test that FAILS pre-fix;
inputs: ?preflight.md
outputs: analysis.md
gate: human
exitWhen: >
  bugfix — a named, deterministic reproduction test asserts the bug's AC and FAILS pre-fix;
  brownfield — the change surface and shared-unit blast radius are mapped in analysis.md
```
