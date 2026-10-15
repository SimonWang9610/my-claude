---
name: design
description: >-
  Optional design stage between a spec and the work: options with pros, cons, and a recommendation for
  open-ended tasks, or architecture at the level(s) a task spans — product (language-agnostic:
  systems, boundaries, data ownership, build vs buy), project (stack-specific: layout, layering,
  cross-cutting concerns), module (interfaces, state, dependencies) — designing, discussing, or
  evaluating, with diagrams, rationale, trade-offs, and best practices. Uses the explore skill for
  facts; researches only when asked or when solutions cannot be proposed without it. Use when a spec
  routes to design, on "how should we structure", "which approach", "what are the options", "is this
  design sound". Input: the spec already in the session; the argument is optional extra requirements
  or, with no spec, the question.
argument-hint: [requirements or question]
---

# design

Uses: skill `explore` (Claude Code `think:explore` · Copilot `/explore`) for facts and research. Hands
off to skill `build` or `write` (Claude Code `think:<name>` · Copilot `/<name>`) only after the gate.

0. **Input.** The latest spec in the session is the task. An argument adds or changes requirements:
   fold them into the spec and say so in one line. No spec in the session → the argument is the
   question. No spec and no argument → ask what to design, or invoke the `prompt` skill.
1. **Frame.** From the spec: the intent — open-ended options, architecture design or discussion, or
   evaluation of a plan or existing structure — and, for architecture, the level(s) per
   [levels.md](references/levels.md). State both in one line.
2. **Facts.** Existing code or docs involved → invoke the `explore` skill first (map altitude).
   Research the ecosystem only when the user asks or no sound option can be proposed without it; then
   the `explore` skill on online sources, dated.
3. **Answer** with the level references ([product](references/levels/product.md),
   [project](references/levels/project.md), [module](references/levels/module.md); a
   `references/stacks/<stack>.md` card when one exists, [template](references/stacks/TEMPLATE.md)):
   - **options** — 2–4, each: what it is · pros · cons · effort · risk; one recommendation with the
     why in 2–3 lines and what would change it.
   - **architecture** — diagram first; one section per level, top-down, the primary level in full and
     dependent levels as implications; rationale, trade-offs, practices to follow.
   - **evaluate** — findings `blocker / major / minor — finding — evidence — fix`, ranked; verdict
     sound · sound with conditions · rework; a re-design sketch on rework.
4. **Gate.** End with at most three critical questions (with defaults) or "Continue to <build | write>?".
   Never continue without permission unless the spec says `gates: auto`. Agreed decisions go into the
   spec's `decide` lines.
