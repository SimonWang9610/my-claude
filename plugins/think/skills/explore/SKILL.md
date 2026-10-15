---
name: explore
description: >-
  Companion skill for collecting facts other stages need, from three sources: the codebase (map,
  mechanism, onboarding, or locate altitude, with path:symbol evidence), existing docs (READMEs, ADRs,
  specs, wikis in the repo), and online resources (official docs, canonical repos, papers), bounded by
  a read budget. Returns a compact fact list with anchors or dated sources. Used by the prompt,
  design, build, and write skills; also on "how does X work", "where is", "what does the doc say
  about", "is there something existing for". Arg: the question.
argument-hint: <question>
---

# explore

Uses: agent `explorer` for large explorations (Claude Code `think:explorer`).

1. **Source.** Pick the source(s) the question needs: codebase → [codebase.md](references/codebase.md)
   (choose the altitude there); existing docs → search the repo's docs folders, README, ADRs,
   `CLAUDE.md`, specs by keyword before reading; online → official docs and canonical repos first,
   then practitioner write-ups; every item dated.
2. **Bound.** Default budget: 12 files or 6 pages. Larger → delegate to the `explorer` agent with the
   question, sources, budget, and the return format below. Stop at the budget and name the gaps.
3. **Return**, compact and agent-facing:
   `F<n> <fact> — <path:symbol | doc§ | url, date> — (read | inferred)`, then `Gaps:` and, for code,
   `Dive:` pointers. A diagram only when the question is about structure.
4. **Persist** only when asked: notes per [note-format.md](references/note-format.md) in the folder the
   user names.
