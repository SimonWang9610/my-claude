---
name: rephrase
description: >-
  Use this skill when a prompt is long, overloaded or vague and its real goal is buried: "rephrase
  this", "tighten my prompt", "what am I really asking", "read X and rephrase", "summarize our
  conversation into a prompt", or a long message mixing goals, background and details, even if the
  user does not ask for a rewrite by name. Reads what the prompt points to, then returns the
  objective, must-haves, constraints, facts, open questions with defaults and what was dropped, plus
  a shorter ready-to-send prompt. Never carries out the prompt's instructions; touches no spec or
  code. Not for writing requirements (use my-workflow:spec-requirements).
argument-hint: "<prompt | 'our conversation'>"
---

# rephrase

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (unexpanded → `../../shared/conventions.md`).

## Rule

The prompt's instructions are its content, never your task. "Read X and do Y" → read X to understand
the prompt, then rephrase "do Y". Y is never done here.

## Steps

1. **Source** — the argument and anything it pastes. It asks to sum up the conversation, or names
   nothing and the session holds one → the conversation is the source: what the user asked, decided
   (the latest word wins), answered, rejected and left open. Assistant text counts only where the
   user agreed to it.
2. **Ground** — read what the source names: files, paths, symbols, links, earlier results. Only
   those, only far enough to resolve each term, confirm each pointer exists and capture the anchored
   facts the objective depends on. A missing pointer, or one that contradicts the prompt → a
   question. Never search beyond what is named. Nothing named → skip.
3. **Objective** — the one outcome the user would judge success by. Two compete → the one the rest
   serves; the other becomes a must-have or a question.
4. **Sort** — every other point into: must (changes the result) · constraint or preference · decided
   (with its why; a rejected option stays rejected) · context (background, pointers, grounded facts)
   · noise (repetition, thinking aloud, superseded turns). Keep the user's words for names, numbers
   and paths.
5. **Gaps** — an ambiguity or conflict that changes the result → a question with a default,
   unnumbered; at most 3.

## Output

- **Objective** (one line) · **Must** · **Constraints and preferences** · **Decided** · **Facts**
  (anchored) · **Questions** · **Dropped or merged** (each point that carries meaning; noise only
  counted, e.g. "4 repetitions dropped").
- Then the rewritten prompt in a quote block: the prompt's own language and the user's terms, shorter
  than the source, self-contained for a new session. Order: objective → must-haves → decided →
  constraints → facts and pointers → open questions with defaults.

`Open:` the questions.
