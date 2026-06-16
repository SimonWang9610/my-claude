#!/usr/bin/env bash
#
# uninstall.sh — LAYER 1 teardown: remove from aggregation dirs the symlinks that resolve into a
# given stack's source dir.
#
# Mirror of install.sh. Scoped by stack (and optionally type). Never touches real files, dirs, or
# symlinks that resolve outside the named stack.
#
#     ./uninstall.sh                   # interactive multi-select of stacks
#     ./uninstall.sh flutter           # all types aggregated from flutter
#     ./uninstall.sh react agents      # just that stack+type
#     ./uninstall.sh specflow commands
#     ./uninstall.sh all               # every stack+type
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPLY_LINE=""

STACKS="flutter react specflow"
TYPES="agents commands skills rules"

# --- helpers ---------------------------------------------------------------

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

# count_stack <dir> <stack_prefix> — how many symlinks in <dir> resolve under $REPO/<stack_prefix>/
count_stack() {
  local dir="$1" prefix="$2" c=0 e
  [ -d "$dir" ] || { echo 0; return; }
  for e in "$dir"/*; do
    [ -L "$e" ] || continue
    case "$(resolve "$e")" in "$REPO/$prefix/"*) c=$((c + 1)) ;; esac
  done
  echo "$c"
}

# remove_stack <label> <dir> <stack_prefix> — remove symlinks in <dir> that resolve under <stack_prefix>
remove_stack() {
  local label="$1" dir="$2" prefix="$3" e removed=0
  [ -d "$dir" ] || { echo "    (no $dir — skipped)"; return; }
  for e in "$dir"/*; do
    [ -L "$e" ] || continue
    case "$(resolve "$e")" in
      "$REPO/$prefix/"*) rm -f "$e"; echo "    removed $(basename "$e")"; removed=$((removed + 1)) ;;
    esac
  done
  echo "    $removed removed"
}

# stack_types <stack> — print which type dirs exist under a stack (space-separated)
stack_types() {
  local stack="$1" t types=""
  for t in $TYPES; do
    [ -d "$REPO/$stack/$t" ] && types="$types $t"
  done
  printf '%s' "${types# }"
}

# count_stack_all <stack> — total bundle symlinks across all type dirs for this stack
count_stack_all() {
  local stack="$1" t total=0 n
  for t in $TYPES; do
    n="$(count_stack "$REPO/$t" "$stack")"
    total=$((total + n))
  done
  echo "$total"
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
  echo "usage: uninstall.sh [stack] [type]"
  echo "  stacks: $STACKS  all"
  echo "  types:  $TYPES"
}

# --- run_stack_uninstall <stack> [type] — remove for one stack
run_stack_uninstall() {
  local stack="$1" only="${2:-}" t types
  types="$(stack_types "$stack")"
  if [ -z "$types" ]; then echo "  (no type dirs found under $stack — skipped)"; return; fi
  for t in $types; do
    if [ -n "$only" ] && [ "$t" != "$only" ]; then continue; fi
    n="$(count_stack "$REPO/$t" "$stack")"
    echo "→ $stack/$t: removing $n bundle symlink(s) from $REPO/$t/"
    remove_stack "$stack/$t" "$REPO/$t" "$stack"
  done
}

# --- arg dispatch ----------------------------------------------------------

arg_stack="${1:-}"
arg_type="${2:-}"

if [ -n "$arg_stack" ]; then
  validate_args "$arg_stack" "$arg_type"
  echo "Removing stack symlinks from aggregation dirs in:  $REPO"
  echo "  only bundle symlinks removed · real files never touched"
  echo
  if [ "$arg_stack" = "all" ]; then
    for s in $STACKS; do run_stack_uninstall "$s" "$arg_type"; done
  else
    run_stack_uninstall "$arg_stack" "$arg_type"
  fi
  echo
  echo "Done."
  exit 0
fi

# --- interactive multi-select menu ----------------------------------------

n_fl="$(count_stack_all flutter)"
n_re="$(count_stack_all react)"
n_sp="$(count_stack_all specflow)"

echo "Remove stack symlinks from aggregation dirs in:  $REPO"
echo "  only bundle symlinks removed · real files and unrelated symlinks never touched"
echo
echo "Stacks — pick any combination:"
echo "  1) flutter   ($n_fl bundle symlink(s) currently in aggregation dirs)"
echo "  2) react     ($n_re bundle symlink(s) currently in aggregation dirs)"
echo "  3) specflow  ($n_sp bundle symlink(s) currently in aggregation dirs)"
echo "  all"
echo
printf "Select stacks to clean [e.g. \"1 2\", \"all\", or empty to cancel]: "
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
if sel 1 flutter;  then run_stack_uninstall flutter;  did=1; else echo "· flutter: not selected — skipped"; fi
if sel 2 react;    then run_stack_uninstall react;    did=1; else echo "· react: not selected — skipped"; fi
if sel 3 specflow; then run_stack_uninstall specflow; did=1; else echo "· specflow: not selected — skipped"; fi

echo
if [ "$did" = 1 ]; then echo "Done."; else echo "Nothing selected — nothing changed."; fi
