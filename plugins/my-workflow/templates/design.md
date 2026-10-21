# Design template

A design: the recommendation, then only the sections the task needs, in this order. decide returns
the Recommendation, Approach, Product, Contracts and data, and Quality; each part's skill returns its
own section. At most one diagram and one table per section.

```markdown
# Design — <title>

**Recommendation:** <one line> — would change if <…>.
Spec: <path | session | none> · Stack: <stack | open>

## Approach
| Option | How | Pros | Cons | Effort (S/M/L) | Risk if it fails |
|---|---|---|---|---|---|

## Product
<flowchart of systems; edges labelled with protocol and sync or async>
- <system> — <responsibility>; owns <facts>
- Boundaries: <protocol, consistency, failure>; scale axis; build or buy; migration

## Structure

## Components

## Contracts and data
| Boundary | Shape and version | Errors and failure | Data owner |
|---|---|---|---|
- Migration: <steps, each shippable alone, and the rollback>

## UI state

## Quality
- <axis the spec's limits name> — <how the design meets it>

## Decisions
- D<n> <decision> — <why>

## Open questions
- Q<n> <question> — default: <answer>

Open: <questions, and any requirement that must change — or nothing>
```
