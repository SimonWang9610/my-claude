---
name: audit-truth
description: >-
  Grounds the truth about code or docs for a question or purpose, the way you would by hand: locate by
  keyword, walk definitions one hop at a time only while the purpose still has an open question, and
  report anchored facts shaped as flows or structures, with where to look deeper and what stayed
  unread. Also confirms or refutes a claim. Use on "how does X work", "where is X", "what's our
  convention for X", "is it true that X", or before designing or building in unfamiliar code. Never
  changes what it reads; not for judging quality (use my-workflow:critique).
argument-hint: "<question, claim or purpose> [sources]"
---

# audit-truth

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Purpose** — the questions the instruction asks; they gate every read. Sources: what the
   instruction names (code, docs, notes, a path), else the workspace. Notes or a summary are read
   before the code they describe (only the index rows and notes that match the purpose, within the
   docs budget), and a fact taken from them is marked (from <file>) until checked against source. Skip
   facts already in the context; never change what you read.
2. **Locate** — grep the purpose's keywords (names, routes, fields, keys, their synonyms) and glob the
   layout for candidate entry points; list their exported surface. A claim: look first for what would
   refute it.
3. **Walk** — from each entry, go to definitions outward only where a purpose question is still open:
   per hop, what it calls, who calls it, and the facts it reads or writes (couplings show up here).
   Stop a branch when it is understood, off-purpose (record its name), already walked, or at a
   boundary. Declare the budget before the first read: a claim or a location ≤5 files · a mechanism
   ≤15 per flow · how an area is organised ≤12 · docs ≤6 pages (repo docs → a documentation tool at
   the detected version → official pages, dated). Spent → stop; a branch cut while still on-purpose
   becomes a Dive pointer.
4. **Ground** — keep a fact only if it changes what the reader does next: a file to touch, a decision,
   a risk or a rule to follow. Boundaries, not implementations: name the exact surface (endpoint,
   table, key, event) and stop. Untagged = read from source · (from <file>) = taken from notes, not
   yet checked · (inferred) = deduced · (uncertain) = carries a Dive pointer.
5. **Report** — per the conventions' Output, at most about 15 lines per question:
   - **Facts**, shaped by what was found, each anchored: a flow (trigger · inputs and where they come
     from · steps · outcome per case, with side effects at the boundary) or a structure (parts and
     their dependency direction · how a fact moves · rules). A claim: confirmed, refuted (with the
     true fact) or unclear, and an unclear one becomes a `Q` with a default.
   - **Rules** — conventions to follow, each with an example path.
   - **Dive** — `path:symbol` pointers for deeper detail.
   - **Open:** the gaps — what stayed unread, and why.
