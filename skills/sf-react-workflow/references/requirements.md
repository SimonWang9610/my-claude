# requirements

```yaml
skills:
  - /sf-requirements
  - /build-acceptance-criteria
prompt: >
  run /sf-requirements using /build-acceptance-criteria to author requirements.md from the given
  inputs; record any unresolved question under `## Open questions` rather than guessing
inputs: ?preflight.md, ?analysis.md, ?references/*
outputs: requirements.md
gate: human
exitWhen: >
  Glossary + EARS FRs present; every US/AC/NFR carries a stable unique ID in observable
  Given/When/Then form; unresolved questions recorded under `## Open questions`
```
