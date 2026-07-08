---
name: scan-resource
description: Audits one or more legacy folders/resources and distills each into a compact markdown reference so a migration agent can query the knowledge base instead of re-scanning source on every step. Produces one reference per folder plus an index. Trigger when asked to "scan", "audit", "survey", "index", "map", or "extract references from" code, packages, or directories — especially across multiple folders — or when legacy resources should be studied up-front so later migration phases rely on saved references rather than re-reading source files.
---

# Scan Resource

Given a set of legacy folders/resources, produce **one markdown reference per folder** plus an **index** — a recallable knowledge base a downstream agent (e.g. migrating Flutter → React) can query on demand instead of re-scanning source. Re-open source files only when a reference flags a gap.

## Inputs

1. **Resources** — one or more folders (and possibly files/URLs). Each folder becomes its own reference.
2. **Instruction** — the purpose/scope (e.g. "to help migrate them to React"). Authoritative; if it names a functionality, scope each scan to that.
3. **Output directory** — where references are saved. If missing, ask the caller to supply one

## Output layout

Save references separately under the output directory, one file per audited folder, plus a single index:

```
<output-dir>/
├── INDEX.md              # what exists, so the agent recalls without re-scanning
├── <folder-slug>.md      # one reference per audited folder
├── <folder-slug>.md
└── ...
```

Derive `<folder-slug>` from the folder's path (e.g. `lib/features/auth/` → `features-auth.md`). Keep slugs stable across runs so re-audits overwrite the same file rather than duplicating it.

## Workflow

1. **Resolve scope** from the instruction. For each folder, decide what's in scope; if the instruction names a functionality, scan only that.
2. **For each folder**: scan it as a unit (grep first, open only relevant files), then write `<folder-slug>.md` using the reference template. Don't merge folders into one file.
3. **Write/refresh `INDEX.md`** so the agent can recall what's available at a glance.
4. **Re-audit behavior**: if a reference already exists, update it in place. Only re-scan source for a folder when its reference is missing, stale, or flagged incomplete.

## INDEX.md format

```markdown
# Migration Reference Index

_Source: <root path(s)> · Scope: <instruction> · Updated: <date>_

| Reference          | Source folder      | Covers                                           | For migration                          |
| ------------------ | ------------------ | ------------------------------------------------ | -------------------------------------- |
| `features-auth.md` | lib/features/auth/ | <1-line: business logic / abstractions captured> | <1-line: what it helps build in the target stack> |
```

## Reference format (one per folder)

ALWAYS use this structure. Omit a section only if it has no in-scope content.

```markdown
# <Folder name / what it is>

## Resource

- **Source:** <folder path>
- **Scope:** <one line: the instruction this is scoped to>

## Overview

<2–4 sentences: what this legacy area does and the business purpose it serves. Big-picture, migration-oriented.>

## Business Logic & Abstractions

<The reusable substance the agent will port — rules, state machines, models, services, contracts. Framework-agnostic where possible (the migration target may differ from the source):>

- `<entity / rule / abstraction>` — <what it does; inputs/outputs or shape; where it lives>

## Map

<Where things live, so the agent can jump straight to source if needed. One line per file/area:>

- `<file or area>` — <its role>

## How It Connects

<Data/control flow and dependencies — entry points, what calls what, what holds state. Short.>

## Migration Notes

<Optional. Source-stack-specific (framework-specific) coupling to unwind, anti-patterns, framework-bound vs. portable logic, and anything that will bite when rebuilding in the target stack. Skip if none.>

## Gaps

<Optional. Anything not fully captured here that may require re-opening the source. Skip if complete.>
```

## Principles

- **One reference per folder** — never merge; save each separately with a stable slug so re-audits overwrite, not duplicate.
- **Recall over re-scan** — re-reading source is the exception, signalled by the `Gaps` section.
- **Portable substance first** — favor business logic and abstractions that survive a framework change over framework-specific detail.
- **Instruction is the filter** — out-of-scope content stays out.
- **Don't invent** — record only what is in the source; flag ambiguity in `Gaps`.
