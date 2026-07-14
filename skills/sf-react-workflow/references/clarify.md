# clarify

```yaml
skills:
  - /sf-clarify
  - /build-acceptance-criteria
prompt: >
  run /sf-clarify using /build-acceptance-criteria to resolve the open questions in
  requirements.md, ranked by Impact × Uncertainty; skip the phase when there are none
inputs: requirements.md, ?references/*
outputs: clarify.md
gate: human
exitWhen: >
  every open question in requirements.md is resolved or re-recorded; each untestable AC is rephrased
  to observable form
```
