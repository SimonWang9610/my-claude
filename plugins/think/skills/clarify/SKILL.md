---
name: clarify
description: >-
  Handle ambiguity and open questions before work starts: for a vague task, requirement, goal, or idea,
  diagnose what is missing, ask a few targeted questions with defaults, lay out candidate solutions
  (what exists, effort, fit, risk), recommend the most approachable one, and converge on a decision and
  a brief that any agent can execute. Use on "I want to…", "help me figure out", "not sure how to",
  "what should we do about", any request without a clear goal, constraints, or done-criterion, and
  whenever a request implies real work. Arg: the request or idea.
argument-hint: <request, goal, or idea>
---

# clarify

1. **Diagnose.** Restate what is known in ≤5 lines, then name what is missing or conflicting among:
   goal (the outcome, not the activity) · scope and non-goals · hard constraints (numbers, platform,
   time, skills, "never" items) · done-criterion · approach. Read `CLAUDE.md` and `DECISIONS.md` when
   present; nothing wider yet. Nothing missing → skip to step 4.
2. **Ask.** At most three questions per round, each with the default you will assume and one line on why
   it matters; prefer the question that eliminates the most options. Up to three rounds; after that,
   proceed on the defaults and say so. A numbered reply answers a round.
3. **Suggest** when the approach is open: two to four candidate directions, each in four lines — what it
   is · what exists to reuse (a research subagent when the host has one, Claude Code: `think:scout`;
   otherwise from knowledge, dated) · effort and fit with the user's skills and constraints · main risk. Recommend the
   most approachable one with the why in 2–3 lines and what would change the pick. A direction that is
   an architecture question hands off to the `architect` skill; one about existing code to the
   `explore` skill.
4. **Converge.** Write the decision ([decision.md](forms/decision.md); into the project's `DECISIONS.md`
   when the user wants it kept) and the brief ([brief.md](forms/brief.md)): Goal · Context · Hard
   constraints · Non-goals · Done when · Ceremony (answer / inline / plan-first / full flow). The brief
   is the sharpened prompt for any agent. Send it and stop; work starts on confirmation.

Keep each round under 40 lines; a diagram only when structure is involved.
