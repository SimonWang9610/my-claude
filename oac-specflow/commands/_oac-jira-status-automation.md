# _oac-jira-status-automation

> ## ⚙️ THE PER-PROJECT ADAPTATION POINT
> **This is the one deliberately project-specific file in the bundle.** Everything else
> (commands, skills, rules, agent) is general React 19 + Vite + TypeScript + Zustand +
> TanStack Query + MUI + Vitest practice and ships unchanged. This file is the seam where
> the general flow plugs into *your* project's issue tracker. The example below is wired to
> a Jira project keyed `ACMT` with a specific status workflow; **rewrite it for your tracker**
> — Jira with a different project key/workflow, Linear, GitHub Issues, or no tracker at all.
> If your project has no tracker integration, delete this file and the Step 0/Step 1 sections
> of `oac-spec-implement` become no-ops. Treat the status names, project key, issue types, and
> automation rules below as a worked example to replace, not as fixed framework behavior.

Shared status-transition playbook for the oac-specflow commands that move work through an issue tracker (here: the Jira `ACMT` workflow). **Not a runnable slash command** (prefix `_`); `oac-spec-implement` (and, read-only, `oac-spec-qa`) reference this file.

> **Why this file is bundled here.** It keeps the oac-specflow bundle self-contained —
> `oac-spec-implement` Step 0/Step 1 can link and transition tracker issues without depending on
> a file that lives only in the project repo. The `oac-spec-*` command names are referenced
> directly; the workflow semantics (issue types, status map, monotonic guard, primitives) are an
> illustration to adapt. Re-sync this copy whenever the project's tracker workflow changes.

---

## Hierarchy / unit of work

Specflow work in ACMT is tracked at the **Story** or **Bug** level — collectively the "issue" this playbook acts on:

```
Epic              (product-owned, status driven manually)
 └── Story / Bug  (product-owned, status driven by automation + commands below)
```

- One Story (or Bug) = one unit of work for one dev.
- One PR per issue is the target (1:1 ideal; 1:many is allowed when work genuinely spans multiple issues).
- Sub-tasks are **not used** — every transition acts directly on the Story or Bug.
- Epics, Sub-tasks, and Tasks are still rejected by automation. Only **Story** and **Bug** are valid issue types.

## Status map (ACMT)

Only the seven statuses below are touched by automation. **Hands-off statuses** are: `Product Review`, `Blocked`, `Ready for Pre-Prod`, `Pre-Prod`, `Pre-Prod Testing`. Automation must never move an issue into or out of those — they're for product/release management.

| Logical name | ACMT status name (case-sensitive) | Category | Driven by |
|---|---|---|---|
| `todo` | `To Do` | To Do | Jira default (initial) |
| `dev` | `Dev In Progress` | In Progress | `/oac-spec-implement` (this bundle) |
| `pr` | `Pull Request (PR)` | In Progress | **Jira automation rule** (admin-configured) |
| `staging` | `In Staging / Ready for QA` | In Progress | **Jira automation rule** (admin-configured) |
| `qa` | `QA In Progress` | In Progress | manual — human only; no automation ever transitions to this status |
| `release-ready` | `Release Ready` | In Progress | manual (or PR-footer force) |
| `done` | `Released-Done` | Done | manual (future: release-tag hook) |
| `wont-do` | `CLOSED - WONT DO` | Done | manual (or PR-footer declaration) |

Transition IDs are resolved per-issue at runtime via `getTransitionsForJiraIssue` — do **not** hardcode IDs in command logic; match by `name`.

## Ordering (for the monotonic guard)

```
todo (0)
  → dev (1)
  → pr (2)
  → staging (3)
  → qa (4)
  → release-ready (5)
  → done (6)
```

`wont-do` is off-axis. A Story already at `wont-do` is terminal — never automate transitions out.

## The primitive: `transitionIssue(issueKey, target)`

Used by every oac-spec command that touches Jira status. Pseudocode:

```
transitionIssue(issueKey, target):
  issue = getJiraIssue(issueKey, fields=[status, issuetype])
  if issue.issuetype.name not in {"Story", "Bug"}:
    abort and surface — automation must only touch Stories or Bugs
  if issue.status in {handsOff}:
    no-op and log — issue is frozen by product/release
  if issue.status == "wont-do":
    no-op — terminal state
  if rank(issue.status) >= rank(target):
    no-op — monotonic, forward-only, never reverse

  transitions = getTransitionsForJiraIssue(issueKey)
  id = transitions.find(t => t.name == nameFor(target)).id
  if not id:
    abort and surface — workflow drift, transition unavailable from current state

  transitionJiraIssue(issueKey, id)
```

