#!/usr/bin/env python3
"""install.py — register the my-claude plugin marketplace and install its plugins
via the `claude plugin` CLI.

  python3 install.py                # marketplace (GitHub) + my-react
  python3 install.py --flutter     # also install my-flutter
  python3 install.py --local       # register THIS checkout as the marketplace (development)
  python3 install.py --rules      # also symlink rules/preferences.md -> ~/.claude/rules/
  python3 install.py --aliases    # also write shell functions for the driver agents
  python3 install.py --uninstall  # remove plugins + marketplace + rules symlink + aliases
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
MARKETPLACE = "my-claude"
GITHUB_SOURCE = "SimonWang9610/my-claude"
PLUGINS = ["my-react", "my-flutter"]
RULES_SRC = REPO / "rules" / "preferences.md"
RULES_LINK = Path.home() / ".claude" / "rules" / "preferences.md"
DRIVER_ALIASES = {"my-react-driver": "my-react:driver", "my-react-oac-driver": "my-react:oac-driver"}
ALIAS_BEGIN = "# >>> my-claude driver aliases >>>"
ALIAS_END = "# <<< my-claude driver aliases <<<"


def rc_file() -> Path:
    import os
    if "zsh" in os.environ.get("SHELL", ""):
        return Path(os.environ.get("ZDOTDIR", Path.home())) / ".zshrc"
    return Path.home() / ".bashrc"


def strip_alias_block(text: str) -> str:
    lines, out, skipping = text.splitlines(), [], False
    for line in lines:
        if line.strip() == ALIAS_BEGIN:
            skipping = True
            continue
        if line.strip() == ALIAS_END:
            skipping = False
            continue
        if not skipping:
            out.append(line)
    return "\n".join(out).rstrip("\n") + "\n" if out else ""


def write_aliases() -> None:
    rc = rc_file()
    base = strip_alias_block(rc.read_text()) if rc.exists() else ""
    block = [ALIAS_BEGIN, "# managed by my-claude/install.py — run --uninstall or delete this block to remove"]
    for name, agent in DRIVER_ALIASES.items():
        block.append(f'{name}() {{ claude --agent {agent} --worktree "$@"; }}')
    block.append(ALIAS_END)
    rc.write_text(base + "\n".join(block) + "\n")
    print(f"Aliases written to {rc} ({', '.join(DRIVER_ALIASES)}) — open a new shell or `source` it.")


def remove_aliases() -> None:
    rc = rc_file()
    if rc.exists() and ALIAS_BEGIN in rc.read_text():
        rc.write_text(strip_alias_block(rc.read_text()))
        print("Removed driver aliases.")


def claude(*args: str, check: bool = True) -> bool:
    """Run a claude CLI command; return True on success."""
    result = subprocess.run(["claude", *args])
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result.returncode == 0


def uninstall() -> None:
    for plugin in PLUGINS:
        claude("plugin", "uninstall", f"{plugin}@{MARKETPLACE}", check=False)
    claude("plugin", "marketplace", "remove", MARKETPLACE, check=False)
    if RULES_LINK.is_symlink() and RULES_LINK.resolve() == RULES_SRC:
        RULES_LINK.unlink()
        print("Removed rules symlink.")
    remove_aliases()
    print("Uninstalled.")


def link_rules() -> None:
    RULES_LINK.parent.mkdir(parents=True, exist_ok=True)
    if RULES_LINK.exists() and not RULES_LINK.is_symlink():
        print(f"WARN: {RULES_LINK} is a real file — left as-is.")
        return
    if RULES_LINK.is_symlink():
        RULES_LINK.unlink()
    RULES_LINK.symlink_to(RULES_SRC)
    print(f"Linked {RULES_SRC} -> {RULES_LINK}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--flutter", action="store_true", help="also install my-flutter")
    parser.add_argument("--local", action="store_true", help="register this checkout as the marketplace")
    parser.add_argument("--rules", action="store_true", help="symlink rules/preferences.md into ~/.claude/rules/")
    parser.add_argument("--aliases", action="store_true", help="write shell functions for the driver agents into your rc file")
    parser.add_argument("--uninstall", action="store_true", help="remove plugins, marketplace, rules symlink, and aliases")
    args = parser.parse_args()

    if shutil.which("claude") is None:
        sys.exit("claude CLI not found — install Claude Code first.")

    if args.uninstall:
        uninstall()
        return

    source = str(REPO) if args.local else GITHUB_SOURCE
    print(f"Registering marketplace '{MARKETPLACE}' from {source}")
    if not claude("plugin", "marketplace", "add", source, check=False):
        claude("plugin", "marketplace", "update", MARKETPLACE)

    claude("plugin", "install", f"my-react@{MARKETPLACE}")
    if args.flutter:
        claude("plugin", "install", f"my-flutter@{MARKETPLACE}")

    if args.rules:
        link_rules()

    if args.aliases:
        write_aliases()

    print("Done. Try: claude --agent my-react:driver --worktree \"<your feature>\"")


if __name__ == "__main__":
    main()
