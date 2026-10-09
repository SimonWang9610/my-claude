#!/usr/bin/env python3
"""UserPromptSubmit hook: one-line nudge when a prompt shows a habit the portrait lists as a
blind spot (terse ask, mixed batch, hedge, vague defect, pause/resume, architecture question).
Never blocks (exit 0); silent unless a signal fires."""
import json, re, sys

APPROVAL = re.compile(r"^\s*(sure|ok(ay)?|yes|go ahead|go|continue|proceed|do it|looks good|agree|approved?|"
                      r"please (go ahead|continue|proceed))[\s.,!]*$", re.I)

def signals(p):
    words = len(p.split()); sig = []
    if re.search(r"usage limit|pause all|stop for now|pause (the|all) work", p, re.I):
        return ["Pause requested: start nothing new, save work in progress, write CHECKPOINT.md (goal, done, in progress, in-flight work, next step, verify)."]
    if re.search(r"\b(resume|continue) (the )?(interrupted|unfinished|previous) work|continue (from )?where|"
                 r"where were we|resume works?\b", p, re.I):
        return ["Resume requested: read CHECKPOINT.md, verify state in a few calls, continue from its next step."]
    if APPROVAL.match(p):
        return ["Approval only: state in one line what is being approved, then act."]
    if re.search(r"\b(architect(ure|ural)?|design the|how (should|would) (i|we|you) (build|structure|approach)|"
                 r"what('s| is) the best way|is there (something|anything) existing|options?\b|good practice|"
                 r"client.server|local.first|monolith|microservices?|layering|boundar(y|ies)|pattern for|"
                 r"is (this|our|the) (design|plan|structure) (sound|ok|right)|review (our|the|this) (architecture|design|plan))", p, re.I):
        sig.append("Architecture question: the `architect` skill (recognises design / discuss / evaluate and the levels it spans).")
    if re.search(r"\b(how does|how do|what happens when|where (is|does|do)|who (calls|writes|owns)|explain (the|this|how)|onboard|walk me through)\b", p, re.I):
        sig.append("Question about existing code: the `explore` skill at the right altitude (map / mechanism / onboarding / locate).")
    if not sig and words <= 12 and not re.search(r"[/\\][\w.-]+|\d", p):
        sig.append(f"Terse ask ({words} words): if it implies real work, the `clarify` skill first "
                   "(hard constraints, what exists, done-criterion; a few questions with defaults).")
    if len(re.findall(r"(^|\s)\d+[.)]\s", p)) >= 3:
        sig.append("Mixed batch: split it, questions first, route each item, confirm the order before starting.")
    if re.search(r"\b(maybe|probably|perhaps|up to you|if you think|or use your (judg|recommend))", p, re.I):
        sig.append("Hedged wording: treat as a hypothesis, verify, then state the decision taken in one line.")
    if re.search(r"\b(looks? (weird|wired|wrong|off)|sometimes|does ?n'?t work|not (rendered|working)|should be improved)\b",
                 p, re.I) and not re.search(r"\b(expected|observed|repro|steps)\b", p, re.I):
        sig.append("Defect without fields: Observed / Expected / Where / Repro; reproduce before changing code.")
    if re.search(r"\b(by yourself|instead of (feeding|spawning|delegat)|push (them|it|after)|worktree|spec ?flow|"
                 r"don'?t spawn|no (more )?(sub)?agents?)\b", p, re.I):
        sig.append("Process instruction: offer to add it as a one-line standing rule in the project's instructions.")
    return sig

def main():
    p = (json.load(sys.stdin).get("prompt") or "").strip()
    if not p or p.startswith("/"):
        return
    sig = signals(p)
    if sig:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                                 "additionalContext": "think: " + " ".join(sig)}}))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
