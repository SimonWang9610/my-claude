---
name: spec-design
description: >-
  Use this skill when the user must decide how to build something: "design X", "which approach",
  "which stack", "how should we structure this", "what are the options", even if they never say
  "design". Weighs options with you, then records only what you chose: a short design.md plus one
  file per unit with small dependency diagrams. Not for reviewing a design (use
  my-workflow:spec-review).
argument-hint: "[question or requirements | path to a workflow.yaml]"
---

# spec-design

Rules: `conventions.md` and `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (unexpanded →
`../../shared/`); already loaded in this conversation → do not read them again. Mode per the spec rules. Other paths are relative to this folder.
Input: the spec (a bug: its root cause and fix options).

## Steps

1. **Level** — module (inside one unit) · component (≥2 dependent units, a new interface, screens) ·
   system (several deployables, a public contract or stored data changes). It sets the layout
   (`assets/design.md`) and the step's `level`.
2. **Ground** — `/my-workflow:audit-truth` on what the design touches; an existing unit keeps its
   atlas id.
3. **Approach** — only when open: 2–3 options with trade-offs and one recommendation, in the
   conversation. The pick → a `D`; spec mode: log what the user weighed to discussions. Inside an agent → return
   them. `gates: auto` → the recommendation.
4. **Units** — `/my-workflow:design-component`: per unit its responsibility, input, output, boundary,
   change (new · modify · reuse) and the `FN`s or `AC`s it delivers.
5. **Parts** — only those needed (`assets/parts.md`; what each must answer: `references/answers.md`):
   structure → `/my-workflow:scaffold-project-structure` · contracts and data · screens · UI state →
   `/my-workflow:analyze-ui-state` · flows.
6. **Limits** — the stack's limits on structure, state and concurrency; one that breaks a unit →
   revise it with a `D`. A rule a lint can enforce → name it under Quality.
7. **Write** — `design.md`: approach, units index, overview diagram, quality, decisions.
   `design/UNIT-<n>-<name>.md` per unit (`assets/unit.md`). `design/<part>.md` per part. One unit →
   `design.md` alone. Spec mode: `spec-check design`.

## Rules

- Existing patterns are the default; deviating takes a `D`. The simplest design that meets the
  criteria and limits.
- Files hold only what the user finalized, stated not explained: one line per item, a why only on a
  `D`.
- At most 6 units per diagram: the overview shows groups, each unit's file its direct neighbours.
- It needs a workaround → the spec rules. A requirement must change → a `Q`.
