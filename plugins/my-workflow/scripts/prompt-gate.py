#!/usr/bin/env python3
"""UserPromptSubmit hook: one-line routing hint for the my-workflow skills. Never blocks. Silent on slash
commands and gate replies; else hints rephrase for a long prompt, then critique, verify, a design skill or
audit-truth by the prompt's shape, or drive-spec for a short task request that opens with a task verb."""
import json, re, sys

GATE = re.compile(r"^(y(es)?|no?|ok(ay)?|go|continue|proceed|sure|agreed|use (the )?defaults?|option \w+)\b", re.I)
TASK = re.compile(r"^(add|fix|build|implement|write|create|refactor|make|draft|design|scaffold|critique|review|"
                  r"check|audit|assess)\b"
                  r"(?!\s+(it|them|this|that|these|those|all|both)\W*$)", re.I)
HINTS = [
    (r"\bis (this|our|the) (design|plan|structure|architecture|code) (sound|ok|right)\b|\b(critique|review|"
     r"check|audit|assess) (this|the|our|my) (design|architecture|structure|code|diff|doc|change|pr|work|branch)",
     "Review: `/my-workflow:critique`."),
    (r"\bacceptance (tests?|checks?)\b|\bdoes (it|this) meet the spec\b|\bverify (the )?(spec|requirements|R\d)",
     "Acceptance: `/my-workflow:verify`."),
    (r"where should (this|the|that|our) (\w+ )?state (live|go)|should (this|it|that) be global|"
     r"what survives (back|reload|sign.?out)",
     "UI state: `/my-workflow:analyze-ui-state`."),
    (r"what components\b|which way should (this|the|that) dependency|should these be one\b",
     "Components: `/my-workflow:design-component`."),
    (r"(folder|directory|project|repo) (structure|layout)|where does (this|it) (go|belong)|by feature or (by )?layer|"
     r"\bscaffold\b.*\b(project|app|repo|service|package|workspace)\b",
     "Project structure: `/my-workflow:scaffold-project-structure`."),
    (r"\b(architect(ure|ural)?|how (should|would) (we|i|you) (build|structure|approach|design)|"
     r"what are (the )?options|which approach|which stack|client.server|local.first|monolith)",
     "Design question: `/my-workflow:decide` (approach or stack, and the design parts it needs)."),
    (r"\b(how does|how do|what happens when|where (is|does|do)|who (calls|writes|owns)|walk me through)\b",
     "Fact-finding: `/my-workflow:audit-truth`."),
]

def signals(p):
    words = p.split()
    if GATE.match(p) or (len(words) <= 3 and not TASK.match(p)):
        return None
    if len(words) > 150:
        return "Long prompt: `/my-workflow:rephrase` puts its main objective first."
    for pattern, hint in HINTS:
        if re.search(pattern, p, re.I):
            return hint
    if (TASK.match(p) and len(words) <= 15 and not p.rstrip().endswith("?")
            and not re.search(r"[/\\][\w.-]+|\d", p)):
        return "Task: `/my-workflow:drive-spec` turns it into a spec and drives it to a verified change."
    return None

def main():
    p = (json.load(sys.stdin).get("prompt") or "").strip()
    if not p or p.startswith("/"):
        return
    s = signals(p)
    if s:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "my-workflow: " + s}}))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
