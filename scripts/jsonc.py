"""Minimal JSONC (VS Code settings) support: read with comments and trailing commas, and update a
top-level key in place without touching the rest of the file (comments and formatting survive)."""

import json
import re


def _strip(text: str) -> str:
    """Drop // and /* */ comments outside strings, then trailing commas."""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\":
                out.append(text[i + 1]); i += 2; continue
            in_str = ch != '"'
        elif ch == '"':
            in_str = True; out.append(ch)
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            i = text.find("*/", i + 2) + 2 or n; continue
        else:
            out.append(ch)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def load(text: str) -> dict:
    return json.loads(_strip(text)) if text.strip() else {}


def _value_span(text: str, key: str):
    """(start, end) of the value of a top-level `"key":` in the raw text, or None."""
    m = re.search(r'"' + re.escape(key) + r'"\s*:\s*', text)
    if not m:
        return None
    i, depth, in_str = m.end(), 0, False
    start = i
    while i < len(text):
        ch = text[i]
        if in_str:
            if ch == "\\":
                i += 2; continue
            in_str = ch != '"'
        elif ch == '"':
            in_str = True
        elif ch in "{[":
            depth += 1
        elif ch in "}]":
            if depth == 0:
                return start, i
            depth -= 1
            if depth == 0:
                return start, i + 1
        elif ch in ",\n" and depth == 0:
            return start, i
        i += 1
    return start, i


def set_key(text: str, key: str, value) -> str:
    """Set a top-level key: replace its value in place, or insert it right after the opening brace."""
    rendered = json.dumps(value, indent=4).replace("\n", "\n    ")
    span = _value_span(text, key)
    if span:
        return text[:span[0]] + rendered + text[span[1]:]
    if not text.strip():
        return "{\n    " + json.dumps(key) + ": " + rendered + "\n}\n"
    brace = text.find("{")
    if brace == -1:
        raise ValueError("settings file has no top-level object")
    return text[:brace + 1] + "\n    " + json.dumps(key) + ": " + rendered + "," + text[brace + 1:]
