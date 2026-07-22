---
name: sflow
description: >
  Runs one phase of the sflow spec-driven workflow — init · preflight · requirements · design ·
  tasks · implement · validate · qa — as its stack-neutral process and gates, a procedure the
  specflow driver sequences. Invoke `/sflow <phase> [instructions]`; the driver decides phase
  order, so this is not auto-selected. Carries the process shell only — the stack know-how lives
  in the contract skills it wraps.
argument-hint: "<phase> [instructions]"
---

# sflow — spec-driven workflow, one phase per call

`/sflow <phase>` runs exactly one phase: its stack-neutral process, artifacts, and exit gate.
The stack skills carry the _how_; this carries the _when_ and _what-must-hold_. The driver
sequences phases and runs each phase's playbook after this. **Load ONLY the invoked phase's
file** (`phases/<phase>.md`).

## Phases

| Phase            | Produces / does                                                        | Procedure                                |
| ---------------- | ---------------------------------------------------------------------- | ---------------------------------------- |
| **init**         | scaffold the spec dir + `.meta.yaml` ledger                            | [init](./phases/init.md)                 |
| **preflight**    | reusable/legacy surfaces + shared-unit impact, before requirements     | [preflight](./phases/preflight.md)       |
| **requirements** | user stories + stable-ID Given/When/Then ACs                           | [requirements](./phases/requirements.md) |
| **design**       | design.md + per-unit interfaces + test strategy + approved journey plan | [design](./phases/design.md)             |
| **tasks**        | dependency-ordered waves, each a test + impl batch                     | [tasks](./phases/tasks.md)               |
| **implement**    | wave-by-wave red→green under an evidence contract                      | [implement](./phases/implement.md)       |
| **validate**     | the blocking pre-gate — clause→test coverage + architecture gate       | [validate](./phases/validate.md)         |
| **qa**           | sign-off-ready audit of the branch (never approves/blocks)             | [qa](./phases/qa.md)                     |

## Conventions — every phase

- **`.meta.yaml` statuses** — `pending | in_progress | completed | skipped | failed`.
- **Artifacts** live under `.specflow/specs/<name>/`; the target repo is read, never written —
  except `implement`. Steering `.specflow/steering/*` is context.
- **Exit is a gate** — a phase completes only when its **Exit** holds; a required input missing
  → run its producing phase (`/sflow <that-phase>`) or STOP. Never advance on an unmet Exit.
