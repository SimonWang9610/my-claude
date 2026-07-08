#!/usr/bin/env bash
#
# internal-unlink.sh — remove a stack's symlinks from THIS repo's aggregation dirs
# (agents/ commands/ rules/ skills/). The inverse of internal-link.sh.
#
#     ./internal-unlink.sh flutter
#     ./internal-unlink.sh all
#
# Only symlinks that resolve into the named stack are removed; real files (shared rules,
# standalone skills) are never touched. External .claude dirs are unaffected (see unlink.sh).
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

usage() { echo "usage: internal-unlink.sh [flutter|react|sflow|all ...]"; }

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
  printf "Stacks to remove from the aggregation dirs [flutter react sflow all]: "
  read_line
  SEL=" $(printf '%s' "$REPLY_LINE" | tr 'A-Z,' 'a-z ')"
fi
case " $SEL " in *" all "*) SEL=" $STACKS " ;; esac
[ -n "${SEL# }" ] || { echo "Nothing selected."; exit 0; }

removed=0
for t in $TYPES; do
  d="$REPO/$t"
  [ -d "$d" ] || continue
  for lnk in "$d"/*; do
    [ -L "$lnk" ] || continue
    tgt="$(readlink "$lnk")"
    for stack in ${SEL# }; do
      case "$tgt" in
        ../"$stack"/*) rm "$lnk"; removed=$((removed+1)); break ;;
      esac
    done
  done
done
echo "Done: $removed removed."
