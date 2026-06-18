---
name: oac-test-contract
description: >
  Authoring-time quality gate for React/TypeScript tests using Vitest and React
  Testing Library. Enforces six rules before any test task is marked complete:
  AC/NFR traceability in describe/it labels, outcome-over-implementation
  assertions, production-typed fixtures with satisfies, no tautologies or
  missing expects, real QueryClientProvider for TanStack Query v5 config NFRs,
  and CI-resident guards for pattern-ban NFRs. Trigger on every new or edited
  test file — whether writing from scratch, updating an existing suite, or
  deciding whether a task may be closed.
---

# oac-test-contract

A forward test-quality contract: six rules a new or edited test file must satisfy before the task that produced it can be marked complete. It front-loads failure-mode classes that retroactive QA would catch later — it does not replace QA.

## When to use

Apply when authoring or auditing tests for acceptance criteria or NFRs — whether writing a new test file, editing an existing one, or reviewing whether a task may be marked done. Not coupled to any specific command or stage.

## Instructions

Walk all six rules in order for every new or modified test file. All six must pass; any FAIL is blocking. For rule detail, rationale, and before→after examples, read `references/rules.md`.

**Rule 1 — Clause→test mapping.**
Every `describe`/`it` string names the AC or NFR ID it covers. A green suite with unmapped tests is not a pass for the ACs those tests could cover. → `references/rules.md §1`

**Rule 2 — Outcome, not implementation.**
Assert rendered text, accessible role/state, or returned value. `toHaveBeenCalled` alone is acceptable only for side effects with no DOM representation, and even then a user-visible assertion must accompany it. → `references/rules.md §2`

**Rule 3 — Production-shaped fixtures.**
Every fixture or stub is typed with `satisfies <ProdType>` or returned by a typed MSW handler. A shape mismatch must be a compile error. → `references/rules.md §3`

**Rule 4 — No tautologies; no arrange-act-no-assert.**
Every test must be able to FAIL: at least one `expect()` exercises a path that differs under different input; no assertion is a mathematical identity over the test's own input; behavior ACs perform an action before asserting. → `references/rules.md §4`

**Rule 5 — Real QueryClient for query-config NFRs.**
Any NFR naming a TanStack Query config value (`staleTime`, `gcTime`, `retry`, `refetchOnWindowFocus`, …) must be asserted inside a real `QueryClientProvider`. Mocking the hook bypasses the config. → `references/rules.md §5`

**Rule 6 — One-shot greps become enduring CI guards.**
Any "no occurrences of X in source" NFR must become a checked-in Vitest assertion (glob + `expect`) or an ESLint rule — not a manual grep at PR review. → `references/rules.md §6`

## References

- `references/rules.md` — per-rule checkable statement, anti-pattern prevented, before→after example, and check step. Read when applying or explaining any rule.
- `references/sources.md` — external links grouped by rule. Cite when justifying a rule.
