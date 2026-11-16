---
name: discuss
description: >-
  Use this skill when the user wants to think a problem through before committing to anything: "let's
  discuss", "brainstorm", "think this through with me", "explore options", "I'm not sure how to
  approach X", "what would you do", even if they never say "discuss". Frames the problem, researches
  the code and the options, weighs trade-offs with a recommendation each round, keeps a ledger of
  what is settled and rejected, and ends with a direction draft a later session can spec. No
  interfaces, files, plan or code. Not for a full design (use my-workflow:spec-design).
argument-hint: "<topic or problem>"
---

# discuss

Conventions: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (unexpanded → `../../shared/conventions.md`).

A conversation over several turns. The aim: a direction firm enough that a later session never
reopens its decisions; not a design to build from.

## Altitude

- **In:** the problem, the goal, scope, the approach or stack, the main boundaries, the trade-offs
  between them.
- **Out:** interfaces, schemas, file layout, tasks, code. A point that matters only at that depth →
  park it as a `Q` for the spec, with a default.

## Each round

1. **Frame** (first round) — the problem behind the ask, the goal, who it is for, what the user has
   already fixed (each a `D`). Restate it in 2–3 lines; a wrong frame is the costliest miss.
2. **Research** — before asking, look up what is knowable: `/my-workflow:audit-truth` for the code
   and the claims the user's points rest on; the conventions' Knowledge sources for external options,
   dated. Bring anchored facts; never ask what can be found.
3. **Weigh** — for the 1–3 open points that would change the direction most: 2–3 realistic options,
   the trade-offs on what this problem cares about, one recommendation, what would flip it. Push back
   with evidence when a user point does not hold.
4. **Ledger** — end the round with what is settled (`D-<n> <decision> — <why>; rejected: <option> —
   <why>`) and what is open (`Q-<n>` with a default). A settled point reopens only when the user says
   so or a new fact breaks its why; say which.

## Draft

When the user asks to wrap up, or no open point would change the direction. Self-contained for a new
session:

- **Goal** — one sentence · **Direction** — the recommendation in 2–4 lines
- **Decisions** — every ledger `D` with its why and the options it rejected
- **Facts and constraints** — anchored · **Out of scope**
- **Risks** — each with what would reopen the direction
- **Questions for the spec** — each `Q` with its default

`Open:` the questions, any point the discussion never reached.
