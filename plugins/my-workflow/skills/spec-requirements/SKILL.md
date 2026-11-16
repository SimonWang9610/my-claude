---
name: spec-requirements
description: >-
  Use this skill when the user wants to pin down what to build: "write the requirements", "user
  stories for X", "acceptance criteria", "what should this do", or a vague feature or improvement
  idea, even if they never say "requirements". Clarifies first, then writes stories and testable
  criteria with stable ids. Not for a bug (use my-workflow:spec-diagnose).
argument-hint: "[request | path to a workflow.yaml]"
---

# spec-requirements

Rules: `conventions.md`, `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (else `../../shared/`), read
once per conversation. Mode per the spec rules. Other paths: this folder.
Template: improvement → `assets/spec-improvement.md`, else `assets/spec-feature.md`.

## Steps

1. **Gather** — the request and what it points to; what it already decides is a `D`.
2. **Ground** — `/my-workflow:audit-truth` on what is left open. A user claim a decision rests on is
   checked; refuted → correct it with the anchor, or stop when fixes compete.
3. **Clarify** — ambiguous terms, sources that disagree, missing actors, edges or failures, the goal
   behind the ask. Ask; spec mode: an answer that was weighed goes to discussions.
4. **Stories** — feature: one `US` per actor goal, one line, with a priority; about 5. Improvement:
   no stories; per quality the current value (measured now), the target, what must not change.
5. **Criteria** — one sentence each, `When <trigger>, <observable result>`, at the outermost surface;
   `Given` only when the starting state matters; the main path, then edges and failures. No story
   owns it → `AC-<n>`. Improvement: `AC-1` the target, then one per invariant. Hard numbers and
   never-events → `R`, with how each is checked.
6. **Functionalities** — optional: an `FN` only when one capability serves several criteria.
7. **Write** — the template, unused parts deleted; `Evidence` lines pending. Spec mode:
   `spec-check ids`.

## Rules

- An `AC` passes this test: a tester could write its test from it alone, and it would fail today.
- Over about 12 criteria → propose splitting the spec.
- Never ask what can be looked up.
