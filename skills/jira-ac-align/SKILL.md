---
name: jira-ac-align
description: >
  Reconcile a completed (and tweaked) implementation against its JIRA ticket and update
  the ticket's acceptance criteria to reflect what was actually built. Use after a ticket's
  implementation is done but requirements were adjusted mid-development, leaving the JIRA
  ticket stale. Triggers: "align the ticket with the implementation", "the JIRA ticket is
  out of date", "update the ticket's acceptance criteria", "reconcile AC with what we built",
  "the ticket description doesn't match the code anymore", "sync the ticket to reality".
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

6. **Write — two writes, in order:**
   1. Set the description via `editJiraIssue` (description field, reconciled AC only — no
      alignment notes).
   2. Post the alignment notes as a **single comment** via `addCommentToJiraIssue`.
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

- **Confirm-first** before any JIRA write. Two writes only: the description (reconciled AC)
  via `editJiraIssue`, then ONE alignment-notes comment via `addCommentToJiraIssue`. Never
  touch status, labels, or custom fields. Keep the description clean — the why-it-changed
  audit lives in the comment, not the description.
- **Preserve non-AC description content** — background, links, acceptance notes outside the
  AC section. Never nuke the ticket.
- **Don't blindly enshrine drift.** If a Changed or Added delta looks like unintended drift or
  scope creep — not a deliberate tweak — flag it and ask whether to fix the code instead of
  rewriting the AC.
- **Keep AC IDs stable.** Append new IDs; never renumber. Renumbering breaks test traceability
  (every `describe('AC-x.y …')` in the test tree becomes a dangling reference).
- **Stack-agnostic.** Works with or without a specflow spec; works with any test runner
  (grep for the AC-ID pattern in test file names/describe strings regardless of framework).

## References

- [references/reconciliation.md](references/reconciliation.md) — three-way matrix format,
  verdict classes, and reason categories.
- [references/description-template.md](references/description-template.md) — clean JIRA
  description layout (reconciled AC only) and the alignment-notes comment format with a
  worked example.
