"""Shared paths, plugin discovery, safe symlinking, and interactive prompts."""

import json
import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOME = Path.home()
CLAUDE_DIR, COPILOT_DIR = HOME / ".claude", HOME / ".copilot"
MARKETPLACE, GITHUB_SOURCE = "my-claude", "SimonWang9610/my-claude"
MARKER = ".installed-by-my-claude"  # inside folders we create (renamed Copilot skills); holds the source path
COPY = False  # set by setup.py --copy


def plugins() -> dict:
    """name → plugin folder, in marketplace order (the single list of what this repo ships)."""
    m = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
    return {p["name"]: (REPO / p["source"]).resolve() for p in m["plugins"]}


def remove(p: Path) -> bool:
    if p.is_symlink() or p.is_file():
        p.unlink(); return True
    if p.is_dir():
        shutil.rmtree(p); return True
    return False


def source_of(p: Path) -> str:
    """Where an installed entry points: a symlink's target, or a marker folder's recorded source."""
    if p.is_symlink():
        return os.path.abspath(os.path.join(p.parent, os.readlink(p)))
    if (p / MARKER).is_file():
        return (p / MARKER).read_text().strip()
    return ""


def ours(p: Path) -> bool:
    """True for entries this installer made: links into the repo, marker folders recording a repo path."""
    return source_of(p).startswith(str(REPO))


def place(src: Path, dst: Path):
    """Symlink dst → src (copy with --copy, or when the OS refuses links); never clobber foreign files."""
    if (dst.exists() or dst.is_symlink()) and not ours(dst):
        print(f"  SKIP {dst}: exists and is not ours (remove it to reinstall)"); return
    if dst.is_symlink() and source_of(dst) == str(src):
        return  # already in place
    remove(dst); dst.parent.mkdir(parents=True, exist_ok=True)
    if not COPY:
        try:
            dst.symlink_to(src, target_is_directory=src.is_dir()); print(f"  {dst} → {src}"); return
        except OSError as e:
            print(f"  symlink refused ({e.strerror}); copying instead")
    shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
    if dst.is_dir():
        (dst / MARKER).write_text(str(src) + "\n")
    print(f"  {dst} (copy of {src})")


def prune_dangling():
    """Remove dangling links into this repo (older installers, renamed skills and agents)."""
    for d in (CLAUDE_DIR / "skills", CLAUDE_DIR / "agents", CLAUDE_DIR / "rules", CLAUDE_DIR / "commands",
              COPILOT_DIR / "skills", COPILOT_DIR / "instructions"):
        for p in (d.iterdir() if d.is_dir() else []):
            if p.is_symlink() and not p.exists() and ours(p):
                p.unlink(); print(f"  removed dangling {p}")
    ins = COPILOT_DIR / "copilot-instructions.md"  # think ≤0.6 linked or edited this file
    if ins.is_symlink() and ours(ins):
        ins.unlink(); print(f"  removed old link {ins}")
    elif ins.is_file() and "<!-- think:start -->" in ins.read_text():
        text = re.sub(r"\n*<!-- think:start -->.*?<!-- think:end -->\n?", "\n", ins.read_text(), flags=re.S).strip()
        ins.write_text(text + "\n") if text else ins.unlink()
        print(f"  removed old think block from {ins}")


def interactive() -> bool:
    return sys.stdin.isatty()


def choose(question: str, options: list, labels: dict = None, default: str = "all") -> list:
    """Multi-choice prompt: numbers separated by commas, 'all', or Enter for the default."""
    if not options:
        return []
    print(question)
    for i, o in enumerate(options, 1):
        print(f"  {i}) {o}{'  ' + labels[o] if labels and labels.get(o) else ''}")
    raw = input(f"Choose (e.g. 1,2 · all · none) [{default}]: ").strip().lower() or default
    if raw == "none":
        return []
    if raw == "all":
        return list(options)
    picked = [options[int(x) - 1] for x in re.split(r"[,\s]+", raw) if x.isdigit() and 0 < int(x) <= len(options)]
    if not picked:
        sys.exit(f"Invalid choice: {raw}")
    return list(dict.fromkeys(picked))
