---
name: answer
description: >-
  Explains how my-invest answers a beginner: the short-answer table (sell? when? price? buy? how
  confident?), the price map, plain-words reasons, news meaning, peer comparison, industry, the user's
  shares and tax, options explained on real contracts, what could change the answer, the glossary, and
  the report page; plus how holdings are read from a question. Use when an agent writes the narrative,
  renders the report or decides which sections a question wants; preloaded into the advisor and analyst
  agents, not invoked by the user.
user-invocable: false
---

# answer

The reader is new to investing and asked a specific question. Answer it first, in their words, in tables
and short bullets: where the price is likely to go at their horizon and in the next months, what to do
from their position, how sure the analyst is, and why — with the assumptions named. Put the technical
detail below a divider. No term from the standard appears above the
divider without its one-line gloss. Every figure keeps the marker it has in its source file; the words
are yours, the numbers never are.

- Shape of the chat answer, the narrative file and the report page: [report-template.md](references/report-template.md).
- Which sections to include: `request.wants` from the question; a sell question leads with the short
  answer and the shares, a news question with the news table, a compare question with the peers table.
  When a wanted section has no data, one line says so.
- Holdings phrasing the question may contain: [holdings.md](references/holdings.md).
- Options operations and their glosses: the score skill's [options-playbook.md](../score/rules/options-playbook.md).
- The narrative goes to `history/<date>-<HHMM>.md`; `report.py --chat --html` renders everything else and
  lints; a lint failure is fixed in the narrative, never by deleting a figure.
- Assumptions forced by the question (`request.constraints`) are said where they matter ("I assumed five
  years because you said long term").
- Positions are read from the question for this answer only; the advisor deletes `facts/holdings*.json`
  afterwards. The dated report snapshot is the record of the answer given.
- The last line of every answer is the disclaimer from the evidence skill.
