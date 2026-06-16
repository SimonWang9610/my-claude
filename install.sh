#!/usr/bin/env bash
#
# install.sh — wire this repo into ~/.claude as your global Claude Code config.
#
# Points ~/.claude/{commands,skills,rules,agents} at this repo's matching folders.
# Idempotent: safe to re-run. Anything already in the way is backed up, never deleted.
# Override the target with CLAUDE_HOME=/path ./install.sh (defaults to ~/.claude).
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_HOME:-$HOME/.claude}"
DIRS=(commands skills rules agents)
STAMP="$(date +%Y%m%d-%H%M%S)"

echo "Installing global Claude config"
echo "  repo:   $REPO"
echo "  target: $CLAUDE_DIR"
mkdir -p "$CLAUDE_DIR"

# Refresh the inner layer first: expose the specflow bundle through the repo dirs.
[ -x "$REPO/link-specflow.sh" ] && "$REPO/link-specflow.sh"

for d in "${DIRS[@]}"; do
  src="$REPO/$d"
  dst="$CLAUDE_DIR/$d"

  [ -d "$src" ] || { echo "  skip  $d  (no $src)"; continue; }

  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    echo "  ok    $d  (already linked)"
    continue
  fi

  if [ -L "$dst" ]; then
    rm "$dst"                                  # wrong symlink: no data to lose
  elif [ -e "$dst" ]; then
    mv "$dst" "$dst.bak.$STAMP"                # real dir/file: preserve it
    echo "  saved $d  → $(basename "$dst").bak.$STAMP"
  fi

  ln -s "$src" "$dst"
  echo "  link  $d  → $src"
done

# Sanity: confirm a bundle symlink resolves through the wiring (catches core.symlinks=false on Windows,
# or a clone where git didn't restore the in-repo symlinks). Commands are not surfaced, so probe an agent.
probe="$CLAUDE_DIR/agents/oac-feature-workflow.md"
if [ -e "$probe" ]; then
  echo "  check oac-feature-workflow.md resolves ✓"
else
  echo "  WARN  $probe does not resolve — if on Windows, enable symlinks:"
  echo "        git config core.symlinks true && git checkout -- ."
fi

echo "Done. Restart Claude Code (or reload) to pick up the global skills / agents / rules."
echo "Note: specflow commands are NOT installed globally — they live in specflow/commands/ and are"
echo "      invoked by name (/spec-*), resolving to your project's own /spec-* commands."
