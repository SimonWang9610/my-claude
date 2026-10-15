"""Claude Code: marketplace install through the `claude` CLI, or a symlink under ~/.claude/skills
that Claude Code loads as `<plugin>@skills-dir` (the path when only the VS Code extension exists)."""

import json
import shutil
import subprocess
import sys

from . import common as c

NAME = "Claude Code"
INSTALLED = c.CLAUDE_DIR / "plugins" / "installed_plugins.json"


def has_cli() -> bool:
    return shutil.which("claude") is not None


def cli(*args: str, check: bool = True) -> bool:
    ok = subprocess.run(["claude", *args]).returncode == 0
    if check and not ok:
        sys.exit(f"claude {' '.join(args)} failed")
    return ok


def installed(name: str) -> str:
    """'' when absent, else how it is installed: 'marketplace', 'link', or both (it then loads twice)."""
    try:
        records = json.loads(INSTALLED.read_text()).get("plugins", {})
    except (OSError, ValueError):
        records = {}
    ways = [w for w, on in (("marketplace", f"{name}@{c.MARKETPLACE}" in records),
                            ("link", c.ours(c.CLAUDE_DIR / "skills" / name))) if on]
    return " + ".join(ways)


def install(names: list, available: dict, link: bool = False, local: bool = False):
    link = link or not has_cli()
    print(f"\n{NAME}: " + ("symlinks (loads as <plugin>@skills-dir)" if link else f"marketplace '{c.MARKETPLACE}'"))
    if link:
        for name in names:
            c.place(available[name], c.CLAUDE_DIR / "skills" / name)
        return
    source = str(c.REPO) if local else c.GITHUB_SOURCE
    if not cli("plugin", "marketplace", "add", source, check=False):
        cli("plugin", "marketplace", "update", c.MARKETPLACE)
    for name in names:  # `install` no-ops when present; `update` bumps the version
        cli("plugin", "install", f"{name}@{c.MARKETPLACE}")
        cli("plugin", "update", f"{name}@{c.MARKETPLACE}", check=False)


def uninstall(names: list, available: dict):
    print(f"\n{NAME}")
    for name in names:
        how = installed(name)
        if "link" in how:
            (c.CLAUDE_DIR / "skills" / name).unlink(); print(f"  removed {c.CLAUDE_DIR / 'skills' / name}")
        if "marketplace" in how and has_cli():
            cli("plugin", "uninstall", f"{name}@{c.MARKETPLACE}", check=False)
        elif "marketplace" in how:
            print(f"  {name}: installed from the marketplace; remove it with /plugins in the extension")
