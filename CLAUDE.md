# CLAUDE.md — editing this repo

This repo is a Claude Code config bundle: sflow (a spec-driven workflow of `/sf-*` commands —
the phase-machine templates live in the project's vendored specflow, not here), two unified
driver agents (`sflow-driver`, `specflow-driver`), and per-stack profiles (React, Flutter) of
skills and rules.
It is vendored into projects (or linked globally) via `link.sh`; the root `agents/ commands/
rules/ skills/` dirs are **committed symlink aggregation views** over the stack sources — they
are what gets linked, never what gets edited.

## Layout

| Path | What it is |
|---|---|
| `sflow/` | Stack-neutral `/sf-*` commands only (no workflow templates — the generators read the project's `specflow/src/workflows/`, `.specflow/workflows/` override) |
| `react/` | React profile — `skills/` (`oac-*`), `rules/`, `commands/` (tracker playbook); no agents |
| `flutter/` | Flutter profile — `skills/` (`fl-*`), `rules/`; no agents |
| `agents/` | The two unified driver agents as REAL files: `sflow-driver.md` (this bundle's `/sf-*` flow), `specflow-driver.md` (company specflow `/spec-*` projects). initialPrompt runs the embedded Setup (worktree check + spec init via `/sf-init` / `/spec-init`), waits for the user's instructions, then generates `workflow.yaml` via the flow's React generator (`/sf-react-workflow` / `/spec-react-workflow`) and enters the Drive Loop |
| `commands/ rules/ skills/` | Committed aggregation views: relative symlinks into the stack sources + real shared files (`rules/engineering-discipline.md`, `rules/preferences.md`, standalone skills incl. the flow-scoped React generators `sf-react-workflow` / `spec-react-workflow` — bind `oac-*` directly; a Flutter/other stack would ship a parallel `*-<tech>-workflow`) |
| `internal-link.sh` / `internal-unlink.sh` | (Re)populate / prune the root aggregation dirs from the stack sources |
| `link.sh` / `unlink.sh` | Install / remove the aggregation entries into a destination `.claude/` (global or project) |

## Editing rules

- **Edit the stack sources** (`sflow/`, `react/`, `flutter/`), never the root aggregation
  entries — those are symlinks that resolve to the sources anyway. Exception: the real shared
  files (root `agents/` drivers, shared `rules/`, standalone `skills/`) are edited in place.
- After **adding, renaming, or removing** an asset, run `./internal-link.sh <stack>` (and
  `./internal-unlink.sh` for removals) to refresh the aggregation dirs; commit the symlink change.
  Pure content edits need no re-link.
- **Every skill is self-contained**: a SKILL.md may reference only files under its own skill dir.
  Cross-skill reuse goes through committed relative symlinks inside the skill's `references/`,
  never a bare `../other-skill/...` path in prose.
- Profiles install independently — don't extract cross-profile shared reference files.
- Rules aggregate with a `<stack>-` prefix (both profiles share basenames); the shared
  `engineering-discipline.md` / `preferences.md` are real files at root `rules/` only, not
  mirrored into profile `rules/`.

## Style bar

- Terse. Files here are consumed by subagents mid-task: procedures, examples, goals — no essays,
  no marketing prose.
- Match the existing voice and structure of the file you're editing; surgical diffs.

## Conventions

- Phase-status enum (specflow-compatible): `pending | in_progress | completed | skipped | failed`.
- Skill prefixes: `oac-*` React, `fl-*` Flutter, `sf-*` stack-neutral sflow commands;
  `_`-prefixed command files are non-runnable playbooks.
