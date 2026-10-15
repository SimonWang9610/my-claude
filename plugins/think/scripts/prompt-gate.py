#!/usr/bin/env python3
"""UserPromptSubmit hook: one-line routing hint for the think workflow. Never blocks; silent unless
the prompt is an imperative short ask, an architecture/options question, or a question about code."""
import json, re, sys

def signals(p):
    if re.search(r"\b(architect(ure|ural)?|how (should|would) (we|i|you) (build|structure|approach|design)|"
                 r"what are (the )?options|which approach|client.server|local.first|monolith|"
                 r"is (this|our|the) (design|plan|structure) (sound|ok|right))", p, re.I):
        return "Design question: the `design` skill (options or architecture at the right level)."
    if re.search(r"\b(how does|how do|what happens when|where (is|does|do)|who (calls|writes|owns)|"
                 r"walk me through)\b", p, re.I):
        return "Fact-finding question: the `explore` skill (code, docs, or online)."
    if len(p.split()) <= 15 and not p.rstrip().endswith("?") and not re.search(r"[/\\][\w.-]+|\d", p):
        return "Short task request: consider the `prompt` skill first to turn it into a spec."
    return None

def main():
    p = (json.load(sys.stdin).get("prompt") or "").strip()
    if not p or p.startswith("/"):
        return
    s = signals(p)
    if s:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "think: " + s}}))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
