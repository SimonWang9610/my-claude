"""Claude Code: marketplace install through the `claude` CLI, or a symlink under ~/.claude/skills
that Claude Code loads as `<plugin>@skills-dir` (the path when only the VS Code extension exists)."""

import functools
import json
import shutil
import subprocess

from . import common as c

NAME = "Claude Code"
INSTALLED = c.CLAUDE_DIR / "plugins" / "installed_plugins.json"


@functools.lru_cache(maxsize=None)
def cli_problem() -> str:
    """'' when a working `claude` CLI is on PATH; otherwise why not. A `claude` name on PATH is not
    enough: editor extensions and old installs can leave a stub that only prints an error."""
    path = shutil.which("claude")
    if not path:
        return "no `claude` command on PATH"
    try:
        r = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"`{path}` could not run ({e.__class__.__name__})"
    return "" if r.returncode == 0 else f"`{path} --version` failed: {(r.stderr or r.stdout).strip()[:120]}"


def has_cli() -> bool:
    return not cli_problem()


def cli(*args: str) -> bool:
    try:
        return subprocess.run(["claude", *args]).returncode == 0
    except OSError:
        return False


def installed(name: str) -> str:
    """'' when absent, else how it is installed: 'marketplace', 'link', or both (it then loads twice)."""
    try:
        records = json.loads(INSTALLED.read_text()).get("plugins", {})
    except (OSError, ValueError):
        records = {}
    ways = [w for w, on in (("marketplace", f"{name}@{c.MARKETPLACE}" in records),
                            ("link", c.ours(c.CLAUDE_DIR / "skills" / name))) if on]
    return " + ".join(ways)


def link_install(names: list, available: dict):
    for name in names:
        c.place(available[name], c.CLAUDE_DIR / "skills" / name)


def install(names: list, available: dict, link: bool = False, local: bool = False):
    if not link and cli_problem():
        print(f"\n{NAME}: {cli_problem()}; installing as symlinks instead (the VS Code extension loads them)")
        link = True
    if link:
        print(f"\n{NAME}: symlinks (loads as <plugin>@skills-dir)")
        return link_install(names, available)
    print(f"\n{NAME}: marketplace '{c.MARKETPLACE}'")
    source = str(c.REPO) if local else c.GITHUB_SOURCE
    if not cli("plugin", "marketplace", "add", source) and not cli("plugin", "marketplace", "update", c.MARKETPLACE):
        print(f"  marketplace registration failed; installing as symlinks instead")
        return link_install(names, available)
    for name in names:  # `install` no-ops when present; `update` bumps the version
        if cli("plugin", "install", f"{name}@{c.MARKETPLACE}"):
            cli("plugin", "update", f"{name}@{c.MARKETPLACE}")
        else:
            print(f"  {name}: marketplace install failed; installing as a symlink instead")
            link_install([name], available)


def uninstall(names: list, available: dict):
    print(f"\n{NAME}")
    for name in names:
        how = installed(name)
        if "link" in how:
            (c.CLAUDE_DIR / "skills" / name).unlink(); print(f"  removed {c.CLAUDE_DIR / 'skills' / name}")
        if "marketplace" in how and has_cli():
            cli("plugin", "uninstall", f"{name}@{c.MARKETPLACE}")
        elif "marketplace" in how:
            print(f"  {name}: installed from the marketplace; remove it with /plugins in the extension")
