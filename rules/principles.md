# Rules & Principles for LLM Coding

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Read Before You Write
**Understand the code and context before changing it**

Before adding code:

- Read the current file and its imported/related files.
- Check whether a function, utility, or constant with the same purpose already exists.
- If a duplicate implementation exists, use it - don't create a second version.
- If you don't understand the intent behind existing code, ask before changing it.

The test: You should know what already exists before you add anything new.

## 6. Hard Token Budgets
**Every loop has a limit. No exceptions.**

For any iterative loop (debugging, refactoring, generation):
- Set a budget up front - max iterations, token count, or time. Tune values per project.
- When the budget is exhausted, stop immediately and show the current result.
- Don't silently keep going "just one more try."
- Don't re-suggest a fix that's already been rejected.
- Don't assume you know the intent behind code - if it's not clear, ask.

The test: Before looping, you should be able to say exactly when you'll stop.

## 7. Convention Beats Novelty
**Follow the codebase, even when you'd do it differently**

- Match existing naming and architectural conventions (e.g. snake_case vs camelCase) unless explicitly asked to change them.
- Introducing a second pattern is worse than living with any single existing one.
- If you think a convention should change, propose it explicitly and wait for approval before acting.

The test: A reviewer shouldn't be able to tell which lines you wrote from style alone.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.