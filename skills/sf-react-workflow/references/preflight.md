# preflight

```yaml
skills:
  - /sf-preflight
  - /scan-resource        # if references or resources are given
  - /oac-figma-decompose  # if design links are given
prompt: >
  run /sf-preflight; use /scan-resource if references or resources are given; use
  /oac-figma-decompose if design links are given — record the reuse verdict and shared-unit impact
  in preflight.md
inputs: none
outputs: preflight.md, ?references/*
gate: human
exitWhen: preflight.md records the reuse verdict and shared-unit impact
```
