#!/usr/bin/env bash
#
# install.sh — register the my-claude plugin marketplace and install its plugins
# via the `claude plugin` CLI.
#
#   ./install.sh                    # marketplace (GitHub) + react-spec
#   ./install.sh --flutter          # also install flutter-spec
#   ./install.sh --local            # register THIS checkout as the marketplace (development)
#   ./install.sh --rules            # also symlink rules/preferences.md -> ~/.claude/rules/
#   ./install.sh --uninstall        # remove plugins + marketplace + rules symlink
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
MARKETPLACE_NAME="my-claude"
GITHUB_SOURCE="SimonWang9610/my-claude"
FLUTTER=no LOCAL=no RULES=no UNINSTALL=no

usage() { grep '^#   ' "$0" | sed 's/^#   //'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --flutter)   FLUTTER=yes ;;
    --local)     LOCAL=yes ;;
    --rules)     RULES=yes ;;
    --uninstall) UNINSTALL=yes ;;
    -h|--help)   usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
  shift
done

command -v claude >/dev/null || { echo "claude CLI not found — install Claude Code first."; exit 1; }

RULES_LINK="$HOME/.claude/rules/preferences.md"

if [ "$UNINSTALL" = yes ]; then
  claude plugin uninstall "react-spec@$MARKETPLACE_NAME"   2>/dev/null || true
  claude plugin uninstall "flutter-spec@$MARKETPLACE_NAME" 2>/dev/null || true
  claude plugin marketplace remove "$MARKETPLACE_NAME"     2>/dev/null || true
  if [ -L "$RULES_LINK" ] && [ "$(readlink "$RULES_LINK")" = "$REPO/rules/preferences.md" ]; then
    rm "$RULES_LINK" && echo "Removed rules symlink."
  fi
  echo "Uninstalled."
  exit 0
fi

SOURCE="$GITHUB_SOURCE"
[ "$LOCAL" = yes ] && SOURCE="$REPO"
echo "Registering marketplace '$MARKETPLACE_NAME' from $SOURCE"
claude plugin marketplace add "$SOURCE" 2>/dev/null || claude plugin marketplace update "$MARKETPLACE_NAME"

claude plugin install "react-spec@$MARKETPLACE_NAME"
[ "$FLUTTER" = yes ] && claude plugin install "flutter-spec@$MARKETPLACE_NAME"

if [ "$RULES" = yes ]; then
  mkdir -p "$HOME/.claude/rules"
  if [ -e "$RULES_LINK" ] && [ ! -L "$RULES_LINK" ]; then
    echo "WARN: $RULES_LINK is a real file — left as-is."
  else
    ln -sf "$REPO/rules/preferences.md" "$RULES_LINK"
    echo "Linked rules/preferences.md -> $RULES_LINK"
  fi
fi

echo "Done. Try: /react-spec:specflow init  ·  claude --agent react-spec:my-specflow-driver"
