# Three-way reconciliation matrix

## Matrix format

Build one row per AC/NFR ID found across any of the three sources.

| AC-ID | Ticket | Spec | Code | Verdict | Reason | Evidence |
|-------|--------|------|------|---------|--------|----------|
| AC-1.1 | ✓ | ✓ | ✓ | Unchanged | — | `table.test.tsx:18` |
| AC-1.2 | old text | old text | new behavior | Changed | tweaked behavior | `table.test.tsx:34`, diff `src/Table.tsx:112` |
| AC-2.1 | — | — | ✓ | Added | added scope | `auth.test.tsx:55` |
| AC-1.3 | ✓ | ✓ | — | Dropped | descoped | no test; removed in diff |
| AC-3.1 | ✓ | stale text | ✓ | Spec-stale | spec not updated | `requirements.md:L42` vs `ticket` |

Columns:
- **Ticket / Spec / Code** — what that source says (or `—` if absent, `✓` if present and matching ground truth).
- **Verdict** — one of the five classes below.
- **Reason** — one of the reason categories below.
- **Evidence** — test name, `file:line`, or commit reference.

## Verdict classes

| Verdict | Meaning |
|---------|---------|
| **Unchanged** | All three sources agree; no action needed. |
| **Changed** | Behavior in code differs from the ticket text; ticket needs updating. |
| **Added** | Criterion exists in code (test asserts it) but is absent from the ticket. |
| **Dropped** | Criterion was in the ticket but is absent from code and no test covers it. |
| **Spec-stale** | Ticket and code agree but `requirements.md` is behind; offer to update the spec. |

## Reason categories

- **tweaked behavior** — deliberate mid-sprint change to how a criterion works.
- **UI design updated** — visual or interaction design changed (layout, labels, flows).
- **descoped** — criterion was explicitly cut from the sprint.
- **added scope** — new behavior shipped that was not in the original ticket.
- **bugfix correction** — the original criterion was wrong; code fixes the actual intent.

## Drift flag

For **Changed** and **Added** rows, assess intent: if the delta looks unintentional (no PR
comment, no design decision, no task note backing it), flag it as **possible unintended drift**
before proposing to rewrite the AC. Ask whether to fix the code instead.
