# my-workflow

A spec-driven software workflow for Claude Code and GitHub Copilot, for any language or framework. It
keeps you in control of code that agents write: you approve the requirements and the design, a script
checks that each requirement is built and backed by evidence, and you review that evidence instead of
every line.

What it solves, how it works and why it is built this way: **[DESIGN.md](DESIGN.md)**.

- [Install](#install)
- [Use](#use)
- [Migrating to 3.x](#migrating-to-3x)

## Install

The repo is a plugin marketplace, so each tool can install straight from GitHub; or clone it and run
its installer. Pick the route that matches what you have.

| You have | Route |
|---|---|
| Claude Code in VS Code, or the `claude` CLI | [Claude Code](#claude-code) |
| GitHub Copilot in VS Code, or the `copilot` CLI | [GitHub Copilot](#github-copilot) |
| Neither CLI, or you want both tools set up in one go | [From a clone](#from-a-clone) |

Needs Claude Code 2.1.219 or later, and Python 3.9 or later for the check script. Installs from
GitHub need `git` on your machine and get what is pushed to the default branch.

### Claude Code

**In VS Code** (no terminal CLI needed; the extension bundles its own):

1. In the Claude Code panel type `/plugins` to open **Manage plugins**.
2. **Marketplaces** tab → enter `SimonWang9610/my-claude`.
3. **Plugins** tab → find `my-workflow` → **Install** → choose a scope.

Update from the same dialog: refresh the marketplace, then update the plugin.

**In a session or a terminal:**

```text
/plugin marketplace add SimonWang9610/my-claude
/plugin install my-workflow@my-claude
```

```bash
claude plugin marketplace add SimonWang9610/my-claude
```

```bash
claude plugin install my-workflow@my-claude
```

Update:

```bash
claude plugin marketplace update my-claude
```

```bash
claude plugin update my-workflow@my-claude
```

Or turn on auto-update: `/plugin` → **Marketplaces** → `my-claude` → **Enable auto-update**.

**By settings file**, with no command at all. Add to `~/.claude/settings.json`; Claude Code fetches the
marketplace and the plugin on the next start:

```json
{
  "extraKnownMarketplaces": {
    "my-claude": {
      "source": { "source": "github", "repo": "SimonWang9610/my-claude" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": { "my-workflow@my-claude": true }
}
```

### GitHub Copilot

Copilot reads this Claude-format plugin as it is.

**In VS Code** (no Copilot CLI needed):

1. Turn agent plugins on and add the marketplace, in your user `settings.json`:

   ```json
   {
     "chat.plugins.enabled": true,
     "chat.plugins.marketplaces": ["SimonWang9610/my-claude"]
   }
   ```

   Or: **Chat: Open Customizations** → **Browse** → **Configure Marketplaces** → **Add Marketplace**.
2. **Browse** → select `my-workflow` → **Install**. The first install from a new marketplace asks you
   to trust it.

Update: run **Chat: Update Plugins** from the Command Palette, or **Plugins** → **Check for and Apply
Updates**.

**With the Copilot CLI:**

```bash
copilot plugin marketplace add SimonWang9610/my-claude
```

```bash
copilot plugin install my-workflow@my-claude
```

Update:

```bash
copilot plugin marketplace update my-claude
```

```bash
copilot plugin update my-workflow@my-claude
```

VS Code picks up plugins the CLI installed. Copilot ignores the agents' model names and runs them on
your session model.

### From a clone

To set up both tools with one command, or on a machine without either CLI. Clone this repo and run its
installer:

```bash
git clone https://github.com/SimonWang9610/my-claude.git
```

```bash
python3 my-claude/setup.py install --tools claude,copilot --plugins my-workflow
```

Where a CLI is missing, the installer links the clone instead: `~/.claude/skills/my-workflow` for
Claude Code, VS Code's `chat.pluginLocations` for Copilot. Keep the clone; it is the install.

Update: `git pull` in the clone, then run the installer again with `--update`.

## Use

### Drive a task

```text
/my-workflow:drive-spec add rate limiting to the upload API
```

It settles the requirements (for a bug, a diagnosis), the design and the plan with you, stopping
for your approval of the requirements and the design. Then it hands the tests, the code and the
review to agents, each in its own context, and checks what they deliver.

- Say "quick" or "deep" to set the size; "just do it" lets a passing check approve the gates.
- At the design gate it says whether it recommends an independent design review; it runs only on
  your yes, or, after "just do it", when it judges the design heavy.
- Run it again to resume. Say so to change direction.
- The work lands in `specs/<task>/`; `coverage.md` there is the report you review.

### Run one step

The four step skills (`spec-requirements`, `spec-diagnose`, `spec-design`, `spec-plan`) pick their
mode themselves. With a `workflow.yaml` a skill checks that it is the current step, saves its
artifact, runs its check and updates its status. Without one it runs the same procedure on your
request and returns the result in the session.

```text
/my-workflow:spec-diagnose uploads fail with a 500 after the second retry
/my-workflow:spec-design which approach for offline sync?
```

Tests, code and review are agents, not skills. Ask for one by name:

```text
Use the my-workflow:spec-code-reviewer agent on the diff of this branch
Use the my-workflow:spec-design-reviewer agent on docs/design.md
```

| Agent | Use it to |
|---|---|
| `spec-tester` | Write a failing acceptance test per criterion, before the code. |
| `spec-implementer` | Build planned tasks against those tests, stopping at a gap. |
| `spec-design-reviewer` | Check a design against its criteria and the code it builds on. |
| `spec-code-reviewer` | Rerun the checks on a change and give a verdict with reproduced findings. |

### Standalone skills

They work without a spec. The step skills call the last four as they need them.

| Skill | Use it to |
|---|---|
| `rephrase <prompt>` | Put the main objective of a long prompt, or of the conversation so far, first. |
| `discuss <topic>` | Talk a problem through and draft a direction a later session can spec. |
| `audit-truth <scope or question>` | Map existing code as units and their dependencies into an atlas, or answer a question from one. |
| `scaffold-project-structure` | Lay out a project by its domain, or fit new code into an existing layout. |
| `design-component` | Split a system into units by the decision each hides. |
| `analyze-ui-state` | Decide where each piece of UI state lives and how it changes. |

### Map unfamiliar code first

```bash
claude --agent my-workflow:code-auditor "billing, to add refunds"
```

A session agent that agrees the scope with you, builds the atlas, answers your questions from it and
ends with a line to paste into a new session: `Atlas: <path>/INDEX.md — read it before the source.`

### Your stack's skills

my-workflow names no language or framework. Each step uses the skills you have installed whose
description names your stack and the step's job (design, implement, test, review). For the agent
steps they are listed per step in `workflow.yaml`, where you can edit them. Rules come from,
first match: your instructions, your project's rules (CLAUDE.md, AGENTS.md, `.claude/rules`, ADRs),
those skills, built-in knowledge.

This repo has two such sets, both still under development: [my-react](../my-react/README.md) for
React and TypeScript, and [my-flutter](../my-flutter/README.md) for Flutter and Dart.

## Migrating to 3.x

Breaking changes since 2.3:

- `/my-workflow:spec-implement` and `/my-workflow:spec-review` are removed. Tests, code and review
  are agents: `my-workflow:spec-tester`, `my-workflow:spec-implementer`,
  `my-workflow:spec-code-reviewer`.
- `my-workflow:spec-reviewer` is split into `my-workflow:spec-design-reviewer` and
  `my-workflow:spec-code-reviewer`; `my-workflow:spec-architect` is removed, design runs in your
  session through `/my-workflow:spec-design`.
- A spec in progress: add a `test` step before `implement` in its `workflow.yaml` and rename the
  review step's agent, or let `drive-spec` do it on resume.
- An atlas written by 2.x uses Input and Output sections; rebuild it to get Depends on, Owns and
  Provides.
- From 3.1, `tasks.md` needs a Batches table and `spec-check plan` fails without one: rerun
  `/my-workflow:spec-plan` on a spec whose plan was written earlier.
