---
name: oac-test-forensics
description: >
  Audits an existing Vitest suite for three gap classes: behaviors with no governing criterion,
  green tests that assert a weaker proxy than the behavior they name, and false positives that stay
  green when the code is broken — via a mutation-test mindset (RTL, Zustand, TanStack Query, MSW),
  each finding confidence-tagged. Use when auditing a suite you didn't necessarily write, or when a
  green suite gives no confidence a real regression would fail. Detection half of oac-test-contract;
  each finding maps to the rule that fixes it.
---

# oac-test-forensics

Detection-time audit of an existing test suite: find the coverage gaps and false positives a green
suite hides. This is the **DETECTION** half of a pair; the authoring-time **PREVENTION** half is the
`oac-test-contract` skill. Every finding names the contract rule that fixes it — via the
"signal → contract rule" table in `references/false-positive-signals.md` — so a finding is always
actionable. You detect and hand back for a rewrite; you do not edit tests here.

**Given** the test suite plus the criteria it must satisfy — the `AC-<story>.<n>` / `NFR-<n>` IDs in
the requirements document the caller points you at. **Produce** findings in three gap classes, each
confidence-tagged and mapped to a contract rule, in the per-surface report table.

## The three gap classes

| Class | A test is in this class when… |
|---|---|
| `no-spec-coverage` | a behavior runs with no governing criterion, or a criterion has zero mapped tests. |
| `tests-pass-but-miss-behavior` | it names a behavior but its body asserts a weaker proxy; the named behavior is unverified. |
| `false-positive` | it passes regardless of whether the code works — inverting the production branch it claims to cover leaves it green. |

They overlap — one surface can exhibit all three — so name the class per finding; each maps to a
different contract rule.

## Procedure

1. **Enumerate behaviors per surface** — props, handlers, render branches, side-effects, error paths.
   → `references/heuristics-behavior-enumeration.md`
2. **Pass 1 — no-spec-coverage.** Map each behavior to a criterion ID and each criterion to a test
   (grep the ID in test labels). Behavior with no criterion → *improvised*; criterion with no test →
   *uncovered clause*. A surface with no tests at all is a Pass-1 finding — record it, skip 2–3 for it.
   → `references/gap-classes.md` (Pass 1)
3. **Pass 2 — tests-pass-but-miss-behavior.** For each criterion-mapped test, read the name as a claim,
   then read the body. Flag when: the triggering action never fires, the assertion is at the wrong
   depth/owner (Zustand copy vs TanStack cache), or a `vi.fn()` is declared but never called.
   → `references/gap-classes.md` (Pass 2) · `references/heuristics-pass2-shapes.md` (shapes A–D)
4. **Pass 3 — false-positive.** Scan for on-sight signals, then confirm with the mutation mindset:
   invert or delete the deciding production branch — does the test still pass? Yes → false positive.
   → `references/gap-classes.md` (Pass 3) · `references/heuristics-pass3-forms.md` (forms 1–5)
   · `references/false-positive-signals.md` (signal catalogue + mutation protocol + signal→rule table)
5. **Tag confidence** high/medium/low; block on high and medium, surface low as advisory. A false
   positive mapped to a criterion is always Critical.
   → `references/gap-classes.md` (calibration + report table)
6. **Cite** any external claim you lean on. → `references/sources.md`

## References

- `references/gap-classes.md` — per-pass procedure, finding formats, confidence calibration, report table.
- `references/heuristics-behavior-enumeration.md` — Pass 1 grep/read recipes.
- `references/heuristics-pass2-shapes.md` — Pass 2 shapes A–D with before→after.
- `references/heuristics-pass3-forms.md` — Pass 3 forms 1–5 + matcher-misuse amplifiers.
- `references/false-positive-signals.md` — on-sight signal catalogue, mutation protocol, signal→rule table.
- `references/sources.md` — external citations grouped by pass.
