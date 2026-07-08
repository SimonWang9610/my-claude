# my-claude — a spec-driven-development bundle for Claude Code

A reusable [Claude Code](https://claude.com/claude-code) bundle that drives a structured,
spec-driven workflow — `init → preflight → requirements → clarify → design → tasks → implement →
validate → qa → drift` — for **React/TypeScript** and **Flutter/Dart** projects.

It ships four kinds of asset:

- **Workflows** — one YAML per workflow variant (`feature`, `brownfield`, `bugfix`, `quickfix`):
  the canonical phase machine (phase order, command, roles, gates, required flags). `/sf-init`
  snapshots the chosen YAML into the spec dir; commands and drivers read that snapshot.
- **Commands** — one generic, stack-neutral `/sf-*` stage set (process, goals, inputs, and gates
  only; they name no skill, rule, or stack).
- **Skills** — the stack-specific know-how the stages use (`oac-*` for React, `fl-*` for Flutter),
  plus standalone review skills.
- **Agents** — per-stack workflow **drivers** (`oac-*-workflow`, `fl-*-workflow`). The driver is a
  pure orchestrator: it starts via `/sf-workflow-startup <tech> <variant>` (worktree → seed →
  bind → init), drives the resulting phases, enforces the human gates, and delegates phase work
  to subagents.

You typically **vendor this repo into your project** (e.g. a git submodule) and link it into the
project's `.claude/`; or link it into your **global `~/.claude`**. Either way the links are relative
to this repo, so they keep resolving wherever the repo lives.

## Layout

```
my-claude/
├── sflow/
│   ├── workflows/    the canonical phase machines — feature/brownfield/bugfix/quickfix.yaml
│   │                 (never linked into .claude — the pickers and /sf-init resolve them internally)
│   ├── commands/     the generic /sf-* stage commands (real files; the canonical command set)
│   └── README.md     the full workflow: stages, the agent-as-binding-layer model, picking a driver
├── react/            React profile — agents/ (drivers), skills/ (oac-*), rules/, commands/ (tracker playbook)
├── flutter/          Flutter profile — agents/ (drivers), skills/ (fl-*), rules/
├── skills/           aggregation view: profile skills (committed symlinks) + shared real skills —
│                 sf-workflow-startup, pick-react-workflow, pick-flutter-workflow, standalone reviews
├── agents/           aggregation view: every profile driver agent (committed symlinks)
├── rules/            canonical shared rules (real) + stack-prefixed profile rule symlinks
├── commands/         aggregation view: the /sf-* commands + the react tracker playbook (committed symlinks)
├── internal-link.sh    populate the root aggregation dirs from the stack sources (repair/refresh)
├── internal-unlink.sh  remove a stack's entries from the root aggregation dirs
├── link.sh             link a per-stack selection of the root dirs into ~/.claude or a project's .claude
└── unlink.sh           remove exactly those symlinks
```

### One layer, two scripts

The root `agents/ commands/ rules/ skills/` dirs are **committed aggregation views**:
per-asset relative symlinks into the stack sources (`flutter/`, `react/`, `sflow/`) plus a few
real shared files (`rules/engineering-discipline.md`, `rules/preferences.md`, and the standalone
skills under `skills/`). Editing a stack source is instantly visible through its aggregation
entry. Two script pairs, two directions:

- **`internal-link.sh` / `internal-unlink.sh`** — INSIDE the repo: (re)populate or prune the
  aggregation dirs from the stack sources (`./internal-link.sh all` also repairs them after any
  damage). Rules get a `<stack>-` prefix because both profiles share basenames.
- **`link.sh` / `unlink.sh`** — OUTSIDE the repo: link the aggregation entries into an external
  `.claude/`. A legacy whole-dir symlink at the destination is auto-migrated to per-file links
  (`unlink.sh` treats it as the thing to remove) — neither script ever reaches through it into
  the repo.

### Rules

```
rules/engineering-discipline.md          REAL FILE  — stack-agnostic, the single source of truth
rules/preferences.md                     REAL FILE  — stack-agnostic, the single source of truth
rules/flutter-architecture-principles.md → ../flutter/rules/architecture-principles.md (gated to *.dart)
rules/flutter-test-quality.md            → ../flutter/rules/test-quality.md
rules/react-architecture-principles.md   → ../react/rules/architecture-principles.md  (gated to *.ts,*.tsx)
rules/react-test-quality.md              → ../react/rules/test-quality.md
```

Rule links are **stack-prefixed** (`<stack>-<basename>`) because the same filenames appear under
both `flutter/rules/` and `react/rules/`; the prefix keeps them distinct.

Rules apply ambiently via their `paths:` frontmatter — the driver agents don't list them. `link.sh` links them into `.claude/rules/` like every other type.

## Install / link

```sh
./link.sh --global all                  # everything into ~/.claude
./link.sh --project ../myapp react      # React profile into a project (sflow auto-added —
                                        #   the drivers need the /sf-* commands)
./link.sh                               # interactive: choose destination + stacks

./unlink.sh --project ../myapp react    # remove the React entries (shared assets stay)
./unlink.sh --global all                # remove everything this repo linked
```

For each selected stack, `link.sh` creates relative per-asset symlinks
`<dest>/.claude/<type>/<name>` → this repo's `<type>/<name>` for the four types
(`agents commands rules skills`); the workflow templates are deliberately not linked — the
pickers and `/sf-init` resolve them through their own installed symlinks back into the bundle. Shared root assets (the cross-stack rules and the
standalone skills) are linked with any selection and removed only by `unlink.sh all` — a
single-stack unlink leaves them for the remaining stack. Existing correct links are skipped; a
foreign real file at a destination path is never clobbered; `unlink.sh` removes only symlinks
that resolve back into this repo and prunes emptied type dirs. Re-running either script is safe.

After linking, `link.sh` offers (or `--aliases` / `--no-aliases` to skip the prompt) to write a
**shell function per linked driver agent** into your rc file as a managed block, so you can launch
a driver directly:

```sh
oac-feature-workflow "add a logout button"     # = claude --agent oac-feature-workflow --worktree <auto-name> "..."
fl-bugfix-workflow
```

`unlink.sh all` offers to remove the block.

> **Submodule tip.** When this repo is vendored in your project, submodules are synced by the
> driver agent's startup (worktree check) on session start — no separate hook installation
> required.

> **Windows symlink note.** Git restores the in-repo symlinks only when `core.symlinks=true` (default
> on macOS/Linux). On Windows, enable Developer Mode or `git config core.symlinks true && git checkout -- .`.

## Run a workflow driver agent in a worktree

Once the agents are linked into a target's `.claude/agents/`, invoke a driver directly
with Claude Code:

```sh
claude --agent <workflow-agent-name> --worktree <worktree-name>
```

The driver orchestrates the entire sflow lifecycle — `init → preflight → requirements → clarify →
design → tasks → implement → validate → qa → drift` — inside the worktree, following the phase
machine in the spec's `workflow.yaml` snapshot.

Available workflow-driver agents:

- **Flutter:** `fl-feature-workflow`, `fl-bugfix-workflow`, `fl-quickfix-workflow`, `fl-brownfield-workflow`
- **React:** `oac-feature-workflow`, `oac-bugfix-workflow`, `oac-quickfix-workflow`, `oac-brownfield-workflow`

> The agent must be linked into the target's `.claude/agents/` first (run `link.sh`).

## Editing

Edit stack content under `sflow/`, `react/`, or `flutter/` directly — the aggregation symlinks
resolve straight to it. When you add, remove, or rename an asset, re-run `./internal-link.sh
<stack>` (and `./internal-unlink.sh` for removals) to refresh the aggregation dirs, commit the
symlink change, then re-run `./link.sh` on each destination.

## The workflow

See **[sflow/README.md](sflow/README.md)** for the full lifecycle, the workflow YAML schema,
the agent-as-binding-layer model, the human verification gate after `/sf-implement`, and how to pick
the right driver agent (`oac-{feature,brownfield,bugfix,quickfix}-workflow` for React, `fl-*` for
Flutter).
