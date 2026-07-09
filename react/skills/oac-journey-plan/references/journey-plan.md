# Journey plan & approval gate

The journey plan is the scope contract for E2E authoring. No E2E test, page object, or harness change is written until a human approves it — scope is the human's call, not an inference.

## Format — `qa-journey-plan.md`

One entry per journey, grouped by user story:

```markdown
# Journey Plan: <Feature>

## US-1: <user story>
### J-1: <journey name>
- **ACs covered:** AC-1.1, AC-1.2
- **Type:** create | read | update | delete | navigate
- **Steps:**
  1. <user action>
  2. <user action>
- **Expected outcome:** <observable end state>
- **Error path** (write journeys — create/update/delete): <the failure the automation forces + its observable result>

### J-2: ...

## Journeys NOT automated
- <journey> — <why: manual-only, out of scope, needs a real backend, …>
```

## Approval gate (blocking)

Present the plan and STOP. The reviewer responds with one of:
- `approve` — author tests for every listed journey.
- `revise: <feedback>` — adjust the plan and re-present.
- `skip J-<n>` — drop that journey (move it to "NOT automated").
- `add: <description>` — add a journey, then re-present.

Record who approved and when before authoring anything. Re-present after any `revise`/`add` — approval is on the final plan, not a draft.
