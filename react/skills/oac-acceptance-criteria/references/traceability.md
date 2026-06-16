# AC → test traceability — making coverage a runnable query

Stable AC IDs flow from `requirements.md` into Vitest test names so "is AC-X.Y covered?"
is a grep, not a manual audit. No BDD framework needed — the discipline is in the naming.

## 1. Naming convention

Embed the AC ID at the start of the `describe` string; mirror the criterion's
Given/When/Then so the test name reads as the behaviour.

```ts
// requirements.md:
//   AC-14.3: Given the table is rendered, when the user clicks a column header,
//            then rows sort by that column and the header shows the sort direction.

// table.test.tsx:
describe('AC-14.3: clicking a column header sorts rows by that column', () => {
  it('sorts ascending and marks the header aria-sort=ascending on first click', () => {
    // action then observable assertion
  })
})
```

The ID at the front makes coverage greppable: a CI step can scan for `AC-14.3` across the
test tree and find exactly the test(s) that claim to cover it.

## 2. Optional: Vitest native test tags

Vitest's `--tags-filter` lets you label tests and filter with logical operators
([vitest.dev](https://vitest.dev/guide/test-tags)). Tags complement the named description:
the description carries the human-readable AC; the tag carries the machine-queryable ID.

```ts
it(
  'sorts ascending on first header click',
  { tags: ['AC-14.3'] },
  () => { /* ... */ },
)
```

```bash
# Does any test claim to cover AC-14.3?
vitest run --tags-filter 'AC-14.3'

# Run every test for story 14 before merging a change to that feature
vitest run --tags-filter 'AC-14.*'
```

Requires Vitest 1.3+. Tags are optional — the ID-in-describe convention alone is enough.
Use tags when the team wants `--tags-filter` queries in CI; be consistent within a spec.

## 3. Downstream gate

The task-breakdown phase generates one test task per AC ID. The test-contract rule
requires every `describe`/`it` in a new or modified test file to name the AC or NFR ID it
covers. The validation phase then counts AC IDs in `requirements.md` against AC IDs in
passing test names — any AC with no mapped passing test is a blocking FAIL.

```
requirements.md  →  AC-14.3
      │
      ▼
tasks.md         →  "test task: cover AC-14.3"
      │
      ▼
table.test.tsx   →  describe('AC-14.3: ...')
      │
      ▼
validate gate    →  count(AC IDs in reqs) == count(AC IDs covered by green tests)
```

Success signal: **unmapped-AC count → 0 at the validation phase.**
