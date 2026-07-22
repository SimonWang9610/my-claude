---
name: build-requirements
description: >
  Recovers the real problem behind a request — challenging stated solutions and wrong
  assumptions from first principles — then writes it as requirements.md: user stories
  with stable AC/NFR ids phrased as observable Given/When/Then outcomes, ambiguity burned
  down in one batched question round. Use when a feature request, idea, or vague scope
  must become a spec someone can build and test against. Not for designing the solution
  (use design-react-contracts) or decomposing a Figma screen (use decompose-figma).
  Output: requirements.md.
---

# build-requirements

Turn the caller's request into a testable spec, and burn down ambiguity **now** — a
question resolved here is a clarify phase that never runs. The request is evidence of a
problem, not the spec — recover the real requirement, don't transcribe the ask.

**Query only to settle an open question.** Requirements usually needs no codebase — you recover
the problem from the request + first principles. But when an ambiguity turns on how existing or
legacy code actually behaves, `/audit-code-flows query "<question>"` **before** it becomes a
question for the user: don't ask what the atlas already answers. Not code-dependent, or no atlas → just ask.

## Inputs

The raw request/idea · the preflight **atlas** (query it to settle a code-dependent open
question) · caller constraints.

## Procedure

1. **First principles** — before any AC: name the problem behind the ask (a requested
   solution is one candidate for its underlying problem, never the requirement — spec
   the problem, note the candidate); list what the request assumes about the system and
   check each against fundamentals — and, when it turns on existing/legacy behavior, against the atlas (`/audit-code-flows query`) — a wrong or unverifiable assumption
   never enters an AC silently, it becomes a batched question (step 3) with evidence +
   recommended correction. Requirements derive from problem + invariants, not from
   current code shape or user belief.
2. **Extract** — one US-<n> per user goal; per story, AC-<story>.<n> as Given/When/Then
   **observable outcomes** (never implementation steps); cross-cutting constraints as
   NFR-<n>. IDs stable and unique; name facts consistently (one glossary term per fact,
   used verbatim everywhere).
3. **Sweep for ambiguity** — walk every AC and ask: is the trigger, the actor, the
   observable outcome, and each edge (error · empty · limit · permission) pinned? A gap that
   turns on existing/legacy behavior → query the atlas first; only what it can't settle — plus
   each step-1 challenged assumption — becomes a numbered question **with a recommended answer**.
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
