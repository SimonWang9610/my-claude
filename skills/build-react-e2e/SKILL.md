---
name: build-react-e2e
description: >
  Authors end-to-end journey tests for a React feature from an approved qa-journey-plan.md
  (Vitest + RTL + MSW): one test per approved journey (J-<n>, happy + forced-error paths) plus a
  journey → test → AC traceability manifest. The plan is typically provided; when missing, this
  skill extracts the journeys from the user stories/ACs and STOPS for human approval before
  authoring anything. Use when a feature needs E2E coverage: "write the journey tests", "plan the
  E2E tests", "which flows should be automated".
---

# build-react-e2e

Author E2E journey tests against an **approved plan**. The plan is typically an input; when it's
missing (or unapproved), generate it and gate — the **human approval gate is blocking**: no E2E
test, page object, or harness change is written until a human approves the plan. Scope is the
human's call, not an inference.

**Given:** `qa-journey-plan.md` (typical); when missing, the feature's user stories and ACs
(`requirements.md`, or whatever the caller supplies). Plus `design.md`'s AC → Verification table
when one exists.
**Produce:** one test per approved journey · a journey → test → AC manifest ·
`qa-journey-plan.md` when it had to be generated.

## Instructions

1. **Locate the plan** — `qa-journey-plan.md` provided and carrying an approval record → skip to
   step 4. Provided but **unapproved** → go to step 3. Missing → generate it (step 2).
2. **Plan the journeys** (only when missing) — Extract one `J-<n>` entry per end-to-end flow from
   the user stories and ACs, grouped by `US-<n>`, in the plan format below. Coverage rules:
   - every user story has ≥1 journey;
   - every **write** journey (create/update/delete) has an error-path counterpart — the failure
     the automation will force, with its observable result;
   - an AC covered by no journey goes under **Journeys NOT automated** with a reason — never
     silently dropped.
3. **Approval gate (blocking)** — Present the plan and STOP. The reviewer answers:
   `approve` · `revise: <feedback>` (adjust, re-present) · `skip J-<n>` (move to NOT automated) ·
   `add: <description>` (add, re-present). Approval is on the **final** plan — record who approved
   and when in the plan's `## Approval` section. The approved plan is the scope contract: one test
   per listed journey, nothing else.
4. **Author the tests** — Follow [authoring.md](./authoring.md): harness + page object first, then
   one test per approved journey, grouped by user story, named by its `J-<n>` and the ACs it
   covers. A journey that proves unautomatable during authoring goes **back to the human** —
   never silently dropped.
5. **Write the manifest** — journey → test file → AC IDs, so coverage is auditable (a deliverable,
   not a second gate). When the feature has a `design.md`, also append each journey to its
   AC → Verification table as a row (`level: journey · location: <test file>`), keeping
   traceability in one place.

## Plan format — `qa-journey-plan.md`

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
- **Error path** (write journeys): <the forced failure + its observable result>

## Journeys NOT automated
- <journey> — <why: manual-only, out of scope, needs a real backend, …>

## Approval
- Approved by <who> on <when> — scope locked to the journeys above.
```
