# my-claude

A plugin marketplace for [Claude Code](https://claude.com/claude-code) and GitHub Copilot. Each
plugin is self-contained, installs on its own and has its own README. What a plugin ships is
namespaced (`/my-workflow:<skill>`, `my-workflow:<agent>`), so it never collides with your own
configuration.

**Only `my-workflow` is ready to use.** The other plugins are still under development: they can
be installed, but expect gaps and breaking changes.

## Plugins

| Plugin | What it is | Status | Read |
|---|---|---|---|
| `my-workflow` | A spec-driven workflow for any language. You settle the requirements, the design and the plan; agents test, build and review; a script checks that every requirement is backed by evidence. | **ready to use** | [README](plugins/my-workflow/README.md) · [design](plugins/my-workflow/DESIGN.md) |
| `my-react` | React and TypeScript rules for coding agents: design, implement, test, review and Figma skills, with no process. Pairs with `my-workflow`. | under development | [README](plugins/my-react/README.md) |
| `my-flutter` | Flutter and Dart rules for coding agents: design, implement, Riverpod, test and review skills, with no process. Pairs with `my-workflow`. | under development | [README](plugins/my-flutter/README.md) |
| `my-invest` | A financial advisor for a beginner in US stocks and funds: cited figures, three options per answer, a daily digest of your holdings. | under development | [README](plugins/my-invest/README.md) |

## Install

Run the installer. It asks which tools (Claude Code, GitHub Copilot) and which plugins:

```bash
python3 setup.py
```

The same without questions, plus uninstall and a status table:

```bash
python3 setup.py install --tools claude,copilot --plugins my-workflow
```

```bash
python3 setup.py uninstall --tools copilot --plugins my-workflow
```

```bash
python3 setup.py status
```

Or install straight from GitHub inside a `claude` session:

```text
/plugin marketplace add SimonWang9610/my-claude
/plugin install my-workflow@my-claude
```

Or try a plugin without installing it:

```bash
claude --plugin-dir ./plugins/my-workflow
```

What the installer does on your machine:

- **Claude Code:** installs through the `claude plugin` CLI. Where that command is missing, or with
  `--link`, it symlinks `~/.claude/skills/<plugin>` to the plugin folder.
- **GitHub Copilot:** installs through the `copilot` CLI. Where that is missing, it adds the plugin
  folders to VS Code's `chat.pluginLocations` in your user `settings.json`, after writing a
  `.my-claude.bak` backup.
- It never overwrites a file it did not create.

`python3 setup.py --help` lists the other options. Each plugin's README has the install steps for
that plugin alone.

## Update

A plugin's version is pinned in its `.claude-plugin/plugin.json`; you get an update when that
version changes.

```bash
claude plugin marketplace update my-claude
```

```bash
claude plugin update my-workflow@my-claude
```

Then restart Claude Code or run `/reload-plugins`. With the installer: `git pull`, then
`python3 setup.py install --update`.

Skill and agent names are the stable interface. A version that renames one says so in that plugin's
README; for `my-workflow` see [Migrating to 3.x](plugins/my-workflow/README.md#migrating-to-3x).

## Telemetry (optional)

[`metrics/`](metrics/README.md) is a local sink for Claude Code's OpenTelemetry output: cost,
tokens, sessions and edit accept rates, with a Grafana dashboard. It is machine-level, so it lives
in the repo and not inside a plugin.

```bash
python3 metrics/stack.py up && python3 metrics/stack.py verify
```

## Working on the plugins

```text
my-claude/
├── .claude-plugin/marketplace.json   the marketplace registry
├── plugins/<plugin>/                 one folder per plugin: skills/, agents/, its README
├── setup.py · scripts/               the installer, standard library only
├── metrics/                          the local telemetry stack
├── CLAUDE.md                         the rules for writing skills in this repo
└── REFINE-LOG.md                     what was adopted or rejected, and why
```

Edit under `plugins/` directly; `/reload-plugins` picks the change up when the plugin is loaded
with `--plugin-dir` or from a local marketplace.

One plugin folder has to stay valid for both tools:

- Agents are named `<name>.agent.md`.
- A skill's `name` field stays unprefixed; both tools invoke it as `/<plugin>:<skill>`.
- Copilot ignores Claude-only agent fields (`skills`, `memory`, `permissionMode`, `effort`,
  `color`), so an agent's body names the skills it uses.

## Migrating from the symlink install

The old `link.sh` and `unlink.sh` installer is removed.

1. Delete the symlinks in `<dest>/.claude/{skills,agents,rules}` that point into this repo.
2. Remove the `# >>> my-claude workflow agents >>>` block from your shell rc, if you installed
   aliases.
3. Install the plugins as above.
4. Invocations are now namespaced: `/review` is `/my-flutter:review`. `my-react`'s driver and
   process skills are gone; see [its README](plugins/my-react/README.md#migrating-from-1x).
5. `rules/preferences.md` is gone; its rules live in `my-workflow`'s
   [`spec-implementer`](plugins/my-workflow/agents/spec-implementer.agent.md) agent.
