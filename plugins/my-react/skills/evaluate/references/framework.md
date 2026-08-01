# Evaluation framework — scale, verdict, report, foundation signal

Stated once; every rubric and report uses these definitions.

## Checks → scores → verdict

A **check** is binary and evidence-typed: it names what to verify, the evidence form
that settles it (grep hit · command output · path:line · ID trace), and its class:

- **cliff** — failing it makes the work unusable or dishonest.
- **core** — failing it costs correctness, the next change, or runtime.
- **polish** — failing it costs clarity; never blocks.

Axis score is derived, never judged: `4` all checks pass · `3` only polish failures ·
`2` one core failure · `1` two+ core failures · `0` any cliff failure.

Verdict from axis minima: **PASS** all axes ≥3 · **CONDITIONAL** lowest axis = 2 (each
core failure listed as a finding the gate decides) · **BLOCK** any axis ≤1.

**Disclosure scores clean.** A routed ASSUMED mark, a ledgered inherited defect, a
raised DESIGN GAP is compliant behavior — checks fail on the silent version only.

## Finding format — one shape for every failed check

```
FINDING — <CRITICAL|HIGH|MEDIUM|LOW> · <check id> · <file:line or artifact §>
Evidence: <one line, in the check's evidence form>
Fix direction: <one line — direction, never a patch> | DESIGN GAP | foundation item
```

Severity: cliff → CRITICAL · core → HIGH (MEDIUM when contained to one unit) ·
polish → LOW. Cap LOW findings so the top severities stay visible; tally what the cap
drops (`suppressed: <n>`).

## Report template — `evaluation-<mode>.md`

```markdown
# Evaluation — <mode> · <spec/scope> · <verdict>

| Axis | Score /4 | Failed checks |
|------|----------|---------------|

<findings, most severe first>

## Foundation (design mode only)
<signal per ledgered defect — see below>

checked: <n> units × <m> checks · suppressed: <n>
```

No findings and nothing suppressed → the header + axis table + closing line only.

## Foundation signal — when refactoring the blast radius is worth it

Design mode reads the inherited-defect ledger and marks each defect:

**REFACTOR NOW** when any of:
- it sits on ≥2 of this design's flows (its cost recurs with every feature touching them);
- it forces any axis of this evaluation to 2 or below (the foundation caps the design);
- the same defect was ledgered in a prior spec (recurring INHERIT = compounding interest).

**CARRY** otherwise — one line: the defect, its INHERIT cost, what would change the call.

Each REFACTOR NOW names payoff and restricted scope, feeding the human gate beside the
design's own refactor proposals. The signal informs the gate; the human decides.
