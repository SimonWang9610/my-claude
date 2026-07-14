# clarify

```yaml
skills:
  - /spec-clarify
  - /build-acceptance-criteria
prompt: >
  run /spec-clarify using /build-acceptance-criteria to resolve the open questions in
  requirements.md
inputs: requirements.md, ?references/*
outputs: clarify.md
gate: human
exitWhen: >
  every open question in requirements.md is resolved or re-recorded; each untestable AC is rephrased
  to observable form
```
