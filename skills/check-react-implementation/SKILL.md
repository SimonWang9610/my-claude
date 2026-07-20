---
name: check-react-implementation
description: >
  Checks a React diff with fresh eyes on three axes — does it observably satisfy its ACs
  and contracts, what will it cost the next change, and what does it cost at runtime —
  returning severity-classified findings with evidence, never fixes. Use after
  implementation to verify work against its contracts, or on demand to audit a diff for
  conformance, maintainability, or performance and memory problems.
---

# check-react-implementation

Findings, not fixes. The checker reads the diff with fresh eyes — never the author's
context — and returns evidence-carrying findings; fixing belongs to the implementer,
re-checking to the caller. One pass per invocation: bounded, never a standing loop.

## Inputs

- **Diff scope** — the changed files (task, wave, or phase), commit-scoped by the caller.
- **Contracts + design.md + traced ACs** — the authority the diff is checked against.

## Checks — three axes, in order, severity first

Behavior, then quality, then runtime cost — code that merely looks correct passes
nothing. Stop collecting advisory findings once the list passes ~12 — the top severities
must stay visible.

1. **Behavior & outcomes** — does the diff do what the requirements say, observably?
   - Each traced AC's named test asserts the AC's observable outcome (run or trace it),
     not a proxy of it.
   - Public API name-for-name, type-for-type — no undeclared props, no widened optionals.
   - Every promised state reachable through the public surface; unhappy cases (error ·
     empty · boundary) behave as contracted — no silent catch, no masking fallback.
   - Stated constraints (must-nots) hold — verify by grep; MODIFY units' listed importers
     unbroken.
   - A deviation with no recorded DESIGN GAP → **CRITICAL** (dishonest divergence).
2. **Quality & maintainability** — what does the diff cost the next change?
   - Family rulebooks, citing the rule file in each finding:
     `design-react-contracts/rules/` (ownership, decomposition, boundaries) ·
     `implement-react-contracts/rules/` (hooks, components, stores/services).
     Correctness outranks style. Capabilities gate citations — package.json read once;
     a rule for an absent library or the wrong react/compiler setup is never cited.
   - Reuse honored — no second unit/type/query key/store slice duplicating an existing one.
   - Seams intact — unit testable through its contract's Test seam, not only via its
     host; no implementation detail leaked into the public surface.
   - Scope surgical — only what the task requires; unrelated edits, drive-by refactors,
     and new dead code are findings.
3. **Performance & memory** — what does the diff cost at runtime? Run
   [rules/performance-check.md](./rules/performance-check.md) for hot paths, perf NFRs,
   or diffs touching subscriptions/services/caches. Route each cause: implementation-level
   → a finding with its fix direction; design-level → a DESIGN GAP finding with the
   measurement as evidence.

## Finding format

```markdown
FINDING — <CRITICAL | HIGH | MEDIUM | LOW> · <file:line> · <unit>
Rule/contract: <cite> · Evidence: <one line — grep hit, type error, measurement>
Fix direction: <one line — direction, never a patch>
```

## Output

Findings most-severe first, then one line: `checked <n> units × <checks run>`, plus a
tally for anything dropped — `suppressed: <n> (<source: advisory cap · caller scope ·
capability gate>)` — so a clean report means clean, never quietly filtered. No findings
and no drops → the one line alone. Never edit files; never restate unchanged code.
