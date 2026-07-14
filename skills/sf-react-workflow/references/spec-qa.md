# spec-qa

```yaml
skills:
  - /sf-qa
  - /sf-validate
  - /build-react-e2e   # if E2E coverage is wanted
prompt: >
  run /sf-qa using /sf-validate first and report its results in chat; if E2E coverage is wanted,
  author the journey tests with /build-react-e2e before the audit — it consumes the approved
  qa-journey-plan.md when present, otherwise generates one and stops for approval; produce
  qa-report.md
inputs: requirements.md, design.md, tasks.md, ?test-manifest.md, code diff
outputs: qa-report.md
gate: human
exitWhen: >
  /sf-validate PASSES; findings dispositioned by the reviewer (sign-off); suite green via a single
  eslint + vitest run
```
