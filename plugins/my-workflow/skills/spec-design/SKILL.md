---
name: spec-design
description: >-
  Use this skill when the user must decide how to build something: "design X", "which approach",
  "which stack", "how should we structure this", "what are the options", even if they never say
  "design". Weighs options with you, then records only what you chose: a short design.md with a
  small dependency diagram, plus a file per group of units only when needed. Not for reviewing a
  design (use the my-workflow:spec-design-reviewer agent).
argument-hint: "[question or requirements | path to a workflow.yaml]"
---

# spec-design

Rules: `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (else `../../shared/`) and
`../drive-spec/references/spec-rules.md`, read once per conversation. Mode per the spec rules. Other
paths: this folder.
Input: the spec (a bug: its root cause and fix options).

## Steps

1. **Ground** — what the design touches, per the conventions' Grounding; an existing unit keeps its
   atlas id, a new one is numbered after the atlas's highest.
2. **Approach** — only when open: 2–3 options with trade-offs and one recommendation, in the
   conversation. The pick → a `D`. `gates: auto` → the recommendation.
3. **Units** — `/my-workflow:design-component`: per unit its responsibility, change (new · modify ·
   reuse) and the `AC`s it delivers. What crosses between two units is an edge label in the
   diagram, stated nowhere else.
4. **Parts** — only those needed (`assets/parts.md`; what each must answer: `references/answers.md`):
   structure → `/my-workflow:scaffold-project-structure` · contracts and data · screens · UI state →
   `/my-workflow:analyze-ui-state` · flows.
5. **Constraints** — what the stack imposes on structure, state and concurrency; one that breaks a
   unit → revise it with a `D`. A rule a lint can enforce → name it under Quality.
6. **Write** — `design.md` (`assets/design.md`). `design/<group>.md` (`assets/group.md`) only for
   units that need a boundary or inside, and for each whose surface is new or changed: its
   Interface, which the tests are written from; `design/<part>.md` per part. Spec mode:
   `spec-check design`.

## Rules

- Existing patterns are the default; deviating takes a `D`. The simplest design that meets the
  criteria and limits.
- Files hold only what the user finalized, stated not explained: one line per item, a why only on a
  `D`.
- It needs a workaround → the spec rules. A requirement must change → a `Q`.
