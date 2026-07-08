#!/usr/bin/env bash
#
# unlink.sh — remove the symlinks link.sh created in a project's .claude/ or ~/.claude/.
#
#     ./unlink.sh --global all
#     ./unlink.sh --project ../myapp flutter
#     ./unlink.sh                            # interactive
#
# Only symlinks that resolve back into THIS repo are ever removed; anything else is left
# untouched. Shared root assets (cross-stack rules, standalone skills) are removed only with
# "all" — a single-stack unlink leaves them for the remaining stack. Empty type dirs are pruned.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
STACKS="flutter react sflow"
TYPES="agents commands rules skills"
REPLY_LINE=""

read_line() {
  local a=""
  if ! { IFS= read -r a </dev/tty; } 2>/dev/null; then IFS= read -r a || true; fi
  REPLY_LINE="$a"
}

# stack_of <resolved-abs-target> — flutter|react|sflow|shared for a path inside this repo.
# Destination links usually point at a root aggregation entry ($REPO/<type>/<name>), which is
# itself a symlink into the stack source — classify by that second hop.
stack_of() {
  local p="$1"
  case "$p" in
    "$REPO"/flutter/*) echo flutter; return ;;
    "$REPO"/react/*)   echo react; return ;;
    "$REPO"/sflow/*)   echo sflow; return ;;
  esac
  if [ -L "$p" ]; then
    case "$(readlink "$p")" in
      ../flutter/*|*/flutter/*) echo flutter; return ;;
      ../react/*|*/react/*)     echo react; return ;;
      ../sflow/*|*/sflow/*)     echo sflow; return ;;
    esac
  fi
  echo shared
}

usage() {
  echo "usage: unlink.sh [--global | --project <dir>] [flutter|react|sflow|all ...]"
}

DEST=""
SEL=""
while [ $# -gt 0 ]; do
  case "$1" in
    --global)  DEST="$HOME/.claude" ;;
    --project) shift; [ $# -gt 0 ] || { usage; exit 2; }
               DEST="$(cd "$1" && pwd -P)/.claude" ;;
    flutter|react|sflow|all) SEL="$SEL $1" ;;
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

if [ -z "${SEL# }" ]; then
  printf "Stacks to unlink [flutter react sflow all]: "
  read_line
  SEL=" $(printf '%s' "$REPLY_LINE" | tr 'A-Z,' 'a-z ')"
fi

ALL=0
case " $SEL " in *" all "*) SEL=" $STACKS "; ALL=1 ;; esac
[ -n "${SEL# }" ] || { echo "Nothing selected."; exit 0; }

selected() {
  case " $SEL " in *" $1 "*) return 0 ;; esac
  [ "$1" = shared ] && [ "$ALL" = 1 ]
}

echo "Unlinking [${SEL# }] from $DEST"
removed=0
for t in $TYPES; do
  d="$DEST/$t"
  # legacy layout guard: never iterate THROUGH a dir symlink (that would delete this repo's
  # own aggregation entries). If it's ours, removing the dir symlink is the unlink.
  if [ -L "$d" ]; then
    case "$(cd "$DEST" && cd "$(readlink "$d")" 2>/dev/null && pwd -P || echo /nonexistent)" in
      "$REPO"*) if [ "$ALL" = 1 ]; then rm "$d"; removed=$((removed+1)); echo "  removed legacy dir symlink $t/"
                else echo "  NOTE $t/ is a legacy whole-dir symlink — run 'unlink.sh ... all' (or link.sh, which migrates it) for per-stack control"; fi ;;
      *) : ;;   # foreign — leave it
    esac
    continue
  fi
  [ -d "$d" ] || continue
  for lnk in "$d"/*; do
    [ -L "$lnk" ] || continue
    tgt="$(cd "$d" && cd "$(dirname "$(readlink "$lnk")")" 2>/dev/null && pwd -P || true)/$(basename "$(readlink "$lnk")")"
    case "$tgt" in "$REPO"/*) ;; *) continue ;; esac   # not ours — leave it
    selected "$(stack_of "$tgt")" || continue
    rm "$lnk"; removed=$((removed+1))
  done
  rmdir "$d" 2>/dev/null || true
done
echo "Done: $removed removed."

# with `all`, also offer to drop the managed shell-function block
if [ "$ALL" = 1 ]; then
  for RC in "${ZDOTDIR:-$HOME}/.zshrc" "$HOME/.bashrc"; do
    [ -f "$RC" ] && grep -q "^# >>> my-claude workflow agents >>>" "$RC" || continue
    printf "Remove the my-claude workflow-agent shell functions from %s? [y/N]: " "$RC"
    read_line
    case "$REPLY_LINE" in
      y|Y|yes) tmp="$(mktemp)"
               sed "/^# >>> my-claude workflow agents >>>/,/^# <<< my-claude workflow agents <<</d" "$RC" > "$tmp"
               mv "$tmp" "$RC"; echo "Removed from $RC." ;;
    esac
  done
fi
