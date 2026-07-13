#!/usr/bin/env bash
#
# link.sh — link this bundle's assets into a project's .claude/ or the global ~/.claude/.
#
# The bundle is flat: skills/ agents/ rules/ are real directories. This script per-entry
# relative-symlinks them into <dest>/.claude/:
#
#     skills/*        -> <dest>/.claude/skills/
#     agents/*        -> <dest>/.claude/agents/
#     rules/*         -> <dest>/.claude/rules/
#
# The /sf-* commands (sflow/commands/) are handled SEPARATELY by link-commands.sh — globally
# they'd shadow a project's own /spec-* set, so linking them is an explicit, standalone step.
#
#     ./link.sh --global                 # into ~/.claude
#     ./link.sh --project ../myapp       # into ../myapp/.claude
#     ./link.sh                           # interactive
#     ./link.sh --global --aliases        # also write a shell function per driver agent
#
# Symlinks are RELATIVE; an existing correct link is skipped; a foreign real file (or a link
# pointing outside this repo) at a destination path is never clobbered (warned, left as-is).
# Re-running is safe. See unlink.sh.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# source dir  ->  dest type under .claude/  (commands are handled by link-commands.sh)
SRC_MAP="skills:skills agents:agents rules:rules"
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
  echo "usage: link.sh [--global | --project <dir>] [--aliases | --no-aliases]"
  echo "  per-entry symlinks skills/ agents/ rules/ into <dest>/.claude/"
  echo "  the /sf-* commands are linked separately — see link-commands.sh"
}

# --- parse args --------------------------------------------------------------
DEST=""
ALIASES=""
while [ $# -gt 0 ]; do
  case "$1" in
    --global)  DEST="$HOME/.claude" ;;
    --project) shift; [ $# -gt 0 ] || { usage; exit 2; }
               DEST="$(cd "$1" && pwd -P)/.claude" ;;
    --aliases)    ALIASES=yes ;;
    --no-aliases) ALIASES=no ;;
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
echo "Linking bundle into $DEST (relative symlinks)"
total=0 skipped=0
for pair in $SRC_MAP; do
  src_dir="$REPO/${pair%%:*}"
  t="${pair##*:}"
  [ -d "$src_dir" ] || continue
  linked_any=0
  for src in "$src_dir"/*; do
    [ -e "$src" ] || continue
    mkdir -p "$DEST/$t"
    dst="$DEST/$t/$(basename "$src")"
    rel="$(relpath "$DEST/$t" "$src")"
    if [ -L "$dst" ]; then
      [ "$(readlink "$dst")" = "$rel" ] && { skipped=$((skipped+1)); continue; }
      case "$(cd "$DEST/$t" && cd "$(dirname "$(readlink "$dst")")" 2>/dev/null && pwd -P || echo /nonexistent)" in
        "$REPO"*) rm "$dst" ;;   # stale link into this repo — replace
        *) echo "  WARN $t/$(basename "$src") links elsewhere — left as-is"; continue ;;
      esac
    elif [ -e "$dst" ]; then
      echo "  WARN $t/$(basename "$src") is a real file in $DEST — left as-is"; continue
    fi
    ln -s "$rel" "$dst"; total=$((total+1)); linked_any=1
  done
  [ "$linked_any" = 1 ] && echo "  → $t/"
done
echo "Done: $total linked, $skipped already linked. Run unlink.sh to remove."

# --- optional shell functions for the linked driver agents ---------------------
rc_file() { case "${SHELL:-}" in */zsh) echo "${ZDOTDIR:-$HOME}/.zshrc" ;; *) echo "$HOME/.bashrc" ;; esac; }

agents_linked=""
if [ -d "$DEST/agents" ]; then
  for a in "$DEST/agents"/*-driver.md; do
    [ -e "$a" ] || continue
    agents_linked="$agents_linked $(basename "$a" .md)"
  done
fi

if [ -n "${agents_linked# }" ]; then
  if [ -z "$ALIASES" ]; then
    printf "Write a shell function per driver agent into %s? [y/N]: " "$(rc_file)"
    read_line
    case "$REPLY_LINE" in y|Y|yes) ALIASES=yes ;; *) ALIASES=no ;; esac
  fi
  if [ "$ALIASES" = yes ]; then
    RC="$(rc_file)"
    BEGIN="# >>> my-claude workflow agents >>>"
    END="# <<< my-claude workflow agents <<<"
    tmp="$(mktemp)"
    [ -f "$RC" ] && sed "/^$BEGIN/,/^$END/d" "$RC" > "$tmp" || : > "$tmp"
    {
      echo "$BEGIN"
      echo "# managed by my-claude/link.sh — run unlink.sh --all or delete this block to remove"
      for name in $agents_linked; do
        printf '%s() { claude --agent %s "$@" --worktree; }\n' "$name" "$name"
      done
      echo "$END"
    } >> "$tmp"
    mv "$tmp" "$RC"
    echo "Shell functions written to $RC (open a new shell or 'source' it)."
  fi
fi
