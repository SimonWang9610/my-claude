---
name: sf-workflow-startup
description: >
  One-call startup for an sflow spec: /sf-workflow-startup <tech> <variant> [seed…]. Owns the
  entire startup sequence — worktree check, seed collection, resume detection, workflow binding
  via the profile's pick-<tech>-workflow skill, and spec scaffolding via /sf-init — and reports
  the spec ready with the next phase to drive. tech: react | flutter (auto-detected from
  package.json / pubspec.yaml when omitted); variant: feature | brownfield | bugfix | quickfix.
  The first action of every workflow driver agent; also usable ad-hoc to stand up a spec.
---

# sf-workflow-startup

Stand up (or resume) one sflow spec, end to end, and hand back a drive-ready state. Nothing
outside this skill needs to know how startup works; the caller drives the phases afterwards.

## Procedure

### Step 1 — Worktree check (write nothing until it passes)

- `git rev-parse --show-toplevel` → `$ROOT`; `git rev-parse --git-common-dir` → common dir.
- Common dir outside `$ROOT` → worktree confirmed: `$ROOT` is the write root; run
  `git submodule update --init --recursive` when `$ROOT/.gitmodules` exists.
- Not in a worktree → STOP: report the current branch and ask how to proceed.

### Step 2 — Resolve tech and variant

- `<tech>` given → use it. Omitted → detect: `pubspec.yaml` → `flutter`; `package.json` with a
  react dependency → `react`; both or neither → ask.
- `<variant>` given → use it. Omitted → gauge complexity and recommend one:
  `feature` (new behavior) / `brownfield` (in-place change) / `bugfix` (defect, repro-test-first) /
  `quickfix` (single-AC change).

### Step 3 — Collect the seed

From the invocation args (ask only for what's missing and required):

| Variant | Required | Optional |
|---|---|---|
| feature | feature description | spec name, design links, legacy source path + folders (port) |
| brownfield | change description + the feature being modified | spec name, design links |
| bugfix | bug report / description | spec name, pointer to the affected file |
| quickfix | concise change description | — |

### Step 4 — Resume check

`.specflow/specs/<name>/` already exists → **resume**: read `.meta.yaml`; if `workflow.yaml` lacks
the `bound:` marker, run `/pick-<tech>-workflow <variant> <spec-dir>` to re-bind it. Skip Steps
5–6 and report (Step 7) with the first non-`complete` phase.

### Step 5 — Bind

Run `/pick-<tech>-workflow <variant>`, passing the seed facts (design links? legacy port?
tracker?). It returns the bound workflow: concrete `skills:` + `notes:` per phase, conditional
roles resolved. The profile must provide this skill; if it's missing, STOP and report.

### Step 6 — Init

Run `/sf-init` with the description, design links, and the bound workflow. It writes
`.specflow/specs/<name>/workflow.yaml` + `.meta.yaml` (the sole writer of the spec dir).

### Step 7 — Report ready

Return to the caller: the spec dir, tech + variant, fresh-or-resume, the next phase to drive,
and the `gate: human` checkpoints ahead.
