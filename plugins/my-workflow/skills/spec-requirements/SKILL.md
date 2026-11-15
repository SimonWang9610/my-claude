---
name: spec-requirements
description: >-
  Writes a spec's requirements for a feature or an improvement: gathers them from your instructions,
  the codebase and the documents, clarifies vague or conflicting points with you first, then writes
  user stories, each with given/when/then acceptance criteria a test can be written from, plus
  limits and decisions, as spec.md (an improvement: current vs target with a measure, and what must
  not change). Use as the first step of a feature or improvement spec, or on "write the
  requirements", "user stories for X", "acceptance criteria for X". Not for a bug (use
  my-workflow:spec-diagnose).
argument-hint: "[request | path to a workflow.yaml]"
---

# spec-requirements

Follow `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md` (if shown unexpanded: `../../shared/conventions.md`
from this skill's folder). Other paths are relative to this skill's folder.

1. **Context** — per the conventions' Spec mode. Template: kind improvement →
   `assets/spec-improvement.md`, else `assets/spec-feature.md`.
2. **Gather** — the request, the docs and rules it points to, the project's context files and a named
   atlas. What the instructions already decide is a `D`; a named path is read, not searched for.
3. **Ground** — `/my-workflow:audit-truth` on what the instructions leave open: how the touched area
   works today, what can be reused. Never ask what you can look up. A user statement a decision
   depends on is a claim: check it; refuted with one obvious fix → `D<n> <fix> (corrects the request)
   — <anchor>`; with competing fixes → stop and recommend.
4. **Clarify** — before writing stories, find what is vague or in conflict: an ambiguous term · two
   sources that disagree · a missing actor, edge or failure case · the goal behind the ask. Ask per
   the conventions' Questions. More than one round, or answers other stakeholders must see →
   `assets/clarifications.md` beside the spec. Every answer lands as a `D` or in a story.
5. **Stories** — a feature: one `US` per actor goal (as a · I want · so that), with a priority; about
   5, more → group them or split the spec. An improvement: no stories; per quality, the current value
   measured by a command run now, the target, and each behaviour that must not change.
6. **Criteria** — per story, `AC`s as given · when · then: one observable behaviour each, at the
   outermost surface the user or caller sees; the main path, then each named edge and failure case.
   The test: a tester could write the check from the row alone, and it would fail today. An
   improvement: `AC1` the target measure, then one `AC` per invariant. Hard numbers, compatibility
   and things that must never happen are limits (`R`), each with how it is checked.
7. **Write** — the template; `Check` cells stay pending until implement fills in the commands. `Open:` the
   questions, and any story without a testable criterion.
