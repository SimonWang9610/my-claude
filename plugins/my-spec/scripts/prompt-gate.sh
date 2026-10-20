#!/usr/bin/env bash
# UserPromptSubmit hook wrapper — see prompt-gate.py. Always exits 0; silent unless a signal fires.
command -v python3 >/dev/null 2>&1 || exit 0
exec python3 -I "$(dirname "$0")/prompt-gate.py"
