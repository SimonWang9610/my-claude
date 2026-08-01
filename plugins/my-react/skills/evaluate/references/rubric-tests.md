# Tests rubric — axes V · A · D

Binary checks per axis; classes and derivation in [framework.md](./framework.md).
Rule cards: `skills/test/rules/` (unit-testing, test-quality). Scope: the test files in
the caller's scope.

## V — Coverage: every promised behavior has its proving test

| id | class | check | evidence |
|----|-------|-------|----------|
| v1 | cliff | every in-scope AC ID greps to ≥1 test label asserting its observable outcome | grep |
| v2 | core | each contract's exposed states (error · empty · loading · boundary) each have an asserting test | trace |
| v3 | core | every UPDATE/DELETE disposition from § Blast radius is executed — no test still asserts superseded behavior | grep |

## A — Assertion strength: tests fail when the behavior breaks

| id | class | check | evidence |
|----|-------|-------|----------|
| a1 | cliff | each critical test demonstrably fails when its behavior is absent — the recorded red baseline run is the evidence (no baseline provided → outcome `unverifiable`, reported) | command |
| a2 | core | assertions target the AC's observable outcome through the contract seam — user-visible signals, not implementation internals | read |
| a3 | core | a test's pass requires the unit's real logic — fixtures and MSW stubs sit at the boundary, so a stub alone can't satisfy it | read |

## D — Discipline: the suite is trustworthy infrastructure

| id | class | check | evidence |
|----|-------|-------|----------|
| d1 | core | the suite passes deterministically — async awaited, no sleeps, no order dependence | command |
| d2 | core | setup pairs with teardown — no leaked timers, listeners, or global state between tests | read |
| d3 | polish | each case earns its place — distinct behavior per test, no redundant or snapshot-dump cases | read |
