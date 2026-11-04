#!/usr/bin/env bash
# run.sh SCRIPT.py [args...] - run a my-invest script with the right Python.
# Project: --project X in the args, else $MY_INVEST_PROJECT, else the working directory.
# Interpreter: "python" in <project>/data/config.json -> <project>/data/.venv/bin/python -> for yahoo.py (needs
# yfinance) a .venv is created from the newest python3.10+ on PATH with requirements.txt -> python3.
set -euo pipefail
if [ "$#" -lt 1 ]; then echo '{"ok": false, "script": "run.sh", "error": "usage: run.sh SCRIPT.py [args]"}'; exit 1; fi
SCRIPT="$1"; shift
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PROJECT="${MY_INVEST_PROJECT:-}"
prev=""
for a in "$@"; do
  if [ "$prev" = "--project" ]; then PROJECT="$a"; fi
  case "$a" in --project=*) PROJECT="${a#--project=}";; esac
  prev="$a"
done
PROJECT="${PROJECT:-$PWD}"
PROJECT="${PROJECT/#\~/$HOME}"
MINE="$PROJECT/data"

PY=""
if [ -f "$MINE/config.json" ]; then
  PY="$(sed -n -E 's/.*"python"[[:space:]]*:[[:space:]]*"([^"]*)".*/\1/p' "$MINE/config.json" | head -n 1)"
fi
PY="${PY/#\~/$HOME}"
case "$PY" in *'${'*) PY="";; esac

provision() {  # create $MINE/.venv from python3.10+ and install requirements.txt; sets PY on success
  local c found=""
  for c in python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then found="$c"; break; fi
  done
  [ -n "$found" ] || return 0
  mkdir -p "$MINE"
  if "$found" -m venv "$MINE/.venv" >&2 && "$MINE/.venv/bin/python" -m pip install --quiet --disable-pip-version-check -r "$HERE/requirements.txt" >&2; then
    echo "my-invest: created data/.venv and installed yfinance" >&2
    PY="$MINE/.venv/bin/python"
  else
    rm -rf "$MINE/.venv"
    echo "my-invest: could not create data/.venv; continuing with python3" >&2
  fi
  return 0
}

if [ -n "$PY" ]; then
  if ! command -v "$PY" >/dev/null 2>&1; then
    echo "{\"ok\": false, \"script\": \"run.sh\", \"error\": \"python in $MINE/config.json is not executable: $PY\"}"; exit 1
  fi
elif [ -x "$MINE/.venv/bin/python" ]; then
  PY="$MINE/.venv/bin/python"
else
  case "$SCRIPT" in yahoo.py) provision;; esac
  PY="${PY:-python3}"
fi
exec "$PY" "$HERE/$SCRIPT" "$@"
