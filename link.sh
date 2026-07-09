#!/usr/bin/env bash
#
# link.sh — link this bundle's assets into a project's .claude/ or the global ~/.claude/.
#
# The root dirs (agents/ commands/ rules/ skills/) are committed aggregation views:
# per-asset relative symlinks into the stack sources (flutter/ react/ sflow/) plus real shared
# files (the agents/ driver agents, rules/engineering-discipline.md, the *-react-workflow
# generator skills and other standalone skills). This script links
# a per-stack selection of those entries into the destination .claude/.
#
#     ./link.sh --global all                 # link everything into ~/.claude
#     ./link.sh --project ../myapp sflow react
#     ./link.sh --project ../myapp flutter   # flutter profile (sflow is added automatically —
#                                            #   the drivers need the /sf-* commands)
#     ./link.sh                              # interactive
#     ./link.sh --global all --aliases       # also write shell functions for the driver agents
#
# Shared root assets (real files: driver agents, cross-stack rules, standalone skills) are
# linked with any selection. This repo ships no workflow templates — the *-react-workflow
# generator skills resolve the PROJECT's vendored specflow templates (specflow/src/workflows/, with
# .specflow/workflows/ as override). Symlinks are RELATIVE; existing
# correct links are skipped; a foreign real file at a destination path is never clobbered (warned
# and left as-is). After linking, offers to write a shell function per linked driver agent
# (managed rc block). Re-running is safe. See unlink.sh.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
STACKS="flutter react sflow"
TYPES="agents commands rules skills"
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

# entry_stack <repo-entry-path> — print flutter|react|sflow|shared for a root aggregation entry
entry_stack() {
  local e="$1" tgt
  if [ -L "$e" ]; then
    tgt="$(readlink "$e")"
    case "$tgt" in
      ../flutter/*|*/flutter/*) echo flutter ;;
      ../react/*|*/react/*)     echo react ;;
      ../sflow/*|*/sflow/*)     echo sflow ;;
      *)                        echo shared ;;
    esac
  else
    echo shared
  fi
}

usage() {
  echo "usage: link.sh [--global | --project <dir>] [flutter|react|sflow|all ...] [--aliases|--no-aliases]"
  echo "  links the root agents/commands/rules/skills entries of the selected stacks"
  echo "  (plus the shared root assets) into <dest>/.claude/<type>/; optionally writes a"
  echo "  shell function per linked driver agent"
}

# --- parse args --------------------------------------------------------------
DEST=""
SEL=""
ALIASES=""
while [ $# -gt 0 ]; do
  case "$1" in
    --global)  DEST="$HOME/.claude" ;;
    --project) shift; [ $# -gt 0 ] || { usage; exit 2; }
               DEST="$(cd "$1" && pwd -P)/.claude" ;;
    flutter|react|sflow|all) SEL="$SEL $1" ;;
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

if [ -z "${SEL# }" ]; then
  printf "Stacks to link [flutter react sflow all — e.g. \"react sflow\"]: "
  read_line
  SEL=" $(printf '%s' "$REPLY_LINE" | tr 'A-Z,' 'a-z ')"
fi

case " $SEL " in *" all "*) SEL=" $STACKS " ;; esac
# a profile without sflow can't run: the drivers invoke the /sf-* commands
case " $SEL " in
  *" flutter "*|*" react "*) case " $SEL " in *" sflow "*) ;; *) SEL="$SEL sflow"; echo "note: sflow added — the profile drivers need it" ;; esac ;;
esac
[ -n "${SEL# }" ] || { echo "Nothing selected."; exit 0; }

selected() { case " $SEL " in *" $1 "*) return 0 ;; esac; [ "$1" = shared ]; }

# --- link --------------------------------------------------------------------
echo "Linking [${SEL# }] into $DEST (relative symlinks)"
total=0 skipped=0
for t in $TYPES; do
  src_dir="$REPO/$t"
  [ -d "$src_dir" ] || continue
  # legacy layout guard: if $DEST/$t is itself a symlink, per-file links would resolve THROUGH
  # it and clobber this repo's own aggregation dirs. Migrate (ours) or skip (foreign).
  if [ -L "$DEST/$t" ]; then
    case "$(cd "$DEST" && cd "$(readlink "$DEST/$t")" 2>/dev/null && pwd -P || echo /nonexistent)" in
      "$REPO"*) rm "$DEST/$t"; echo "  migrated legacy dir symlink $t/ → per-file links" ;;
      *) echo "  WARN $DEST/$t is a foreign symlink — skipped"; continue ;;
    esac
  fi
  linked_any=0
  for src in "$src_dir"/*; do
    [ -e "$src" ] || [ -L "$src" ] || continue
    name="$(basename "$src")"
    selected "$(entry_stack "$src")" || continue
    mkdir -p "$DEST/$t"
    dst="$DEST/$t/$name"
    rel="$(relpath "$DEST/$t" "$src")"
    if [ -L "$dst" ]; then
      [ "$(readlink "$dst")" = "$rel" ] && { skipped=$((skipped+1)); continue; }
      case "$(cd "$DEST/$t" && cd "$(dirname "$(readlink "$dst")")" 2>/dev/null && pwd -P || echo /nonexistent)" in
        "$REPO"*) rm "$dst" ;;   # stale link into this repo — replace
        *) echo "  WARN $t/$name links elsewhere — left as-is"; continue ;;
      esac
    elif [ -e "$dst" ]; then
      echo "  WARN $t/$name is a real file in $DEST/$t — left as-is"; continue
    fi
    ln -s "$rel" "$dst"; total=$((total+1)); linked_any=1
  done
  [ "$linked_any" = 1 ] && echo "  → $t/"
done
echo "Done: $total linked, $skipped already linked. Run unlink.sh to remove."

# --- optional shell functions for the linked driver agents ---------------------
rc_file() {
  case "${SHELL:-}" in
    */zsh)  echo "${ZDOTDIR:-$HOME}/.zshrc" ;;
    *)      echo "$HOME/.bashrc" ;;
  esac
}

agents_linked=""
if [ -d "$DEST/agents" ]; then
  # unified drivers are *-driver.md; keep *-workflow.md so stale per-stack installs still round-trip
  for a in "$DEST/agents"/*-driver.md "$DEST/agents"/*-workflow.md; do
    [ -e "$a" ] || continue
    agents_linked="$agents_linked $(basename "$a" .md)"
  done
fi

if [ -n "${agents_linked# }" ]; then
  if [ -z "$ALIASES" ]; then
    printf "Write a shell function per driver agent (%s) into %s? [y/N]: " "$(echo ${agents_linked# } | wc -w | tr -d ' ') agents" "$(rc_file)"
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
      echo "# managed by my-claude/link.sh — run unlink.sh (all) or delete this block to remove"
      for name in $agents_linked; do
        printf '%s() { claude --agent %s "$@" --worktree; }\n' "$name" "$name"
      done
      echo "$END"
    } >> "$tmp"
    mv "$tmp" "$RC"
    echo "Shell functions written to $RC (open a new shell or 'source' it)."
  fi
fi
