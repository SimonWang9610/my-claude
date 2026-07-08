# sflow — unified spec-driven development workflow

`sflow` (formerly `specflow` — renamed so the bundle never collides with a project's own
`specflow/` folder or `/spec-*` command set) is a stack-neutral, spec-driven development workflow
that ensures a spec marked "Completed" provably means *the stated behavior is verified in an
independently testable unit*. It binds every acceptance criterion to a named, outcome-asserting
test **at authoring time** and gates the architecture **at phase exit**.

## Three stack-neutral layers

```
sflow/workflows/  ── PHASE MACHINES: one YAML per workflow variant — phase order, per-phase
         │              command, capability roles, inputs/outputs, gate (human/auto), required flag
         │              declared by
sflow/commands/   ── PROCESS: 12 stack-neutral /sf-* commands (9 phases + scaffold + 2 utils;
         │              no skill names)
         │ started by
skills/sf-workflow-startup ── STARTUP (shared, repo root): one call (worktree → seed → resume? → bind → init)
         │              that stands up or resumes a spec and reports it drive-ready
         │ bound by
skills/pick-<tech>-workflow ── BINDING SKILLS (repo root, beside the templates): convert a
         │              template's roles into concrete profile skills + stage notes → the
         │              bound workflow.yaml
         │ driven by
profiles/agents/     ── ORCHESTRATORS: one driver per workflow variant; obtains the bound
         │              workflow.yaml, drives its phases, enforces gates, delegates to subagents
profiles/skills/     ── IMPLEMENTATION: self-contained problem-solvers with references/ + examples
profiles/rules/      ── ALWAYS-ON: short, path-gated topic files (no code listings)
```

**Domain skills and rules know nothing about sflow.** No domain skill or rule names a phase, an
`/sf-*` command, or the spec dir — each is a standalone problem-solver usable outside the workflow;
anything one needs (spec dir, artifact paths, output dir) is passed in by the caller. The single
deliberate exception is each profile's **workflow-binding skill** (`pick-react-workflow` /
`pick-flutter-workflow`) — it *is* the binding layer: it owns the role→skill map and the stack
stage notes, and emits the bound `workflow.yaml` the driver orchestrates from.

## Workflows — the canonical phase machines

`sflow/workflows/` holds one YAML per workflow variant: `feature`, `brownfield`, `bugfix`,
`quickfix`. Each declares its `phases` — `id`, `command` (the `/sf-*` stage, absent for
driver-led phases like bugfix `analysis` / quickfix `describe`), `roles` (capability roles the
driver binds to skills; a trailing `?` marks a conditional role), `inputs`/`outputs`, `gate`
(`human` or `auto`), `required`, and a one-line `exit` condition. `bugfix` and `quickfix` also
carry an `escalate` rule.

