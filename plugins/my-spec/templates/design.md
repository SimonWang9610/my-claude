# Design

`design.md`: only the sections the task needs, in this order. decide writes Approach and Product;
each part's skill writes its own section.

````markdown
# Design — <title>

spec: <path> · stack: <stack | not chosen>

## Approach

| option | how | pros | cons | effort S/M/L | risk (its failure) |
|---|---|---|---|---|---|

Recommendation: <option> — <why, ≤2 lines>; would change if <…>.

## Product

<flowchart: systems, edges labelled protocol + sync/async> · per system its responsibility · fact →
owner · boundaries: protocol, consistency, failure · scale axis · build vs buy · migration.

## Structure

## Components

## UI state

## Decisions

- D<n> <decision> — <why>
- Q<n> <question> — default: <answer>
````
