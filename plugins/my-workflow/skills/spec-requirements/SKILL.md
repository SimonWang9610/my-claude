---
name: spec-requirements
description: >-
  Use this skill when the user wants to pin down what to build before building it: "write the
  requirements", "user stories for X", "acceptance criteria for X", "what exactly should this do",
  "scope this feature", or a vague feature or improvement idea that needs clarifying, even if they
  never say "requirements". Asks about what is vague or in conflict first, then writes spec.md: user
  stories, testable given/when/then criteria and the functionalities behind them, each with a stable
  id (an improvement: current vs target, and what must not change). Also the first step of a feature
  or improvement spec. Not for a bug (use my-workflow:spec-diagnose).
argument-hint: "[request | path to a workflow.yaml]"
---

# spec-requirements

Rules: `conventions.md` and `spec-rules.md` in `${CLAUDE_PLUGIN_ROOT}/shared/` (unexpanded → `../../shared/`).
Other paths are relative to this folder.

## Input

Per the spec rules' Spec mode. Template: kind improvement → `assets/spec-improvement.md`, else
`assets/spec-feature.md`.

## Steps

1. **Gather** — the request, the docs and rules it points to, the project's context files, a named
   atlas. What the instructions decide is a `D`. A named path is read, not searched for.
2. **Ground** — `/my-workflow:audit-truth` on what the instructions leave open: how the touched area
   works today, what can be reused. A user statement a decision rests on is a claim: check it.
   Refuted with one obvious fix → `D-<n> <fix> (corrects the request) — <anchor>`; competing fixes →
   stop and recommend.
3. **Clarify** — before writing, find what is vague or in conflict: an ambiguous term · two sources
   that disagree · a missing actor, edge or failure case · the goal behind the ask. Ask per the
   conventions' Questions. Every answer lands as a `D` or in a story; spec mode: the round is logged
   per the spec rules' History.
4. **Stories** — feature: one `US` per actor goal (as a · I want · so that) with a priority; about 5,
   more → group them or split the spec. Improvement: no stories; per quality, the current value from
   a command run now, the target, each behaviour that must not change.
5. **Criteria** — per story, `AC`s as given · when · then: one observable behaviour each, at the
   outermost surface the user or caller sees; the main path, then each named edge and failure.
   A criterion no story owns (cross-cutting, technical) → standalone `AC-<n>`. Improvement: `AC-1` the
   target measure, then one `AC` per invariant. Hard numbers, compatibility
   and what must never happen → limits (`R`), each with how it is checked.
6. **Functionalities** — one `FN` per thing the system must do (verb + object) and the `AC`s it
   serves. Feature: every `AC` is served by at least one. One no criterion observes (a migration, a
   job, internal plumbing) → standalone, Serves `—`, proved by its tasks' checks. Improvement: only
   where new functionality appears.
7. **Write** — the template, unused template rows deleted. `Check` cells stay pending; implement
   fills them. Spec mode: `spec-check ids` passes.

## Rules

- Never ask what can be looked up.
- The test for an `AC`: a tester could write the check from its row alone, and it would fail today.
- An `FN` says what the system does, never how: no unit, file or library.

## Output

The spec per its template. `Open:` the questions, any story without a testable criterion.
