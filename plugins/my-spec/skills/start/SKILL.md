---
name: start
description: >-
  Turns a request into a spec: goal, requirements, limits, done and the route (decide, build, write or
  critique), with a fast track for small, clear changes. Use when starting any task: "build X", "fix
  X", "write a plan for X", "I want …", or a request with no clear goal or done criterion. Not for
  fact-finding (use my-spec:explore).
argument-hint: "<request>"
---

# start

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Look** — before asking, `/my-spec:explore` at locate depth (mechanism when behaviour must be
   traced) on the code, docs, stack and patterns involved. Never ask what you can look up.
2. **Size** — code or non-code (both → two specs, code last); fast or full track per the conventions.
3. **Ask** — only questions whose answer changes the result, ≤3, each with its default. Fast track:
   each default becomes a `D` line in the shown spec; a question with no safe default → full track.
   Full track: they become the spec's `open` lines for the gate.
4. **Spec** — fill `templates/spec.md`; the facts found go in `context`. Route: `decide` when an
   approach, a structure, components or UI state is open, or for a new project; `critique` when the
   ask is to judge existing work; else `build` or `write`. Full track sets `review on`.
5. **Hand on** — fast: show the short spec and continue with the route's skill in the same turn. Full:
   save per the conventions and gate; from here on the spec is the task.
