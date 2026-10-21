# my-workflow conventions

The rules every skill shares. Steps are defaults, not a script: skip, merge or reorder any step the
task does not need, and say which in one line. Numbers in a skill (counts, budgets, caps) are defaults
too: go past one when the task needs it, with the reason in one line. Rules worded "never" or "only
with a `D`" are not defaults.

## Ids and facts

- Ids only where a result will be referenced later; a small result uses plain bullets. `R<n>`
  requirement · `D<n> <decision> — <why>` · `Q<n> <question> — default: <answer>` · `T<n>` task ·
  `I<n>` issue. Assigned once, never renumbered; a dropped one stays as `R<n> dropped — <why>`. A
  choice still open is a `Q`, never also a `D`. Continue from the highest id already in the session or
  the given files.
- A fact carries its anchor: `path:line`, `doc §`, `url (date)` or `run: <command> → <result>`; not
  read → (inferred).

## Questions

At most 3 questions whose answers would change the result most, each with its default (any others
listed as defaults). An answered or defaulted `Q` becomes a `D` in place, keeping its id. Earlier
results (a spec, design or plan) come from the session or from files the user names; several versions
→ the latest; none → the request is the requirements. Inside an agent or another skill, return the
questions instead of asking them.

## Output

Markdown with short headings, one-line bullets and tables; an id leads its bullet; the why follows an
em dash; empty sections omitted. Return the result in the session and never save it as a file; whoever
runs the skill decides whether and where to keep it. Code, tests and scaffolding are the work itself,
not results, and go where they belong. End with `Open:` — what is still unresolved (questions, gaps,
requirements not done), or `Open: nothing`.

## Knowledge

Analysis and design name roles; a library or tool appears only where a step maps a role to it (an
option, a `D`, the tree, a "maps to" or "enforced by" column, the spec's Context). Names and code
follow the project's existing patterns first, then, for the question the step asks:

- Rules: the project's rules (CLAUDE.md, AGENTS.md, `.claude/rules`, ADRs) → one installed skill whose
  description names the detected stack and this step's phase (apply its rules only, never its
  procedure, output files or questions) → built-in knowledge.
- API facts: a documentation tool (MCP) at the detected version → official docs, dated → built-in,
  marked (built-in).
- Name the sources you used in the output.

## Diagrams

Mermaid `flowchart`, `sequenceDiagram` or `stateDiagram-v2` only; flowchart labels in double quotes,
ids `[A-Za-z0-9_]`. Directory trees in a `text` block. A table beside each diagram carries the
meaning.
