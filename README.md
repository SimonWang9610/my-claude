# my-claude

My global [Claude Code](https://claude.com/claude-code) configuration — the single source of truth for
`~/.claude`. Clone it, run `./install.sh`, and your commands, skills, rules, and agents are wired up on
a new machine.

## Layout

```
my-claude/
├── commands/        global slash commands (/name)        — your own + specflow links
├── skills/          global skills                         — your own + specflow links
├── rules/           global rules (path-gated where set)   — your own + specflow links
├── agents/          global subagents                      — specflow links
├── specflow/        12 generic stack-neutral /spec-* stage commands + unified README
├── react/           React profile: agents (binding layer), skills, rules, commands
├── flutter/         Flutter profile: agents (binding layer), skills, rules
├── CLAUDE.md        global instructions
├── link-specflow.sh inner-layer wiring: exposes specflow/react/flutter into flat repo dirs
└── install.sh       outer-layer wiring: ~/.claude → this repo
```

`commands/`, `skills/`, `rules/`, and `agents/` hold your own assets **plus relative symlinks** that
surface the `specflow/`, `react/`, and `flutter/` bundles, e.g.:

```
commands/spec-qa.md                → ../specflow/commands/spec-qa.md
commands/_oac-jira-status-automation.md → ../react/commands/_oac-jira-status-automation.md
skills/oac-qa-report               → ../react/skills/oac-qa-report
skills/fl-riverpod                 → ../flutter/skills/fl-riverpod
rules/architecture-principles.md  → ../react/rules/architecture-principles.md  (React-owned)
rules/test-quality.md             → ../react/rules/test-quality.md             (React-owned)
rules/engineering-discipline.md   REAL FILE — top-level canonical, shared by all profiles
rules/preferences.md              REAL FILE — top-level canonical, shared by all profiles
agents/oac-feature-workflow.md    → ../react/agents/oac-feature-workflow.md
agents/fl-feature-workflow.md     → ../flutter/agents/fl-feature-workflow.md
```

These symlinks are **relative**, so they keep resolving no matter where the repo is cloned.
`engineering-discipline.md` and `preferences.md` are the single source of truth in `rules/` — the
per-profile `rules/` directories hold symlinks back to these files, not copies.

## Install

```sh
git clone git@github.com:SimonWang9610/my-claude.git
cd my-claude
./install.sh
```

`install.sh` runs `link-specflow.sh` (inner layer, prunes stale links and creates new ones), then
points `~/.claude/{commands,skills,rules,agents}` at this repo. It is **idempotent** (re-run any
time) and never deletes: a pre-existing real folder is moved to `<dir>.bak.<timestamp>` first.
Restart Claude Code afterward to pick everything up. Target a non-default location with
`CLAUDE_HOME=/path ./install.sh`.

## How it propagates across machines

| What | Tracked by git? | Restored by |
|---|---|---|
| Your assets + the relative specflow symlinks (inside the repo) | **Yes** | `git clone` / `pull` |
| `~/.claude/{commands,skills,rules,agents}` dir-symlinks (outside the repo) | No | `./install.sh` |

So the full reproduce-on-a-new-machine flow is **`git clone` → `./install.sh`**.

> **Symlink note.** Git restores the in-repo symlinks only when `core.symlinks=true` (the default on
> macOS/Linux). On Windows, enable Developer Mode or run `git config core.symlinks true && git checkout -- .`.

## Editing

Edit files directly in this repo — `~/.claude` points straight at them, so changes take effect after a
Claude Code reload. For spec workflow content, edit under `specflow/`, `react/`, or `flutter/`; the
relative symlinks in `commands/`, `skills/`, `rules/`, and `agents/` update automatically.

## specflow

A unified, spec-driven-development workflow — `init → preflight → requirements → clarify →
design → tasks → implement → validate → qa → drift` — with two stack profiles (React and Flutter)
and a shared set of 12 stack-neutral stage commands. Stages are invoked as **`/spec-*`**. Each
profile's driver agent (the sole binding layer) loads the profile's skills, applies its rules, and
binds the generic commands to concrete skill calls. Drive the whole lifecycle with the per-workflow
driver agent, or run individual `/spec-*` commands directly.

See [specflow/README.md](specflow/README.md) for the full process, the agent-as-binding-layer model,
and how to pick the right driver agent.
