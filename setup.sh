#!/usr/bin/env bash
#
# setup.sh — LAYER 2: link (or remove) the my-claude aggregation dirs into a target .claude/.
#
# Links agents/, commands/, and skills/ from this repo into <dest>/.claude/ as RELATIVE symlinks.
# (Rules are consumed via CLAUDE.md @-imports, not ~/.claude, so they are not linked here.)
#
#     ./setup.sh                          # interactive: choose global or a project, then types
#     ./setup.sh link --global            # link into ~/.claude
#     ./setup.sh link --project ../myapp  # link into ../myapp/.claude
#     ./setup.sh remove --global          # remove this repo's symlinks from ~/.claude
#     ./setup.sh remove --project ../app  # remove from ../app/.claude
#
# Bare `setup.sh` (no link|remove) auto-detects whether the chosen target is already linked with
# this repo's symlinks and offers to unlink them. Passing link or remove explicitly skips that
# prompt — explicit intent wins.
#
# See install.sh to populate the aggregation dirs from stack source dirs (Layer 1).
# See uninstall.sh to reverse Layer 1.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPLY_LINE=""

# Only these types are linked into external .claude targets (NOT rules).
LINK_TYPES="agents commands skills"

# --- helpers ---------------------------------------------------------------

# relpath <from-dir> <to-path> — print <to-path> as a path relative to <from-dir>
relpath() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import os,sys; print(os.path.relpath(sys.argv[2], sys.argv[1]))' "$1" "$2"
  else
    perl -MFile::Spec -e 'print File::Spec->abs2rel($ARGV[1], $ARGV[0])' "$1" "$2"
  fi
}

# resolve <path> — print the absolute realpath a symlink resolves to (follows all hops)
resolve() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$1"
  else
    perl -MCwd -e 'print(Cwd::abs_path($ARGV[0]) // "")' "$1"
  fi
}

# read_line — read one line into $REPLY_LINE; prefer the tty so it works even when stdin is piped
read_line() {
  local a=""
  if ! { IFS= read -r a </dev/tty; } 2>/dev/null; then IFS= read -r a || true; fi
  REPLY_LINE="$a"
}

# count <dir> — count entries in a directory
count() { local d="$1"; [ -d "$d" ] || { echo 0; return; }; ls "$d" 2>/dev/null | wc -l | tr -d ' '; }

