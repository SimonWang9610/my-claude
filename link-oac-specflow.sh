#!/usr/bin/env bash
#
# link-oac-specflow.sh — INNER LAYER: expose the oac-specflow bundle through the
# repo's top-level commands/ skills/ rules/ agents/ dirs as relative symlinks.
#
# Relationship to install.sh (OUTER LAYER):
#   install.sh wires ~/.claude/{commands,skills,rules,agents} → $REPO/{commands,skills,rules,agents}
#   This script wires $REPO/{commands,skills,rules,agents}/<entry> → ../oac-specflow/<dir>/<entry>
#   Run together they form a two-hop chain: ~/.claude/<dir>/<entry> resolves into the bundle.
#
# Idempotent and re-runnable. Prunes stale bundle symlinks, never clobbers real files.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for d in commands skills rules agents; do
  src_dir="$REPO/oac-specflow/$d"
  dst_dir="$REPO/$d"

  if [ ! -d "$src_dir" ]; then
    echo "  skip    $d  (no oac-specflow/$d)"
    continue
  fi

  mkdir -p "$dst_dir"

  # --- Prune stale bundle links ---
  # Remove symlinks whose target starts with ../oac-specflow/$d/ but no longer resolves.
  for link in "$dst_dir"/*; do
    # Guard against empty glob
    [ -e "$link" ] || [ -L "$link" ] || continue

    if [ -L "$link" ]; then
      target="$(readlink "$link")"
      prefix="../oac-specflow/$d/"
      # Only touch links that point into this bundle dir
      case "$target" in
        "$prefix"*)
          if [ ! -e "$link" ]; then
            rm "$link"
            echo "  prune   $d/$(basename "$link")  (stale → $target)"
          fi
          ;;
      esac
    fi
  done

  # --- Link every bundle entry ---
  for src_entry in "$src_dir"/*; do
    # Guard against empty glob
    [ -e "$src_entry" ] || continue

    name="$(basename "$src_entry")"
    rel="../oac-specflow/$d/$name"
    link="$dst_dir/$name"

    if [ -L "$link" ]; then
      current="$(readlink "$link")"
      if [ "$current" = "$rel" ]; then
        echo "  ok      $d/$name"
        continue
      else
        # Wrong target — replace it
        rm "$link"
        ln -s "$rel" "$link"
        echo "  link    $d/$name  (updated → $rel)"
      fi
    elif [ -e "$link" ]; then
      echo "  WARN    $d/$name  is a real file/dir — skipping (will not clobber)" >&2
    else
      ln -s "$rel" "$link"
      echo "  link    $d/$name  → $rel"
    fi
  done
done

echo "Done. oac-specflow bundle linked into repo dirs."
