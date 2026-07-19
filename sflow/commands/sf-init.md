---
description: Scaffold a new spec directory and .meta.yaml phase ledger (feature workflow).
---
# sf:init

Scaffold `.specflow/specs/<feature-name>/` + `.meta.yaml` — the entry point; sole writer of
the spec dir. Only the `feature` workflow is supported; its phase list is embedded below.
Inputs: feature name + one-line description from the caller; optional design source links
for UI work; steering `.specflow/steering/*` as context.

**Steps.**

1. UI work → ask for design source links, record as `design_links` (absent otherwise).
2. Create `.specflow/specs/<feature-name>/`.
3. Write `.meta.yaml` exactly per the template below — every phase `pending`,
   `current_phase: preflight`.
4. Report what was created.

**`.meta.yaml` template** — `phase_status` carries status only. Statuses:
`pending | in_progress | completed | skipped | failed`.

```yaml
name: <feature-name>
workflow: feature
created_at: <ISO 8601>
updated_at: <ISO 8601>
current_phase: preflight
phase_status:
  preflight: pending
  requirements: pending
  clarify: pending
  design: pending
  tasks: pending
  implement: pending
  spec-qa: pending
design_links: []         # only when captured
checksums: {}            # reserved for project tooling
```

**Exit.** `.meta.yaml` exists exactly per the template, all phases `pending`.