# link_group <label> <src_dir> <dst_dir> — relative-symlink each entry of src_dir into dst_dir
link_group() {
  local label="$1" src_dir="$2" dst_dir="$3"
  if [ ! -d "$src_dir" ]; then echo "    (nothing at $src_dir — skipped)"; return; fi
  mkdir -p "$dst_dir"
  local linked=0 skipped=0 src name dst rel
  for src in "$src_dir"/*; do
    [ -e "$src" ] || [ -L "$src" ] || continue
    name="$(basename "$src")"
    dst="$dst_dir/$name"
    rel="$(relpath "$dst_dir" "$src")"
    if [ -L "$dst" ]; then
      if [ "$(readlink "$dst")" = "$rel" ]; then skipped=$((skipped + 1)); continue; fi
      rm "$dst"; ln -s "$rel" "$dst"; linked=$((linked + 1))
    elif [ -e "$dst" ]; then
      echo "    WARN  $name is a real file in $dst_dir — left as-is"
    else
      ln -s "$rel" "$dst"; linked=$((linked + 1))
    fi
  done
  echo "    $linked linked, $skipped already-linked"
}

# remove_group <label> <dir> — remove symlinks in <dir> that resolve under $REPO/
remove_group() {
  local label="$1" dir="$2" e removed=0
  [ -d "$dir" ] || { echo "    (no $dir — skipped)"; return; }
  for e in "$dir"/*; do
    [ -L "$e" ] || continue
    case "$(resolve "$e")" in
      "$REPO/"*) rm -f "$e"; echo "    removed $(basename "$e")"; removed=$((removed + 1)) ;;
    esac
  done
  echo "    $removed removed"
}

# count_linked <claude_dir> — count symlinks across agents/commands/skills that resolve under $REPO/
count_linked() {
  local claude="$1" t dir e total=0
  for t in $LINK_TYPES; do
    dir="$claude/$t"
    [ -d "$dir" ] || continue
    for e in "$dir"/*; do
      [ -L "$e" ] || continue
      case "$(resolve "$e")" in "$REPO/"*) total=$((total + 1)) ;; esac
    done
  done
  echo "$total"
}

usage() {
  echo "usage: setup.sh [link|remove] [--global | --project <dir>]"
  exit 2
}

# --- parse action ----------------------------------------------------------

action="${1:-}"
action_explicit=0
case "$action" in
  link|remove) action_explicit=1; shift ;;
  --global|--project|"") action="link" ;;  # default action = link; location flag follows
  *) usage ;;
esac

# --- parse location --------------------------------------------------------

parent=""
case "${1:-}" in
  --global)
    parent="$HOME"
    ;;
  --project)
    parent="$(cd "${2:?usage: setup.sh [link|remove] --project <dir>}" && pwd -P)"
    ;;
  "")
    echo "Where should this bundle be ${action}ed?"
    echo "  1) Global   — ~/.claude  (applies to every project)"
    echo "  2) Project  — <some-project>/.claude  (just that project)"
    printf "Choose [1/2, empty to cancel]: "
    read_line
    case "$REPLY_LINE" in
      1) parent="$HOME" ;;
      2)
        printf "Project directory: "
        read_line
        [ -n "$REPLY_LINE" ] || { echo "No path given — cancelled."; exit 0; }
        parent="$(cd "$REPLY_LINE" && pwd -P)"
        ;;
      *) echo "Cancelled."; exit 0 ;;
    esac
    ;;
  *) usage ;;
esac

CLAUDE="$parent/.claude"

# --- auto-detect already-linked target (only when action wasn't given explicitly) --------

if [ "$action_explicit" = 0 ]; then
  n_linked="$(count_linked "$CLAUDE")"
  if [ "$n_linked" -gt 0 ]; then
    echo
    echo "This target already has $n_linked linked entry(s) from this repo:  $CLAUDE"
    echo "  1) Unlink them"
    echo "  2) Re-link / update"
    echo "  3) Cancel"
    printf "Choose [1/2/3, empty to cancel]: "
    read_line
    case "$REPLY_LINE" in
      1) action="remove" ;;
      2) action="link" ;;
      *) echo "Cancelled."; exit 0 ;;
    esac
  fi
fi

# --- type selection --------------------------------------------------------

n_agt="$(count "$REPO/agents")"
n_cmd="$(count "$REPO/commands")"
n_skl="$(count "$REPO/skills")"

echo
echo "$action into: $CLAUDE"
echo "  from: $REPO"
echo "  relative symlinks · already-linked skipped · your own files never clobbered"
echo
echo "Types — pick any combination:"
echo "  1) agents    $n_agt entry(s)  →  $CLAUDE/agents/"
echo "  2) commands  $n_cmd entry(s)  →  $CLAUDE/commands/"
echo "  3) skills    $n_skl entry(s)  →  $CLAUDE/skills/"
echo
printf "Select types [e.g. \"1 3\", \"all\", or empty to cancel]: "
read_line
SEL="$(printf '%s' "$REPLY_LINE" | tr 'A-Z,' 'a-z ')"

# sel <num> <name> — is this item selected?
sel() {
  case " $SEL " in *" all "*) return 0 ;; esac
  local t
  for t in $SEL; do [ "$t" = "$1" ] && return 0; [ "$t" = "$2" ] && return 0; done
  return 1
}

# --- run -------------------------------------------------------------------

did=0
echo
if [ "$action" = "link" ]; then
  if sel 1 agents;   then echo "→ agents:   linking $n_agt entry(s) into $CLAUDE/agents/";   link_group   agents   "$REPO/agents"   "$CLAUDE/agents";   did=1; else echo "· agents: not selected — skipped"; fi
  if sel 2 commands; then echo "→ commands: linking $n_cmd entry(s) into $CLAUDE/commands/"; link_group   commands "$REPO/commands" "$CLAUDE/commands"; did=1; else echo "· commands: not selected — skipped"; fi
  if sel 3 skills;   then echo "→ skills:   linking $n_skl entry(s) into $CLAUDE/skills/";   link_group   skills   "$REPO/skills"   "$CLAUDE/skills";   did=1; else echo "· skills: not selected — skipped"; fi
else
  if sel 1 agents;   then echo "→ agents:   removing bundle symlinks from $CLAUDE/agents/";   remove_group agents   "$CLAUDE/agents";   did=1; else echo "· agents: not selected — skipped"; fi
  if sel 2 commands; then echo "→ commands: removing bundle symlinks from $CLAUDE/commands/"; remove_group commands "$CLAUDE/commands"; did=1; else echo "· commands: not selected — skipped"; fi
  if sel 3 skills;   then echo "→ skills:   removing bundle symlinks from $CLAUDE/skills/";   remove_group skills   "$CLAUDE/skills";   did=1; else echo "· skills: not selected — skipped"; fi
fi

echo
if [ "$did" = 1 ]; then
  if [ "$action" = "link" ]; then
    echo "Done. Reload Claude Code in $parent to pick up the links. Run 'setup.sh remove' to undo."
  else
    echo "Done. Reload Claude Code in $parent."
  fi
else
  echo "Nothing selected — nothing changed."
fi
