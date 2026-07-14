# implement

```yaml
skills:
  - /sf-implement
  - /implement-react-code
prompt: >
  run /sf-implement using /implement-react-code to produce code + test-manifest.md; never edit a
  test to make code pass
inputs: tasks.md, contracts/*, ?references/*
outputs: code, test-manifest.md
gate: human
exitWhen: >
  every task Status → completed with its Gate passing; no test edited to make code pass; design gaps
  resolved or human-dispositioned; test-manifest.md written
```
