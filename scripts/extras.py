"""Claude Code extras: my-react driver shell aliases, telemetry stack, LSP check."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import common as c

DRIVER_ALIASES = {"my-react-driver": "my-react:driver"}
BEGIN, END = "# >>> my-claude driver aliases >>>", "# <<< my-claude driver aliases <<<"


def rc_file() -> Path:
    if "zsh" in os.environ.get("SHELL", ""):
        return Path(os.environ.get("ZDOTDIR", c.HOME)) / ".zshrc"
    return c.HOME / ".bashrc"


def _strip(text: str) -> str:
    return re.sub(rf"\n?{re.escape(BEGIN)}.*?{re.escape(END)}\n?", "\n", text, flags=re.S).strip("\n") + "\n"


def write_aliases():
    rc = rc_file(); base = _strip(rc.read_text()) if rc.exists() else ""
    block = [BEGIN, "# managed by my-claude/setup.py — run `setup.py uninstall` or delete this block"]
    block += [f'{n}() {{ claude --agent {a} --worktree "$@"; }}' for n, a in DRIVER_ALIASES.items()] + [END]
    rc.write_text(base + "\n".join(block) + "\n")
    print(f"  aliases written to {rc} ({', '.join(DRIVER_ALIASES)}); open a new shell")


def remove_aliases():
    rc = rc_file()
    if rc.exists() and BEGIN in rc.read_text():
        rc.write_text(_strip(rc.read_text())); print(f"  removed driver aliases from {rc}")


def start_metrics():
    subprocess.run([sys.executable, str(c.REPO / "metrics" / "stack.py"), "up"])


def check_lsp():
    missing = [b for b in ("typescript-language-server", "tsserver") if shutil.which(b) is None]
    if missing:
        print("  NOTE my-react registers a TypeScript language server, but " + ", ".join(missing) + " is not on PATH:\n"
              "       npm install -g typescript-language-server typescript")
