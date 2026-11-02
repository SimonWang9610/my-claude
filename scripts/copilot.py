"""GitHub Copilot: the plugins are installed as plugins, in the Claude format Copilot reads directly
(.claude-plugin/plugin.json, skills/, agents/, hooks/hooks.json).

- Copilot CLI present and working → `copilot plugin marketplace add` + `copilot plugin install`.
  VS Code Copilot Chat picks up CLI-installed plugins automatically.
- Otherwise (VS Code only) → the local plugin folders go into VS Code's `chat.pluginLocations`, and
  `chat.plugins.enabled` is turned on. The settings file is edited in place (comments kept) after a
  backup; `git pull` then updates the plugins with no reinstall.
Earlier versions symlinked skills and agents one by one; those links are removed on every run."""

import functools
import os
import platform
import shutil
import subprocess
from pathlib import Path

from . import common as c
from . import jsonc

NAME = "GitHub Copilot"
ENABLED, LOCATIONS = "chat.plugins.enabled", "chat.pluginLocations"


def vscode_settings() -> Path:
    """VS Code user settings path (override with MY_CLAUDE_VSCODE_SETTINGS, e.g. for Insiders)."""
    if os.environ.get("MY_CLAUDE_VSCODE_SETTINGS"):
        return Path(os.environ["MY_CLAUDE_VSCODE_SETTINGS"]).expanduser()
    system = platform.system()
    if system == "Darwin":
        base = c.HOME / "Library" / "Application Support"
    elif system == "Windows":
        base = Path(os.environ.get("APPDATA", c.HOME / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", c.HOME / ".config"))
    return base / "Code" / "User" / "settings.json"


@functools.lru_cache(maxsize=None)
def cli_problem() -> str:
    path = shutil.which("copilot")
    if not path:
        return "no `copilot` command on PATH"
    try:
        r = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"`{path}` could not run ({e.__class__.__name__})"
    return "" if r.returncode == 0 else f"`{path} --version` failed"


def cli(*args: str) -> bool:
    try:
        return subprocess.run(["copilot", *args]).returncode == 0
    except OSError:
        return False


def _read_settings():
    f = vscode_settings()
    text = f.read_text() if f.exists() else ""
    return f, text, jsonc.load(text)


def _write_settings(f: Path, old: str, new: str):
    if new == old:
        return
    if old:
        backup = f.with_name(f.name + ".my-claude.bak")
        if not backup.exists():
            backup.write_text(old); print(f"  backup {backup}")
    f.parent.mkdir(parents=True, exist_ok=True); f.write_text(new)


def installed(name: str, available: dict) -> str:
    ways = []
    root = c.COPILOT_DIR / "installed-plugins"
    if root.is_dir() and any(p.name == name for p in root.rglob(name) if p.is_dir()):
        ways.append("cli")
    try:
        if _read_settings()[2].get(LOCATIONS, {}).get(str(available[name])):
            ways.append("vscode")
    except ValueError:
        pass
    return " + ".join(ways)


def remove_legacy(names: list, available: dict):
    """Undo the per-skill symlinks, renamed-skill folders, agent links, and hook files of setup ≤ 2026-10-15."""
    for name in names:
        plugin = str(available[name])
        for d in (c.COPILOT_DIR / "skills", c.CLAUDE_DIR / "agents"):
            for p in (d.iterdir() if d.is_dir() else []):
                if c.source_of(p).startswith(plugin + os.sep):
                    c.remove(p); print(f"  removed old {p}")
        hook = c.COPILOT_DIR / "hooks" / f"{name}.json"
        if hook.is_file() and plugin in hook.read_text():
            hook.unlink(); print(f"  removed old {hook}")


def install(names: list, available: dict, local: bool = False):
    remove_legacy(names, available)
    f, text, data = _read_settings()
    if cli_problem():
        print(f"\n{NAME}: {cli_problem()}; registering the plugin folders in VS Code ({f})")
        locations = dict(data.get(LOCATIONS, {}))
        locations.update({str(available[n]): True for n in names})
        new = jsonc.set_key(jsonc.set_key(text, ENABLED, True), LOCATIONS, locations)
        _write_settings(f, text, new)
        for n in names:
            print(f"  {n}: {available[n]}")
        return
    print(f"\n{NAME}: Copilot CLI marketplace '{c.MARKETPLACE}' (VS Code picks CLI-installed plugins up)")
    source = str(c.REPO) if local else c.GITHUB_SOURCE
    cli("plugin", "marketplace", "add", source) or cli("plugin", "marketplace", "update", c.MARKETPLACE)
    for n in names:
        cli("plugin", "install", f"{n}@{c.MARKETPLACE}") and cli("plugin", "update", f"{n}@{c.MARKETPLACE}")
    if f.exists() and data.get(ENABLED) is not True:
        _write_settings(f, text, jsonc.set_key(text, ENABLED, True)); print(f"  enabled {ENABLED} in {f}")


def uninstall(names: list, available: dict):
    print(f"\n{NAME}")
    remove_legacy(names, available)
    f, text, data = _read_settings()
    locations = dict(data.get(LOCATIONS, {}))
    dropped = [n for n in names if locations.pop(str(available[n]), None) is not None]
    if dropped:
        _write_settings(f, text, jsonc.set_key(text, LOCATIONS, locations))
        print(f"  removed from {LOCATIONS}: {', '.join(dropped)}")
    if not cli_problem():
        for n in names:
            if "cli" in installed(n, available):
                cli("plugin", "uninstall", f"{n}@{c.MARKETPLACE}")
