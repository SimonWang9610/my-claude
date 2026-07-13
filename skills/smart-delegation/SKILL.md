---
name: smart-delegation
description: >
  Decide whether a piece of work should be delegated to a subagent, kept in the current session,
  or run in a fork — then, when delegating, construct a complete self-contained prompt and verify
  the result. Use whenever orchestrating work: "should I delegate this", before spawning any
  subagent, when a phase/task could run in parallel, or when exploration would flood the current
  context.
---

# smart-delegation

Spend context where it has leverage: the current session holds the authoritative picture and makes
decisions; subagents absorb noise and parallelism. A subagent is a **cold start that inherits
nothing** — delegation pays only when isolation, parallelism, or fresh eyes buy more than the
handoff costs.

## Decide

**Delegate to a subagent when any of these hold:**

- **Parallel fan-out** — independent units of work with no shared sequence (batch them in ONE
  message so they run concurrently).
- **Noisy exploration** — many file reads/searches whose value is a compact conclusion; the
  session needs the summary, not the dump.
- **Fresh eyes** — reviewing or challenging work this session produced; the context that wrote it
  will defend it (give the reviewer only the artifacts, never the reasoning).
- **Separation of duties** — one agent must not grade its own work (e.g. a test author vs. an
  implementer).

**Stay in the current session when:**

- The work is **trivial and cache-cheap** — a single read, a 1–2 call lookup, a quick grep, a
  small edit. Spawning costs more than doing.
- The steps are **tightly sequential**, each needing the previous result — a relay of subagents
  just re-pays the handoff every leg.
- The work **is the decision** — synthesis, judgment, scope calls, anything the caller holds you
  accountable for. Orchestrators never delegate the verdict.
- The context needed is **large and already here** but too entangled to hand off compactly.

**Fork (a child that inherits this session's context) when** the work needs what the session
already knows and splitting is only about keeping the main thread clean — a fork rides the warm
cache; a fresh subagent would re-read everything.

## Delegate

A subagent inherits nothing — build every prompt from this template, every field filled:

```
Working Directory: <the exact tree to write in — never a new/isolated worktree unless told>
Skills:            <the skills to apply, and when to invoke each>
Rules:             <the relevant constraints — guidance, not a whitelist>
Responsibilities:  <the exact deliverable — do ONLY this, change nothing else>
Materials:         <exact file paths it needs — never "look around">
Done When:         <a mechanically checkable condition — a named test green, a file existing>
Report Back:       <the compact structured return — files changed, results; on failure: failure
                    type, what was tried, partial findings — never a bare "failed">
```

- **Batch independents** in one message; sequence only what truly depends.
- **Demand compact structured returns** — the session consumes conclusions, not transcripts.
- **Scope tightly** — a subagent with a vague charter wanders; "do ONLY this" is load-bearing.
