---
name: fl-test-contract
description: >
  Six-rule authoring-time test-quality contract for Flutter/Dart tests. Blocks the
  anti-patterns that retroactive review catches later: missing criterion-to-test
  traceability, implementation-detail assertions, hand-written map fixtures, tautologies,
  bypassed async machinery, and transient grep enforcement.
---

# fl-test-contract

A forward test-quality contract: six core rules (plus four targeted assertion rules) a new or edited test file must satisfy before the task that produced it can be marked complete. It front-loads failure-mode classes that retroactive QA would catch later — it does not replace QA.

## When to use

Apply when authoring or auditing tests for acceptance criteria or NFRs in a Flutter/Dart project — whether writing a new test file, editing an existing one, or reviewing whether a task may be marked done. Not coupled to any specific command or stage.

## Instructions

Walk all rules in order for every new or modified test file. All must pass; any FAIL is blocking. For terse rule statements, wrong→right notes, and check steps, read `references/rules.md`.

**Rule 1 — Observable outcomes, not implementation.**
Assert rendered UI state (`find.text`, `find.byType`, enabled/disabled, visible/absent). `verify(...)` only for fire-and-forget side effects with no other observable. → `references/rules.md §1`

**Rule 2 — Clause→test mapping.**
Every `group(...)` names the AC or NFR ID it covers. A green suite with unmapped tests is not a PASS for those ACs. → `references/rules.md §2`

**Rule 3 — Production-shaped fixtures.**
Fixtures use the real domain constructor or `freezed` `.copyWith(...)` — no loose `Map<String,dynamic>`. Shape mismatch must be a compile error. → `references/rules.md §3`

**Rule 4 — No tautologies; prefer fakes over mocks.**
Don't assert a mock returns what you stubbed. Use an in-memory fake so real logic is exercised. `mocktail` is the default; `verify` only for side effects. → `references/rules.md §4`

**Rule 5 — Real async/stream machinery for async ACs.**
Use `expectLater(..., emitsInOrder([...]))` and `fakeAsync`/`elapse`. No `Future.delayed`; no `pumpAndSettle()` with live network or infinite timers — use `pump(Duration)`. → `references/rules.md §5`

**Rule 6 — One-shot greps become enduring CI guards.**
Any "no occurrences of X" NFR must have a checked-in test or `analysis_options.yaml` entry — not just a PR-review grep. → `references/rules.md §6`

**Additional assertion rules** (see `references/rules.md §7–§10`):
- §7 Dual-assert for service tests — return value AND specific endpoint + args.
- §8 Three-assert for state-holder/cache command tests — state + emit count + collaborator call.
- §9 Negative equality per field for model tests — each field change must break equality.
- §10 Error path is a first-class test — fix swallowed errors in production, not in the test.

## References

- `references/rules.md` — terse rule statements, wrong→right notes, and check steps for all ten rules.
- `references/sources.md` — external links grouped by rule. Cite when justifying a rule.
