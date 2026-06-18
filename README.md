# my-claude — a spec-driven-development bundle for Claude Code

A reusable [Claude Code](https://claude.com/claude-code) bundle that drives a structured,
spec-driven workflow — `init → preflight → requirements → clarify → design → tasks → implement →
validate → qa → drift` — for **React/TypeScript** and **Flutter/Dart** projects.

It ships three kinds of asset:

- **Commands** — one generic, stack-neutral `/spec-*` stage set (process, goals, inputs, and gates
  only; they name no skill, rule, or stack).
- **Skills** — the stack-specific know-how the stages use (`oac-*` for React, `fl-*` for Flutter),
  plus standalone review skills.
- **Agents** — per-stack workflow **drivers** (`oac-*-workflow`, `fl-*-workflow`). The driver is the
  binding layer: it runs each `/spec-*` stage, supplies the right skills, applies the rules, and
  enforces the human gates.

You typically **vendor this repo into your project** (e.g. a git submodule) and link it into the
project's `.claude/`; or link it into your **global `~/.claude`**. Either way the links are relative
to this repo, so they keep resolving wherever the repo lives.

## Layout

```
my-claude/
├── specflow/
│   ├── commands/     the generic /spec-* stage commands (real files; the canonical command set)
│   └── README.md     the full workflow: stages, the agent-as-binding-layer model, picking a driver
├── react/            React profile — agents/ (drivers), skills/ (oac-*), rules/
├── flutter/          Flutter profile — agents/ (drivers), skills/ (fl-*), rules/
├── skills/           aggregated view: every profile skill + standalone skills (relative symlinks + real files)
├── agents/           aggregated view: every profile driver agent (relative symlinks)
├── rules/            canonical rules + profile rule symlinks (see below)
├── commands/         aggregated view: specflow commands (relative symlinks)
├── install.sh        LAYER 1 — symlink stack source dirs into aggregation dirs (within this repo)
├── uninstall.sh      LAYER 1 teardown — remove stack symlinks from aggregation dirs
└── setup.sh          LAYER 2 — link/remove aggregation dirs into ~/.claude or a project's .claude
```

### Two-layer model

**Layer 1 — `install.sh` / `uninstall.sh`** operates entirely within this repo: it symlinks
`<stack>/<type>/*` into the aggregation dir `<type>/`. For example, `specflow/commands/*` is
symlinked into `commands/`, and `flutter/agents/*` into `agents/`. The aggregation dirs are what
Layer 2 consumes.

**Layer 2 — `setup.sh`** links the aggregated `agents/`, `commands/`, and `skills/` dirs into an
external `.claude/` (global `~/.claude` or a project's `.claude/`). Rules are not linked here —
they are consumed via `CLAUDE.md` `@`-imports instead.

`skills/`, `agents/`, `commands/`, and `rules/` are **aggregated views**. Some entries are relative
symlinks to stack sources (managed by `install.sh`); others are real files that must never be
removed (e.g. `rules/engineering-discipline.md`, `rules/preferences.md`, and the standalone skills
under `skills/`).

### Rules

```
rules/engineering-discipline.md          REAL FILE  — stack-agnostic, the single source of truth
rules/preferences.md                     REAL FILE  — stack-agnostic, the single source of truth
rules/flutter-architecture-principles.md → ../flutter/rules/architecture-principles.md (gated to *.dart)
rules/flutter-test-quality.md            → ../flutter/rules/test-quality.md
rules/react-architecture-principles.md   → ../react/rules/architecture-principles.md  (gated to *.ts,*.tsx)
rules/react-test-quality.md              → ../react/rules/test-quality.md
```

Rule links are **stack-prefixed** (`<stack>-<basename>`) because the same filenames appear under both
`flutter/rules/` and `react/rules/`; the prefix keeps them distinct and `install.sh` idempotent.

Rules apply ambiently via their `paths:` frontmatter — the driver agents don't list them.

## Install / link

Three scripts, all **relative-symlink** based.

### Step 1 — populate the aggregation dirs (once, or when you add/remove a stack asset)

```sh
./install.sh                    # interactive: pick which stacks to aggregate
./install.sh all                # aggregate every stack
./install.sh flutter            # all types under flutter
./install.sh specflow commands  # just specflow commands
./install.sh react agents       # just react agents

./uninstall.sh specflow commands  # remove specflow command symlinks from commands/
./uninstall.sh all                # remove all stack symlinks from all aggregation dirs
```

`install.sh` scoped by stack+type. Already-linked entries are skipped. Real files (e.g.
`rules/engineering-discipline.md`, standalone skills) are never touched — only symlinks that
resolve back into the named stack are ever created or removed.

### Step 2 — link into ~/.claude or a project (Layer 2)

```sh
./setup.sh                          # interactive: choose global or project, then types
./setup.sh link --global            # link agents/commands/skills into ~/.claude
./setup.sh link --project ../myapp  # link into ../myapp/.claude
./setup.sh remove --global          # remove this repo's symlinks from ~/.claude
./setup.sh remove --project ../app  # remove from ../app/.claude
```

`setup.sh` multi-selects which of `agents`, `commands`, `skills` to link. For each selected type it
creates **one directory symlink**: `<dest>/.claude/<type>` → this repo's `<type>/`. The per-file
relative symlinks inside those dirs are owned by `install.sh`. Rules are **not** linked — they are
loaded via `CLAUDE.md` `@`-imports. Re-running is safe: if the destination already has a legacy
per-file bundle (the old per-file layout), `setup.sh` auto-migrates it to the single dir symlink. A
directory that contains your own files is never clobbered — the script warns and leaves it intact
(move it, then re-run). `remove` only removes a dir symlink (or legacy per-file dir) that resolves
back into this repo. Bare `./setup.sh` (no `link`/`remove`) auto-detects a target that's already
linked with this repo and offers to unlink it instead; passing `link` or `remove` explicitly skips
that prompt.

> **Submodule tip.** When this repo is vendored in your project, submodules are synced by the
> driver agent's `initialPrompt`/Initialize step on session start — no separate hook installation
> required.

> **Windows symlink note.** Git restores the in-repo symlinks only when `core.symlinks=true` (default
> on macOS/Linux). On Windows, enable Developer Mode or `git config core.symlinks true && git checkout -- .`.

### Step 3 — run a workflow driver agent in a worktree

Once the agents are linked into a target's `.claude/agents/` (Step 2), invoke a driver directly
with Claude Code:

```sh
claude --agent <workflow-agent-name> --worktree <worktree-name>
```

The driver orchestrates the entire specflow lifecycle — `init → preflight → requirements → clarify →
design → tasks → implement → validate → qa → drift` — inside the worktree.

Available workflow-driver agents:

- **Flutter:** `fl-feature-workflow`, `fl-bugfix-workflow`, `fl-quickfix-workflow`, `fl-brownfield-workflow`
- **React:** `oac-feature-workflow`, `oac-bugfix-workflow`, `oac-quickfix-workflow`, `oac-brownfield-workflow`

> The agent must be linked into the target's `.claude/agents/` first (run `setup.sh`).

When `setup.sh` links `agents`, it also writes a **permanent shell command per driver agent** into
your shell rc (`~/.zshrc` or `~/.bashrc`). Each command is a function named exactly after the agent:

```sh
oac-feature-workflow "add a logout button"
fl-bugfix-workflow
```

These are the **recommended** way to launch a driver — no need to remember `--agent` or `--worktree`
flags. The commands are written as a removable managed block; run `source ~/.zshrc` (or open a new
shell) to pick them up. `setup.sh remove` deletes the block.

## Editing

Edit profile content under `specflow/`, `react/`, or `flutter/` directly — the aggregated `skills/`,
`agents/`, `rules/` symlinks resolve straight to it. If you add or remove a skill/agent in a profile,
re-run `./link-specflow.sh` to refresh the aggregated views.

## The workflow

See **[specflow/README.md](specflow/README.md)** for the full lifecycle, the agent-as-binding-layer
model, the human verification gate after `/spec-implement`, and how to pick the right driver agent
(`oac-{feature,brownfield,bugfix,quickfix}-workflow` for React, `fl-*` for Flutter).
