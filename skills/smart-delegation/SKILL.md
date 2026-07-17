---
name: smart-delegation
description: >
  Decide inline vs subagent vs fork, then build a self-contained prompt and verify the
  compact return. Use before spawning any subagent, when phases/tasks could run in
  parallel, or when exploration would flood the current context.
---

# smart-delegation

Spend context where it has leverage: the current session holds the authoritative picture
and makes decisions; subagents absorb noise and parallelism. A subagent is a **cold start
that inherits nothing** — delegation pays only when isolation, parallelism, or fresh eyes
buy more than the handoff costs. Output tokens cost more than input: a subagent that
returns a transcript has failed even when its work succeeded.

## Decide

**Delegate when any of these hold:**

- **Parallel fan-out** — independent work items (a tasks.md wave); batch them in ONE
  message so they run concurrently.
- **Noisy exploration** — many reads/searches whose value is a compact conclusion (an
  audit, an inventory scan); the session needs the summary, never the dump.
- **Fresh eyes** — reviewing or challenging work this session produced; the context that
  wrote it will defend it. Give the reviewer only the artifacts, never the reasoning.
- **Separation of duties** — one agent must not grade its own work (escalated test/work
  split).

**Stay inline when:**

- **Trivial and cache-cheap** — a single read, a quick grep, a small edit; spawning costs
  more than doing.
- **Tightly sequential** — each step needs the previous result; a relay of subagents
  re-pays the handoff every leg.
- **The work is the decision** — synthesis, judgment, scope calls, gate verdicts.
  Orchestrators never delegate the verdict.

**Fork** (inherits this session's context) when the work needs what the session already
knows and splitting is only about keeping the main thread clean.

## Delegate — every field filled, nothing inherited

```
Working Directory: <the exact tree — never a new/isolated worktree unless told>
Skills:            <the skills to invoke, and when>
Rules:             <the constraints in force — e.g. "test files only", "source only">
Responsibilities:  <the exact deliverable — do ONLY this, change nothing else>
Materials:         <exact paths, sliced to the task: the unit's contract, its task row,
                    the AC lines it traces — never a whole spec dir or "look around">
Done When:         <a mechanically checkable condition — named test green, file exists>
Report Back:       <the exact return format — line-oriented, hard item cap, zero prose;
                    facts verbatim (paths, IDs, the one decisive error line); on failure:
                    failure type + what was tried + partial findings, never bare "failed">
```

- **Batch independents** in one message; sequence only what truly depends.
- **Scope tightly** — "do ONLY this" is load-bearing; a vague charter wanders.
- **Verify the return yourself** — existence, grep, named tests; never advance on a
  subagent's word.
