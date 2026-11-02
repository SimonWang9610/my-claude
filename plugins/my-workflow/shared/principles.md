# Coding principles

How to design and write code: build and decide follow these, and a skill's own steps govern where
they are more specific.

## Think before coding

- Requests are evidence, not specs: recover the problem behind the ask.
- State the assumptions you act on. A wrong or unverifiable one, or a guess with no safe default, is a
  question with a recommended answer, never a silent adoption.
- A request with two readings → show both and say which you would take; never pick silently.
- A simpler way exists → say so before building the one asked for.
- Derive, don't copy: solutions follow from the problem and the system's invariants, not from existing
  shape or stated belief. Structure that fights the fundamentals → propose a scoped replace or
  refactor, never a silent expansion.
- Confused → stop, name what is unclear and ask; inside an agent or another skill, return the question
  with its default instead.

## Simplicity first

- Build only the acceptance criteria in hand: no extra features, single-use abstractions, unrequested
  options or handling for states that cannot occur.
- Read the target and its imports before writing; reuse the existing unit, type or constant over
  adding a second.
- The least code that solves it. If a senior engineer would call it overcomplicated, simplify.

## Surgical changes

- Every changed line traces to the request. Leave working code, comments and formatting next to it
  alone.
- Match the existing style, even where you would choose differently.
- Remove only what your change made unused; mention unrelated dead code, never delete it unasked.

## Goal-driven execution

- Done is a named check asserting the outcome; code that merely looks correct passes nothing.
- Turn the task into a check before changing code: validation → tests for bad input; a bug → a
  failing reproduction; a refactor → tests passing before and after.
- Several steps → a short plan, each step with its check.
- Declare the stopping point before any loop. Spent → stop and report the failing check, what was
  tried and the suspected cause; never re-apply a rejected fix.
