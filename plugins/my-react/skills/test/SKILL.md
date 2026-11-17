---
name: test
description: >-
  Use this skill when writing or fixing tests for React and TypeScript code: "write tests for this
  component or hook", "an acceptance test for this screen", "a journey test", "this test is
  flaky", with Vitest, React Testing Library, MSW and user-event. Gives the rules for the harness
  per kind of unit, mocking at the boundary, async discipline, journey tests over the mounted app,
  and what makes a green test honest. Knowledge only: it runs no process (with my-workflow, the
  spec-tester and spec-implementer agents do). Not for the code under test (use
  my-react:implement).
---

# test

React testing rules. Which behaviour to test comes from the task; these are the rules for how.

- A test drives a unit through its **test seam** and asserts the **states its contract exposes**
  (the design names both; see `my-react:design`). A test that cannot be written that way is a
  design finding: raise it as a gap, never work around it.
- **Pick the level by the surface.** Behaviour a user sees on a screen or across a flow → a
  journey test over the mounted app. A unit's own behaviour → a unit test through its seam.
- **Name a test by the behaviour it proves.**
- A failing test is fixed in the code, never by weakening the test.

## Rules

| Card | Read when |
|---|---|
| [unit-testing.md](./rules/unit-testing.md) | a component, hook, store or service test: the harness per seam, mocking at the boundary, async, leaks |
| [journey-testing.md](./rules/journey-testing.md) | an acceptance or end-to-end test of a screen or flow |
| [test-quality.md](./rules/test-quality.md) | every test: assertions, fixtures, the mutation litmus |
