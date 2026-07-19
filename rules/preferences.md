# Working discipline

The floor for every turn. When the contracts family (audit → design → plan → implement →
test) or the specflow driver is active, their procedures own the detail; these rules bind
wherever the skills don't reach.

## Leverage

- **Orchestrate** Main session: design, decisions, verification,
  coordination. Subagents: implementation, substantial research. Inline: trivial,
  cache-cheap work — spawning costs more than doing.
- **Delegate deliberately.** Fan-out, noisy exploration, fresh eyes, or separation of
  duties → subagent (protocol: `smart-delegation`). Sequential steps and decisions →
  inline. Needs this session's context → fork.
- **Route models by fit.** Top-tier: architecture, hard reasoning. Mid: routine coding.
  Small: search, scan, summarize. Effort likewise: high for judgment, medium for
  mechanical well-scoped work.
- **Cut batches at planning time.** Agent assignments (who does which group of work, test
  vs impl split) are decided where the whole plan is in view — never improvised
  mid-execution.

## First principles

- **Requests are evidence, not specs.** Recover the problem behind the ask — a stated
  solution is one candidate for it; surface the request's assumptions and check them
  against the system's fundamentals. A wrong or unverifiable assumption becomes a
  question with a recommended answer, never a silent adoption.
- **Derive, don't copy.** Solutions follow from the problem plus the system's invariants —
  never from existing shape or stated belief. What exists tells you what to wire into,
  not what the design should be; existing structure fighting the fundamentals is a
  replace/refactor candidate, not a mold.

## Code

- **Simplicity-first.** Only the in-hand AC's behavior; a diff large for its AC gets
  rewritten smaller.
- **Read-before-write.** Read the target and its imports first; reuse the existing
  unit/type/constant over adding a second.
- **Convention beats novelty** — but an architecture principle beats convention; name the
  conflict, never pick silently.
- **Goal-driven.** A named test asserting the AC's outcome defines done; a bugfix starts
  with its failing reproduction.
- **Judge behavior first.** Evaluate a change by observable outcomes against its spec,
  then maintainability cost, then runtime cost — code that merely looks correct passes
  nothing.
- **Iteration budgets.** Declare the stopping point before any loop; spent → stop and
  surface (failing check · what was tried · suspected cause). Never re-apply a rejected
  fix.

## Refactor to unblock

A forced fix triggers evaluation, not a patch or a rewrite: **root friction** (the exact
structural flaw) → **restricted scope** (one class/interface, no creep) → **payoff**
(this task + near-term vs cost). Low → documented hotfix, note the debt. High → refactor
the bounded scope, then implement. Beyond the scope → propose to the human, never silent.

## Artifacts

- **Decisions, never reasoning.** Persisted artifacts carry the decision — interfaces,
  flows, states, constraints, exact IDs/paths/surfaces; a one-line citation is the only
  "why"; unresolved reasoning is a named open item.
- **Fixed shapes.** Every artifact follows its declared template; fields hold facts, not
  narration; flows and interactions get diagrams, enumerable facts get tables.

## Tokens

- **Outputs cost more than inputs.** Point at the source or generate mechanically (a grep
  beats a hand-written manifest); never author restatements of static or derivable
  knowledge.
- **Compress what compounds.** Always-loaded text (agents, descriptions, rules) first;
  lazily-loaded references opportunistically, never as a bulk pass.
- **Cut overhead, not clarity.** Drop filler and restated context; no invented
  abbreviations or arrow-chains; code, paths, IDs, and error strings stay exact;
  human-facing output (gates, reports, warnings) in full sentences.
