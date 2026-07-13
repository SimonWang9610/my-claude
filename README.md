# my-claude — a spec-driven-development bundle for Claude Code

A reusable [Claude Code](https://claude.com/claude-code) bundle that drives a structured,
spec-driven workflow — `preflight → requirements → clarify → design → tasks → implement → qa` —
for **React/TypeScript** and **Flutter/Dart** projects.

## Moving parts

- **Workflows** — the phase machine comes from your project's vendored specflow template
  (`specflow/src/workflows/<variant>.yaml`, override `.specflow/workflows/`), not this bundle.
  `/sf-react-workflow` translates it into the spec's `workflow.yaml`, binding the OAC React skills
  to each phase (`id / command / inputs / outputs / skills / gate / exitWhen`; ids match
  `.meta.yaml`). Specflow-managed projects use `/spec-*` instead.
- **Commands** — one generic, stack-neutral `/sf-*` stage set (process + gates only; names no
  skill or stack).
- **Skills** — the stack-specific know-how the stages bind (the OAC React set, `fl-*` Flutter),
  with prevention and detection folded into each skill (rule cards, gates, checks)
  and the workflow generators (`sf-react-workflow`, `oac-workflow`).
- **Agents** — two **drivers**: `sflow-driver` (`/sf-*`) and `oac-specflow-driver`
  (`/spec-*`). A driver is a pure orchestrator — see [How the driver works](#how-the-driver-works).

Vendor this repo into your project (e.g. a git submodule) and link it into the project's
`.claude/`, or into your global `~/.claude/`. Links are relative, so they resolve wherever the
repo lives.

## How the driver works

The driver holds no process knowledge of its own — it reads the spec's `workflow.yaml` and runs
the phases:

1. **Setup** — worktree check, scaffold the spec (`/sf-init` or `/spec-init`), then **wait for
   your instructions and context**.
2. **Generate** — turn the template into the spec's `workflow.yaml` via `/sf-react-workflow`
   (or `/spec-react-workflow`).
3. **Drive Loop** (per phase) — read its `command / skills / gate / exitWhen`; run it, delegating
   heavy work to subagents; verify the `exitWhen` holds; record the result in `.meta.yaml` and
   advance to the next phase.
4. **Implement** — each unit runs as a **TestAgent** (writes the failing AC test) → **WorkAgent**
   (implements it to green, never touching the test), across the tasks' parallel waves; a
   **ReviewAgent** then reviews the whole branch and loops fixes back.
5. **Human gates** — at each `gate: human` (e.g. the post-implement code check, QA sign-off) it
   presents the artifacts and waits for your approval; it never advances past an open gate.

## Layout

```
my-claude/
├── skills/      the React skill set (real dirs) + shared skills + the two workflow generators
├── agents/      the driver agents (real files) — sflow-driver, oac-specflow-driver
├── rules/       shared rules (real files)
├── sflow/       the /sf-* stage commands (sflow/commands/) + the full workflow README
├── flutter/     Flutter profile — skills/ (fl-*), rules/ (dormant, not linked by default)
├── link.sh / unlink.sh           link/remove skills+agents+rules into a .claude/
└── link-commands.sh / unlink-commands.sh   link/remove the /sf-* commands (separate)
```

## Linking

The bundle is flat — `skills/ agents/ rules/` are real directories and the `/sf-*` command files
live in `sflow/commands/`. Two script pairs per-entry relative-symlink them into a destination
`.claude/`, kept separate so the commands never get installed by accident:

| Script | Source → Destination |
|--------|----------------------|
| `link.sh` / `unlink.sh` | `skills/* agents/* rules/*` → `<dest>/.claude/{skills,agents,rules}/` |
| `link-commands.sh` / `unlink-commands.sh` | `sflow/commands/*` → `<dest>/.claude/commands/` |

The `/sf-*` commands live in their **own** script pair because, installed globally, they shadow a
project's own `/spec-*` set — so link them only where an sflow workflow is actually used (usually a
specific project, not `~/.claude`). Both pairs use relative links; an existing correct link is
skipped; a foreign real file (or a link pointing outside this repo) is never clobbered; re-running
is safe. The `unlink*` scripts remove only symlinks that resolve back into this repo.

## Install

```sh
./link.sh --global                 # link skills+agents+rules into ~/.claude
./link.sh --project ../myapp       # link into ../myapp/.claude
./link.sh                          # interactive
./link-commands.sh --project ../myapp   # add the /sf-* commands to that project only
./unlink.sh --project ../myapp     # remove skills+agents+rules from ../myapp/.claude
./unlink-commands.sh --project ../myapp # remove the /sf-* commands
./unlink.sh --global --aliases     # remove links + the managed rc block
```

`link.sh` can also write a **shell function per driver** into your rc file (`--aliases` /
`--no-aliases` to skip the prompt), so you can launch one directly — otherwise invoke it raw:

```sh
sflow-driver "add a logout button"     # = claude --agent sflow-driver "..." --worktree
claude --agent oac-specflow-driver --worktree my-feature
```

> **Submodules** are synced by the driver's Setup on session start — no hook needed. **Windows:**
> in-repo symlinks need `core.symlinks=true` (enable Developer Mode, then `git checkout -- .`).

## Editing

Edit `skills/ agents/ rules/` and `sflow/commands/` directly — the links are per-entry, so a new
skill/agent/rule shows up after one `./link.sh` (a new command after one `./link-commands.sh`) at
each destination (removals need the matching `./unlink*.sh`).

## The workflow

See **[sflow/README.md](sflow/README.md)** for the full lifecycle, the `workflow.yaml` schema, the
agent-as-binding-layer model, the human gate after `/sf-implement`, and picking a driver. sflow
interoperates with the project-side **specflow** toolchain.
