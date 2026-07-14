# spec-qa

```yaml
skills:
  - /spec-qa
  - /spec-validate
  - /build-react-e2e   # if E2E coverage is wanted or qa-journey-plan.md is present
prompt: >
  run /spec-qa using /spec-validate first and report its results in chat; produce
  qa-report.md
inputs: requirements.md, design.md, tasks.md, ?test-manifest.md, code diff
outputs: qa-report.md
gate: human
exitWhen: >
  /spec-validate PASSES; findings dispositioned by the reviewer (sign-off); suite green via a single
  eslint + vitest run
```
