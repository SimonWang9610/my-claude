# my-claude — a spec-driven-development bundle for Claude Code

A reusable [Claude Code](https://claude.com/claude-code) bundle that drives a structured,
spec-driven workflow — `preflight → requirements → design → tasks → implement → validate → qa` —
for **React/TypeScript** and **Flutter/Dart** projects.

It ships three layers you install into a project's (or your global) `.claude/`:

| Layer | What it is | Lives in |
|-------|-----------|----------|
| **Skills** | the stack know-how — *how to do a phase well* | `skills/`, `flutter/` |
| **Agents** | who runs the work — orchestrators + workers | `agents/` |
| **Commands** | the stack-neutral `/sf-*` process + gates | `sflow/commands/` |
| **Scripts** | per-entry symlink installers | `*.sh` (repo root) |

Skills carry the judgment, agents carry the execution, commands carry the process. You drive it
by launching a **driver agent**; everything else is bound or spawned from there.

---

## Skills — the know-how

A skill is a self-contained procedure Claude loads on demand. Invoke one directly with
`/<skill-name>`, or let its description auto-trigger it; a driver binds the right skill to each
phase, and a worker agent preloads its skills at startup (`skills:` frontmatter). Each skill
states its own inputs, procedure, output shape, and rules.

**The React contract flow** (spec → shipped code), one artifact per phase:

- `build-requirements` → `requirements.md` (user stories + observable Given/When/Then ACs)
- `design-react-contracts` → `design.md` + `contracts/` (per-unit API, data flow, state)
- `plan-react-contracts` → `tasks.md` (dependency-ordered waves, test + impl batches)
- `test-react-contracts` → tests named for the AC they prove (Vitest · RTL · MSW · Playwright)
- `implement-react-contracts` → source that makes the batch's failing tests pass
- `check-react-implementation` → severity-classified conformance findings (no verdict)
- `review-react-changes` → PR/branch review + a block/pass merge verdict

**Cross-cutting** (any codebase, any phase):

- `audit-code-flows` — reverse-engineers existing code into a queryable **atlas**, then answers
  questions from it and heals itself on a miss (`build` / `query`). The go-to before designing
  against or changing code you didn't write.
- `decompose-figma` — a Figma screen → a component map (EXISTING / PARTIAL / NEW)
- `smart-delegation` — routes a piece of work to the cheapest execution (inline / fork / subagent)
- `jira-ac-align` — reconciles a JIRA ticket's AC against the spec + shipped code

**Flutter/Dart:** `fl-pr-review` — reviews a Flutter PR against the architecture/Riverpod/Dart 3
rules. Flutter rules live in `flutter/rules/` (dormant — not linked by default).

---

## Agents — who runs it

An agent is a scoped Claude with its own tools, model, and bound skills. There are two kinds.

**Drivers — you launch these.** A pure orchestrator for one spec: it decides, verifies
mechanically, and records; it holds no stack know-how (that's in the skills) and never does heavy
work itself (that goes to workers). It reads the spec's `.meta.yaml` phase ledger and runs each
phase — its `/sf-<phase>` command first, then the phase playbook — pausing at human gates.

- `my-specflow-driver` — drives this bundle's `/sf-*` commands.
- `oac-specflow-driver` — drives an external **specflow** project's `/spec-*` commands (the
  bundle interoperates with, but does not ship, that command set).

**Workers — drivers spawn these** (you can also invoke one directly). Each is an expert with a
narrow tool fence and its skills preloaded:

- `code-auditor-agent` — owns `audit-code-flows` end-to-end (build / query the atlas). Any
  language; reads code, never modifies it.
- `react-test-agent` — authors the failing tests for a batch. Writes test files only.
- `react-impl-agent` — implements units to green. Writes source only, never touches a test.
- `react-checker-agent` — read-only fresh-eyes conformance check on a diff (Read/Grep/Glob/Bash,
  no Write/Edit — so it reports findings, never fixes).

**How a feature runs:** you launch a driver → Setup (worktree check, `/sf-init` scaffolds the spec
+ `.meta.yaml`) → it drives the phases, delegating heavy work to workers via `smart-delegation`.
Implement runs red→green per wave — spawn `react-test-agent` (RED) → spawn `react-impl-agent`
(green, test paths byte-unchanged) — then an optional `react-checker-agent` pass before the human
gate. It never advances past an open gate.

```sh
my-specflow-driver "add a logout button"     # if aliases were installed
claude --agent my-specflow-driver --worktree "add a logout button"   # raw
```

---

## Scripts — installing the bundle

The bundle is flat: `skills/ agents/ rules/` are real directories and the `/sf-*` command files
live in `sflow/commands/`. Two script pairs relative-symlink them, per entry, into a destination
`.claude/` — kept separate so the commands never install by accident:

| Script pair | Source → Destination |
|-------------|----------------------|
| `link.sh` / `unlink.sh` | `skills/* agents/* rules/*` → `<dest>/.claude/{skills,agents,rules}/` |
| `link-commands.sh` / `unlink-commands.sh` | `sflow/commands/*` → `<dest>/.claude/commands/` |

The `/sf-*` commands get their **own** pair because, installed globally, they shadow a project's
own `/spec-*` set — so link them only where an sflow workflow is actually used (a specific
project, rarely `~/.claude`). Links are relative (they resolve wherever the repo lives); an
existing correct link is skipped; a foreign real file or an outside-pointing link is never
clobbered; re-running is safe. `unlink*` removes only symlinks that resolve back into this repo.

```sh
./link.sh --global                        # skills+agents+rules → ~/.claude
./link.sh --project ../myapp              # → ../myapp/.claude
./link.sh                                 # interactive (pick global/project)
./link-commands.sh --project ../myapp     # add the /sf-* commands to that project only
./unlink.sh --project ../myapp            # remove skills+agents+rules
./unlink-commands.sh --project ../myapp   # remove the /sf-* commands
./unlink.sh --global --aliases            # remove links + the managed rc block
```

`link.sh --aliases` also writes a **shell function per driver** into your rc file, so you can
launch a driver by name (`my-specflow-driver "..."`); `--no-aliases` skips the prompt.

> **Windows:** in-repo symlinks need `core.symlinks=true` (enable Developer Mode, then
> `git checkout -- .`). **Submodules** are synced by the driver's Setup on session start.

---

## Editing & layout

Edit `skills/ agents/ rules/` and `sflow/commands/` directly — links are per-entry, so a new
skill/agent/rule appears after one `./link.sh` (a new command after one `./link-commands.sh`) at
each destination; removals need the matching `./unlink*.sh`.

```
my-claude/
├── skills/    React contract flow + cross-cutting skills (real dirs)
├── agents/    2 drivers + 4 workers (real files)
├── rules/     shared rules — preferences.md
├── sflow/     /sf-* stage commands (sflow/commands/) + the full workflow README
├── flutter/   Flutter profile — rules/ (dormant, not linked by default)
└── *.sh       link/unlink installers (bundle + commands, separate pairs)
```

For the full phase lifecycle, the `.meta.yaml` ledger, human gates, and picking a driver, see
**[sflow/README.md](sflow/README.md)**.
