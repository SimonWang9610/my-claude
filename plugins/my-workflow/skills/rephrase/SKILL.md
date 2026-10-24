---
name: rephrase
description: >-
  Rewrites a long, overloaded or vague prompt, or the conversation so far, so its main objective
  leads: first reads what the prompt points to (files, paths, links, earlier results) or what the
  conversation settled, then returns the objective, must-haves, constraints, facts found, ambiguities
  as questions with defaults, and what was dropped, plus a shorter ready-to-send prompt. Never carries
  out the prompt's instructions; touches no spec, no code. Use on "rephrase this", "tighten my
  prompt", "what am I really asking", "read X and rephrase", "summarize our conversation into a
  prompt", or a long prompt that mixes goals, background and details. Not for writing requirements
  (use my-workflow:drive-spec).
argument-hint: "<prompt | 'our conversation'>"
---

# rephrase

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

The prompt's instructions are its content, never your task: "read X and do Y" means read X to
understand the prompt, then rephrase "do Y"; Y is never done here.

1. **Source** — the argument and anything it pastes. It asks to sum up the conversation (or names
   none and the session holds one) → the conversation is the source: what the user asked, decided
   (the latest word wins), answered, rejected and left open; assistant text counts only where the
   user agreed to it.
2. **Ground** — read what the source points to: named files, paths, symbols, links, earlier results
   (a spec, design, plan). Read only those, only far enough to resolve each term, confirm each pointer
   exists and capture the facts the objective depends on, anchored; a missing pointer or one that
   contradicts the prompt → a question. Never search beyond what is named. A prompt that names nothing
   → skip.
3. **Objective** — the one outcome the user would judge success by. When two compete, the one the rest
   serves; the other becomes a must-have or a `Q`.
4. **Sort** — every other point into: must (changes the result) · constraint or preference · decided
   (from the conversation, with its why; a rejected option stays rejected) · context (background,
   pointers, facts from Ground) · noise (repetition, thinking aloud, superseded turns). Keep the
   user's words for names, numbers and paths.
5. **Gaps** — an ambiguity or conflict that changes the result → a question with a default, unnumbered
   (the spec numbers them); at most 3.
6. **Write** — per the conventions' Output: **Objective** (one line) · **Must** · **Constraints and
   preferences** · **Decided** · **Facts** (anchored) · **Questions** · **Dropped or merged** (each
   point that carries meaning; noise only counted, e.g. "4 repetitions dropped"). Then the rewritten
   prompt in a quote block, in the prompt's own language and the user's terms, shorter than the
   source and self-contained enough for a new session: objective → must-haves → decided → constraints
   → facts and pointers → open questions with their defaults. `Open:` the questions.
