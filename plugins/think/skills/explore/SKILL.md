---
name: explore
description: >-
  Explore a codebase from a question, at the altitude the question needs: map (structure, boundaries,
  data flow), mechanism (how X works, entry to effect, with path:symbol evidence), onboarding (where
  to start, key concepts, reading order), or locate (where X lives, who touches it). Any stack.
  Findings persist as indexed notes in a folder you choose, so later questions answer from notes and
  read source only for gaps. Use on "how does X work", "where is", "explain the architecture of",
  "help me onboard", "what happens when". Arg: the question.
argument-hint: <question> [notes=<dir>]
---

# explore

1. **Altitude.** Classify the question with [altitudes.md](references/altitudes.md) (map ·
   mechanism · onboarding · locate) and restate it in one line with the altitude. Ambiguous: answer at
   the altitude asked and offer the other in one line.
2. **Notes folder.** `notes=<dir>` wins. Otherwise find an existing atlas:
   `grep -rl '^<!-- think-atlas -->' --include=INDEX.md . 2>/dev/null | head -1`. None: ask once,
   "Where should exploration notes live?" with default `docs/atlas/`, then create `<dir>/INDEX.md` from
   [note-format.md](references/note-format.md).
3. **Notes first.** `grep -rHE '^(id|title|altitude|keywords|outline):' <dir>`; open only the bodies
   that match. Answer from them when they suffice; name what is stale or missing.
4. **Source for the gap, bounded.** Up to ~6 files or 2 hops: read inline. More: when the host can
   delegate to a subagent (Claude Code: the `think:explorer` agent), hand it the question, altitude,
   notes dir, the notes to extend, a read budget (default 20 files), and the return format in
   [altitudes.md](references/altitudes.md); otherwise read inline within the same budget. Never re-read what the
   notes already cover.
5. **Deliver** in the altitude's shape: diagram first whenever structure is involved, then bullets;
   every fact anchored `path:symbol` or marked `(inferred)`; the design rationale in 2–3 lines when it
   is visible in the code; `Dive:` pointers for the next level down; `Gaps:` for what was not read.
6. **Persist.** Write or extend the note and its `INDEX.md` row per [note-format.md](references/note-format.md). Chat answer ≤ 30
   lines; the note holds the detail.
