# init

Scaffold the spec directory + `.meta.yaml` ledger — the entry point and sole writer of the spec
dir. Only the `feature` workflow; its phase list is embedded below.

**Writes** `.specflow/specs/<name>/` + `.meta.yaml` · **Reads** feature name + one-line
description from the caller · optional design source links (UI work).

**Steps**
1. **Design links** — UI work → ask for design source links, record as `design_links` (else absent).
2. **Scaffold** — create `.specflow/specs/<name>/`.
3. **Ledger** — write `.meta.yaml` per the template: every phase `pending`, `current_phase: preflight`.
4. **Report** what was created.

```yaml
name: <name>
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
design_links: []      # only when captured
```

**Exit** — `.meta.yaml` exists exactly per the template, all phases `pending`.
