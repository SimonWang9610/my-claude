# implement

```yaml
skills:
  - /spec-implement
  - /implement-react-code
  - /build-react-e2e   # if E2E coverage is wanted or qa-journey-plan.md is approved
prompt: >
  run /spec-implement using /implement-react-code to produce code + test-manifest.md; never edit a
  test to make code pass; if E2E coverage is needed, author the journey tests with /build-react-e2e before the audit — it consumes the approved qa-journey-plan.md when present, otherwise generates one and stops for approval;
inputs: tasks.md, contracts/*, ?references/*, ?qa-journey-plan.md
outputs: code, test-manifest.md
gate: human
exitWhen: >
  every task Status → completed with its Gate passing; no test edited to make code pass; design gaps
  resolved or human-dispositioned; test-manifest.md written
```
