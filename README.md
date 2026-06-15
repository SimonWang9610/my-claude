# my-claude

My global [Claude Code](https://claude.com/claude-code) configuration — the single source of truth for
`~/.claude`. Clone it, run `./install.sh`, and your commands, skills, rules, and agents are wired up on
a new machine.

## Layout

```
my-claude/
├── commands/        global slash commands (/name)        — your own + oac-specflow links
├── skills/          global skills                         — your own + oac-specflow links
├── rules/           global rules (path-gated where set)   — your own + oac-specflow links
├── agents/          global subagents                      — oac-specflow link
├── oac-specflow/    self-contained spec-driven-dev bundle (see its own README)
├── CLAUDE.md        global instructions
└── install.sh       wires ~/.claude → this repo
```

`commands/`, `skills/`, `rules/`, and `agents/` hold your own assets **plus relative symlinks** that
surface the `oac-specflow/` bundle, e.g.:

```
commands/oac-spec-qa.md   -> ../oac-specflow/commands/oac-spec-qa.md
skills/oac-qa-report      -> ../oac-specflow/skills/oac-qa-report
rules/architecture-principles.md -> ../oac-specflow/rules/architecture-principles.md
agents/oac-spec-driver.md -> ../oac-specflow/agents/oac-spec-driver.md
```

These symlinks are **relative**, so they keep resolving no matter where the repo is cloned.

## Install

```sh
git clone git@github.com:SimonWang9610/my-claude.git
cd my-claude
./install.sh
```

`install.sh` points `~/.claude/{commands,skills,rules,agents}` at this repo. It is **idempotent**
(re-run any time) and never deletes: a pre-existing real folder is moved to `<dir>.bak.<timestamp>`
first. Restart Claude Code afterward to pick everything up. Target a non-default location with
`CLAUDE_HOME=/path ./install.sh`.

## How it propagates across machines

| What | Tracked by git? | Restored by |
|---|---|---|
| Your assets + the relative `oac-specflow` symlinks (inside the repo) | **Yes** | `git clone` / `pull` |
| `~/.claude/{commands,skills,rules,agents}` dir-symlinks (outside the repo) | No | `./install.sh` |

So the full reproduce-on-a-new-machine flow is **`git clone` → `./install.sh`**.

> **Symlink note.** Git restores the in-repo symlinks only when `core.symlinks=true` (the default on
> macOS/Linux). On Windows, enable Developer Mode or run `git config core.symlinks true && git checkout -- .`.

## Editing

Edit files directly in this repo — `~/.claude` points straight at them, so changes take effect after a
Claude Code reload. For the spec workflow, edit under `oac-specflow/`; the relative symlinks in
`commands/`, `skills/`, `rules/`, and `agents/` update automatically.

## oac-specflow

A self-contained, spec-driven-development workflow — `init → preflight → requirements → clarify →
design → tasks → implement → validate → qa → drift` — with paired `(WorkAgent, TestAgent)`
implementation, a verifiable-unit architecture gate, and a sign-off-ready QA audit. Drive the whole
lifecycle with the **`oac-spec-driver`** agent, or run individual **`/oac-spec-*`** commands. The
bundle is general React/TypeScript practice; the one per-repo seam to adapt is
`oac-specflow/commands/_oac-jira-status-automation.md`. See [oac-specflow/README.md](oac-specflow/README.md).
