# analysis

```yaml
skills:
  - /spec-preflight # if brownfield and preflight.md does not exist
  - /analyze-react
prompt: >
  run /analyze-react to produce analysis.md — bugfix: author a named, deterministic reproduction
  test that FAILS pre-fix; brownfield: run /spec-preflight if preflight.md does not exist, then map the change surface and shared-unit blast radius in analysis.md.
inputs: ?preflight.md
outputs: analysis.md
gate: human
exitWhen: >
  bugfix — a named, deterministic reproduction test asserts the bug's AC and FAILS pre-fix;
  brownfield — the change surface and shared-unit blast radius are mapped in analysis.md
```
