# my-workflow conventions

Steps and numbers are defaults: skip, merge or exceed one when the task needs it, saying so in one
line. "Never", "must" and "only with approval" are not defaults.

- **Facts** — each carries an anchor: `path:line`, `path:symbol`, `doc §`, `url (date)` or
  `run: <command> → <result>`. Not read → (inferred).
- **Units** — a function, class, module or component, shaped `Unit = F(Unit_A, Unit_B, …)`: the
  units it depends on and what it takes from each · the logic `F` it solely owns · what it provides
  for others to depend on. Decompose until a human can take one unit over; no further.
- **Grounding** — read existing code the cheapest way that gives an anchored fact, and say which in
  one line. An atlas exists (a spec's `atlas`, or one named) → `/my-workflow:audit-truth query`,
  first. None → grep and read; a search likely to open more than 3 files → the
  `my-workflow:code-scout` agent, every open question in one call (no agent tool → search
  yourself): open only the anchors a decision rests on, and mark a fact you did not open (scout).
  A design that builds on or changes 3 or more existing units, an improvement to existing units,
  or a question about how units work together → `/my-workflow:audit-truth build`.
- **Questions** — `Q-<n> <question> — default: <answer>`; answered → `D-<n> <decision> — <why>`. Ask
  at most 3, those that change the result most; give the rest as defaults. Inside an agent, or a
  skill called for part of another skill's step → return them.
- **Knowledge** — the project's existing patterns first. Rules: the user → project rules (CLAUDE.md,
  AGENTS.md, `.claude/rules`, ADRs) → installed skills naming this stack and step → built-in. API
  facts: documentation at the detected version, dated.
- **Diagrams** — Mermaid `flowchart`, `sequenceDiagram` or `stateDiagram-v2`; labels in double
  quotes; node ids `[A-Za-z0-9_]` (`UNIT_1["UNIT-1 <name>"]`); an arrow points at what a unit depends
  on. More than 6 nodes → an overview of groups plus one diagram per group; in a design `spec-check`
  enforces it. Trees and wireframes in
  a `text` block.

## Output

Output tokens cost the most: say each thing once, in phrases.

- **Needs you** — a question, choice, approval, conflict or correction goes in the reply itself,
  first, under that bold line; one line per item: what to decide · options or default · what waits.
  A file records; it never asks.
- Short headings, one-line bullets; an id leads its bullet; the why after an em dash; empty sections
  omitted.
- A table only when every cell is a few words; else a sub-section per item with `**Label:** value`
  lines.
- No preamble, restated request, narrated plan or closing summary; no narration between tool calls.
- Saved to a file → reply with its path, the check's result line and at most 5 lines; never its
  content.
- Change a file with the smallest edit. Cite a command's result line; never paste its output.
- Inside an agent → send back only what its prompt's Send back line asks; none → what its definition
  says.
- End with `Open:` what is unresolved, or `Open: nothing`.
