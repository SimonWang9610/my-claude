#!/usr/bin/env bash
#
# unlink.sh — remove the symlinks link.sh created in a project's .claude/ or ~/.claude/.
#
#     ./unlink.sh --global
#     ./unlink.sh --project ../myapp
#     ./unlink.sh                            # interactive
#     ./unlink.sh --global --aliases         # also drop the managed shell-function block
#
# Removes skills/ agents/ rules/ links (the sflow workflow is the skills/sflow/ skill, removed
# with them). Only symlinks that resolve back into THIS repo are removed; anything else is left
# untouched. Empty type dirs are pruned. Re-running is safe. See link.sh.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
TYPES="skills agents rules"
REPLY_LINE=""

read_line() {
  local a=""
  if ! { IFS= read -r a </dev/tty; } 2>/dev/null; then IFS= read -r a || true; fi
  REPLY_LINE="$a"
}

usage() { echo "usage: unlink.sh [--global | --project <dir>] [--aliases]"; }

DEST=""
DROP_ALIASES=""
while [ $# -gt 0 ]; do
  case "$1" in
    --global)  DEST="$HOME/.claude" ;;
    --project) shift; [ $# -gt 0 ] || { usage; exit 2; }
               DEST="$(cd "$1" && pwd -P)/.claude" ;;
    --aliases) DROP_ALIASES=yes ;;
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

echo "Unlinking bundle from $DEST"
removed=0
for t in $TYPES; do
  d="$DEST/$t"
  [ -d "$d" ] || continue
  for lnk in "$d"/*; do
    [ -L "$lnk" ] || continue
    tgt="$(cd "$d" && cd "$(dirname "$(readlink "$lnk")")" 2>/dev/null && pwd -P || true)/$(basename "$(readlink "$lnk")")"
    case "$tgt" in "$REPO"/*) rm "$lnk"; removed=$((removed+1)) ;; *) : ;; esac  # only ours
  done
  rmdir "$d" 2>/dev/null || true
done
echo "Done: $removed removed."

# optionally drop the managed shell-function block
if [ "$DROP_ALIASES" = yes ]; then
  for RC in "${ZDOTDIR:-$HOME}/.zshrc" "$HOME/.bashrc"; do
    [ -f "$RC" ] && grep -q "^# >>> my-claude workflow agents >>>" "$RC" || continue
    tmp="$(mktemp)"
    sed "/^# >>> my-claude workflow agents >>>/,/^# <<< my-claude workflow agents <<</d" "$RC" > "$tmp"
    mv "$tmp" "$RC"; echo "Removed shell functions from $RC."
  done
fi
