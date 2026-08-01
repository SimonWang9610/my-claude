# JIRA output templates

Two separate writes. Description is clean AC only; alignment audit goes in a comment.

---

## Part 1 — Description layout

Preserve all non-AC content from the original description verbatim. Replace only the
Acceptance Criteria section. No alignment notes, no changelog, no audit trail here.

```
<original non-AC content — background, links, context — preserved verbatim>

---

## Acceptance Criteria

[ ] AC-1.1: Given <precondition>, when <action>, then <observable result>.
[ ] AC-1.2: Given <precondition>, when <action>, then <observable result>.
...

[ ] NFR-1: Given <condition>, when <trigger>, then <measurable system behavior>.
```

### AC section rules

- Every criterion uses `AC-<story#>.<n>` or `NFR-<n>` ID, stable and unique.
- Phrasing: Given/When/Then; Then clause is user-observable (no internal calls or state).
- New criteria from implementation get the next available IDs appended — never renumber
  existing IDs (renumbering silently breaks `describe('AC-x.y …')` test names).

---

## Part 2 — Alignment-notes comment

Posted as a single comment via `addCommentToJiraIssue` after the description is updated.

```
Acceptance-criteria alignment — <date>

- AC-x.y — <Verdict>: <what changed> (<reason>)
- AC-x.z — <Verdict>: <what changed> (<reason>) [flag: possible drift — verify intent]
```

### Comment rules

- One bullet per non-Unchanged verdict.
- Format: `AC-x.y — <Verdict>: <what changed> (<reason>)`.
- Append `[flag: possible drift — verify intent]` inline for any Changed or Added delta that looks unintended.

### Worked example

```markdown
Acceptance-criteria alignment — 2026-06-16

- AC-1.2 — Changed: sort now defaults to descending on first click, not ascending (tweaked behavior)
- AC-2.1 — Added: empty-state message when no results match the filter (added scope)
- AC-1.3 — Dropped: bulk-select was descoped; no test coverage, removed from diff (descoped)
- AC-3.1 — Spec-stale: ticket and code agree; requirements.md still has old phrasing (spec not updated)
```
