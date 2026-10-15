---
name: write
description: >-
  The non-coding workflow from an agreed non-code spec: plan an outline mapped to the spec's
  must-contain items, gather sources with the explore skill, draft, check the draft against the
  spec's done-when, and run a fresh-eyes review only when the user turns it on. Gates after every
  stage. Use for documents, plans, task breakdowns, reports, decision records, research write-ups,
  and any deliverable that is not code. Input: the non-code spec already in the session; the argument
  is optional extra requirements.
argument-hint: [requirements]
---

# write

Uses: skill `prompt` when no spec exists, skill `explore` for sources (Claude Code `think:<name>` ·
Copilot `/<name>`); agent `reviewer` for review (Claude Code `think:reviewer` · Copilot `reviewer`).

**Input.** The latest non-code spec in the session (with any design decisions agreed after it) is the
task. An argument adds or changes requirements: fold them into the spec as `must` or `limits` lines and
say so in one line. No spec in the session → invoke the `prompt` skill first, with the argument as the
raw request. Stages, each ending in a gate:

1. **Outline.** Sections in order; each names the `must` items (C1…) it covers and its sources. Every
   C item lands in exactly one section. Facts missing → the `explore` skill (docs, codebase, or online,
   dated). Gate.
2. **Draft.** Write for the spec's `reader` in the spec's `output` form and length. Diagrams where
   structure or flow matters; tables for comparisons; claims carry their source. A changed
   requirement updates the spec and the affected sections only. Gate.
3. **Check.** Tick the spec's `done` checklist line by line; report gaps with the section that would
   fix them. Gate.
4. **Review** — only when the spec says `review: on` or the user asks: hand the `reviewer` agent the
   spec and the draft; relay its findings. Gate.

Gate = at most three critical questions (with defaults) or "Continue to <next stage>?". Never start the
next stage without the user's permission unless the spec says `gates: auto`. Deliver inline; save to a
file only when the spec's `output` names a location or the user asks.
