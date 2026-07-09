# my-claude — a spec-driven-development bundle for Claude Code

A reusable [Claude Code](https://claude.com/claude-code) bundle that drives a structured,
spec-driven workflow — `preflight → requirements → clarify → design → tasks → implement → qa` —
for **React/TypeScript** and **Flutter/Dart** projects.

## Moving parts

- **Workflows** — the phase machine comes from your project's vendored specflow template
  (`specflow/src/workflows/<variant>.yaml`, override `.specflow/workflows/`), not this bundle.
  `/sf-react-workflow` translates it into the spec's `workflow.yaml`, binding React `oac-*` skills
  to each phase (`id / command / inputs / outputs / skills / gate / exitWhen`; ids match
  `.meta.yaml`). Specflow-managed projects use `/spec-*` instead.
- **Commands** — one generic, stack-neutral `/sf-*` stage set (process + gates only; names no
  skill or stack).
- **Skills** — the stack-specific know-how the stages bind (`oac-*` React, `fl-*` Flutter),
  including prevent/detect pairs (`oac-implementation` ↔ `oac-implementation-review`,
  `oac-test-contract` ↔ `oac-test-forensics`) and the `*-react-workflow` generators.
- **Agents** — two stack-neutral **drivers**: `sflow-driver` (`/sf-*`) and `specflow-driver`
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
├── sflow/       generic /sf-* stage commands (real) + the full workflow README
├── react/       React profile — skills/ (oac-*), rules/
├── flutter/     Flutter profile — skills/ (fl-*), rules/
├── skills/      aggregation: profile skills (symlinks) + shared real skills
│                (the *-react-workflow generators, jira-ac-align, scan-resource)
├── agents/      the two driver agents (real files) — sflow-driver, specflow-driver
├── rules/       shared rules (real) + stack-prefixed profile rule symlinks
├── commands/    aggregation: the /sf-* commands (symlinks)
├── internal-link.sh / internal-unlink.sh   build/prune the aggregation dirs from stack sources
└── link.sh / unlink.sh                     link/remove a stack selection into a .claude/
```

## Linking — one layer, two script pairs

The root `agents/ commands/ rules/ skills/` are **committed aggregation views**: per-asset
relative symlinks into `flutter/ react/ sflow/`, plus real shared files (the drivers, the shared
rules, the generators). Editing a stack source shows through its aggregation entry instantly.

- **`internal-link.sh` / `internal-unlink.sh`** — inside the repo: (re)build or prune the
  aggregation from the stack sources (`./internal-link.sh all` also repairs). Rules get a
  `<stack>-` prefix because both profiles share basenames; they apply ambiently via their `paths:`
  frontmatter, so the drivers never list them.
- **`link.sh` / `unlink.sh`** — outside the repo: link/remove a per-stack selection into an
  external `.claude/`. Relative links; existing correct links skipped; foreign files never
  clobbered; `unlink.sh all` also removes shared assets and the rc block; re-running is safe.

## Install

```sh
./link.sh --global all                 # everything into ~/.claude
./link.sh --project ../myapp react     # React into a project (sflow auto-added — drivers need /sf-*)
./link.sh                              # interactive
./unlink.sh --project ../myapp react   # remove React entries (shared assets stay)
./unlink.sh --global all               # remove everything this repo linked
```

`link.sh` can also write a **shell function per driver** into your rc file (`--aliases` /
`--no-aliases` to skip the prompt), so you can launch one directly — otherwise invoke it raw:

```sh
sflow-driver "add a logout button"     # = claude --agent sflow-driver "..." --worktree
claude --agent specflow-driver --worktree my-feature
```

> **Submodules** are synced by the driver's Setup on session start — no hook needed. **Windows:**
> in-repo symlinks need `core.symlinks=true` (enable Developer Mode, then `git checkout -- .`).

## Editing

Edit under `sflow/ react/ flutter/` directly. On add/remove/rename, re-run `./internal-link.sh
<stack>` (`./internal-unlink.sh` for removals), commit the symlink change, then `./link.sh` each
destination.

## The workflow

See **[sflow/README.md](sflow/README.md)** for the full lifecycle, the `workflow.yaml` schema, the
agent-as-binding-layer model, the human gate after `/sf-implement`, and picking a driver. sflow
interoperates with the project-side **specflow** toolchain.
