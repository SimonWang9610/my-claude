#!/usr/bin/env python3
"""UserPromptSubmit hook: one-line routing hint for the my-spec workflow. Never blocks. Silent on slash
commands and gate replies; else hints critique, decide or explore by the prompt's shape, or start for a
short task request that opens with a task verb."""
import json, re, sys

GATE = re.compile(r"^(y(es)?|no?|ok(ay)?|go|continue|proceed|sure|agreed|use (the )?defaults?|option \w+)\b", re.I)
TASK = re.compile(r"^(add|fix|build|implement|write|create|refactor|make|draft|design|scaffold|critique|review|"
                  r"check|audit|assess)\b"
                  r"(?!\s+(it|them|this|that|these|those|all|both)\W*$)", re.I)
HINTS = [
    (r"\bis (this|our|the) (design|plan|structure|architecture|code) (sound|ok|right)\b|\b(critique|review|"
     r"check|audit|assess) (this|the|our|my) (design|architecture|structure|code|diff|doc)",
     "Review: `/my-spec:critique`."),
    (r"\b(architect(ure|ural)?|how (should|would) (we|i|you) (build|structure|approach|design)|"
     r"what are (the )?options|which approach|client.server|local.first|monolith|"
     r"(folder|directory|project|repo) (structure|layout)|where does (this|it) (go|belong)|by feature or (by )?layer|"
     r"\bscaffold\b.*\b(project|app|repo|service|package|workspace)\b|what components\b|"
     r"which way should (this|the|that) dependency|where should (this|the|that|our) (\w+ )?state (live|go)|"
     r"should (this|it|that) be global|what survives (back|reload|sign.?out))",
     "Design question: `/my-spec:decide` (approach, structure, components or UI state)."),
    (r"\b(how does|how do|what happens when|where (is|does|do)|who (calls|writes|owns)|walk me through)\b",
     "Fact-finding: `/my-spec:explore`."),
]

def signals(p):
    words = p.split()
    if GATE.match(p) or (len(words) <= 3 and not TASK.match(p)):
        return None
    for pattern, hint in HINTS:
        if re.search(pattern, p, re.I):
            return hint
    if (TASK.match(p) and len(words) <= 15 and not p.rstrip().endswith("?")
            and not re.search(r"[/\\][\w.-]+|\d", p)):
        return "Task: `/my-spec:start` turns it into a spec (fast track for small changes)."
    return None

def main():
    p = (json.load(sys.stdin).get("prompt") or "").strip()
    if not p or p.startswith("/"):
        return
    s = signals(p)
    if s:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "my-spec: " + s}}))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
