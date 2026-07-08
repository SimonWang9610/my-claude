---
name: pick-flutter-workflow
description: >
  Binds an sflow workflow template (feature | brownfield | bugfix | quickfix) to the Flutter
  profile: resolves each phase's capability roles to concrete fl-* skills, resolves conditional
  roles against the actual spec/project (design links, legacy port, Riverpod in pubspec.yaml),
  attaches the Flutter stage notes, and returns the bound workflow the driver agent orchestrates
  from. Usage: /pick-flutter-workflow <variant> [spec-dir]. Run BEFORE /sf-init when starting a
  spec — it returns the bound workflow for /sf-init to write; pass a spec-dir only to RE-BIND an
  existing spec whose workflow.yaml still carries unbound roles.
---

# pick-flutter-workflow

Convert a workflow template into the **bound** phase machine for a Flutter spec. Pure binder — it
scaffolds nothing; `/sf-init` owns the spec dir. Two modes:

- **Fresh bind** (default — no spec dir exists yet): `/pick-flutter-workflow <variant>` — return
  the bound workflow to the caller, who passes it to `/sf-init`.
- **Re-bind**: `/pick-flutter-workflow <variant> <spec-dir>` — the spec's `workflow.yaml` exists
  but still carries unbound `roles:`; rewrite it in place.

`<variant>` is `feature` | `brownfield` | `bugfix` | `quickfix`.

## Procedure

### Step 1 — Locate the template

- **Re-bind mode** — the template is the existing `<spec-dir>/workflow.yaml`.
- **Fresh mode** — the bundle's template for `<variant>`, located **relative to this skill**:
  from this skill's own directory (`skills/pick-flutter-workflow/`, resolve its real path first
  since it is symlinked into `.claude/`), the template is `../../sflow/workflows/<variant>.yaml`.
  Never read templates from the project's own `.specflow/` tree — that belongs to the project's
  tooling.

Never invent phases: bind exactly what the template declares.

### Step 2 — Resolve conditional roles (`"role?"`) and the state-management package

Check each trigger against the actual spec/project and **decide now** where possible:

| Conditional role | Keep when | Drop when |
|---|---|---|
| `design-decompose?` | the caller reports design links (or `.meta.yaml` records them, when re-binding); unbound — see Step 3 | no design links |
| `resource-scan?` | legacy/cross-stack port, or a large existing subsystem to audit | greenfield, small scope |
| `journey-tests?` / `tracker-sync?` / `tracker-align?` | the project supplies an equivalent skill/playbook | otherwise drop (unbound in this profile) |
| `architecture-design?` (quickfix validate) | keep with its condition — decidable only after implement | — |

**Riverpod check:** when `pubspec.yaml` lists `riverpod` / `flutter_riverpod` /
`riverpod_generator`, append `/fl-riverpod` to the `architecture-design` and `implementation`
bindings below.

### Step 3 — Bind roles to skills

| Role | Flutter binding |
|---|---|
| acceptance-criteria | `/fl-acceptance-criteria` |
| architecture-design | `/fl-architecture-design` (+ `/fl-riverpod` per Step 2) |
| task-design | `/fl-task-design` |
| implementation | `/fl-implementation` (+ `/fl-riverpod` per Step 2) |
| test-contract | `/fl-test-contract` |
| qa-report | *unbound* — the driver assembles `qa-report.md` per the `/sf-qa` steps |
| test-forensics | `/fl-test-forensics` |
| design-decompose | *unbound* — document `design_links` into `references/design-units.md` manually |
| resource-scan | `/scan-resource` — parallel subagents, one per legacy folder |
| journey-tests / tracker-sync / tracker-align | *unbound* — drop unless the project supplies one |

### Step 4 — Attach the Flutter stage notes

Add a `notes:` line to these phases (verbatim):

- **preflight** (brownfield): `impact analysis — map the shared-widget adoption table (ADOPTED units + external importers); never plan a modification to an adopted shared widget without explicit approval`
- **implement**: `run only the changed tests + flutter analyze on changed files, never the full suite; every "completed" item has an AC-traceable Dart test that passes; adopted shared widgets are read-only (copy, never modify); stop for the human code check before validate/qa`
- **qa**: `run flutter test --coverage exactly once — a single, non-parallel run, no extra passes; plus forensics + contract audits`
- **validate**: `static only, runs no tests or build; blocking: modified adopted shared widget, PR closing keyword, incomplete required phase`

### Step 5 — Emit the bound workflow

Rewrite each phase's `roles:` as `skills:` (bound entries; an unbound role becomes a
parenthesized instruction; an undecided conditional keeps its condition), keep every other field
(`id`, `command`, `inputs`, `outputs`, `gate`, `required`, `exit`, top-level `escalate`)
untouched, and add `bound: flutter` at the top level. **Fresh mode**: return the full bound YAML
to the caller — do not write any file. **Re-bind mode**: overwrite `<spec-dir>/workflow.yaml`.
Example phase after binding:

```yaml
  - id: qa
    command: /sf-qa
    skills: ["/fl-test-forensics", "/fl-test-contract",
             "(qa-report unbound — assemble qa-report.md per the /sf-qa steps)"]
    inputs: [requirements.md, design.md, tasks.md]
    outputs: [qa-report.md]
    gate: human
    required: true
    exit: enters only after validate PASS; build + suite green; findings dispositioned by the reviewer (sign-off)
    notes: run flutter test --coverage exactly once — a single, non-parallel run, no extra passes; plus forensics + contract audits
```

### Step 6 — Report

Return to the caller: the bound workflow (fresh mode) or the rewritten file path (re-bind mode),
the Riverpod decision, which conditional roles were kept/dropped and why, and any role left
undecided.
