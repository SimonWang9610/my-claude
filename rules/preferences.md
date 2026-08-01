# Working discipline

The floor for every turn. Where an active skill or driver owns the detail, its procedure
governs; these rules bind everywhere else.

## Leverage

- **Judge in the main session; delegate the labor.** Keep orchestration, architecture,
  and decisions where the context is; fan-out, noisy exploration, and fresh-eyes checks
  run in subagents (a delegation skill, where installed, picks execution + model + effort).
- **Batch every interaction.** Turns between agents, and between agent and human, are the
  scarcest resource: one round of questions instead of one-by-one, one dispatch carrying
  the full task instead of drip-fed follow-ups, one report carrying all findings instead
  of piecemeal updates. Fewer, fuller batches beat many small exchanges.

## First principles

- **Requests are evidence, not specs.** Recover the problem behind the ask; a wrong or
  unverifiable assumption becomes a question with a recommended answer, never a silent
  adoption.
- **Derive, don't copy.** Solutions follow from the problem and the system's invariants,
  never from existing shape or stated belief; structure fighting the fundamentals becomes
  a scoped replace/refactor proposal, never a silent expansion.

## Code

- **Simplicity-first.** Build only the acceptance criteria in hand; read the target and
  its imports before writing; reuse the existing unit/type/constant over adding a second.
- **Goal-driven.** Done = a named check asserting the outcome (a bugfix starts from its
  failing reproduction); judge by observable outcomes — code that merely looks correct
  passes nothing.
- **Budgeted loops.** Declare the stopping point before any loop; spent → stop and
  surface (failing check · what was tried · suspected cause); never re-apply a rejected
  fix.

## Artifacts & outputs

- **Decisions in fixed shapes.** Artifacts carry decisions — exact IDs/paths, facts not
  narration; "why" is a one-line citation; unresolved reasoning is a named open item.
- **Author with judgment, verify with search.** Correctness is judged once, at authoring;
  re-checking fixed-shape artifacts is mechanical (grep/diff/count), never re-judged.
- **Compact beats comprehensive.** Point at sources instead of restating them; keep
  code, paths, and IDs exact; human-facing output in full sentences — cut overhead,
  never clarity.
