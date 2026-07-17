---
name: build-requirements
description: >
  Formalize a raw request into requirements.md — US/AC/NFR as observable Given/When/Then
  outcomes — and burn down ambiguity in one batched question round with recommended
  answers. Use at the requirements phase, or whenever an ambiguous scope must become a
  testable spec.
---

# build-requirements

Turn the caller's request into a testable spec, and burn down ambiguity **now** — a
question resolved here is a clarify phase that never runs.

## Inputs

The raw request/idea · preflight/audit notes when they exist (existing behavior grounds
the ACs) · caller constraints.

## Procedure

1. **Extract** — one US-<n> per user goal; per story, AC-<story>.<n> as Given/When/Then
   **observable outcomes** (never implementation steps); cross-cutting constraints as
   NFR-<n>. IDs stable and unique; name facts consistently (one glossary term per fact,
   used verbatim everywhere).
2. **Sweep for ambiguity** — walk every AC and ask: is the trigger, the actor, the
   observable outcome, and each edge (error · empty · limit · permission) pinned? Each
   gap becomes a numbered question **with a recommended answer**.
3. **Ask in one batch** — present all questions at once; wait. Never pad the spec with
   guesses; never ask one-at-a-time.
4. **Incorporate** — fold answers into the ACs; record each Q→A as one line under
   `## Clarifications`. Unanswered questions stay listed there as **OPEN** — the caller
   routes them (e.g. a later clarify phase).
5. **Self-check** — every AC observable and testable (an outcome a test can assert);
   no AC restates another; every NFR names its verification (measure, config, or
   pattern-ban); zero silent assumptions.

## `requirements.md` shape

```markdown
# <Feature> — requirements

## US-1: <user goal>
- AC-1.1: Given <state>, When <action>, Then <observable outcome>
- AC-1.2: …

## NFRs
- NFR-1: <constraint> — verified by <measure | config | pattern-ban guard>

## Glossary
- <fact>: <one-line definition>

## Clarifications
- Q1 <question> → <answer> (<who>, <when>)
- Q2 <question> → OPEN
```

**Output discipline:** terse and goal-accurate — outcomes, not prose; one line per AC;
no design or implementation language (no component names, no state tiers).
