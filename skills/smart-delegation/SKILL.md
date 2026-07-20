---
name: smart-delegation
description: >
  Decide inline vs subagent vs fork — and, when delegating, the spawn's model + effort —
  then build a self-contained prompt and verify the compact return. Use before spawning
  any subagent, when phases/tasks could run in parallel, or when exploration would flood
  the current context.
---

# smart-delegation

Spend context where it has leverage: the current session holds the authoritative picture
and makes decisions; subagents absorb noise and parallelism. A subagent is a **cold start
that inherits nothing** — delegation pays only when isolation, parallelism, or fresh eyes
buy more than the handoff costs. Output tokens cost more than input: a subagent that
returns a transcript has failed even when its work succeeded.

## Decide — three calls, in order

**1. Delegate at all?** Delegate when any of these hold:

- **Parallel fan-out** — independent work items (a tasks.md wave); batch them in ONE
  message so they run concurrently.
- **Noisy exploration** — many reads/searches whose value is a compact conclusion (an
  audit, an inventory scan); the session needs the summary, never the dump.
- **Fresh eyes** — reviewing or challenging work this session produced; the context that
  wrote it will defend it. Give the reviewer only the artifacts, never the reasoning.
- **Separation of duties** — one agent must not grade its own work (escalated test/work
  split).

Stay inline when: **trivial and cache-cheap** (spawning costs more than doing) ·
**tightly sequential** (a relay of subagents re-pays the handoff every leg) · **the work
is the decision** (synthesis, scope calls, gate verdicts — orchestrators never delegate
the verdict). **Fork** (inherits this session's context) when the work needs what the
session already knows and splitting only keeps the main thread clean.

**2. Choose model + effort** — spawn parameters, set here, never prompt content:

- **test/impl work** (authoring from contracts, scoped changes) → **Sonnet**; effort
  **medium** when the contract fully pins the work, **high** when it spans units or
  carries heavy context.
- **search/explore** (scans, inventories, locating) → **Haiku**; escalate to Sonnet when
  the goal needs synthesis (an audit build, behavior distillation), not just locating.
- **judgment** (design, forensics, review verdicts) → top tier, **high** effort.

**3. Bind skills + slice materials** — name the skills the subagent must invoke (and
when), and collect the exact material slice: the unit's contract, its task rows, the AC
lines it traces — never a whole spec dir, never "look around". These fill the template's
Skills and Materials fields verbatim.

## Delegate — every field filled, nothing inherited

Every field a pointer or constraint — no field ever carries background narration or your
reasoning; the Materials artifacts carry the context.

```
Working Directory: <exact tree — never a new/isolated worktree unless told>
Skills:            <the bindings from Decide step 3 — which skills, and when>
Rules:             <constraints in force — "test files only", "source only">
Responsibilities:  <the exact deliverable — do ONLY this>
Materials:         <the slice from Decide step 3 — exact paths>
Done When:         <mechanically checkable — named test green, file exists>
Report Back:       <line-oriented, hard item cap, zero prose; facts verbatim (paths,
                    IDs, the decisive error line); failure = type + tried + partial
                    findings, never bare "failed">
```

- **Batch independents** in one message; sequence only what truly depends.
- **Scope tightly** — "do ONLY this" is load-bearing; a vague charter wanders.
- **Verify the return yourself** — existence, grep, named tests; never advance on a
  subagent's word.
