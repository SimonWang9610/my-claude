---
name: architect
description: >-
  Think about architecture from a question: design something new, discuss an open question, or judge a
  plan or an existing project. Recognises the intent and the level(s) the question spans — product
  (language-agnostic: systems, boundaries, data ownership, build vs buy), project (stack-specific:
  layout, layering, cross-cutting concerns), module (interfaces, state, dependencies inside one unit) —
  and answers each level in turn, top-down, with what exists, practices and pitfalls, one recommendation
  with the reason, and the decisions you must make, as a diagram plus bullets. Use on "how should we
  structure", "client-server or local-first", "which pattern for", "is this design sound", "review our
  architecture". Arg: the question.
argument-hint: <question>
---

# architect

1. **Recognise.** From the question alone, per [levels.md](references/levels.md):
   the intent (design · discuss · evaluate) and the level(s) it spans. State both in one line, e.g.
   "evaluate · product, with project implications". Never ask the user to name the level.
2. **Ground.** Non-negotiables and the end state from `DECISIONS.md`, `CLAUDE.md`, and the question;
   missing ones → a few questions with defaults, or the `clarify` skill when the goal itself is open. A repo is present → detect the stack from its
   manifests and read its own rules; existing code is the subject → the `explore` skill at map altitude
   first (or its notes). Product-level reasoning stays language-agnostic even when a stack is known.
3. **Landscape.** Read the reference of each level involved: [product](references/levels/product.md),
   [project](references/levels/project.md), [module](references/levels/module.md); read
   `references/stacks/<stack>.md` when a card exists ([template](references/stacks/TEMPLATE.md)). For what exists in the ecosystem, delegate to a
   research subagent when the host has one (Claude Code: `think:scout`) with the question, levels,
   stack, and constraints; otherwise research or answer from knowledge inline, dated.
4. **Answer top-down, one section per level.** The primary level (where the decision lives) gets the
   level's full output template; each dependent level gets "Implications at <level>" in ≤5 bullets that
   follow from the choice above. Every recommendation carries the why in 2–3 lines and what would
   change it. No abstract trade-off tables.
   - **design / discuss:** diagram · what exists (fit) · practices and pitfalls · recommendation ·
     you decide (≤3, defaults) · next.
   - **evaluate:** findings `severity (blocker / major / minor) — finding — evidence — consequence —
     fix`, ranked, judged against the level's "Evaluate" checks and the project's stated goals; one
     verdict: sound · sound with conditions (listed) · rework (why, two lines); the 2–3 changes that
     matter most; on rework a re-design sketch: target diagram, what moves and what stays, migration in
     ≤6 steps, the first step small enough to do today.
5. **Close** with one question. A decision taken is recorded with the clarify skill's decision form
   ([decision.md](../clarify/forms/decision.md)); nothing is built before.
