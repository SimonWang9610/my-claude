#!/usr/bin/env bash
#
# link-commands.sh — link this bundle's /sf-* command files into a .claude/commands/.
#
# The /sf-* stage commands live in sflow/commands/. This script per-entry relative-symlinks them:
#
#     sflow/commands/* -> <dest>/.claude/commands/
#
# They are linked SEPARATELY from the core bundle (link.sh handles skills/ agents/ rules/) because,
# installed globally, the /sf-* set shadows a project's own /spec-* commands. Link them only where
# an sflow (/sf-*) workflow is actually used — typically a specific project, not ~/.claude.
#
#     ./link-commands.sh --global             # into ~/.claude/commands
#     ./link-commands.sh --project ../myapp   # into ../myapp/.claude/commands
#     ./link-commands.sh                      # interactive
#
# Symlinks are RELATIVE; an existing correct link is skipped; a foreign real file (or a link
# pointing outside this repo) is never clobbered (warned, left as-is). Re-running is safe.
# See unlink-commands.sh to remove.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SRC_DIR="$REPO/sflow/commands"
REPLY_LINE=""

relpath() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import os,sys; print(os.path.relpath(sys.argv[2], sys.argv[1]))' "$1" "$2"
  else
    perl -MFile::Spec -e 'print File::Spec->abs2rel($ARGV[1], $ARGV[0])' "$1" "$2"
  fi
}

read_line() {
  local a=""
  if ! { IFS= read -r a </dev/tty; } 2>/dev/null; then IFS= read -r a || true; fi
  REPLY_LINE="$a"
}

usage() {
  echo "usage: link-commands.sh [--global | --project <dir>]"
  echo "  per-entry symlinks sflow/commands/* into <dest>/.claude/commands/"
}

# --- parse args --------------------------------------------------------------
DEST=""
while [ $# -gt 0 ]; do
  case "$1" in
    --global)  DEST="$HOME/.claude" ;;
    --project) shift; [ $# -gt 0 ] || { usage; exit 2; }
               DEST="$(cd "$1" && pwd -P)/.claude" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
  shift
done

if [ -z "$DEST" ]; then
  printf "Destination — 1) global ~/.claude  2) project dir [1/2]: "
  read_line
  case "$REPLY_LINE" in
    2) printf "Project dir: "; read_line
       [ -d "$REPLY_LINE" ] || { echo "No such dir: $REPLY_LINE"; exit 2; }
       DEST="$(cd "$REPLY_LINE" && pwd -P)/.claude" ;;
    *) DEST="$HOME/.claude" ;;
  esac
fi

# --- link --------------------------------------------------------------------
[ -d "$SRC_DIR" ] || { echo "No such source dir: $SRC_DIR"; exit 1; }
echo "Linking /sf-* commands into $DEST/commands (relative symlinks)"
total=0 skipped=0
for src in "$SRC_DIR"/*; do
  [ -e "$src" ] || continue
  mkdir -p "$DEST/commands"
  dst="$DEST/commands/$(basename "$src")"
  rel="$(relpath "$DEST/commands" "$src")"
  if [ -L "$dst" ]; then
    [ "$(readlink "$dst")" = "$rel" ] && { skipped=$((skipped+1)); continue; }
    case "$(cd "$DEST/commands" && cd "$(dirname "$(readlink "$dst")")" 2>/dev/null && pwd -P || echo /nonexistent)" in
      "$REPO"*) rm "$dst" ;;   # stale link into this repo — replace
      *) echo "  WARN commands/$(basename "$src") links elsewhere — left as-is"; continue ;;
    esac
  elif [ -e "$dst" ]; then
    echo "  WARN commands/$(basename "$src") is a real file in $DEST — left as-is"; continue
  fi
  ln -s "$rel" "$dst"; total=$((total+1))
done
echo "Done: $total linked, $skipped already linked. Run unlink-commands.sh to remove."
