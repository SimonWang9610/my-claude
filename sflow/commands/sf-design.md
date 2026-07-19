---
description: Produce the technical design, per-unit contracts, per-AC test strategy, and the approved QA journey plan.
---
# sf:design

Decide the structure before any code — one contract per unit (module, data model,
API/service) so tasks decompose against real interfaces — and design the verification with
the feature: test strategy, journey plan, and blast radius are authored here, not deferred
to QA. Writes `design.md` + `contracts/` (+ `qa-journey-plan.md` when the spec has
user-facing journeys) under `.specflow/specs/<name>/`. Requires `requirements.md` (run
`/sf-requirements` if missing); optional `clarify.md`, `preflight.md`,
`references/design-units.md`; steering as context; the target repo is read, never written.

**Steps.**

1. **Architecture** — decompose into units with clear responsibilities and interactions,
   data models, error-handling strategy; diagram where it clarifies; every AC lands on a
   unit and a flow.
2. **Reconcile with existing code** — a reuse verdict per touched existing unit; a Shared
   Unit Plan classifying each shared unit Reuse or Copy — never modify an adopted unit;
   reconcile with the design-units map when present.
3. **Contracts** — one `contracts/<unit>.md` per introduced unit: its interface, the
   AC-IDs it traces, its testability seam; `design.md` indexes them, never restates them.
4. **Test strategy** — per AC/NFR a verification level (unit / journey / manual) in a
   `design.md` table, reconciling the requirements-time classification and resolving any
   unclassified AC; name each behavior as a positive + a negative + a boundary; **ask the
   user what failure modes are missing** before finalizing.
5. **Journey plan** — driven by the test strategy: no AC classified journey-level → skip,
   one-line note in `design.md`. Otherwise `qa-journey-plan.md`: per journey-level story a
   happy-path + every error/boundary journey step 4 surfaced (`J-<n>`: precondition ·
   steps with expected outcomes · covers ACs), each entry marked **NEW** or
   **MODIFY <existing test path>** — an existing journey test already covering the
   affected flow is planned as a change, never duplicated — plus a "Journeys NOT
   automated" table with reasons.
6. **Journey approval** — present the plan at design review:
   `approve` · `revise: <feedback>` · `skip J-<n>` · `add: <description>`; incorporate and
   re-present until approved — the file reflects the final approved plan. On approval, add
   an "E2E Surface" note to `design.md`: where journey tests live per project convention,
   one suite per story, one test per `J-<n>` citing its ACs.
7. **Blast radius** — `design.md` section listing the existing tests this change can
   break: reverse-import closure of the changed files → their tests (may legitimately be
   empty — say so). An existing test that must *change* is flagged, never silently planned.
8. **Architecture gate** — ONE pass: every AC covered, no God-unit, no dual source of
   truth, no missing testability seam; PASS or record each justification in `design.md`.

**Exit.** Every `AC-<story#>.<n>` / testable `NFR-<n>` covered by ≥1 contract and one test
strategy row; a `contracts/<unit>.md` per introduced unit with AC trace + testability seam;
`design.md` indexes them + carries the Shared Unit Plan, test strategy, and blast radius;
`qa-journey-plan.md` approved (or its skip noted); architecture gate PASS or every trigger
justified in `design.md`.
