# False-positive signal catalogue + mutation-test protocol

On-sight signals flag a *suspicion* before you run a mutation; the mutation *confirms* the test cannot
fail. Pair every blocking finding with at least one confirmed mutation or a mechanically-verifiable fact.

---

## On-sight signals

### Assertion-level

- **No `expect()` in the block.** Arrange-act-no-assert. Always a confirmed false positive. *(high)*
- **`expect()` of a value the test supplied.** `getByText(message)` where `message` is the prop passed
  in; `toEqual(input)` against the literal just constructed. A tautology. *(high)*
- **`toBeTruthy()` / `toBeDefined()` on a `getBy*` result.** The `getBy*` already throws if absent; the
  matcher is dead code. *(high)*
- **`toContain` on a single DOM node, `toBe`/`toEqual` on DOM nodes, `>= N` count assertions.** Matcher
  misuse or loose bound; passes through regressions. *(medium → high once confirmed a no-op)*
- **`toHaveClass('bg-…')` for a color/contrast NFR.** JSDOM cannot resolve CSS variables; class
  presence never verifies the rendered color. *(high)*

### Mock / fixture

- **Inline fixture with no `satisfies <ProdType>`.** Free to drift; a branch on an omitted field never
  runs. *(medium; high once you confirm the source branches on the omitted field)*
- **`mockResolvedValue` on a write/mutation path.** Always-resolving mock hides a missing `await`, a
  rejected-write path, and `onError` handling. *(high)*
- **Hand-rolled socket/event payload vs the real wire shape.** Fields differ from the production
  message; the test asserts fields that do not exist in production. *(high)*
- **The whole hook/component under test is mocked.** `vi.mock('…/useFeature')` — the test covers only
  wiring and bypasses the criterion's behavior. *(high)*
- **`vi.mock('@tanstack/react-query')` with a query-config NFR.** `QueryClient` config never
  exercised. *(high)*
- **Test redefines a decoder/parser/mapper that lives in `src/`.** If production drifts, the test stays
  green. *(high)*

### Event-target / wiring

- **Keyboard event fired on a text node** instead of the dialog/backdrop/focused element. Event does
  not bubble as in production; handler wiring unverified. *(high)*
- **Generic mock callback name** (`onSave`) where the criterion distinguishes branches. Cannot tell
  which code path ran. *(medium)*
- **Module-scope singleton not reset between tests** (query-prefix list, registry `Map`, singleton
  client). State leaks across tests; lifecycle untestable without a `_resetForTest()` seam. *(medium;
  high once you show a test passes only because a prior test seeded state)*

### Spec-side

- **Test codifies buggy behavior.** Both code and test encode a mapping the criterion contradicts; the
  test locks the bug in. *(high)*
- **In-file comment admitting a limitation** ("mock lacks X", "TODO: wire to real API"). Written
  admission the test does not test what it claims. *(high)*

---

## The mutation-test protocol (confirmation)

**Mental form** (every criterion-mapped test):

1. Open the production code the test claims to cover; find the deciding branch, `await`, config value,
   or mapping.
2. Mentally invert or delete it: `if (canWrite)` → `if (!canWrite)`; remove the `await`; drop
   `staleTime: Infinity`; flip a status string.
3. Would this test now fail? **No → false positive.**

**Executed form** (high-risk criteria only — security, data integrity, write paths):

```bash
# 1. apply the mutation in the production file (invert/comment the deciding branch)
# 2. run only the mapped test file
vitest run <specific-test-file> --reporter=verbose
# 3. still passes → confirmed false positive (Critical when criterion-mapped)
# 4. REVERT the mutation immediately
```

Keep executed mutations scoped to one file and one mutation; revert before moving on. Record the exact
mutation in the finding so the fix is unambiguous and reproducible. Cap executed mutations at the
high-risk criteria set; for the rest, the mental form plus an on-sight signal is sufficient.

---

## Signal → contract rule

Every finding maps back to the `oac-test-contract` rule that prevents it, so the fix is unambiguous.

| Signal / form | Contract rule |
|---|---|
| No `expect()` / tautology | Rule 4 — every test must be able to fail; act before asserting |
| Proxy assertion (mock-only, class-only, wrong owner) | Rule 2 — assert the observable outcome |
| Fixture drift / un-awaited write under `mockResolvedValue` | Rule 3 — production-shaped fixtures via `satisfies` / typed MSW |
| CSS-class instead of resolved value | Rule 2 (+ Rule 6 — promote to a CI guard) |
| Query-config mocked away | Rule 5 — real `QueryClient` for query-config NFRs |
| Behavior with no criterion | Rule 1 — clause→test mapping |
