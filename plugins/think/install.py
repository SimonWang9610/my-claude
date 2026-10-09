#!/usr/bin/env python3
"""install.py — link the `think` skillset into Claude Code and/or GitHub Copilot, no plugin CLI needed.

  python3 install.py              # both hosts, user scope, symlinks (git pull updates in place)
  python3 install.py --claude     # Claude Code (CLI or VS Code extension): ~/.claude/skills/think → this folder
  python3 install.py --copilot    # GitHub Copilot (VS Code / CLI): ~/.copilot/{skills,hooks,copilot-instructions.md}, ~/.claude/agents
  python3 install.py --copy       # copy instead of symlink (Windows without symlink rights)
  python3 install.py --uninstall  # remove every link or file this script placed

Stdlib only. Re-running is safe. Claude Code loads ~/.claude/skills/think as the plugin `think@skills-dir`
(skills, agents, hooks). Copilot loads skills from ~/.copilot/skills, Claude-format agents from
~/.claude/agents, instructions from ~/.copilot/copilot-instructions.md, hooks from ~/.copilot/hooks.
"""
import argparse, json, os, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = Path.home()
SKILLS = ["clarify", "explore", "architect"]
AGENTS = ["explorer", "scout"]
START, END = "<!-- think:start -->", "<!-- think:end -->"
COPY = False


def remove(p: Path):
    if p.is_symlink() or p.is_file():
        p.unlink(); return True
    if p.is_dir():
        shutil.rmtree(p); return True
    return False


def place(src: Path, dst: Path):
    """Symlink dst → src (copy with --copy, or when the OS refuses symlinks)."""
    remove(dst); dst.parent.mkdir(parents=True, exist_ok=True)
    if not COPY:
        try:
            dst.symlink_to(src, target_is_directory=src.is_dir()); print(f"  {dst} → {src}"); return
        except OSError as e:
            print(f"  symlink refused ({e.strerror}); copying instead")
    shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst); print(f"  {dst} (copy)")


def install_claude():
    print("Claude Code: ~/.claude/skills/think (loads as plugin think@skills-dir)")
    place(HERE, HOME / ".claude" / "skills" / "think")


def install_copilot():
    cp = HOME / ".copilot"
    print("GitHub Copilot")
    for name in SKILLS:
        place(HERE / "skills" / name, cp / "skills" / name)
    for name in AGENTS:  # Claude-format agents; VS Code Copilot reads this location as such
        place(HERE / "agents" / f"{name}.md", HOME / ".claude" / "agents" / f"{name}.md")
    ins = cp / "copilot-instructions.md"; protocol = HERE / "PROTOCOL.md"
    if not ins.exists() or ins.is_symlink():
        place(protocol, ins)  # the whole file is ours → link it
    else:  # the user has their own instructions → keep them, (re)insert our block between markers
        block = f"{START}\n{protocol.read_text().strip()}\n{END}\n"; old = ins.read_text()
        ins.write_text(re.sub(rf"{START}.*?{END}\n?", block, old, flags=re.S) if START in old else old.rstrip() + "\n\n" + block)
        print(f"  {ins} (block between markers)")
    hooks = cp / "hooks"; hooks.mkdir(parents=True, exist_ok=True); script = HERE / "scripts" / "prompt-gate.py"
    (hooks / "think.json").write_text(json.dumps({"hooks": {"UserPromptSubmit": [{
        "type": "command", "command": f'python3 -I "{script}"', "windows": f'python -I "{script}"', "timeout": 10}]}}, indent=2) + "\n")
    print(f"  {hooks / 'think.json'} → {script}")


def uninstall():
    cp = HOME / ".copilot"
    for p in [HOME / ".claude" / "skills" / "think", *(cp / "skills" / n for n in SKILLS),
              *(HOME / ".claude" / "agents" / f"{n}.md" for n in AGENTS), cp / "hooks" / "think.json", cp / "hooks" / "think"]:
        if remove(p): print(f"  removed {p}")
    ins = cp / "copilot-instructions.md"
    if ins.is_symlink() and ins.resolve() == (HERE / "PROTOCOL.md").resolve():
        ins.unlink(); print(f"  removed {ins}")
    elif ins.is_file() and START in ins.read_text():
        text = re.sub(rf"\n*{START}.*?{END}\n?", "\n", ins.read_text(), flags=re.S).strip()
        (ins.write_text(text + "\n") if text else ins.unlink()); print(f"  cleaned {ins}")


def main():
    global COPY
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for f in ("claude", "copilot", "copy", "uninstall"): ap.add_argument(f"--{f}", action="store_true")
    a = ap.parse_args(); COPY = a.copy
    if a.uninstall: return uninstall()
    both = not (a.claude or a.copilot)
    if a.claude or both: install_claude()
    if a.copilot or both: install_copilot()
    print("Done. Claude Code: /think:clarify, /think:explore, /think:architect (restart or /reload-plugins)."
          "\n      Copilot: /clarify, /explore, /architect (reload the window).")


if __name__ == "__main__":
    sys.exit(main())
