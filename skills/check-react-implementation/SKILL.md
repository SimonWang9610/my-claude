---
name: check-react-implementation
description: >
  Post-implementation conformance check for React diffs: verifies changed units against
  their contracts (API, states, constraints), the family rulebooks, and a performance &
  memory diagnostic — emitting severity-classified findings only, never fixes. Use after
  an implement phase completes, or on demand ("check this diff against the contracts").
---

# check-react-implementation

Findings, not fixes. The checker reads the diff with fresh eyes — never the author's
context — and returns evidence-carrying findings; fixing belongs to the implementer,
re-checking to the caller. One pass per invocation: bounded, never a standing loop.

## Inputs

- **Diff scope** — the changed files (task, wave, or phase), commit-scoped by the caller.
- **Contracts + design.md** — the authority the diff is checked against.

## Checks — in order, severity first

Stop collecting advisory findings once the list passes ~12 — the top severities must
stay visible.

1. **Contract conformance** (per changed unit)
   - Public API name-for-name, type-for-type — no undeclared props, no widened optionals.
   - Every promised state reachable and observable; the unit's traced ACs demonstrably
     satisfied.
   - Stated constraints (must-nots) hold — verify by grep; MODIFY units' listed importers
     unbroken.
   - A deviation with no recorded DESIGN GAP → **CRITICAL** (dishonest divergence).
2. **Rule conformance** — audit the diff against the family rulebooks, citing the rule
   file in each finding: `design-react-contracts/rules/` (ownership, decomposition,
   boundaries) · `implement-react-contracts/rules/` (hooks, components, stores/services).
   Correctness outranks style.
3. **Performance & memory** — run
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

Findings most-severe first, then one line: `checked <n> units × <checks run>`. No
findings → that one line alone. Never edit files; never restate unchanged code.
