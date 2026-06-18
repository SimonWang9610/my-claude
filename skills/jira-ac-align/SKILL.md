---
name: jira-ac-align
description: >
  Performs a three-way reconcile of a JIRA ticket's acceptance criteria against the spec
  (requirements.md) and the shipped implementation (test assertions + branch diff), then
  updates the ticket description with accurate AC and posts a single alignment-notes comment.
  Trigger when a ticket's AC is stale after mid-development requirement changes: e.g.
  "align the ticket with the implementation", "the JIRA ticket is out of date",
  "update the ticket's acceptance criteria", "reconcile AC with what we built",
  "the ticket description doesn't match the code", "sync the ticket to reality".
---

# jira-ac-align

Three-way reconcile across ticket, spec, and code — then update the JIRA ticket description
(reconciled AC only, clean) and post alignment notes as a single comment. Confirm-first;
never write without approval.

## Workflow

1. **Resolve the ticket.** Key from: explicit arg → else `.specflow/specs/<name>/.meta.yaml`
   `jira_issues:` → else infer from the branch name (e.g. `ACMT-86` in `feat/ACMT-86-...`).
   Fetch via `getJiraIssue` (resolve `cloudId` at runtime via `getAccessibleAtlassianResources`).
   Confirm the issue type is **Story or Bug** — reject Epics, Sub-tasks, Tasks. If no key is
   resolvable, ask.

2. **Gather the three AC sources** (→ `references/reconciliation.md` for the matrix format):
   - **Ticket AC** — parse the acceptance criteria out of the current ticket description.
   - **Spec AC** — `.specflow/specs/<name>/requirements.md` AC-/NFR- IDs and their
     Given/When/Then text, if the file exists.
   - **Implementation AC (ground truth)** — grep test files for `describe('AC-…')` /
     `it('AC-…')` (or equivalent per stack) to find what each test asserts as observable
     behavior; also read the branch diff (`git diff <base>..HEAD`, base = merge-base with the
     repo default branch) for behavior actually shipped.

3. **Three-way reconcile** — build a per-criterion matrix across {ticket, spec, code}; classify
   each row (Unchanged / Changed / Added / Dropped / Spec-stale) with evidence (test name,
   file:line) and a reason category (tweaked behavior / UI design updated / descoped / added
   scope / bugfix correction). See `references/reconciliation.md`.

4. **Compose two outputs** per `references/description-template.md`:
   - **(a) Ticket description** — preserve all non-AC content from the original description
     (background, links, context) verbatim; replace only the Acceptance Criteria section with
     the reconciled, accurate AC (stable IDs, Given/When/Then, observable Then clauses). Keep
     it clean — no changelog, no alignment notes, no audit trail in the description.
   - **(b) Alignment-notes comment** — one bullet per non-Unchanged delta in the form
     `AC-x.y — <Verdict>: <what changed> (<reason>)`, with
     `[flag: possible drift — verify intent]` inline where the delta looks unintended.

5. **Human gate — confirm first.** Present both the proposed description (AC section only,
   clean) and the proposed alignment-notes comment. Do **not** write to JIRA until the user
   approves.

6. **Write — two calls, in order:**
   - Call `editJiraIssue` to set the description field (reconciled AC only; no alignment notes).
   - Call `addCommentToJiraIssue` to post the alignment-notes comment.
   Report both writes. If the three-way found spec drift, offer to also update
   `.specflow/specs/<name>/requirements.md` locally.

## Inputs

- **Ticket key** (optional) — e.g. `ACMT-86`; if omitted, resolved from `.meta.yaml` or branch.
- **Spec name / path** (optional) — `.specflow/specs/<name>/`; skipped gracefully if absent.
- **Diff base branch** (optional) — defaults to merge-base with the repo default branch.

## Output

Updated ticket description (reconciled AC, clean) + one alignment-notes comment — both
written after approval — plus a short reconciliation summary. Optionally a local
`alignment.md` if the user wants a durable record.

## Rules

- **Confirm-first.** Present both proposed outputs (description AC section and alignment-notes
  comment) and wait for approval before any JIRA write. Exactly two writes: `editJiraIssue`
  for the description, then `addCommentToJiraIssue` for the notes. Never touch status, labels,
  or custom fields. The description stays clean — the audit trail belongs in the comment.
- **Preserve non-AC content.** All non-AC content in the original description (background,
  links, context) is carried over verbatim; only the Acceptance Criteria section is replaced.
- **Do not blindly enshrine drift.** If a Changed or Added delta appears unintentional rather
  than a deliberate tweak, flag it and ask whether to fix the code instead of updating the AC.
- **Keep AC IDs stable.** Append new IDs at the end; never renumber existing ones. Renumbering
  silently breaks every `describe('AC-x.y …')` test name that references the old ID.
- **Stack-agnostic.** Works with or without a specflow spec; works with any test runner —
  grep for the `AC-<story>.<n>` pattern in test file describe/it strings regardless of framework.

## References

- [references/reconciliation.md](references/reconciliation.md) — three-way matrix format,
  verdict classes, and reason categories.
- [references/description-template.md](references/description-template.md) — clean JIRA
  description layout (reconciled AC only) and the alignment-notes comment format with a
  worked example.
