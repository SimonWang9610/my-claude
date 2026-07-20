---
name: build-requirements
description: >
  Recovers the real problem behind a request — challenging stated solutions and wrong
  assumptions from first principles — then writes it as requirements.md: user stories
  with stable AC/NFR ids phrased as observable Given/When/Then outcomes, ambiguity burned
  down in one batched question round. Use when a feature request, idea, or vague scope
  must become a spec someone can build and test against.
---

# build-requirements

Turn the caller's request into a testable spec, and burn down ambiguity **now** — a
question resolved here is a clarify phase that never runs. The request is evidence of a
problem, not the spec — recover the real requirement, don't transcribe the ask.

## Inputs

The raw request/idea · preflight/audit notes when they exist (existing behavior grounds
the ACs) · caller constraints.

## Procedure

1. **First principles** — before any AC: name the problem behind the ask (a requested
   solution is one candidate for its underlying problem, never the requirement — spec
   the problem, note the candidate); list what the request assumes about the system and
   check each against audit notes and fundamentals — a wrong or unverifiable assumption
   never enters an AC silently, it becomes a batched question (step 3) with evidence +
   recommended correction. Requirements derive from problem + invariants, not from
   current code shape or user belief.
2. **Extract** — one US-<n> per user goal; per story, AC-<story>.<n> as Given/When/Then
   **observable outcomes** (never implementation steps); cross-cutting constraints as
   NFR-<n>. IDs stable and unique; name facts consistently (one glossary term per fact,
   used verbatim everywhere).
3. **Sweep for ambiguity** — walk every AC and ask: is the trigger, the actor, the
   observable outcome, and each edge (error · empty · limit · permission) pinned? Each
   gap — and each step-1 challenged assumption — becomes a numbered question **with a
   recommended answer**.
4. **Ask in one batch** — present all questions at once; wait. Never pad the spec with
   guesses; never ask one-at-a-time.
5. **Incorporate** — fold answers into the ACs; record each Q→A as one line under
   `## Clarifications`. Unanswered questions stay listed there as **OPEN** — the caller
   routes them (e.g. a later clarify phase).
6. **Self-check** — every AC observable and testable (an outcome a test can assert);
   no AC restates another; every NFR names its verification (measure, config, or
   pattern-ban); zero silent assumptions — including inherited ones the request smuggled
   in.

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
