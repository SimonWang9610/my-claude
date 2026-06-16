#!/usr/bin/env bash
#
# link-specflow.sh — INNER LAYER: expose the unified specflow bundle through the
# repo's top-level skills/ rules/ agents/ dirs as relative symlinks.
# Commands are intentionally NOT surfaced — they stay as real files in
# specflow/commands/ and are invoked by name (/spec-*), resolving to a project's
# own /spec-* commands when present.
#
# Relationship to install.sh (OUTER LAYER):
#   install.sh wires ~/.claude/{commands,skills,rules,agents} → $REPO/{commands,skills,rules,agents}
#   This script wires $REPO/{commands,skills,rules,agents}/<entry> → relative targets inside the
#   specflow/, react/, and flutter/ profile directories.
#   Run together they form a two-hop chain: ~/.claude/<dir>/<entry> resolves into the bundle.
#
# Idempotent and re-runnable. Prunes stale bundle symlinks, never clobbers real files.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Helper: link one entry
#   link_entry <dest_dir> <link_name> <rel_target>
# ---------------------------------------------------------------------------
link_entry() {
  local dest_dir="$1" name="$2" rel="$3"
  local link="$dest_dir/$name"

  if [ -L "$link" ]; then
    local current
    current="$(readlink "$link")"
    if [ "$current" = "$rel" ]; then
      echo "  ok      $(basename "$dest_dir")/$name"
      return
    else
      rm "$link"
      ln -s "$rel" "$link"
      echo "  link    $(basename "$dest_dir")/$name  (updated → $rel)"
    fi
  elif [ -e "$link" ]; then
    echo "  WARN    $(basename "$dest_dir")/$name  is a real file/dir — skipping (will not clobber)" >&2
  else
    ln -s "$rel" "$link"
    echo "  link    $(basename "$dest_dir")/$name  → $rel"
  fi
}

# ---------------------------------------------------------------------------
# Prune stale symlinks across all flat repo dirs.
# Remove symlinks whose target:
#   (a) points into a now-dead path containing "oac-specflow" or "flutter-specflow"
#   (b) points into ../specflow, ../react, or ../flutter but no longer resolves
# Conservative: only removes symlinks, never real files/dirs.
# ---------------------------------------------------------------------------
prune_stale() {
  local dir="$1"
  [ -d "$dir" ] || return

  for link in "$dir"/*; do
    [ -e "$link" ] || [ -L "$link" ] || continue
    [ -L "$link" ] || continue   # only symlinks

    local target
    target="$(readlink "$link")"

    # (a) Dead paths from old bundle locations
    case "$target" in
      *oac-specflow*|*flutter-specflow*)
        if [ ! -e "$link" ]; then
          rm "$link"
          echo "  prune   $(basename "$dir")/$(basename "$link")  (stale → $target)"
        fi
        ;;
      # (b) Links into new profile dirs that no longer resolve
      ../specflow/*|../react/*|../flutter/*)
        if [ ! -e "$link" ]; then
          rm "$link"
          echo "  prune   $(basename "$dir")/$(basename "$link")  (stale → $target)"
        fi
        ;;
    esac
  done
}

# ---------------------------------------------------------------------------
# Prune across all four flat dirs first
# ---------------------------------------------------------------------------
for flat_dir in commands skills rules agents; do
  prune_stale "$REPO/$flat_dir"
done

mkdir -p "$REPO/commands" "$REPO/skills" "$REPO/rules" "$REPO/agents"

# ---------------------------------------------------------------------------
# 1. Commands are NOT surfaced into ~/.claude.
#    All commands live as real files in specflow/commands/ (the reference set).
#    Workflow agents invoke them by name (/spec-*), which resolves to the
#    project's OWN /spec-* commands when present — avoiding conflicts. Link the
#    bundled versions manually if you want them globally. Here we only remove
#    any stale command symlinks left in commands/ by older installs.
# ---------------------------------------------------------------------------
dst_dir="$REPO/commands"
if [ -d "$dst_dir" ]; then
  for link in "$dst_dir"/*; do
    [ -L "$link" ] || continue
    case "$(readlink "$link")" in
      ../specflow/commands/*|../react/commands/*)
        rm "$link"
        echo "  unlink  commands/$(basename "$link")  (commands no longer surfaced)"
        ;;
    esac
  done
fi

# ---------------------------------------------------------------------------
# 3. react/skills/* → skills/
# ---------------------------------------------------------------------------
src_dir="$REPO/react/skills"
dst_dir="$REPO/skills"
if [ -d "$src_dir" ]; then
  for src_entry in "$src_dir"/*; do
    [ -e "$src_entry" ] || continue
    name="$(basename "$src_entry")"
    link_entry "$dst_dir" "$name" "../react/skills/$name"
  done
fi

# ---------------------------------------------------------------------------
# 4. flutter/skills/* → skills/
# ---------------------------------------------------------------------------
src_dir="$REPO/flutter/skills"
if [ -d "$src_dir" ]; then
  for src_entry in "$src_dir"/*; do
    [ -e "$src_entry" ] || continue
    name="$(basename "$src_entry")"
    link_entry "$dst_dir" "$name" "../flutter/skills/$name"
  done
fi

# ---------------------------------------------------------------------------
# 5. react/agents/* → agents/
# ---------------------------------------------------------------------------
src_dir="$REPO/react/agents"
dst_dir="$REPO/agents"
if [ -d "$src_dir" ]; then
  for src_entry in "$src_dir"/*; do
    [ -e "$src_entry" ] || continue
    name="$(basename "$src_entry")"
    link_entry "$dst_dir" "$name" "../react/agents/$name"
  done
fi

# ---------------------------------------------------------------------------
# 6. flutter/agents/* → agents/
# ---------------------------------------------------------------------------
src_dir="$REPO/flutter/agents"
if [ -d "$src_dir" ]; then
  for src_entry in "$src_dir"/*; do
    [ -e "$src_entry" ] || continue
    name="$(basename "$src_entry")"
    link_entry "$dst_dir" "$name" "../flutter/agents/$name"
  done
fi

# ---------------------------------------------------------------------------
# 7. Stack rules → rules/ (path-gated globally). architecture-principles is surfaced
#    under a stack-distinct alias per profile (react-/flutter-) so both coexist; React's
#    test-quality keeps its generic name (only React's test-quality is surfaced).
#    engineering-discipline + preferences are top-level canonical real files.
# ---------------------------------------------------------------------------
dst_dir="$REPO/rules"
[ -e "$REPO/react/rules/architecture-principles.md" ]   && link_entry "$dst_dir" "react-architecture-principles.md"   "../react/rules/architecture-principles.md"
[ -e "$REPO/react/rules/test-quality.md" ]              && link_entry "$dst_dir" "test-quality.md"                    "../react/rules/test-quality.md"
[ -e "$REPO/flutter/rules/architecture-principles.md" ] && link_entry "$dst_dir" "flutter-architecture-principles.md" "../flutter/rules/architecture-principles.md"

echo "Done. specflow bundle linked into repo dirs."
