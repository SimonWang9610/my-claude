# design

```yaml
skills:
  - /spec-design
  - /design-react-architecture
prompt: >
  run /spec-design using /design-react-architecture to produce design.md + contracts/*
inputs: requirements.md,  ?preflight.md, ?clarify.md, ?references/*
outputs: design.md, contracts/*
gate: human
exitWhen: >
  one contracts/<unit>.md per MODIFY/NEW unit in the index; every AC/NFR has an AC → Verification
  row; C1–C8 hand-off criteria met (no open CRITICAL; HIGH passed or justified; MEDIUM passed or
  debt-recorded)
```
