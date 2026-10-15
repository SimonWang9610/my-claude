"""GitHub Copilot: skills symlinked into ~/.copilot/skills, Claude-format agents into ~/.claude/agents
(the location VS Code Copilot reads in that format), hooks written to ~/.copilot/hooks/<plugin>.json.

Copilot has one flat skill namespace. A skill name shared by several installed plugins is installed as
`<plugin>-<skill>` for each of them: a real folder with a SKILL.md whose `name` is rewritten (Copilot
requires folder name == name) and symlinks for everything else. Names are recomputed over every plugin
installed for Copilot on each install and uninstall, so prefixes appear and disappear as clashes do."""

import json
import os
import re

from . import common as c

NAME = "GitHub Copilot"
SKILLS, AGENTS, HOOKS = c.COPILOT_DIR / "skills", c.CLAUDE_DIR / "agents", c.COPILOT_DIR / "hooks"


def skills_of(plugin) -> list:
    return sorted(s.parent for s in (plugin / "skills").glob("*/SKILL.md"))


def installed(name: str, available: dict) -> str:
    plugin = available[name]
    for skill in skills_of(plugin):
        for p in (SKILLS / skill.name, SKILLS / f"{name}-{skill.name}"):
            if c.source_of(p) == str(skill):
                return "link"
    return ""


def names_for(plugin_names: list, available: dict) -> dict:
    """(plugin, skill folder) → Copilot skill name; shared names get the plugin prefix."""
    found = [(p, s) for p in plugin_names for s in skills_of(available[p])]
    count = {}
    for _, s in found:
        count[s.name] = count.get(s.name, 0) + 1
    return {(p, s): (f"{p}-{s.name}" if count[s.name] > 1 else s.name) for p, s in found}


def place_renamed(src, dst, name: str):
    """A skill under a new name: SKILL.md with `name:` rewritten, every other entry symlinked."""
    if (dst.exists() or dst.is_symlink()) and not c.ours(dst):
        print(f"  SKIP {dst}: exists and is not ours (remove it to reinstall)"); return
    c.remove(dst); dst.mkdir(parents=True)
    for child in src.iterdir():
        if child.name == "SKILL.md":
            (dst / "SKILL.md").write_text(re.sub(r"(?m)^name:.*$", f"name: {name}", child.read_text(), count=1))
        else:
            c.place(child, dst / child.name)
    (dst / c.MARKER).write_text(str(src) + "\n")
    print(f"  {dst} → {src} (as {name}; re-run setup after pulling changes to its SKILL.md)")


def hooks_for(plugin) -> dict:
    """The plugin's hooks.json flattened to Copilot's shape, ${CLAUDE_PLUGIN_ROOT} resolved."""
    src = plugin / "hooks" / "hooks.json"
    out = {}
    for event, groups in (json.loads(src.read_text()).get("hooks", {}) if src.exists() else {}).items():
        for group in groups:
            for h in group.get("hooks", [group]):
                if h.get("type") == "command":
                    cmd = h["command"].replace("${CLAUDE_PLUGIN_ROOT}", str(plugin))
                    out.setdefault(event, []).append({"type": "command", "command": cmd, "timeout": h.get("timeout", 30)})
    return {"hooks": out} if out else {}


def sync_skills(plugin_names: list, available: dict):
    """Place every skill of these plugins under its current name; drop the other variant if ours."""
    for (p, skill), name in names_for(plugin_names, available).items():
        target, other = SKILLS / name, SKILLS / (skill.name if name != skill.name else f"{p}-{skill.name}")
        if c.source_of(other) == str(skill):
            c.remove(other); print(f"  removed {other} (now {name})")
        c.place(skill, target) if name == skill.name else place_renamed(skill, target, name)


def install(names: list, available: dict, already: list):
    print(f"\n{NAME}: symlinks")
    sync_skills(list(dict.fromkeys(already + names)), available)
    for name in names:
        plugin = available[name]
        for agent in sorted((plugin / "agents").glob("*.md")):
            c.place(agent, AGENTS / agent.name)
        hooks = hooks_for(plugin)
        if hooks:
            HOOKS.mkdir(parents=True, exist_ok=True)
            (HOOKS / f"{name}.json").write_text(json.dumps(hooks, indent=2) + "\n"); print(f"  {HOOKS / (name + '.json')}")
        if any("CLAUDE_PLUGIN_ROOT" in f.read_text() for f in (plugin / "skills").rglob("*.md")):
            print(f"  NOTE {name}: its skills reference ${{CLAUDE_PLUGIN_ROOT}}, which Copilot does not resolve.")


def uninstall(names: list, available: dict, remaining: list):
    print(f"\n{NAME}")
    for name in names:
        plugin = available[name]
        for skill in skills_of(plugin):
            for p in (SKILLS / skill.name, SKILLS / f"{name}-{skill.name}"):
                if c.source_of(p) == str(skill):
                    c.remove(p); print(f"  removed {p}")
        for agent in (plugin / "agents").glob("*.md"):
            p = AGENTS / agent.name
            if c.source_of(p) == str(agent):
                p.unlink(); print(f"  removed {p}")
        hook = HOOKS / f"{name}.json"
        if hook.exists() and str(plugin) in hook.read_text():
            hook.unlink(); print(f"  removed {hook}")
    if remaining:
        sync_skills(remaining, available)  # a clash may be gone: prefixed names revert to plain ones
