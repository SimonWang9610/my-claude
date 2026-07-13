#!/usr/bin/env bash
#
# unlink-commands.sh — remove the /sf-* command symlinks link-commands.sh created.
#
#     ./unlink-commands.sh --global
#     ./unlink-commands.sh --project ../myapp
#     ./unlink-commands.sh                    # interactive
#
# Only symlinks in <dest>/.claude/commands/ that resolve back into THIS repo are removed;
# anything else is left untouched. An emptied commands/ dir is pruned. Re-running is safe.
# See link-commands.sh.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPLY_LINE=""

read_line() {
  local a=""
  if ! { IFS= read -r a </dev/tty; } 2>/dev/null; then IFS= read -r a || true; fi
  REPLY_LINE="$a"
}

usage() { echo "usage: unlink-commands.sh [--global | --project <dir>]"; }

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

echo "Unlinking /sf-* commands from $DEST/commands"
removed=0
d="$DEST/commands"
if [ -d "$d" ]; then
  for lnk in "$d"/*; do
    [ -L "$lnk" ] || continue
    tgt="$(cd "$d" && cd "$(dirname "$(readlink "$lnk")")" 2>/dev/null && pwd -P || true)/$(basename "$(readlink "$lnk")")"
    case "$tgt" in "$REPO"/*) rm "$lnk"; removed=$((removed+1)) ;; *) : ;; esac  # only ours
  done
  rmdir "$d" 2>/dev/null || true
fi
echo "Done: $removed removed."
