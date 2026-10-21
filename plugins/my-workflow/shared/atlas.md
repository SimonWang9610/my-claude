# Atlas format

How the code-auditor agent organizes grounded truths into an atlas. It reveals them in three levels:
`INDEX.md` (read first) → notes (opened when their keywords or outline match) → source (through the
notes' anchors). Write only inside the atlas folder.

## Files

- `INDEX.md` — this exact name, the only index. Notes: `<id>-<kebab-name>.md`, at the atlas root or in
  folders; each note has exactly one index row.

## INDEX.md

```markdown
# Atlas — <scope>

<purpose: the questions this atlas answers, one or two lines>
Audited: <date> at <commit>

## Start here
- <entry point> — <what it does> — `path:symbol`
- <the rule most likely to bite> — `path:symbol`

## Notes
| Note | File | Entry | Couples with |
|---|---|---|---|
| F1 <flow> | flows/F1-<name>.md | `path:symbol` | → F3 (writes <fact>) |
| S1 <structure> | structure/S1-<name>.md | `path:symbol` | ← F1, F3 (carries <fact>) |

## Gaps
- <area or flow not audited> — <why>
```

"Start here" has at most 5 lines. Couplings live only in the index.

## Note frontmatter (both shapes)

```markdown
---
id: F<n> | S<n>
title: <id> <flow or structure>
keywords: <2–3-word search terms, comma-separated>
outline: <what it solves, the shape of the solution, what it is not; 1–3 sentences>
---
```

## Flow note `F<n>`: a trigger → outcome

```markdown
## Trigger
<what starts it (user action, request, timer, event) and its guards>

## Inputs
- <fact> — <where it comes from: exact surface and shape> · <preconditions>

## Steps
1. <what data, from where to where, how> — `path:symbol`

## Outcomes
| Case | Result | State changed, where | Side effect at the boundary |
|---|---|---|---|
| success · error · empty · race · permission | … | … | <method + path + shape · table · key · event> |

## Dive
- `path:symbol` — <what deeper detail lives there>
```

Indirection: name the whole chain; open the hops the purpose needs, and box the rest with their
input and output shapes plus a Dive pointer.

## Structure note `S<n>`: a cross-cutting structure

```markdown
## Parts
<one Mermaid flowchart: participants and dependency direction, each node anchored>

## How a fact moves
<one Mermaid sequenceDiagram of the generic path, each hop anchored>

## Rules
- <who may depend on whom · where new code attaches · extension points> — `path:symbol` or (inferred)

## Dive
- `path:symbol` — <what deeper detail lives there>
```

## Every note

- Only facts that change what a reader does next; omit a section that does not apply.
- Untagged = read from source · (inferred) = deduced · (uncertain) = carries a Dive pointer.
- Deepen a note in place; never a second note for the same flow.

## Format check

```bash
find <atlas> -name '*.md'                                    # INDEX.md and exactly the indexed notes
grep -rL '^id: ' --include='*.md' <atlas> | grep -v INDEX.md  # must print nothing
```

Index rows and note files match one to one: a file with no row is unreachable; a row with no file is
wrong.
