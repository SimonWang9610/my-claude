---
description: Surface and resolve untestable or ambiguous acceptance criteria via ranked questions.
---
# spec:clarify

Resolve ambiguity through structured Q&A; flag untestable acceptance criteria.

---

**Purpose.** Drive out the ambiguity that later becomes agent improvisation — and close one recurring gap in particular: acceptance criteria that are not observably testable (the seed of false-positive tests).

## Spec Artifacts

Write `clarify.md` under `.specflow/specs/<name>/`.
- **Required:** `requirements.md` — run `/spec-requirements` if missing.
- **Optional:** `preflight.md`; prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*`.

## Gate / exit

Exits when the top ambiguities (ranked Impact × Uncertainty) are resolved into `clarify.md`, and every not-observably-testable AC is rephrased or recorded as a clarification.

## Steps

1. **Scan for ambiguities** — scope, data model, UX flow, stack-relevant NFRs (per steering), integrations, edge cases, constraints, terminology.
2. **Ask prioritized questions** — up to 5, ranked Impact × Uncertainty; one at a time, each with a recommended answer.
3. **Flag untestable ACs** — rephrase any AC that asserts an implementation step rather than an observable outcome.
4. **Append answers** — record each clarification to `clarify.md`; report a coverage summary.
