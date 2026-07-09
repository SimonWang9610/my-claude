---
name: oac-test-contract
description: >
  Authoring-time quality gate for React/TS tests (Vitest + RTL + MSW): makes every test able to
  fail for the right reason via six blocking rules — AC/NFR IDs in describe/it labels, observable-
  outcome assertions (not toHaveBeenCalled), production-typed fixtures, no tautologies, a real
  QueryClientProvider for query-config NFRs, and CI-resident guards for pattern-ban NFRs. Use while
  writing or editing any test file. Prevention half; the audit counterpart is oac-test-forensics.
---

# oac-test-contract

These six rules make a test worth having *while it is being written* — each closes a way a
green test can lie. The detection half, auditing an existing suite for the damage these rules
prevent, is `oac-test-forensics`; its signal catalogue maps every finding back to the rule that
fixes it.

## Inputs (caller-supplied)

- The test file(s) being written or edited.
- The unit under test (component / hook / store / query) and its contract.
- The AC/NFR IDs that unit must satisfy — the clauses each test must trace to.

## Procedure

Walk all six rules in order over every new or modified test file. **Every rule must pass; any
FAIL is blocking** — the test task is not complete until all six hold. Open `references/rules.md`
for each rule's before→after example and check step; cite `references/sources.md` when a rule is
challenged.

| # | Rule | FAIL when |
|---|------|-----------|
| 1 | **Clause→test mapping** — every `describe`/`it` label embeds the AC/NFR ID it covers, verbatim, so `grep -r "AC-2.1" src/` returns the test and its unit. | A behavior under test has no label carrying its AC/NFR ID; coverage is un-greppable. → `rules.md §1` |
| 2 | **Outcome, not implementation** — assert rendered text, accessible role/state, navigation, visible toast, or returned value. Drive interaction with `userEvent.setup()` + `await user.*`. | `toHaveBeenCalled`/`toHaveBeenCalledWith` is the only assertion for a behavior that renders something. → `rules.md §2` |
| 3 | **Production-typed fixtures** — every fixture is `satisfies <ProdType>`; every MSW handler is typed with the production `ApiResponse<T>`. | A bare inline literal that adding a required field to the prod type would *not* break at compile time. → `rules.md §3` |
| 4 | **No tautology, no arrange-act-no-assert** — each test can fail: ≥1 `expect` exercises an input-dependent path; behavior ACs act before asserting. | An `it`/`test` with no `expect`, or an assertion that is an identity over the test's own input. → `rules.md §4` |
| 5 | **Real QueryClient for query-config NFRs** — any NFR naming `staleTime`/`gcTime`/`retry`/`refetchOnWindowFocus`/`enabled`/… is asserted inside a real `QueryClientProvider`. | The query hook is mocked, so the config value the NFR specifies is never exercised. → `rules.md §5` |
| 6 | **One-shot greps become CI guards** — any "no occurrences of X in source" NFR becomes a checked-in Vitest glob assertion or an ESLint rule. | Enforcement is only a manual PR-review grep that vanishes after merge. → `rules.md §6` |

Apply the mutation mindset as the cross-cutting test of every assertion: *if I invert this
condition in the production code, does this test fail?* If not, the assertion is a proxy or a
tautology — Rules 2 and 4 catch it.

## References

- `references/rules.md` — per rule: checkable statement, anti-pattern prevented, before→after
  example, and the check step. Open when applying or explaining any rule.
- `references/sources.md` — external links grouped by rule. Cite when a rule is questioned.
