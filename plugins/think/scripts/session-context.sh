#!/usr/bin/env bash
# SessionStart hook: inject PROTOCOL.md as standing context.
root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd -P)}"
cat "$root/PROTOCOL.md"
exit 0