Starting a spec is **one call**: `/sf-workflow-startup <tech> <variant>` performs the worktree
check, collects the seed, detects resume, then runs **bind → init**: it invokes the profile's
binding skill
(`/pick-react-workflow <variant>` or `/pick-flutter-workflow <variant>`), a pure binder that
resolves the template's `roles` into concrete `skills:` (deciding conditional roles against the
actual project — design links, legacy port, Riverpod in `pubspec.yaml`, tracker presence) and
attaches per-phase stage `notes:`, then hands the bound workflow to `/sf-init`, the **sole
writer** of the spec dir, which materializes it as `.specflow/specs/<name>/workflow.yaml` alongside
`.meta.yaml`. (Ad-hoc, `/sf-init` copies the raw template instead; the binder can later re-bind an
existing spec's `workflow.yaml` in place. Templates are never linked into
`.claude/` and are read only from the bundle's `sflow/workflows/` — never from the project's own
`.specflow/` tree, which belongs to the project's tooling.) Every later command and the driver
read that snapshot — never the bundle path — so a spec is self-contained and resumable.

## Command set

The `sflow/commands/` directory holds 12 stack-neutral `/sf-*` commands — 9 numbered phases plus the `init` scaffold and the `status`/`steering` utilities
(the `sf-` prefix keeps them distinct from any project-local `/spec-*` set):

| Command | Stage | Goal | Inputs |
|---|---|---|---|
| `/sf-init` | scaffold | Scaffold `.meta.yaml` + the `workflow.yaml` snapshot; capture design links if UI change (not a tracked phase — the scaffold step) | Story / ticket, optional design URL |
| `/sf-preflight` | 1 · preflight | Reuse scan; shared-unit impact; optional design decompose | `.meta.yaml` |
| `/sf-requirements` | 2 · requirements | Stable AC IDs + observable Given/When/Then phrasing | Story, preflight output |
| `/sf-clarify` | 3 · clarify | Surface untestable or ambiguous ACs | Acceptance criteria |
| `/sf-design` | 4 · design (gate) | Draft `design.md` + `contracts/`; architecture gate PASS or justification | ACs, preflight output |
| `/sf-tasks` | 5 · tasks | One test task per AC + edge-case tasks | ACs, design |
| `/sf-implement` | 6 · implement (gate) | WorkAgent/TestAgent phases; "completed" ⇒ AC-traceable test green | Tasks |
| `/sf-validate` | 7 · validate (gate) | Machine pre-gate: clause→test coverage + architecture gate | impl output |
| `/sf-qa` | 8 · qa | QA audit → `qa-report.md` → human sign-off (enters only after validate PASS) | validated branch |
| `/sf-drift` | 9 · drift | Shared-unit drift + no unspecced behavior | `qa-report.md` |
| `/sf-status` | any | Observability: current phase, open gates, blockers | `.meta.yaml`, in-flight docs |
| `/sf-steering` | any | Generate/update the project steering docs (product, structure, tech, conventions) | The target repo |

Commands are **stack-neutral by role**: they name capability roles (e.g. "run the
architecture-design skill"), not concrete skill names. The workflow YAML declares which roles a
phase uses; the profile's binding skill resolves each role to a concrete skill. The same command
set and YAMLs drive both the React and Flutter stacks by swapping the binding skill.

Gates are the phases marked "(gate)" above — the spec cannot advance past them until the gate
condition is met (PASS or an accepted justification). After `/sf-implement` every workflow stops
for a **human code check** before validate/qa. Validate (static, cheap) runs before qa (expensive, human-dispositioned): a spec that fails the machine gate never burns QA effort.

## Stack profiles — `react/` and `flutter/`

Two sibling profile directories live alongside `sflow/`:

```
react/
  agents/   oac-{feature,brownfield,bugfix,quickfix}-workflow.md  ← the orchestrators
  skills/   oac-acceptance-criteria  oac-architecture-design  oac-task-design  oac-implementation
            oac-figma-decompose  oac-journey-tests  oac-qa-report
            oac-test-contract  oac-test-forensics
  rules/    architecture-principles.md  test-quality.md  (+ engineering-discipline/preferences symlinks)
  commands/ _oac-jira-status-automation.md  ← per-project adaptation point (tracker-sync role)

flutter/
  agents/   fl-{feature,brownfield,bugfix,quickfix}-workflow.md   ← the orchestrators
  skills/   fl-acceptance-criteria  fl-architecture-design  fl-task-design  fl-implementation
            fl-pr-review  fl-riverpod  fl-test-contract  fl-test-forensics
  rules/    architecture-principles.md  test-quality.md  (+ engineering-discipline/preferences symlinks)
```

Responsibilities split cleanly in each profile: the **binding skill** (`pick-<stack>-workflow`)
owns the role→skill map and the stack stage notes and emits the bound `workflow.yaml`; the
**driver agent** is a pure orchestrator — it obtains the bound workflow, drives its phases,
enforces gates, runs the driver-led phases (bugfix `analysis`, quickfix `describe`), handles
variant behaviors (legacy port mode, escalation), and delegates phase work to subagents with
explicit context. No command or domain skill references anything outside the profile by name.

### React profile (`react/`)

Stack: **React 19 + Vite + TypeScript + Zustand + TanStack Query + MUI + Vitest**.

Agents bind roles to `oac-*` skills, split by altitude: `oac-architecture-design` owns the
architecture rules and runs the verifiable-unit gate (sf-design + sf-validate); `oac-task-design`
turns design + contracts into `tasks.md` (sf-tasks); `oac-implementation` owns the
performance/idiom rules for code inside a fixed contract (sf-implement). The per-project
adaptation seam is `react/commands/_oac-jira-status-automation.md` — the `tracker-sync?` role
(rewrite for your issue tracker, or delete).

### Flutter profile (`flutter/`)

Stack: **Flutter/Dart**, state-management-package agnostic. The core rules cover four-layer
architecture, SSOT, sealed async, and disposal. Package-specific idioms live in the `fl-riverpod`
skill (or an analogous `fl-bloc` / `fl-provider` skill); the agent loads the package skill when it
detects the package in `pubspec.yaml`. The Flutter profile has no tracker playbook — the
`tracker-sync?`/`tracker-align?` roles are unbound there.

## How to drive a spec

**Recommended:** invoke the matching driver agent for your stack and change type. The agent drives
all phases of the workflow YAML in order, enforces gates, and loads the right skills.

| Change type | Workflow YAML | React agent | Flutter agent |
|---|---|---|---|
| New feature / port | `feature.yaml` | `oac-feature-workflow` | `fl-feature-workflow` |
| In-place change to existing feature | `brownfield.yaml` | `oac-brownfield-workflow` | `fl-brownfield-workflow` |
| Bug fix | `bugfix.yaml` | `oac-bugfix-workflow` | `fl-bugfix-workflow` |
| Small self-contained change | `quickfix.yaml` | `oac-quickfix-workflow` | `fl-quickfix-workflow` |

**Ad-hoc:** run `/sf-*` stage commands directly. The commands are stack-neutral; you supply the
stack context manually (or the ambient rules + skills provide it).

## Keeping assets consistent — the editing rules

Apply these whenever an asset is added or changed; every conflict found so far violated one:

- **One producer per fact.** Phase order/gates live only in the workflow YAMLs; role→skill
  bindings only in the pickers; startup only in `sf-workflow-startup`; the spec dir is written
  only by `/sf-init` (re-bind excepted). Never restate another asset's fact — point at it.
- **Consumers name the producer's exact signal** — `bound:`, `complete`, `<spec-dir>`, `gate:
  human`. No synonyms (`completed`, "validated build").
- **Commands name roles; agents name no skills; domain skills and rules know nothing about
  sflow.** The pickers and `sf-workflow-startup` are the only assets allowed to name both sides.
- **Artifact requirements are per-workflow**, never a fixed list — the lighter workflows have
  `analysis.md`/`describe.md`, not `requirements.md`+`design.md`.
- **A field nothing reads is deleted**, not kept "for later".
- **Agents may restate a global rule** (engineering-discipline) for subagent copying, but copy it
  verbatim or reference it — never reword it.

## Shared stack-agnostic rules

`engineering-discipline.md` and `preferences.md` are the single source of truth for cross-stack
coding discipline and delegation preferences. They live as **real files** in the repo's top-level
`/rules/` directory. Both profile `rules/` directories hold symlinks back to these files. Do not
edit or duplicate them inside a profile.