**Forward-only.** This primitive only moves issues forward in the ordering. Never reverse, never skip into a hands-off bucket, never re-fire if target equals current.

> The `getJiraIssue` / `getTransitionsForJiraIssue` / `transitionJiraIssue` primitives are the Atlassian MCP tools available in the target environment. They take a `cloudId` for the ACMT site; resolve it at runtime (e.g. via `getAccessibleAtlassianResources`) rather than relying on a hardcoded literal.

## How issues get associated with a spec

`/oac-spec-implement` is responsible for capturing the issue key(s). On first run for a spec, if `.meta.yaml` does not yet contain a `jira_issues:` field, `/oac-spec-implement`:

1. Scans the spec docs (`requirements.md`, `clarify.md`, `design.md`, `tasks.md`) for `ACMT-\d+` references and surfaces them as **suggestions — never auto-accept**.
2. Asks the user which issue (or issues, in the 1:many case) this spec maps to. At least one key required; abort if user provides none.
3. Validates each via `getJiraIssue` — the issue must exist and have `issuetype.name in {"Story", "Bug"}`. **Reject Epics, Sub-tasks, Tasks** (abort cleanly).
4. Writes the keys to `.meta.yaml`:
   ```yaml
   jira_issues:
     - ACMT-86   # Story or Bug
   ```
5. Proceeds with the `transitionIssue(<key>, dev)` call.

Subsequent runs read `jira_issues:` from `.meta.yaml` and skip the prompt.

`/oac-spec-qa` reads the same field and aborts with an actionable message if it's missing — but it never calls `transitionIssue` (QA transitions are human-only).

> Back-compat: if a spec still has the legacy `jira_stories:` key, commands should read it as a synonym for `jira_issues:` (no rewrite required, but new specs use `jira_issues:`).

## Trigger map

| Trigger | Implementation | Target |
|---|---|---|
| `/oac-spec-implement` starts on a spec | Command (this bundle) calls `transitionIssue(<key>, dev)` for each issue listed in `.meta.yaml` | `dev` |
| Dev opens a PR referencing an ACMT issue key (Story or Bug) | **Jira automation rule** (admin-configured) | `pr` |
| PR merged to default branch | **Jira automation rule** (admin-configured) | `staging` |
| QA engineer begins QA | Manual — human sets `QA In Progress` in Jira; `/oac-spec-qa` reads issue status as context but never calls `transitionIssue` | `qa` |
| QA passes | Manual — human disposition step at end of `/oac-spec-qa` | `release-ready` |
| Released | Manual (future: release-tag hook) | `done` |
| De-scoped | Manual, or via PR-footer declaration | `wont-do` |

## Jira automation rules — admin setup

The PR-open and PR-merge transitions are **not** driven by these commands; they live in Jira project ACMT's Automation settings (Project settings → Automation):

- **PR opened** → `Pull Request (PR)` — trigger *Development → Pull request created*; conditions: linked issue project `ACMT`, type in (`Story`, `Bug`), status in (`To Do`, `Dev In Progress`).
- **PR merged** → `In Staging / Ready for QA` — trigger *Development → Pull request merged* (branch `main`); conditions: linked issue project `ACMT`, type in (`Story`, `Bug`), status in (`Dev In Progress`, `Pull Request (PR)`).

Both rely on the Atlassian-for-GitHub integration so PR events reach Jira and `ACMT-N` keys in PR title/body/branch/commits resolve. If your project does not have these rules, the `pr`/`staging` transitions must be applied manually — this bundle never fires them.

## PR-description footer (escape hatch)

For cases automation can't handle, the dev declares intent in the PR body:

```
<!-- jira-transitions -->
Issues: ACMT-500 → release-ready (force)
Issues: ACMT-499 → wont-do
```

- `Issues: <key> → release-ready (force)` — used when QA / staging is being skipped intentionally. Rare. Justify in PR description.
- `Issues: <key> → wont-do` — the only way automation will move an issue to `CLOSED - WONT DO`.
- The legacy header `Stories:` is still accepted as a synonym for `Issues:`.

The **force** flag temporarily relaxes the monotonic guard for that one transition.

## What is **not** automated

| Trigger | Why |
|---|---|
| `Product Review`, `Blocked`, `Ready for Pre-Prod`, `Pre-Prod`, `Pre-Prod Testing` | Product / release management. Automation never touches. |
| `In Staging / Ready for QA` → `QA In Progress` | Human-only. The QA engineer sets this manually; `/oac-spec-qa` reads status as context but never transitions. |
| QA pass → `Release Ready` | Human call; `/oac-spec-qa` writes the report, the human acts on it. |
| Release tag cut → `Released-Done` | No release-tag hook today. |
| Story creation | Product owns Story creation; specflow never creates Stories. |
