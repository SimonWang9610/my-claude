---
name: review
description: >-
  Use this skill when reviewing React and TypeScript code or its tests: "review this React diff",
  "is this component correct", "why is this slow", "are these tests honest". Gives the React
  checks: a unit keeping its contract, silent failures, state and effect standards, request
  waterfalls, test honesty, and a performance diagnostic that finds the level a cause lives at.
  Knowledge only: the verdict, severity scale and report belong to the reviewer (with
  my-workflow, the spec-code-reviewer agent). Not for writing the fix (use my-react:implement).
---

# review

React review checks. Scope, severity and the report's shape belong to the reviewer; these say what
to look for in React code and how to prove it.

- **Capabilities first** — read `package.json` once; a check for an absent library, or for the
  wrong React or compiler setup, does not apply.
- **A finding cites its rule.** The standard is the cards of the other skills:
  `../design/rules/`, `../implement/rules/`, `../test/rules/`.
- **Executed evidence outranks reading.** Run the named tests, the type-check and the greps before
  judging what cannot be run.
- **Find the level a cause lives at.** A defect the design mandates is a design gap, not a finding
  against the code; one that predates the diff is inherited, not the author's.

## Rules

| Card | Read when |
|---|---|
| [checklist.md](./rules/checklist.md) | every review: run each check that applies |
| [behavior.md](./rules/behavior.md) | the code does what its contract says and fails loudly: silent failures, waterfalls, test honesty, races |
| [quality.md](./rules/quality.md) | state, effect, component and boundary standards; the type-check |
| [performance-check.md](./rules/performance-check.md) | a hot path, a performance limit, a diff touching subscriptions, services or caches, or a reported symptom |
