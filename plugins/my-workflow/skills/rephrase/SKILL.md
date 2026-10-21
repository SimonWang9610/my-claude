---
name: rephrase
description: >-
  Rewrites a long, overloaded or vague prompt so its main objective leads: the objective, must-haves,
  constraints and preferences, context pointers, ambiguities as questions with defaults, and what was
  dropped or merged, then a shorter ready-to-send prompt. Touches no spec, no code. Use on "rephrase
  this", "tighten my prompt", "what am I really asking", or a long prompt that mixes goals, background
  and details. Not for writing requirements (use my-workflow:drive-spec).
argument-hint: "<prompt>"
---

# rephrase

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Read** — the prompt and anything it pastes; read nothing else.
2. **Objective** — the one outcome the user would judge success by. When two compete, the one the rest
   serves; the other becomes a must-have or a `Q`.
3. **Sort** — every other point into: must (changes the result) · constraint or preference · context
   (background, pointers) · noise (repetition, thinking aloud). Keep the user's words for names,
   numbers and paths.
4. **Gaps** — an ambiguity or conflict that changes the result → a question with a default, unnumbered
   (the spec numbers them); at most 3.
5. **Write** — per the conventions' Output: **Objective** (one line) · **Must** · **Constraints and
   preferences** · **Context** · **Questions** · **Dropped or merged** (each point that carries
   meaning; noise only counted, e.g. "4 repetitions dropped"). Then the rewritten prompt in a quote
   block, in the prompt's own language and the user's terms, shorter than the original: objective →
   must-haves → constraints → context pointers → open questions with their defaults. `Open:` the
   questions.
