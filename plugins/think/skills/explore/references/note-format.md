# Note format — explore notes, written only when the user asks to keep them

`<dir>/INDEX.md` is the only index; every note has one row. The first line of INDEX.md is the marker
`<!-- think-atlas -->` so later runs find the folder. Notes are `<id>-<short-name>.md`
(`N3-request-pipeline.md`); ids increase; a note is extended in place, never duplicated.

## INDEX.md

```markdown
<!-- think-atlas -->
# Atlas — <project>
| Note | Altitude | File | Entry anchor | Keywords |
|------|----------|------|--------------|----------|
| N1 <title> | map | N1-<name>.md | `path:symbol` | <3–6 words> |
```

## Note file

```markdown
---
id: N1
title: <one line>
altitude: map | mechanism | onboarding | locate
keywords: <comma-separated terms a future question would use>
outline: <one line: what the note answers>
anchors: <path:symbol, …>
updated: <YYYY-MM-DD>
---
## Question
## Answer            (≤ 20 lines; diagram first when structure is involved)
## Evidence          (table: path:symbol | fact | (read | inferred))
## Why               (2–3 lines of design rationale, when visible)
## Dive              (path:symbol pointers for the next level down)
## Gaps              (what was not read; the budget that stopped it)
```

Frontmatter is functional: later runs route by grepping it, so a note without it is invisible.
