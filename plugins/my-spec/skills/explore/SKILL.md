---
name: explore
description: >-
  Grounds a task in what already exists (code, the repo's docs or the web) within a read budget →
  anchored facts, the patterns and conventions to follow, and gaps. Use on "how does X work", "where is
  X", "what's our convention for X", "is there something for X", or before designing or building in an
  existing codebase. Not for judging quality (use my-spec:critique).
argument-hint: "<question>"
---

# explore

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Depth** — pick the one the question needs:
   - locate ("where is", "is there") — grep names and synonyms, then the owning unit · ≤5 files
   - mechanism ("how does", "what happens when") — the entry, then calls and state one hop at a time ·
     ≤15 files
   - map ("how is X organised", a new area) — manifests, entry points, top folders, one flow end to
     end · ≤12 files
   - docs or web — the repo's docs first; online, official sources first, each dated · ≤6 pages
2. **Read** — only what the question needs; stop at the budget and name the gaps. Wider than the
   budget and you can spawn → one `explorer` agent per sub-question, each within its depth's budget.
3. **Report** — facts with anchors; `Patterns:` the conventions to follow, each with an exemplar path
   (layout, naming, errors, state, tests, the libraries in use); `Gaps:`. A diagram only for a
   structure or flow question.
