---
name: discuss
description: >-
  Holds an open design discussion before any spec: frames the problem, questions it, researches the
  code and the options, weighs trade-offs with a recommendation each round, and keeps a ledger of what
  is settled and what was rejected, then drafts the direction: the goal, the chosen approach, each
  decision with the options it rejected and why, constraints, risks and what would reopen it, and the
  questions left for the spec. A draft, not a final design: no interfaces, files, plan or code. Use on
  "let's discuss", "brainstorm", "think this through with me", "explore options before we spec", or
  to settle a direction a later session will spec and build. Not for a full design (use
  my-workflow:decide).
argument-hint: "<topic or problem>"
---

# discuss

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

A conversation over several turns, not one result. The aim is a direction firm enough that a later
session never reopens its decisions, not a design it can build from.

## Altitude

- In scope: the problem, the goal, scope, the approach or stack, the main boundaries and the
  trade-offs between them.
- Out of scope: interfaces, schemas, file layout, tasks, code. A point that matters only at that depth
  → park it as a `Q` for the spec, with a default, and move on.

## Each round

1. **Frame** (first round) — the problem behind the ask, the goal, who it is for, and what the user
   has already fixed (each a `D`). Restate it in 2–3 lines; a wrong frame is the costliest miss.
2. **Research** — before asking, look up what is knowable: `/my-workflow:audit-truth` for the code and
   claims the user's points rest on; the conventions' Knowledge sources for external options, dated.
   Bring facts with anchors, never ask what you can find.
3. **Weigh** — for the 1–3 open points that would change the direction most: 2–3 realistic options,
   the trade-offs on what this problem cares about, one recommendation, and what would flip it. Push
   back with evidence when a user point does not hold.
4. **Ledger** — end the round with what is now settled (`D<n> <decision> — <why>; rejected: <option> —
   <why>`) and what is still open (`Q<n>` with a default). A settled point reopens only when the user
   says so or a new fact breaks its why; say which.

## Draft

When the user asks to wrap up, or no open point would change the direction, return the draft per the
conventions' Output, self-contained for a new session:

- **Goal** — one sentence · **Direction** — the recommendation in 2–4 lines
- **Decisions** — every ledger `D` with its why and the options it rejected
- **Facts and constraints** — anchored · **Out of scope**
- **Risks** — each with what would reopen the direction
- **Questions for the spec** — each `Q` with its default
- `Open:` the questions, and any point the discussion never reached
