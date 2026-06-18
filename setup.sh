#!/usr/bin/env bash
#
# setup.sh — LAYER 2: link (or remove) the my-claude aggregation dirs into a target .claude/.
#
# Links each selected type (agents, commands, skills) as ONE relative DIRECTORY symlink:
#   <dest>/.claude/<type>  →  this repo's <type>/
# The per-file relative symlinks inside those dirs are owned by install.sh (Layer 1).
# (Rules are consumed via CLAUDE.md @-imports, not ~/.claude, so they are not linked here.)
# Linking `agents` also installs a shell command per driver agent — a function named after the
# agent that runs `claude --agent <name> --worktree` — into your shell rc (~/.zshrc or ~/.bashrc).
# `setup.sh remove` deletes them.
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

# dir_is_safe_to_replace <dir> — true if <dir> is empty OR every entry is a symlink resolving under $REPO/
#   (i.e. the legacy per-file bundle layout, or an empty dir — safe to delete and replace with a dir symlink)
dir_is_safe_to_replace() {
  local d="$1" e
  [ -d "$d" ] || return 1
  for e in "$d"/* "$d"/.[!.]*; do
    [ -e "$e" ] || [ -L "$e" ] || continue
    [ -L "$e" ] || return 1
    case "$(resolve "$e")" in "$REPO/"*) ;; *) return 1 ;; esac
  done
  return 0
}

# link_type <type> — symlink $CLAUDE/<type> → $REPO/<type> as one relative directory symlink
link_type() {
  local ltype="$1" src="$REPO/$1" dst="$CLAUDE/$1" rel
  if [ ! -d "$src" ]; then echo "    (nothing at $src — skipped)"; return; fi
  mkdir -p "$CLAUDE"
  rel="$(relpath "$CLAUDE" "$src")"
  if [ -L "$dst" ]; then
    if [ "$(readlink "$dst")" = "$rel" ]; then echo "    already linked"; return; fi
    case "$(resolve "$dst")" in
      "$REPO/"*) rm "$dst"; ln -s "$rel" "$dst"; echo "    re-linked" ;;
      *)         echo "    WARN  $dst is a foreign symlink — left as-is" ;;
    esac
  elif [ -e "$dst" ]; then
    if dir_is_safe_to_replace "$dst"; then
      rm -rf "$dst"; ln -s "$rel" "$dst"; echo "    linked (migrated legacy per-file links)"
    else
      echo "    WARN  $dst already exists with your own content — left as-is (move it, then re-run)"
    fi
  else
    ln -s "$rel" "$dst"; echo "    linked"
  fi
}

# remove_type <type> — remove $CLAUDE/<type> if it links into this repo (or is a legacy bundle dir)
remove_type() {
  local ltype="$1" dst="$CLAUDE/$1" e removed=0
  if [ -L "$dst" ]; then
    case "$(resolve "$dst")" in
      "$REPO/"*) rm "$dst"; echo "    unlinked" ;;
      *)         echo "    WARN  $dst is a foreign symlink — left as-is" ;;
    esac
  elif [ -d "$dst" ]; then
    if dir_is_safe_to_replace "$dst"; then
      rm -rf "$dst"; echo "    unlinked (legacy per-file dir removed)"
    else
      for e in "$dst"/*; do
        [ -L "$e" ] || continue
        case "$(resolve "$e")" in "$REPO/"*) rm -f "$e"; removed=$((removed + 1)) ;; esac
      done
      rmdir "$dst" 2>/dev/null && echo "    unlinked" || echo "    removed $removed bundle link(s), kept your own files"
    fi
  else
    echo "    nothing linked"
  fi
}

# rc_file — the shell rc to manage, chosen from $SHELL (defaults to ~/.zshrc)
rc_file() {
  case "$(basename "${SHELL:-zsh}")" in
    bash) echo "$HOME/.bashrc" ;;
    *)    echo "$HOME/.zshrc" ;;
  esac
}

ALIAS_BEGIN="# >>> my-claude workflow commands >>>"
ALIAS_END="# <<< my-claude workflow commands <<<"

# manage_aliases <add|remove> — write/remove one shell command per driver agent in the rc.
#   Each command is a function named after the agent that launches it in an auto-named git
#   worktree: `<agent>() { claude --agent <agent> "$@" --worktree; }`. The block is delimited by
#   ALIAS_BEGIN/ALIAS_END markers so it is idempotent (regenerated on add) and cleanly removable.
manage_aliases() {
  local mode="$1" rc tmp f name
  rc="$(rc_file)"
  touch "$rc"
  # Strip any existing managed block, then trim trailing blank lines, so re-runs are byte-idempotent.
  tmp="$(mktemp)"
  awk -v b="$ALIAS_BEGIN" -v e="$ALIAS_END" '
    $0==b {skip=1}
    skip==0 {print}
    $0==e {skip=0}
  ' "$rc" | awk '{ a[NR]=$0 } END { last=NR; while (last>0 && a[last] ~ /^[[:space:]]*$/) last--; for (i=1;i<=last;i++) print a[i] }' > "$tmp"
  mv "$tmp" "$rc"
  if [ "$mode" = "remove" ]; then
    echo "    workflow commands removed from $rc"
    return
  fi
  # Rebuild the block from the agents currently in this repo.
  {
    echo ""
    echo "$ALIAS_BEGIN"
    echo "# Auto-generated by my-claude setup.sh — one command per workflow driver agent."
    echo "# Each launches the agent in an auto-named git worktree. 'setup.sh remove' deletes this block."
    for f in "$REPO"/agents/*.md; do
      [ -e "$f" ] || continue
      name="$(basename "$f" .md)"
      printf '%s() { claude --agent %s "$@" --worktree; }\n' "$name" "$name"
    done
    echo "$ALIAS_END"
  } >> "$rc"
  echo "    workflow commands written to $rc — run 'source $rc' or open a new shell"
}

# count_linked <claude_dir> — count linked types (dir symlink into $REPO, or a legacy bundle dir)
count_linked() {
  local claude="$1" t dst e total=0
  for t in $LINK_TYPES; do
    dst="$claude/$t"
    if [ -L "$dst" ]; then
      case "$(resolve "$dst")" in "$REPO/"*) total=$((total + 1)) ;; esac
    elif [ -d "$dst" ]; then
      for e in "$dst"/*; do
        [ -L "$e" ] || continue
        case "$(resolve "$e")" in "$REPO/"*) total=$((total + 1)); break ;; esac
      done
    fi
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
  if sel 1 agents;   then echo "→ agents:   linking $CLAUDE/agents → $REPO/agents";       link_type agents;   manage_aliases add;    did=1; else echo "· agents: not selected — skipped"; fi
  if sel 2 commands; then echo "→ commands: linking $CLAUDE/commands → $REPO/commands";   link_type commands; did=1; else echo "· commands: not selected — skipped"; fi
  if sel 3 skills;   then echo "→ skills:   linking $CLAUDE/skills → $REPO/skills";       link_type skills;   did=1; else echo "· skills: not selected — skipped"; fi
else
  if sel 1 agents;   then echo "→ agents:   unlinking $CLAUDE/agents";   remove_type agents;   manage_aliases remove; did=1; else echo "· agents: not selected — skipped"; fi
  if sel 2 commands; then echo "→ commands: unlinking $CLAUDE/commands"; remove_type commands; did=1; else echo "· commands: not selected — skipped"; fi
  if sel 3 skills;   then echo "→ skills:   unlinking $CLAUDE/skills";   remove_type skills;   did=1; else echo "· skills: not selected — skipped"; fi
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
