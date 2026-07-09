# The specflow contract

Facts about the company's specflow toolchain that `/spec-react-workflow` generates the
phase machine from, and the drive rules the specflow-driver honors. The project's commands —
including any project overrides (e.g. Jira integration, journey-plan approval gates) — always
govern process and file formats; the bound skills govern engineering quality. This file is
self-contained: act from it alone.

## Detection

Specflow-managed ⇔ `.claude/commands/spec-init.md` (or `.specflow/config.yaml`) exists, or the
target spec dir has `.meta.yaml` but no `workflow.yaml` snapshot.

## Contract facts

| Fact | Value |
|---|---|
| Spec dir | `.specflow/specs/<slug>/` (kebab slug) |
| Artifacts | `preflight.md` `requirements.md` `clarify.md` `design.md` `qa-journey-plan.md` `tasks.md` `issues.md` `test-manifest.md` `qa-report.md` |
| `.meta.yaml` keys | `name`, `workflow`, `created_at`, `updated_at` (ISO 8601), `current_phase`, `phase_status` (map phase-id → status), `checksums: {}` — extra keys tolerated (project overrides may add e.g. `jira_issues:`) |
| Status enum | `pending` \| `in_progress` \| `completed` \| `skipped` \| `failed` |
| Workflows | `feature` is the only non-deprecated workflow (`brownfield`/`bugfix`/`quickfix` are deprecated in specflow) |
| Workflow templates | `specflow/src/workflows/<variant>.yaml` (vendored specflow repo), overridable at `.specflow/workflows/<variant>.yaml`; per phase: `id`, `approval` (`human\|auto\|skip`), `required`, `inputs`, `outputs`, plus `generator`/`executor`, `validators`, `hooks` (ignored by the generator) |
| Commands | `/spec-init` `/spec-preflight` `/spec-requirements` `/spec-clarify` `/spec-design` `/spec-tasks` `/spec-taskstoissues` `/spec-implement` `/spec-qa` `/spec-status` `/spec-validate` `/spec-drift` `/spec-steer` — installed at the project's `.claude/commands/spec-*.md`, file-driven (git/gh only, no CLI shell-outs); the project's version of a command always governs |

### Feature phases (exact `.meta.yaml` phase ids, in order)

| Phase | Approval | Required |
|---|---|---|
| preflight | human | — |
| requirements | human | — |
| clarify | human | — |
| design | human | — |
| tasks | auto | — |
| taskstoissues | human | — |
| implement | auto | — |
| spec-qa | human | true |

No `validate`/`qa`/`drift` phase ids exist in this ledger — `/spec-validate` gates `spec-qa`'s
`exitWhen` (run it, report results in chat), `/spec-drift` is an optional post-merge follow-up,
and neither ever appears in `phase_status`.

### Conventions specflow enforces

- `requirements.md`: EARS-notation FRs (`### FR-<id>:`), `- **NFR-<id>:**`, user stories
  `**As a** … **I want to** … **So that** …`, ACs `AC-<story>.<n>`, journeys `J-N`.
- `tasks.md`: tasks as `### Task <id>: <title>` with `- **Status:**`, `- **Depends on:**`,
  `- **Files:**`; test tasks ordered before impl tasks.
- implement: updates each task's Status → `completed` and writes `test-manifest.md`.
- design (feature) also outputs `qa-journey-plan.md`.
- PR bodies NEVER contain closing keywords (`closes`/`fixes`/`resolves #N`) — use
  `Linked issues: #…`.
- Adopted shared components are immutable.

## Drive rules

- `approval: human` phases are hard stops — present the artifacts and wait.
- Honor project command overrides — the project's `.claude/commands/spec-*.md` version governs.
- Update `.meta.yaml` `phase_status` with the enum values only; keep `updated_at` ISO 8601.
  Never add keys beyond the template's phase ids (validate/drift are not phases) — the
  project's tooling owns that map.
- Never modify adopted shared components.
- No PR closing keywords — `Linked issues: #…` only.
