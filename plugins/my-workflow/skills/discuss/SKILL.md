---
name: discuss
description: >-
  Use this skill when the user wants to think a problem through before committing: "let's discuss",
  "brainstorm", "explore options", "I'm not sure how to approach X", "what would you do".
  Researches, weighs trade-offs with a recommendation each round, and ends with a direction draft a
  later session can spec. No interfaces, plan or code. Not for a full design (use
  my-workflow:spec-design).
argument-hint: "<topic or problem>"
---

# discuss

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (unexpanded → `../../shared/conventions.md`);
already loaded in this conversation → do not read it again.

A conversation over several turns, toward a direction a later session will not reopen.

- **In:** the problem, goal, scope, approach, main boundaries, trade-offs.
- **Out:** interfaces, schemas, files, tasks, code → park as a `Q` for the spec.

## Each round

1. **Frame** (first) — the problem behind the ask, the goal, who it is for, what is already fixed;
   restate it in 2–3 lines.
2. **Research** — `/my-workflow:audit-truth` and dated external sources; never ask what can be found.
3. **Weigh** — the 1–3 points that most change the direction: 2–3 options, trade-offs, one
   recommendation, what would flip it. Push back with evidence.
4. **Ledger** — settled (`D-<n> <decision> — <why>; rejected: <option> — <why>`) and open (`Q-<n>`
   with a default). A settled point reopens only on the user's word or a new fact.

## Draft

On wrap-up, self-contained for a new session: Goal · Direction (2–4 lines) · Decisions with their
rejected options · Facts and constraints · Out of scope · Risks and what would reopen it · Questions
for the spec.
