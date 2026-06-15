# Authoring journey tests

Runner-abstracted patterns. Read the steering files for the project's E2E runner, harness, and
network-intercept API; this file is the discipline, not the tooling.

## Page object

One page object per feature view. Expose stable locators (prefer role / test-id over text) for every
element the approved journeys touch, and keep selectors here — not inline in tests — so a UI rename
fixes one file. Add missing test-ids to the implementation only with explicit sign-off (a QA stage
must not silently change the code under test).

## Driving the app

Use a harness or route that renders the feature in a known state seeded by params, so a journey starts
deterministically without manual setup. If the feature isn't reachable yet, test through the nearest
consumer and note the gap.

## Happy vs error paths

- **Happy path** — stub the feature's writes to succeed (intercept at the network boundary) and assert
  the user-visible success outcome.
- **Error path** — force the failure (4xx/5xx or abort the request) and assert the user-visible error
  surface. Every write must have at least one error-path journey.
- Track intercepted write requests, so a silently-changed endpoint surfaces as an unmatched intercept
  rather than a falsely-green test.

## Naming & grouping

Group tests by user story (one block per `US-*`); name each test by its `J-<n>` and the ACs it covers,
so a failure names both the journey and the criterion.

## Traceability manifest

After authoring, write a manifest mapping journey → test → AC. It is an auditable coverage deliverable,
not a second approval gate.
