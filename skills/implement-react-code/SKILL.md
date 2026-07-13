---
name: implement-react-code
description: >
  Guides writing React code at any scope with level-specific rules
  for components, hooks, stores, and other classes.
---

# implement-react-code

Implementation altitude: write the code that satisfies the requested behaviour, inside whatever
boundaries govern it. The governing decision decided _what_; you decide _how_. When the _what_ fails at code level, classify and raise — never widen an API, move state ownership, or cross a boundary silently.
With no formal design in force, raise the same block against the caller's request or the
codebase convention it conflicts with.

## Instructions

1. **Scope the work.** From the input — task(s), issue, request, diff — establish: the units to
   touch, the behaviour expected of each, and the constraints in force (contract fields, design
   decisions, or the conventions visible in the code). Read the target files and their imports
   first; **reuse** the existing component/hook/type/query-key/store-slice — never add a second
   one. Check once whether `babel-plugin-react-compiler` is configured — it inverts all
   manual-memoization advice.
2. **Implement by level.**
   - distinguish the task levels, and consult [How to use the rules](#how-to-use-the-rules) to pick the right rule cards for each: component, hook, store, service/manager class
   - obey the picked rules, and the governing decisions, for each level touched.
   - raise a [design-gap protocol](#design-gap-protocol) with evidence when a governing decision is ambiguous, missing a case, or provably wrong — never silently deviate, never blindly implement a defect.
3. **Self-review the diff.** Rescan every changed unit against its levels' cards, then against
   whatever done-condition applies — the task's gate when one exists; otherwise typecheck, the
   relevant tests, and the constraints from step 1.
   - Flag only real regressions on live paths.
   - If tests define the expected behaviour, make the code satisfy them
   - NEVER rewrite a test to make failing code pass.
4. **Verify** check whether all tasks are complete, and that the diff is ready for hand-off. A task is complete when its gate passes, and the diff is ready for hand-off when every changed unit passes its levels' rules and the done-condition from step 3.

## How to use the rules

The rules live as one-card-per-rule files, grouped by the **level** of the code being written.
Each card is self-contained: YAML front-matter (`title` · `impact` CRITICAL/HIGH/MEDIUM/LOW ·
`impactDescription` · `tags`), the one-sentence rule, and a CORRECT + BAD example.

| Directory                                         | Open when writing or altering                                   |
| ------------------------------------------------- | --------------------------------------------------------------- |
| [general-rules/](./references/general-rules/)     | anything — cross-cutting disciplines (type honesty)             |
| [component-rules/](./references/component-rules/) | JSX render output, props, composition, what ships in the bundle |
| [hook-rules/](./references/hook-rules/)           | any hook body — effects, derived values, query/mutation wiring  |
| [store-rules/](./references/store-rules/)         | a Zustand store's shape/actions, or any component consuming one |
| [service-rules/](./references/service-rules/)     | a plain-TS service/manager class, or its React bridge           |

**Most changes are mixed-level.** A unit is governed by every level it participates in — a
filtered-list feature touches component-rules (render states, list size), hook-rules (query
wiring, derived values), and store-rules (selector discipline) at once. Walk the levels the diff
actually touches; skip the rest.

**Prioritize by front-matter.**

- `impact: CRITICAL/HIGH` cards are non-negotiable — check every one whose level you touch.
- `MEDIUM` cards apply where the code touches their concern; `LOW` are opportunistic.
- Cards tagged `hot-path` bind only when the path is hot (per-frame, large list, main
  interaction) — write clear code first; never pre-optimize a cold path.
- Tags are searchable: working on a mutation → grep the cards for `tags:.*mutation`; chasing a
  re-render → `tags:.*rerender`.

**When two cards collide** (e.g. a memoization card vs. the compiler check from step 1), the
correctness card wins over the performance card, and the project-level fact wins over the
generic advice.

## Design-gap protocol

Raise a block when a governing decision is ambiguous, missing a case, or provably wrong. Wait for human instructions before continuing. Never silently deviate, never widen an API, move state ownership, or cross a boundary.

| Gap           | Looks like                                                                                                                     | Do                                                                                            |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| **Ambiguity** | the spec is silent on a case you must handle (a state, an input, an error path)                                                | implement the **narrowest safe interpretation**, and raise the gap for the spec to be amended |
| **Friction**  | the decision makes the code fight — a seam missing, responsibilities tangled where you must edit                               | don't force it with a hack; raise it as a re-design candidate                                 |
| **Defect**    | the decision is provably wrong at the tech level — e.g. a per-frame value assigned to a store, a mechanism the library removed | **stop; don't implement a known defect.** Raise it with evidence                              |

**Raising a gap** — one block, attached to the result:

```markdown
DESIGN GAP — <unit> · <ambiguity | friction | defect>
Decision says: <the contract/design/spec line — or the convention observed>
Code shows: <the concrete evidence — file:line, API doc, measured behaviour>
Suggestion: <the amendment>
Status: <implemented narrowest-safe | blocked pending decision>
```
