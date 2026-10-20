#!/usr/bin/env python3
"""setup.py — install or uninstall this repo's plugins for Claude Code and/or GitHub Copilot.

  python3 setup.py                     # interactive install: pick tools, then plugins
  python3 setup.py uninstall           # interactive uninstall
  python3 setup.py status              # what is installed where
  python3 setup.py install --tools claude,copilot --plugins my-spec,my-react
  python3 setup.py install --tools copilot --plugins all --update

Already-installed plugins are skipped per tool unless --update is given. Claude Code installs through
the `claude` CLI when it works, otherwise (or with --link) as a symlink loaded as `<plugin>@skills-dir`.
Copilot reads the same Claude-format plugins: through the `copilot` CLI when it works, otherwise by
registering the plugin folders in VS Code's chat.pluginLocations. Every run removes dangling links into this repo left by older installers.
Stdlib only; modules live in scripts/.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # works under `python3 -I` too

from scripts import claude, common, copilot, extras  # noqa: E402

TOOLS = {"claude": claude, "copilot": copilot}


def status_of(tool: str, name: str, available: dict) -> str:
    return claude.installed(name) if tool == "claude" else copilot.installed(name, available)


def pick(args, available: dict, uninstall: bool):
    """Tools first, then plugins; a plugin is offered when at least one chosen tool still needs it."""
    if args.tools:
        tools = list(TOOLS) if args.tools == "all" else [t.strip() for t in args.tools.split(",")]
    elif common.interactive():
        tools = [{"Claude Code": "claude", "GitHub Copilot": "copilot"}[t] for t in
                 common.choose("Which tools?", ["Claude Code", "GitHub Copilot"], default="1")]
    else:
        sys.exit("No --tools given and no terminal to ask in. Example: setup.py install --tools claude --plugins my-spec")
    bad = [t for t in tools if t not in TOOLS]
    if bad:
        sys.exit(f"Unknown tool(s): {', '.join(bad)}. Use claude, copilot, or all.")

    def wanted(tool, name):
        present = bool(status_of(tool, name, available))
        return present if uninstall else (args.update or not present)

    labels = {n: " · ".join(f"{TOOLS[t].NAME}: {status_of(t, n, available) or 'not installed'}" for t in tools)
              for n in available}
    offer = [n for n in available if any(wanted(t, n) for t in tools)]
    if args.plugins:
        names = list(available) if args.plugins == "all" else [p.strip() for p in args.plugins.split(",")]
        unknown = [n for n in names if n not in available]
        if unknown:
            sys.exit(f"Unknown plugin(s): {', '.join(unknown)}. Available: {', '.join(available)}")
        names = [n for n in names if n in offer]
    elif common.interactive():
        if not offer:
            print("Nothing to " + ("uninstall." if uninstall else "install: every plugin is already installed (use --update).")); return tools, {}
        names = common.choose("Which plugins?" + ("" if uninstall else " (already installed ones are not listed)"),
                              offer, labels)
    else:
        sys.exit("No --plugins given and no terminal to ask in.")
    return tools, {t: [n for n in names if wanted(t, n)] for t in tools}


def migrate_renamed(plan: dict):
    """Uninstall a renamed plugin's old name from each tool that is installing its new name."""
    for old, new in common.RENAMED.items():
        legacy = {old: common.REPO / "plugins" / old}
        for tool, names in plan.items():
            if new in names and status_of(tool, old, legacy):
                print(f"{TOOLS[tool].NAME}: {old} was renamed {new}; removing {old}")
                TOOLS[tool].uninstall([old], legacy)


def status(available: dict):
    for name in available:
        print(f"{name:12} " + "  ".join(f"{TOOLS[t].NAME}: {status_of(t, name, available) or '-'}" for t in TOOLS))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", nargs="?", default="install", choices=["install", "uninstall", "status"])
    ap.add_argument("--tools", help="claude, copilot, or both comma-separated / 'all' (asked when omitted)")
    ap.add_argument("--plugins", help="comma-separated plugin names or 'all' (asked when omitted)")
    ap.add_argument("--update", action="store_true", help="also reinstall/update plugins that are already installed")
    ap.add_argument("--link", action="store_true", help="Claude Code: symlink instead of the marketplace (automatic without the CLI)")
    ap.add_argument("--local", action="store_true", help="register this checkout as the marketplace (CLI installs)")
    ap.add_argument("--copy", action="store_true", help="copy instead of symlinking")
    ap.add_argument("--rules", action="store_true", help="Claude Code: link rules/preferences.md into ~/.claude/rules/")
    ap.add_argument("--aliases", action="store_true", help="Claude Code: shell functions for the my-react driver agents")
    ap.add_argument("--metrics", action="store_true", help="Claude Code: start the local telemetry stack")
    args = ap.parse_args()
    common.COPY = args.copy
    available = common.plugins()

    if args.action == "status":
        return status(available)
    uninstall = args.action == "uninstall"
    tools, plan = pick(args, available, uninstall)
    if not any(plan.values()) and not (args.rules or args.aliases or args.metrics):
        print("Nothing to do."); return
    for tool, names in plan.items():
        print(f"{TOOLS[tool].NAME}: {', '.join(names) or 'nothing'}")
    print("Cleaning dangling links:"); common.prune_dangling()

    if uninstall:
        if plan.get("claude"):
            claude.uninstall(plan["claude"], available)
        if plan.get("copilot"):
            copilot.uninstall(plan["copilot"], available)
        if "claude" in tools and (args.rules or args.aliases):
            extras.unlink_rules(); extras.remove_aliases()
        print("\nDone."); return

    migrate_renamed(plan)
    if plan.get("claude"):
        claude.install(plan["claude"], available, link=args.link, local=args.local)
        if "my-react" in plan["claude"]:
            extras.check_lsp()
    if plan.get("copilot"):
        copilot.install(plan["copilot"], available, local=args.local)
    if "claude" in tools:
        if args.rules: extras.link_rules()
        if args.aliases: extras.write_aliases()
        if args.metrics: extras.start_metrics()
    print("\nDone. Claude Code: restart or /reload-plugins. Copilot: reload the window. Skills are /<plugin>:<skill> in both.")


if __name__ == "__main__":
    main()
