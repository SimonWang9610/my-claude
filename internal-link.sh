#!/usr/bin/env bash
#
# internal-link.sh — populate THIS repo's aggregation dirs (agents/ commands/ rules/ skills/)
# with relative symlinks to the stack sources (flutter/ react/ sflow/).
#
#     ./internal-link.sh all               # aggregate every stack (also repairs after damage)
#     ./internal-link.sh flutter react
#     ./internal-link.sh                   # interactive
#
# Operates entirely within this repo — no external .claude is touched (that's link.sh).
# Rules are prefixed by stack (react-/flutter-) because both profiles use the same basenames.
# Real files in the aggregation dirs (shared rules, standalone skills) are never touched.
# Idempotent: correct links are skipped, stale links into this repo are re-pointed.
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

usage() { echo "usage: internal-link.sh [flutter|react|sflow|all ...]"; }

SEL=""
while [ $# -gt 0 ]; do
  case "$1" in
    flutter|react|sflow|all) SEL="$SEL $1" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
  shift
done

if [ -z "${SEL# }" ]; then
  printf "Stacks to aggregate [flutter react sflow all]: "
  read_line
  SEL=" $(printf '%s' "$REPLY_LINE" | tr 'A-Z,' 'a-z ')"
fi
case " $SEL " in *" all "*) SEL=" $STACKS " ;; esac
[ -n "${SEL# }" ] || { echo "Nothing selected."; exit 0; }

linked=0 skipped=0
for stack in ${SEL# }; do
  for t in $TYPES; do
    src_dir="$REPO/$stack/$t"
    [ -d "$src_dir" ] || continue
    mkdir -p "$REPO/$t"
    prefix=""
    [ "$t" = "rules" ] && prefix="$stack-"   # rules basenames collide across stacks
    for src in "$src_dir"/*; do
      [ -e "$src" ] || continue
      name="$(basename "$src")"
      dst="$REPO/$t/${prefix}${name}"
      rel="../$stack/$t/$name"
      if [ -L "$dst" ]; then
        [ "$(readlink "$dst")" = "$rel" ] && { skipped=$((skipped+1)); continue; }
        rm "$dst"
      elif [ -e "$dst" ]; then
        echo "  WARN $t/${prefix}${name} is a real file — left as-is"; continue
      fi
      ln -s "$rel" "$dst"; linked=$((linked+1))
    done
  done
  echo "→ $stack aggregated"
done
echo "Done: $linked linked, $skipped already linked."
