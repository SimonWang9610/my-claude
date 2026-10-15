---
name: prompt
description: >-
  Turn a raw, vague, or incomplete request into a compact agent-facing spec before any work: classify
  it as code or non-code, gather missing facts with the explore skill, ask the critical questions
  (with defaults), and return the spec in a fixed template — goal, decisions, refined requirements,
  constraints, context, done-when, route. The spec replaces the raw request for the rest of the
  session. Use at the start of any task (develop, design, write, plan, research) and whenever a
  request lacks a goal, constraints, or a done-criterion. Arg: the raw request.
argument-hint: <raw request>
---

# prompt

Uses: skill `think:explore` for facts. Routes to skill `think:design`, `think:build`, or `think:write`
only after the gate.

1. **Classify.** Code: the deliverable is code, config, tests, or a change in a repo. Non-code:
   documents, plans, reports, decisions, research. Both: write two specs, code last.
2. **Look before asking.** When the request touches existing code, docs, or named things you cannot
   resolve, invoke the `explore` skill (bounded) first. Never ask the user what you can look up.
3. **Ask.** At most three critical questions per round, each with the default you will assume and one
   line on why it matters. Priority: hard constraints → what already exists → done-when → size.
4. **Write the spec** with [code.md](templates/code.md) or [non-code.md](templates/non-code.md).
   Agent-facing: terse lines, IDs, paths, numbers; omit empty fields; no prose. Inline in chat; save
   to a file only when the user asks.
5. **Gate.** End with either the next critical questions or "Continue to <route>?". Do not start the
   next stage without the user's permission unless the spec says `gates: auto`. From here on, the
   spec is the task; the raw request is history.
