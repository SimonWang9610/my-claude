---
name: smart-delegation
description: >
  Routes a piece of work to the cheapest execution that can do it well — inline, a fork
  that inherits this session's context, or a subagent (bound or ad-hoc) with its own —
  and fixes what the spawn must carry back. Use before spawning anything, when work could
  run in parallel, when exploration would flood this context, or when a reviewer must not
  see the reasoning that produced the work. Output: an execution choice (inline / fork /
  subagent) and the handoff the spawn carries.
---

# smart-delegation

Spend context where it has leverage: this session holds the authoritative picture and
makes the decisions; everything else absorbs noise. Output tokens cost more than input —
a spawn that returns a transcript has failed even when its work succeeded.

## 1. Pick the execution

| Route | Gets | Costs | Use when |
|-------|------|-------|----------|
| **Inline** | everything | nothing | trivial · tightly sequential · the work IS the decision (synthesis, scope calls, verdicts) |
| **Fork** | full conversation history, same tools/model/permissions | **cheap — reuses this session's prompt cache** | the work needs what this session already knows; splitting only keeps the main thread clean |
| **Subagent** | fresh context + its own definition, separate cache | cold start | isolation, parallel fan-out, fresh eyes, different tools/model/fences |

**Fork is the default when context is the payload.** Identical system prompt and tools
mean its first request hits the parent's cache — cheaper than re-explaining the world to
a stranger. A fork can't give you fresh eyes (it inherits your reasoning) or a narrower
tool fence.

**Subagent when the fresh context is the point:** noisy exploration whose value is a
compact conclusion · independent items that run concurrently (batch them in ONE message)
· review that must not inherit the author's reasoning · separation of duties (nobody
grades their own work).

## 2. Bound agent, or ad-hoc?

Match the work against the available agents' `description` — a purpose-built agent pins
its fences, skills, model, and return contract, so none of that gets re-authored or
forgotten. No match → ad-hoc spawn: set model + effort yourself (mechanical, scoped work
→ mid tier, medium · locating/scanning → small tier, escalated when the goal needs
synthesis · design, forensics, verdicts → top tier, high).

## 3. Hand off — four things, always

Whatever the route, the prompt carries only: **where** (the exact tree — never a fresh
worktree unless told) · **what** (the deliverable, "do ONLY this") · **materials** (exact
paths, sliced to the task — never a whole directory or "look around") · **done when**
(mechanically checkable). Ad-hoc spawns add the fences and skills a bound agent would
have carried. Never background narration, never your reasoning — the materials are the
context.

**Demand a compact return:** line-oriented, hard item cap, facts verbatim (paths, IDs,
the one decisive error line); on failure — type + what was tried + partial findings,
never a bare "failed".

**Verify it yourself** — existence, grep, named tests. Never advance on a spawn's word.
