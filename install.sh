#!/usr/bin/env bash
#
# install.sh — LAYER 1: relative-symlink each stack's assets into the my-claude aggregation dirs.
#
# For a selected stack+type, symlinks every entry of $REPO/<stack>/<type>/* into $REPO/<type>/.
# Operates entirely within this repo — no external target is touched.
#
#     ./install.sh                   # interactive multi-select of stacks
#     ./install.sh flutter           # all existing types under flutter
#     ./install.sh react agents      # just that stack+type
#     ./install.sh specflow commands
#     ./install.sh all               # every stack+type
#
# Symlinks are RELATIVE. Already-linked entries are skipped. Real files are never clobbered.
# See setup.sh to link the aggregated dirs into ~/.claude or a project. See uninstall.sh to remove.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPLY_LINE=""

STACKS="flutter react specflow"
TYPES="agents commands skills rules"

# --- helpers ---------------------------------------------------------------

# relpath <from-dir> <to-path> — print <to-path> as a path relative to <from-dir>
relpath() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import os,sys; print(os.path.relpath(sys.argv[2], sys.argv[1]))' "$1" "$2"
  else
    perl -MFile::Spec -e 'print File::Spec->abs2rel($ARGV[1], $ARGV[0])' "$1" "$2"
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

# link_group <label> <src_dir> <dst_dir> [name_prefix] — relative-symlink each entry of src_dir
# into dst_dir, naming each link <name_prefix><basename> (name_prefix defaults to empty)
link_group() {
  local label="$1" src_dir="$2" dst_dir="$3" name_prefix="${4:-}"
  if [ ! -d "$src_dir" ]; then echo "    (nothing at $src_dir — skipped)"; return; fi
  mkdir -p "$dst_dir"
  local linked=0 skipped=0 src name dst rel
  for src in "$src_dir"/*; do
    [ -e "$src" ] || [ -L "$src" ] || continue
    name="$(basename "$src")"
    dst="$dst_dir/${name_prefix}${name}"
    rel="$(relpath "$dst_dir" "$src")"
    if [ -L "$dst" ]; then
      if [ "$(readlink "$dst")" = "$rel" ]; then skipped=$((skipped + 1)); continue; fi
      rm "$dst"; ln -s "$rel" "$dst"; linked=$((linked + 1))
    elif [ -e "$dst" ]; then
      echo "    WARN  ${name_prefix}${name} is a real file in $dst_dir — left as-is"
    else
      ln -s "$rel" "$dst"; linked=$((linked + 1))
    fi
  done
  echo "    $linked linked, $skipped already-linked"
}

# stack_types <stack> — print which type dirs exist under a stack (space-separated)
stack_types() {
  local stack="$1" t types=""
  for t in $TYPES; do
    [ -d "$REPO/$stack/$t" ] && types="$types $t"
  done
  printf '%s' "${types# }"
}

# validate_args — exit 2 with usage if positional args are unrecognised
validate_args() {
  local stack="${1:-}" type="${2:-}"
  if [ -n "$stack" ] && [ "$stack" != "all" ]; then
    case " $STACKS " in *" $stack "*) ;; *) echo "Unknown stack: $stack"; usage; exit 2 ;; esac
  fi
  if [ -n "$type" ]; then
    case " $TYPES " in *" $type "*) ;; *) echo "Unknown type: $type"; usage; exit 2 ;; esac
  fi
}

usage() {
  echo "usage: install.sh [stack] [type]"
  echo "  stacks: $STACKS  all"
  echo "  types:  $TYPES"
}

# --- run_stack <stack> [type] — link one stack (all types or just the given one)
run_stack() {
  local stack="$1" only="${2:-}"
  local t types
  types="$(stack_types "$stack")"
  if [ -z "$types" ]; then echo "  (no type dirs found under $stack — skipped)"; return; fi
  local prefix
  for t in $types; do
    if [ -n "$only" ] && [ "$t" != "$only" ]; then continue; fi
    # rules from different stacks share basenames, so namespace them by stack to avoid collisions
    if [ "$t" = "rules" ]; then prefix="$stack-"; else prefix=""; fi
    echo "→ $stack/$t: linking into $REPO/$t/"
    link_group "$stack/$t" "$REPO/$stack/$t" "$REPO/$t" "$prefix"
  done
}

# --- arg dispatch ----------------------------------------------------------

arg_stack="${1:-}"
arg_type="${2:-}"

if [ -n "$arg_stack" ]; then
  validate_args "$arg_stack" "$arg_type"
  echo "Linking from stacks into aggregation dirs (within $REPO)"
  echo "  relative symlinks · already-linked skipped · real files never clobbered"
  echo
  if [ "$arg_stack" = "all" ]; then
    for s in $STACKS; do run_stack "$s" "$arg_type"; done
  else
    run_stack "$arg_stack" "$arg_type"
  fi
  echo
  echo "Done."
  exit 0
fi

# --- interactive multi-select menu ----------------------------------------

n_fl="$(stack_types flutter)"
n_re="$(stack_types react)"
n_sp="$(stack_types specflow)"

echo "Link stack assets into aggregation dirs in:  $REPO"
echo "  relative symlinks · already-linked skipped · real files never clobbered"
echo
echo "Stacks — pick any combination:"
echo "  1) flutter  ($(stack_types flutter | tr ' ' ','))"
echo "  2) react    ($(stack_types react   | tr ' ' ','))"
echo "  3) specflow ($(stack_types specflow | tr ' ' ','))"
echo "  all"
echo
printf "Select stacks to link [e.g. \"1 3\", \"all\", or empty to cancel]: "
read_line
SEL="$(printf '%s' "$REPLY_LINE" | tr 'A-Z,' 'a-z ')"

# sel <num> <name> — is this item selected?
sel() {
  case " $SEL " in *" all "*) return 0 ;; esac
  local t
  for t in $SEL; do [ "$t" = "$1" ] && return 0; [ "$t" = "$2" ] && return 0; done
  return 1
}

did=0
echo
if sel 1 flutter;  then run_stack flutter;  did=1; else echo "· flutter: not selected — skipped"; fi
if sel 2 react;    then run_stack react;    did=1; else echo "· react: not selected — skipped"; fi
if sel 3 specflow; then run_stack specflow; did=1; else echo "· specflow: not selected — skipped"; fi

echo
if [ "$did" = 1 ]; then
  echo "Done. Run setup.sh to link the aggregated dirs into ~/.claude or a project. Run uninstall.sh to remove."
else
  echo "Nothing selected — nothing changed."
fi
