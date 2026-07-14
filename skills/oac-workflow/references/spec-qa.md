# spec-qa

```yaml
skills:
  - /spec-qa
  - /spec-validate
  - /build-react-e2e   # if E2E coverage is wanted or qa-journey-plan.md is present
prompt: >
  run /spec-qa using /spec-validate first and report its results in chat; if E2E coverage is needed,
  author the journey tests with /build-react-e2e before the audit — it consumes the approved
  qa-journey-plan.md when present, otherwise generates one and stops for approval; produce
  qa-report.md
inputs: requirements.md, design.md, tasks.md, ?test-manifest.md, code diff, ?qa-journey-plan.md
outputs: qa-report.md
gate: human
exitWhen: >
  /spec-validate PASSES; findings dispositioned by the reviewer (sign-off); suite green via a single
  eslint + vitest run
```
