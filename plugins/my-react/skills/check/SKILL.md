---
name: check
description: >
  Checks a React diff with fresh eyes on three axes — does it observably satisfy its ACs
  and contracts, what will it cost the next change, and what does it cost at runtime — and
  re-derives the author's scorecard as a constrained verifier (a delta that crosses a
  verdict boundary is a finding). A design mode re-scores design.md + contracts before any code exists. Use after
  implementation to verify work against its contracts, before the design gate for a
  fresh-eyes design re-score, or on demand to audit a diff. Not for a pre-merge PR
  review that gates the merge (use my-react:review) or building the atlas (use
  my-react:audit). Output: severity-classified findings + a scorecard delta, never fixes.
---

# check

Findings, not fixes. The checker reads the diff with fresh eyes — never the author's
context — and returns evidence-carrying findings; fixing belongs to the implementer,
re-checking to the caller. One pass per invocation: bounded, never a standing loop.

Two modes: **diff mode** (default — the three axes below, then the scorecard re-score)
and **design mode** (no code yet — re-score `design.md` + `contracts/` +
`design-scorecard.md` per § Scorecard re-score alone; a fresh-eyes pass before the
design gate).

## Inputs

- **Diff scope** — the changed files (task, wave, or phase), commit-scoped by the caller.
  Absent → design mode.
- **Contracts + design.md + traced ACs** — the authority the diff is checked against.
- **Scorecards** — `design-scorecard.md` / `impl-scorecard.md` when they exist; the
  author's claims to verify. Missing scorecard → re-score from scratch and say so.

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
   - design.md § Blast radius dispositions executed — an UPDATE-flagged existing test
     still asserting the superseded behavior, or a KEEP test broken, is a finding.
   - A deviation with no recorded DESIGN GAP → **CRITICAL** (dishonest divergence).
2. **Quality & maintainability** — what does the diff cost the next change?
   - Family rulebooks, citing the rule file in each finding:
     `${CLAUDE_PLUGIN_ROOT}/skills/design/rules/` (ownership, decomposition, boundaries) ·
     `${CLAUDE_PLUGIN_ROOT}/skills/implement/rules/` (hooks, components, stores/services).
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

## Scorecard re-score — constrained verifier, same pass

Re-derive the author's scorecard per the **re-score protocol** in
`${CLAUDE_PLUGIN_ROOT}/skills/design/references/scorecard.md` (design axes G·F·S·T·B;
impl axes C·S·R·H in `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/scorecard.md`).
Not a second sweep: each checklist outcome above doubles as its matching anchor's
outcome (axis 1 ≈ C anchors, axis 2 ≈ S/H, axis 3 ≈ R) — one derivation over the whole
diff scope feeds findings and axis scores alike. The protocol owns the delta rules
(verdict-boundary crossings, evidence-shift, cap exemption).

## Finding format

```markdown
FINDING — <CRITICAL | HIGH | MEDIUM | LOW> · <file:line> · <unit>
Rule/contract: <cite> · Evidence: <one line — grep hit, type error, measurement>
Fix direction: <one line — direction, never a patch>
```

## Output

Findings most-severe first, then the scorecard delta table (`axis · author · re-score ·
evidence` — only rows that moved; none moved → `scorecard: concur <verdict>`), then one
line: `checked <n> units × <checks run>`, plus a tally for anything dropped —
`suppressed: <n> (<source: advisory cap · caller scope · capability gate>)` — so a clean
report means clean, never quietly filtered. No findings and no drops → the closing lines
alone. Never edit files; never restate unchanged code.
