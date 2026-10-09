# think — a skillset for working with AI agents better and more efficiently

Three skills, all used as `/<skill> <question>`, for Claude Code and GitHub Copilot alike.
Stack-neutral, project-neutral, self-contained: nothing here depends on other plugins or local paths.
`PROTOCOL.md` is a short CLAUDE.md-style preferences file (how the user likes to work, which skill fits
which moment); it states preferences, not rules, so it does not conflict with a project's own
instructions.

| Skill | Claude Code | Copilot | What it does |
|---|---|---|---|
| clarify | `/think:clarify <request>` | `/clarify <request>` | Handles ambiguity: diagnoses what is missing (goal, scope, constraints, done, approach), asks a few questions with defaults in up to three rounds, lays out candidate solutions (what exists, effort, fit, risk), recommends the most approachable one, converges on a decision and a brief any agent can execute. |
| explore | `/think:explore <question>` | `/explore <question>` | Explores a codebase at the altitude the question needs: map, mechanism (`path:symbol` evidence), onboarding, locate. Persists indexed notes in a folder you name on first use (default `docs/atlas/`), answers from notes later. |
| architect | `/think:architect <question>` | `/architect <question>` | Recognises the intent (design, discuss, evaluate) and the level(s) the question spans: product (language-agnostic), project (stack-specific), module. Answers top-down, one section per level: what exists, practices and pitfalls, one recommendation with the why, the decisions you must make. Evaluate: ranked findings, a verdict, a re-design sketch on rework. |

Stack specifics for project and module levels come from the repo's manifests and own rules, the
`scout` agent's research, and an optional card you write at `skills/architect/references/stacks/<stack>.md`
(template provided). Agents: `explorer` (reads code for explore) and `scout` (ecosystem research); the
skills fall back to inline work when a host cannot delegate. Forms for a brief and a decision record:
`skills/clarify/forms/`.

## Install

Pick one path per host; re-running any of them is safe.

**Claude Code with the `claude` CLI**

```
claude plugin marketplace add SimonWang9610/my-claude
claude plugin install think@my-claude
```

**Claude Code VS Code extension, no CLI** (any of these)

- In the chat panel type `/plugins`, open the **Marketplaces** tab, add `SimonWang9610/my-claude`, then
  install `think` from the **Plugins** tab.
- Or clone this repo and run `python3 plugins/think/install.py --claude`: it symlinks `~/.claude/skills/think`
  to the folder, which Claude Code loads in every session as `think@skills-dir` with its skills, agents,
  and hooks; `git pull` updates it in place. No Python: `ln -s <clone>/plugins/think ~/.claude/skills/think`.
- Or add to `~/.claude/settings.json` and restart; the marketplace is cloned and the plugin installed in
  the background:

  ```json
  {
    "extraKnownMarketplaces": { "my-claude": { "source": { "source": "github", "repo": "SimonWang9610/my-claude" } } },
    "enabledPlugins": { "think@my-claude": true }
  }
  ```

Use one of the three, not several, or the plugin loads twice.

**GitHub Copilot (VS Code, or the Copilot CLI)**

```
git clone https://github.com/SimonWang9610/my-claude
python3 my-claude/plugins/think/install.py --copilot
```

This symlinks the skills into `~/.copilot/skills/`, the agents into `~/.claude/agents/` (a location VS Code
Copilot reads in Claude format), links `~/.copilot/copilot-instructions.md` to `PROTOCOL.md` (or inserts
it between markers when you already have instructions there), and registers the prompt nudge in
`~/.copilot/hooks/think.json` pointing at the script in the clone (hooks are a preview feature in VS Code;
the file is inert when hooks are off). Reload the window; skills appear as `/clarify`, `/explore`,
`/architect`. No Python: `ln -s` the same targets by hand.

`python3 install.py` with no flag installs both hosts. Everything is a symlink into the clone, so
`git pull` updates both hosts in place; `--copy` copies instead (Windows without symlink rights), and the
script falls back to copying by itself when the OS refuses a link. `--uninstall` removes everything the
script placed. Marketplace installs are removed with `claude plugin uninstall think@my-claude`.

## Notes

- Skill folders and their `name` fields match, as Copilot requires; files a skill needs are referenced as
  Markdown links relative to `SKILL.md`, which both hosts load progressively.
- Hooks in Claude Code: `SessionStart` injects `PROTOCOL.md`; `UserPromptSubmit` adds a one-line nudge on
  short, batched, hedged, vague-defect, pause/resume, architecture, or how-does-it-work prompts; silent
  otherwise, never blocking; needs `python3` (absent → silent).
- Preferences change: edit `PROTOCOL.md` by hand, then re-run the installer or let the plugin reload.
