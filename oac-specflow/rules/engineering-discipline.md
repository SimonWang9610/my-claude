# Engineering discipline
Applies on every code-writing turn. Full verbatim text:

- **Simplicity-first.** Implement only the behavior the in-hand AC names. No speculative
  features, abstractions for a single call site, or handling for impossible states. If the
  diff is large for the AC, rewrite it smaller.
- **Surgical / minimal changes.** Touch only what the task requires. Don't reformat, rename,
  or refactor adjacent code. Remove only orphans your own change created; mention pre-existing
  dead code, don't delete it.
- **Read-before-write.** Read the target file and its imports first; reuse an existing
  component, hook, util, type, or constant rather than adding a second one. If intent is
  unclear, ask before overwriting.
- **Convention-beats-novelty.** Match existing naming, layout, and patterns. A second pattern
  beside an existing one is worse than the existing one. But when local convention conflicts
  with an architecture principle, the principle wins — name the conflict, don't pick silently.
- **Goal-driven execution.** Restate the task as a runnable goal before coding: a named test
  that asserts the AC's outcome. "Done" means that test passes. For a bugfix, write a failing
  reproduction test first, then make it pass.
- **Hard iteration budgets.** Declare a stopping point before any debug/refactor loop (e.g.
  "max 3 attempts"). When spent, stop and surface the failing test, what you tried, and the
  suspected cause. Never re-apply a rejected fix; if intent is unclear, ask.
