# my-workflow conventions

Rules every skill shares. Steps and numbers (counts, budgets, caps) are defaults: skip, merge, reorder
or exceed one when the task needs it, and say so in one line. Rules worded "never", "must" or "only
with approval" are not defaults.

## Facts

A fact carries its anchor: `path:line`, `path:symbol`, `doc §`, `url (date)` or
`run: <command> → <result>`. Not read → (inferred).

## Units

A unit is a function, method, class, module or component, shaped `Output = Unit(Input)`:

- **Input** — what it receives, and from which units.
- **Unit** — its own logic, and what it solely owns.
- **Output** — what it delivers, and to which units.

A unit may hold smaller units. Decompose until a human can understand one unit and take it over; no
further.

## Questions and decisions

- `Q-<n> <question> — default: <answer>` · `D-<n> <decision> — <why>`. An open choice is a `Q`, never
  also a `D`; answered or defaulted, it is recorded as a `D`. Numbered once, never renumbered; a
  small result uses plain bullets.
- Ask at most 3, the ones whose answers change the result most, each with its default; list the rest
  as defaults.
- Inside an agent or another skill → return the questions instead of asking.

## Output

Output tokens cost the most. Say each thing once, in the fewest words that stay exact.

- **Shape** — Markdown: short headings, one-line bullets, tables; an id leads its bullet; the why
  follows an em dash; empty sections omitted. Phrases over sentences; a table cell is a phrase.
- **Never** — a preamble, the request restated, a plan narrated before doing it, a closing summary,
  the same fact in two places.
- **Saved to a file** → never repeat it in the chat. Reply with: the path · the check's result line ·
  at most 5 lines the reader must decide or know.
- **Changing a file** → the smallest edit. Never rewrite a file to change a row or a status.
- **A command's output** → cite its result line; on failure, the failing lines only. Never paste it.
- **Between tool calls** → no narration; one line when the step changes.
- **Inside an agent** → return only the Outcome block its definition gives.

End with `Open:` — what is unresolved (questions, gaps, ids not
covered), or `Open: nothing`.

## Knowledge

Analysis and design name roles; a library or tool appears only where a step maps a role to it. Names
and code follow the project's existing patterns first. Then, where sources conflict, the earlier wins:

- **Rules** — the user's instructions → the project's rules (CLAUDE.md, AGENTS.md, `.claude/rules`,
  ADRs) → installed skills (in a spec: this step's `skills`, available not mandatory; else one whose
  description names the stack and this step) → built-in knowledge. Load them before working. Use an
  installed skill only where it serves the step: apply its rules, or run it for a section or check.
- **API facts** — a documentation tool (MCP) at the detected version → official docs, dated →
  built-in, marked (built-in).
- Name the sources used in the output.

## Diagrams

Mermaid `flowchart`, `sequenceDiagram` or `stateDiagram-v2` only; labels in double quotes; node ids
`[A-Za-z0-9_]` (a unit: `UNIT_1["UNIT-1 <name>"]`). An arrow points at what a unit depends on.
Directory trees and wireframes in a `text` block. A table beside each diagram carries the meaning.
