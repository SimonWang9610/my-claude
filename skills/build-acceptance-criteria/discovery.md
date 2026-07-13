# Discovery — turn ambiguous instructions into a mapped scope

Run this *before* writing any acceptance criteria. The user's instructions are the raw input —
often partial or ambiguous. The goal of discovery is to understand what they actually want,
break it into stories and concrete examples, and find every gap where their intent is unclear.

Work through three passes. Each pass produces something the next one builds on.

## 1. Scope — what are we building, and what are we not?

Restate the request in your own words: the feature, its user, and the boundary. Name what is
**in scope** and what is **out of scope**. If the request implies something you're unsure
belongs, that's the first gap — note it as a question, don't assume.

## 2. Stories and rules — break the scope down

Split the scope into user stories (`US-<n>`: As a … I want … so that …). For each story, list
the **rules** that govern it — the business constraints it must obey.

Then make each rule concrete with **examples**:

- **Happy** — the normal case, what the user sees when it works.
- **Edge** — boundaries and unusual-but-valid inputs.
- **Counter** — what must *not* happen (rejected input, blocked action).

Every example must be an **observable outcome** — what the user sees or a value a consumer
reads — never an internal step.

> **US-2 "Add a device"**
> - *Rule:* a device name must be unique within the scope.
>   - happy: add "Door A" to a scope with none → it appears in the list.
>   - counter: add "Door A" when one exists → inline error "Name already in use"; nothing added.
> - *Rule:* the add form opens empty.
>   - happy: click "Add Device" → the form opens with all fields blank.

## 3. Gaps — find them, then pave them

A gap is any point where you cannot write a confident example: a rule with no example, an
ambiguous term, a missing case, contested behaviour. **Do not guess past a gap.**

- If you can pave it from context or an obvious convention, do so — and state the assumption.
- If you cannot, it's an **open question**. Record it under `## Open questions` and return it to
  the caller. Write its example (and later its AC) only once it's answered.

**"Done" =** every rule has ≥1 observable example, and every remaining gap is written down as an
open question — nothing silently assumed.

## Output

The examples you gathered become the acceptance criteria in the next step: each becomes one
`AC-<story#>.<n>` (→ [phrasing-contract](./phrasing-contract.md)). Discovery just guarantees you
found all of them — happy, edge, and counter — before numbering.
