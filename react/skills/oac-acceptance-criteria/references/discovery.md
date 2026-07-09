# Discovery — Example Mapping, glossary, and Examples-table ACs

Discovery runs *before* acceptance criteria are locked. It is an authoring technique, not a
tool — no Gherkin, no `.feature` files, no runner. Its output feeds the existing
`AC-<story>.<n>` pipeline: examples become ACs, open questions are returned to the caller, and the
glossary keeps requirements, design, and tests speaking one vocabulary.

## 1. Example Mapping — run it per story

For each user story, enumerate four kinds of card:

- **Story** — the user story (`US-<n>`: As a … I want … so that …).
- **Rules** — the business rules / acceptance constraints that govern the story.
- **Examples** — concrete, observable instances of each rule: the happy path, the edge cases,
  and the counter-examples (what must *not* happen).
- **Questions** — anything unknown or contested that blocks writing a confident example.

Work rule-by-rule: state a rule, then make it concrete with examples. If you cannot give a
concrete example for a rule, that gap is a **Question**, not an example — write it down.

"Enough" = every rule has ≥1 example, and every example is phrased as an observable outcome
(what the user sees, or a value a consumer reads), never an internal step.

### Worked sketch — US-2 "Add a device"
- **Rule:** a device name must be unique within the scope.
  - *Example (happy):* add "Door A" to a scope with no "Door A" → it appears in the list.
  - *Example (counter):* add "Door A" when one exists → inline error "Name already in use"; no device added.
- **Rule:** the add form opens empty.
  - *Example:* click "Add Device" → the drawer opens with all fields blank.
- **Question:** is name uniqueness case-sensitive? → flag as an open question.

## 2. Examples → acceptance criteria

Each example becomes one `AC-<story>.<n>` in the observable Given/When/Then form
(→ `ac-format.md` §3). The example *is* the AC body; Example Mapping just ensures you found
all of them — happy, edge, and counter — before numbering. This is how edge and negative
coverage is captured at authoring time instead of being deferred to task-breakdown.

## 3. Open questions → surface, don't guess

Do not guess past a Question. Return every unresolved Question to the caller, and write its
example (and the AC) only once it's answered. During discovery you only surface the gap into
`## Open questions`; ranking and settling contested/ambiguous/untestable criteria happens in the
Hard-checks step (rank by Impact × Uncertainty, settle with the caller, then rephrase or record).

## 4. Ubiquitous language — a small glossary

Capture the feature's domain terms, one definition each, in a **Glossary** section of
`requirements.md`. Use those exact terms — verbatim — in ACs, `design.md`, contracts, and test
names. One word per concept, no synonyms; this is what stops "scope" / "site" / "group"
drifting across artifacts.

| Term  | Definition |
|-------|------------|
| Scope | A logical grouping of devices an operator administers. |
| Door  | A single access-controlled entry point. |

## 5. Examples-table ACs (data-varying behaviour)

When one rule has many examples that differ only by data, write **one** parameterized AC plus a
table instead of many near-duplicate ACs. Each row still expands to its own named test.

```
AC-5.1: Given a cart holding <items>, when checkout runs, then the order total shows <total>.

| items      | total  |
|------------|--------|
| (empty)    | $0.00  |
| 1 × $5.00  | $5.00  |
| 2 × $5.00  | $10.00 |
```

Test naming keeps the ID grep-able: `describe('AC-5.1 [items=2×$5.00]: total shows $10.00', …)`.
Coverage stays a grep on `AC-5.1`.
