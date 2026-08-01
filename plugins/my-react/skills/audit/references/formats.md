# formats — the atlas artifact contracts

Every writing mode (build · distill · query's heal) conforms to these; finish any write
with the **Format check** below.

## Files

**Location:** `atlas/` lives under the **invoking project** (the current workspace — e.g.
its spec dir), even when the audited code is elsewhere: auditing project A from workspace
B → `atlas/` under B. A caller-designated directory overrides.

`atlas/INDEX.md` — the always-loaded routing tier; this exact name, never README.md or
SUMMARY.md (a differently named file is never read). Notes may sit at the atlas root or in
nested folders (`flows/`, `arch/`, a domain per folder — whatever aids navigation), but
**INDEX.md is the single manager**: every note has exactly one Index row carrying its
relative path; no per-folder indexes. One file per note, named `<id>-<short-name>.md` —
the id plus a meaningful kebab name (`F3-device-selection.md`, `A1-state-management.md`).

**The envelope never varies** — file naming + frontmatter are identical for both note
shapes; only the body sections differ. Frontmatter is functional, not style: query routes
by grepping `^(id|title|keywords|outline):` recursively, so a note without it is invisible
to every downstream query.

## `INDEX.md`

````markdown
# Atlas
<scope>
<purpose — one or two lines>

## Index
| Note | Kind | File | Entry anchor | Units touched | Couples with |
|------|------|------|--------------|---------------|--------------|
| F1 <name> | existing | flows/F1-device-selection.md | `path:symbol` | <units> | → F3 (invalidates <fact>) |
| A1 <structure> | existing | arch/A1-state-management.md | `path:symbol` | <units> | ← F1, F3 (carries <fact>) |

## interaction map
<mermaid: nodes = notes, labeled edges = coupling + direction; hub units several flows
couple through flagged — widest change radius. Omit under 2 interacting notes. Too big for
one readable diagram → split smartly into several (by connected component, domain, or
around a hub), each titled one line; a note appears in every diagram it couples into.>

## Gaps
<what wasn't audited and why, one line each>
````

## Note frontmatter — identical for both shapes

````markdown
---
id: F<n> | A<n>
title: <id> <flow or structure>
keywords: <query keywords, 2-3 words each, comma-separated>
outline: <what it solves + solution shape, when useful, what it is not; 1-3 sentences>
source: <omit if audited from source; `distilled from <path>` if from an external atlas>
---
````

## Bodies — facts in the fewest lines; omit an inapplicable section

**Feature note** `F<n>` — a trigger→outcome flow:

````markdown
## GIVEN
per fact: origin (surface + shape) · preconditions (auth · flag · prior flow) · initial state
## WHEN
trigger (user action · timer · external event · state change) + guards
## THEN
per case (happy · error · empty · race · permission): outcome · state changed + where · propagation
## HOW
transforms per hop · side effects (exact surface: method+path+body · storage key · event) ·
mechanism per hop; indirection names the full chain (config origin → interpreter →
collector → submission), each hop anchored, opened or boxed
````

**Architecture note** `A<n>` — a cross-cutting structure or mechanism:

````markdown
## STRUCTURE
a mermaid `graph` (REQUIRED): participants + dependency direction, each node anchored
`path:symbol`; prose only for what the diagram can't carry
## MECHANISM
how a fact travels the structure — a mermaid `sequenceDiagram` of the generic pathway
(REQUIRED; e.g. component → hook → apiClient → interceptor), per hop anchored; the exact
boundary surfaces it crosses
## RULES
invariants the structure enforces (who may depend on whom · where a kind of code attaches ·
extension points for new work), each anchored or tagged `(inferred)`
````

**Shared tail** (both shapes):

````markdown
## Dependents / Verdict       <!-- existing only -->
external importers · REUSE | MODIFY | REPLACE — one-line reason (a proposal; the caller confirms)
## Preserve / drop            <!-- legacy only -->
behaviors kept vs deliberately dropped
## Self-audit pointers
`path:symbol` — what deeper detail lives there + which decision needs it
````

## Format check — mechanical, after any write

Fix every violation before returning — a malformed atlas silently defeats query routing:

```bash
find atlas -name '*.md'                                      # INDEX.md + exactly the indexed notes
grep -rL '^id: ' --include='*.md' atlas | grep -v INDEX.md   # must print nothing
```

Index rows ↔ note files one-to-one (each row carries its File path) — a file with no row
is unreachable; a row with no file is a lie.
