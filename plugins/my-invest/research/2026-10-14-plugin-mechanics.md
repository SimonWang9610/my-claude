# Scout report — Claude Code plugin mechanics (2026-10-14)

Docs at https://code.claude.com/docs/en/ (plugins, plugins-reference, skills, sub-agents, hooks, scheduled-tasks, desktop-scheduled-tasks, routines), fetched 2026-10-14, undated pages referencing v2.1.29x. Local CLI 2.1.58.

## Plugin layout
- Manifest `.claude-plugin/plugin.json`; `name` is the only required key. Components live at plugin root: skills/<name>/SKILL.md, agents/*.md, hooks/hooks.json, .mcp.json, bin/ (on Bash PATH while enabled; rejected by claude.ai and Cowork), settings.json (agent and subagentStatusLine only).
- Skills namespace `/<plugin>:<skill>`; agents register as `<plugin>:<name>`.
- Local convention (think, my-react): plugin.json with name, version, description, keywords only; default dirs; hooks/hooks.json shell form with quoted "${CLAUDE_PLUGIN_ROOT}"/scripts/*.sh, timeout 10.

## Skill frontmatter
- Fields: name, description, when_to_use, argument-hint, arguments, disable-model-invocation, user-invocable, allowed-tools, disallowed-tools, model, effort, context (fork), agent, background, hooks, paths, shell, metadata. Unknown keys silently ignored.
- `context: fork` runs the skill as a subagent with the skill body as prompt; no conversation history, so the body must be self-contained.
- description + when_to_use truncated at 1,536 chars in the listing; trigger first.
- Local skills use name, description, argument-hint only.

## Agent frontmatter
- Fields: name, description (both required), tools, disallowedTools, model (sonnet|opus|haiku|fable|full id|inherit), permissionMode, maxTurns, skills (preloads full content, up to 32), memory (user|project|local), background, isolation (worktree), color, effort, omitClaudeMd.
- For plugin subagents permissionMode, hooks and mcpServers are ignored (hooks go in hooks/hooks.json).
- Pitfall in this repo: my-react agents set permissionMode: auto (ignored for plugin agents); driver.md and oac-driver.md use `permissions: auto`, an undocumented key.

## Scripts and variables
- ${CLAUDE_PLUGIN_ROOT} = install dir of the plugin version (moves on update). ${CLAUDE_PLUGIN_DATA} = ~/.claude/plugins/data/<id>/, persistent across updates, removed on last uninstall unless --keep-data. ${CLAUDE_PROJECT_DIR} = project root. ${CLAUDE_SKILL_DIR} = the skill's own dir.
- Variables substitute inline in skill, command and agent Markdown bodies and in allowed-tools Bash rules. They are NOT in the env of Bash-tool commands: write the literal path in the body, never $VAR.
- Pattern: `allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/x.py *)`; body runs `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/x.py" ...`. The docs name no Python interpreter (unverified).

## Hooks
- hooks/hooks.json with top-level "hooks". 33 events (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SubagentStop, PreCompact, ...). Handler types: command, http, mcp_tool, prompt, agent. Exit 0 success (JSON stdout parsed), exit 2 blocking, other non-zero non-blocking. Skill frontmatter may also carry hooks, registered on invocation.

## State persistence
- ${CLAUDE_PLUGIN_DATA} is the documented persistent per-plugin dir; never write state under ${CLAUDE_PLUGIN_ROOT}.
- userConfig options (string, number, boolean, directory, file; `multiple`; `sensitive` goes to the OS secure store) are saved to pluginConfigs in user settings.json; for settings, not for large lists.
- Agent memory field exists; storage path unverified.

## Scheduling
- No schedule key in the manifest; plugins document scheduling, never declare it. experimental.monitors runs a background process in interactive sessions (not cron).
- /loop: `/loop 1d <prompt>`, units s/m/h/d, recurring tasks expire after 7 days, needs an open session.
- Desktop scheduled task: min 1 minute; Manual/Hourly/Daily/Weekdays/Weekly; needs app open and machine awake; one catch-up within 7 days; definition at ~/.claude/scheduled-tasks/<name>/SKILL.md.
- Cloud routine: research preview; min 1 hour; fresh clone of selected repos; uses skills committed to the repo, not locally installed plugins; so a plugin-only skill or a local watchlist is unavailable to it.

## Recommendation
Scripts under ${CLAUDE_PLUGIN_ROOT}/scripts called via allowed-tools Bash rules; watchlist in ${CLAUDE_PLUGIN_DATA} (survives updates); user creates a Desktop scheduled task or /loop whose prompt invokes the digest skill, documented in README. Changes if runs must happen while the laptop is closed (cloud routine with skill and watchlist committed to a repo) or the watchlist is shared with a team (committed project folder).
