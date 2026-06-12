# spec-run

Drive the full specflow lifecycle end-to-end for one spec, with human approval gates, the phased
`/spec-phase` + `/implement` model wired in, and `/spec-taskstoissues` skipped. Resumable.

Usage: `/spec-run <spec-name> [--auto]`

---

You are the **orchestrator** for the specflow spec-driven lifecycle. You run each phase in order by
invoking its skill, gate on human approval, and persist progress to `.meta.yaml` so re-running
`/spec-run <name>` resumes exactly where it left off. You do NOT implement phases yourself — each
phase's skill does the work in this same context.

**All spec work happens inside an isolated git worktree with the `specflow` submodule checked out**
(that submodule holds every `spec-*` command). Bootstrap that environment (Step 0) before any phase.

## Arguments

- `<spec-name>` — **required**. The spec under `.specflow/specs/<name>/`.
- `--auto` — optional. Bypass the optional approval pauses for an unattended run. Even with `--auto`,
  you ALWAYS pause once **before `/implement`** (it changes source code) and surface any prompt a
  phase raises (e.g. `/implement` Step 0 Jira linking).

If `<spec-name>` is missing, ask the user for it and stop.

## Canonical pipeline

Run phases in exactly this order. `taskstoissues` is **never** run.

| # | `current_phase` | Skill | Gate after (default) |
|---|---|---|---|
| 0 | `init` | `spec-init` (only if no spec dir yet) | interactive — needs description |
| 1 | `preflight` | `spec-preflight` | auto-proceed |
| 2 | `requirements` | `spec-requirements` | **pause for approval** |
| 3 | `clarify` | `spec-clarify` | interactive Q&A (inherent), then auto-proceed |
| 4 | `design` | `spec-design` | **pause for approval** |
| 5 | `tasks` | `spec-tasks` | auto-proceed |
| 6 | `phase` | `spec-phase` | **pause for approval** (review `phases.md`) |
| 7 | `implement` | `implement` | **pause before**; pause after unless `--auto` |
| 8 | `spec-qa` | `spec-qa` | **pause for approval** (required phase) |
| 9 | `simplify` | `simplify` | auto-proceed |
| 10 | `validate` | `spec-validate` | report + stop |

- Gate defaults mirror `specflow/src/workflows/feature.yaml` `approval:` flags: `human` → pause,
  `auto` → proceed. `--auto` suppresses the optional pauses but never the pre-`implement` pause.
- `simplify` and `validate` are mandatory (CLAUDE.md: "NEVER skip `/simplify` or `/spec-validate`").

## Procedure

### 0. Bootstrap — worktree + submodule (do this first, every run)

Spec work MUST happen inside an isolated git worktree (under `.claude/worktrees/`) with the
`specflow` submodule populated. A freshly-added worktree does **not** auto-checkout submodules, so
the submodule pull is mandatory — without it the `spec-*` commands do not exist in the worktree.

**A. Ensure the worktree.**
- If the current working directory is already under `.claude/worktrees/` → you're in a worktree; skip to B.
- **New spec** (no `.specflow/specs/<name>/` anywhere yet): create and enter one.
  1. `git fetch origin`
  2. `git worktree add -b feature/<name> .claude/worktrees/<name> origin/main`
     — branches fresh from `origin/main`, matching the `feature/{name}` convention in CLAUDE.md.
     If that branch or path already exists, reuse it (e.g. `git worktree add .claude/worktrees/<name> feature/<name>`) instead of failing.
  3. Switch the session in: `EnterWorktree({ path: ".claude/worktrees/<name>" })`.
- **Resume** of a spec that lives in an existing worktree: `EnterWorktree({ path: ".claude/worktrees/<name>" })`
  if not already inside it.

**B. Pull the submodule.** From the worktree root:
- `git submodule update --init --recursive specflow`
- Verify with `git submodule status` — a leading `-` on the `specflow` line means it is still
  uninitialized; re-run the update before continuing.

Only after both A and B succeed do you proceed. If either fails, STOP and surface the error.

### 1. Resolve state

Read `.specflow/specs/<name>/.meta.yaml` (inside the worktree).

- **No directory / no `.meta.yaml`** → the spec does not exist yet. Start at phase 0: invoke the
  `spec-init` skill (it collects the feature description and workflow type from the user). Then go
  to step 2 (Normalize).
- **Exists** → read `current_phase` and `phase_status`. Resume at the first phase in the pipeline
  that is not yet `completed` or `skipped`. Report to the user which phase you're resuming at before
  running anything.

### 2. Normalize meta (once, right after init)

After `spec-init` (or on first `/spec-run` of an existing spec that predates this command), make
`.meta.yaml` match the pipeline:

- Keep `workflow: feature`.
- Ensure `phase_status` contains keys in pipeline order, **inserting `phase` immediately after
  `tasks`** and **before `implement`**.
- Set `taskstoissues: skipped`.
- Leave already-`completed` phases as-is; new keys default to `pending`.

Use Read + Edit on `.meta.yaml` for these mutations — do not rewrite unrelated fields.

### 3. Run the loop

For each remaining phase in pipeline order:

1. Set `.meta.yaml` `current_phase` to this phase's id (Edit).
2. **Invoke the phase's skill** via the Skill tool (column "Skill" above). Phases 0/3/7 may prompt
   the user (init description, clarify Q&A, implement's Jira Step 0) — let those surface naturally.
3. When the skill finishes, mark this phase `completed` in `phase_status` (Edit). Let each skill own
   its own artifacts (`requirements.md`, `design.md`, `tasks.md`, `phases.md`, `qa-report.md`, …) —
   do not duplicate their writes.
4. **Gate:**
   - If this phase is human-gated (per the table) and `--auto` is NOT set → **STOP your turn**.
     Give a 2–4 line summary of what was produced and tell the user to review it, then re-run
     `/spec-run <name>` to continue. Do not start the next phase.
   - Before `implement` (phase 7): STOP and confirm even under `--auto` is off; without `--auto`,
     pause both before and after. With `--auto`, still pause once before `implement`, then proceed.
   - Otherwise (auto-proceed) → continue to the next phase in the same turn.

### 4. Stop conditions

- If any phase **fails or blocks** (skill reports an error, validation fails, user declines): STOP,
  surface the error/output verbatim, leave `current_phase` on the failed phase, and do not advance.
- After `validate` completes, present its report and end the run.

## Notes

- Step 0 (worktree + submodule) is **not** a tracked phase — it has no `current_phase` value and is
  not recorded in `phase_status`. It is environment setup that must hold before any phase runs.
- `/spec-phase` writes `.specflow/specs/<name>/phases.md` (the `(WorkAgent, TestAgent)` roadmap);
  `/implement` reads it and executes by phase. Run `phase` before `implement` — never the reverse.
- Never invoke `spec-taskstoissues`.
- This command edits only `.meta.yaml` directly; everything else is produced by the phase skills.
