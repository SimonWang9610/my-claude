# The three gap classes — detection procedure

Three recurring ways a React/TS suite stays green while behavior is broken. Run the passes in order.
Confirm every grep hit by reading the file — greps only narrow where to look.

---

## Pass 1 — `no-spec-coverage`

**Definition.** Code exhibits a behavior with no governing criterion, OR a criterion exists with zero
mapped tests. Either way the behavior is trivially reversible by a later edit with no failing test.

**Procedure**

1. Build the behavior inventory for each owned surface (see `heuristics-behavior-enumeration.md`):
   - **component** — each prop that changes output; each exposed handler (`onX`); each conditional
     render branch (loading / empty / error / success / permission-gated).
   - **hook** — each returned value/callback; each side-effect path (`useEffect`, query, mutation,
     subscription).
   - **api/lib** — each exported function's observable contract, including error/fallback branches.
2. Map each behavior to a criterion ID (`AC-<story>.<n>` / `NFR-<n>`) whose Given/When/Then covers it.
   A behavior with no owner is **improvised** → finding.
3. Map each criterion to a test. Grep test files for the ID (`describe('AC-1.2 …')`, `it('… AC-1.2 …')`,
   `tags: ['AC-1.2']`). Zero hits → **uncovered clause** → finding.
4. A surface with no tests touched at all is outstanding test debt → one finding at surface level;
   skip Passes 2–3 for it.

**Finding format**

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

**Definition.** A green test whose name describes a behavior but whose body asserts a weaker proxy.
The named behavior is never verified. Usually the dominant class in a suite.

**Procedure** — for each criterion-mapped test:

1. Read the test name as a behavioral claim (e.g. "calls onSort with the column id").
2. Find the assertion that would prove that claim; confirm the test performs the triggering action
   *before* asserting. Recurring React/TS shapes: `heuristics-pass2-shapes.md`.
3. Classify the gap:
   - *no action performed* — renders and asserts presence; the click / submit / toggle never fires.
   - *wrong assertion depth/owner* — asserts a structural proxy, or the wrong owner (Zustand copy vs
     TanStack cache).
   - *mock declared, never called* — a `vi.fn()` is set up but the action that would call it never fires.

**Finding format**

```
MISS-BEHAVIOR: <test-file>:<line> "<test-name>" names "<behavior>" but asserts "<proxy>";
the named action is never <fired|exercised>.
  Confidence: <high|medium|low>
  Resolution (Rule 2): fire the action, then assert the observable outcome — rendered text,
  accessible role/state, returned value, or the authoritative owner's value.
```

---

## Pass 3 — `false-positive`

**Definition.** A test that passes regardless of whether the code works — it exercises nothing that
could break it. Five recurring React/TS forms (`heuristics-pass3-forms.md`).

**Procedure** — for each criterion-mapped test: scan for on-sight signals
(`false-positive-signals.md`), then apply the mutation mindset — invert or delete the production
branch the test claims to cover; if the test still passes, it is a false positive.

| Form | Signature |
|---|---|
| 1 — Tautology / arrange-act-no-assert | `expect()` asserts a value the test supplied, or no `expect()` at all. |
| 2 — Mock-shape drift | hand-rolled fixture shape differs from the production TS type; a branch on an omitted field never runs. |
| 3 — Un-awaited write hidden by `mockResolvedValue` | always-resolving mock hides a missing `await`; the failure path is never reached. |
| 4 — CSS-class instead of resolved value | JSDOM can't resolve CSS custom properties; class presence never verifies rendered color/contrast. |
| 5 — Query-config never exercised | a `staleTime`/`refetch*`/`retry` NFR "tested" via a hook mock that bypasses the `QueryClient` config. |

**Finding format**

```
FALSE-POSITIVE (form <1-5>): <test-file>:<line> "<test-name>" passes even when <mutation/drift>.
<criterion-id> has no real verification.
  Confidence: <high|medium|low>   Severity: Critical when mapped to a criterion.
  Resolution: form 1 → Rule 4; form 2/3 → Rule 3; form 4 → Rule 2 (+Rule 6); form 5 → Rule 5.
```

---

## Reporting

One table per surface:

```
| Class | Surface / Test | Behavior / Criterion | Confidence | Severity | Contract rule | Resolution |
|-------|----------------|----------------------|------------|----------|---------------|------------|
```

Block on any **high** or **medium** finding; surface **low** as advisory. A false positive mapped to a
criterion is always **Critical**.

---

## Confidence calibration

| Confidence | Assign when |
|---|---|
| **high** | Mechanically verifiable: no `expect()`, confirmed mutation leaves the test green, fixture fails `satisfies <ProdType>`, or the criterion has zero grep hits in test files. |
| **medium** | Strong structural signal but the runtime outcome depends on data/config not executed: fixture looks short vs the prod type but the branch is unconfirmed; `waitFor` suspected to mask timing. |
| **low** | A hunch worth recording, not blocking: name reads like a proxy but the body isn't fully traced; a possible lifecycle gap. |
