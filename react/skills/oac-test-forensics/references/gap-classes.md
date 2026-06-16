# The three gap classes — detection procedure

Three recurring classes of how React/TS tests pass while behavior is broken. They overlap — a surface can
exhibit all three simultaneously — so naming the class matters because each maps to a different fix.

---

## Pass 1 — `no-spec-coverage`

**Definition.** The code exhibits a behavior with no governing criterion, OR a criterion exists with zero
mapped tests. The behavior is trivially reversible by a later edit with no failing test.

### Procedure

1. Build the behavior inventory for each owned surface (see `react-ts-heuristics.md` §"Behavior enumeration"):
   - **component** — each prop that changes output; each exposed handler (`onX`); each conditional render
     branch (loading / empty / error / success / permission-gated).
   - **hook** — each returned value/callback; each side-effect path (`useEffect`, query, mutation, subscription).
   - **api/lib** — each exported function's observable contract, including error/fallback branches.
2. Map each behavior to a governing criterion. Find a criterion ID (`AC-<story>.<n>` / `NFR-<n>`) whose
   Given/When/Then covers it. A behavior with no criterion owner is **improvised** → finding.
3. Map each criterion to a test. Grep test files for the criterion ID (`describe('AC-1.2 …')`,
   `it('… AC-1.2 …')`, `tags: ['AC-1.2']`). Zero hits → **uncovered clause** → finding.
4. If a spec has no test files touched at all, the whole spec is outstanding test debt → finding at spec level.

### Finding format

```
NO-SPEC-COVERAGE (improvised): <surface> exhibits "<behavior>" with no governing criterion.
  Confidence: <high|medium|low>
  Resolution: add a criterion to requirements.md and an outcome-asserting test (Rule 1),
  OR remove the behavior as out-of-scope.

NO-SPEC-COVERAGE (uncovered clause): <criterion-id> has 0 mapped tests in <test-dir>.
  Resolution: add a test naming <criterion-id> that asserts its observable outcome.
```

---

## Pass 2 — `tests-pass-but-miss-behavior`

**Definition.** A green test whose name describes a behavior but whose body asserts a weaker proxy. The
named behavior is unverified. This is typically the dominant class in a suite.

### Procedure

For each criterion-mapped test:

1. Read the test name as a behavioral claim (e.g. "calls onSort with the column id").
2. Find the assertion that would prove that claim, and check that the test performs the triggering action
   before asserting. See `react-ts-heuristics.md` §"Pass 2 shapes" for recurring React/TS shapes.
3. Classify the gap:
   - *no action performed* — renders and asserts presence; the criterion's behavior (click, submit, toggle) never fires.
   - *wrong assertion depth* — asserts a structural proxy or the wrong owner (Zustand store vs TanStack cache).
   - *mock declared, never called* — a `vi.fn()` is set up but the action that would call it never triggers.

### Finding format

```
MISS-BEHAVIOR: <test-file>:<line> "<test-name>" names "<behavior>" but asserts "<proxy>";
the named action is never <fired|exercised>.
  Confidence: <high|medium|low>
  Resolution (Rule 2): fire the action, then assert the observable outcome — rendered text,
  accessible role/state, returned value, or the authoritative owner's value.
```

---

## Pass 3 — `false-positive`

**Definition.** A test that passes regardless of whether the code works — it exercises nothing that could
break it. Five recurring React/TS forms.

### Procedure

For each criterion-mapped test, scan for on-sight signals (`false-positive-signals.md`), then apply the
mutation mindset: invert/delete the production branch the test claims to cover; if the test still passes,
it is a false positive. Grep/read recipes for each form are in `react-ts-heuristics.md` §"Pass 3 forms".

- **Form 1 — Tautology / arrange-act-no-assert.** `expect()` asserts a value the test supplied, or no
  `expect()` at all.
- **Form 2 — Mock-shape drift.** Hand-rolled fixture shape differs from the production TS type; a branch
  on an omitted field never runs.
- **Form 3 — Un-awaited write hidden by `mockResolvedValue`.** Always-resolving mock hides a missing
  `await`; the failure path is never reached.
- **Form 4 — CSS-class presence instead of resolved value.** JSDOM cannot resolve CSS custom properties;
  class presence never verifies the rendered color/contrast.
- **Form 5 — Query-config never exercised.** A `staleTime`/`refetch*`/`retry` NFR "tested" via a
  module-level hook mock that bypasses the `QueryClient` config entirely.

### Finding format

```
FALSE-POSITIVE (form <1-5>): <test-file>:<line> "<test-name>" passes even when <mutation/drift>.
<criterion-id> has no real verification.
  Confidence: <high|medium|low>   Severity: Critical when mapped to a criterion.
  Resolution: form 1 → Rule 4; form 2/3 → Rule 3; form 4 → Rule 2; form 5 → Rule 5.
```

---

## Reporting

Emit one table per surface:

```
| Class | Surface / Test | Behavior / Criterion | Confidence | Severity | Contract rule | Resolution |
|-------|----------------|----------------------|------------|----------|---------------|------------|
```

Block on any **high** or **medium** finding; surface **low** as advisory. A false positive mapped to a
criterion is always **Critical**.

---

## Confidence calibration

| Confidence | When to assign |
|---|---|
| **high** | Mechanically verifiable: no `expect()`, confirmed mutation leaves test green, fixture fails `satisfies <ProdType>`, criterion has zero grep hits in test files. |
| **medium** | Strong structural signal but runtime outcome depends on data/config not executed: fixture looks short vs prod type but branch not confirmed; `waitFor` suspected to mask timing. |
| **low** | A hunch worth recording but not blocking: test name reads like a proxy but body not fully traced; possible lifecycle gap. |
