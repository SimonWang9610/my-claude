# specflow — unified spec-driven development workflow

`specflow` is a stack-neutral, spec-driven development workflow that ensures a spec marked "Completed"
provably means *the stated behavior is verified in an independently testable unit*. It binds every
acceptance criterion to a named, outcome-asserting test **at authoring time** and gates the
architecture **at phase exit**.

## Command set — 12 generic stages

The `specflow/commands/` directory holds 12 stack-neutral stage commands, invoked as `/spec-*`:

| Command | Stage | Goal | Inputs |
|---|---|---|---|
| `/spec-init` | 1 · init | Scaffold `.meta.yaml`; capture Figma links if UI change | Story / ticket, optional Figma URL |
| `/spec-preflight` | 2 · preflight | Reuse scan; shared-component impact; optional Figma decompose | `.meta.yaml` |
| `/spec-requirements` | 3 · requirements | Stable AC IDs + observable Given/When/Then phrasing | Story, preflight output |
| `/spec-clarify` | 4 · clarify | Surface untestable or ambiguous ACs | Acceptance criteria |
| `/spec-design` | 5 · design (gate) | Draft `design.md` + `contracts/`; architecture gate PASS or justification | ACs, preflight output |
| `/spec-tasks` | 6 · tasks | One test task per AC + edge-case tasks | ACs, design |
| `/spec-implement` | 7 · implement (gate) | WorkAgent/TestAgent phases; "completed" ⇒ AC-traceable test green | Tasks |
| `/spec-validate` | 8 · validate (gate) | Clause→test coverage + architecture gate | impl output |
| `/spec-qa` | 9 · qa | QA audit → `qa-report.md` → human sign-off | validated branch |
| `/spec-drift` | 10 · drift | Shared-component drift + no unspecced behavior | `qa-report.md` |
| `/spec-status` | any | Observability: current phase, open gates, blockers | `.meta.yaml`, in-flight docs |
| `/spec-steer` | any | Steering: replan, re-scope, or unblock a stalled phase | Current state |

Commands are **stack-neutral by role**: they name capability roles (e.g. "run the architecture-design
skill", "run the QA-report skill"), not concrete skill names. The driver agent binds each role to the
concrete skill it owns. This means the same command set drives both the React and Flutter stacks by
rebinding the role→skill mapping in the agent layer.

Gates are the phases marked "(gate)" above — the spec cannot advance past them until the gate
condition is met (PASS or an accepted justification).

## Stack profiles — `react/` and `flutter/`

Two sibling profile directories live alongside `specflow/`:

```
react/
  agents/   oac-{feature,brownfield,bugfix,quickfix}-workflow.md  ← the binding layer
  skills/   oac-acceptance-criteria  oac-architecture-design
            oac-figma-decompose  oac-journey-tests  oac-qa-report
            oac-test-contract  oac-test-forensics
  rules/    architecture-principles.md  test-quality.md  (+ engineering-discipline/preferences symlinks)
  commands/ _oac-jira-status-automation.md  ← per-project adaptation point

flutter/
  agents/   fl-{feature,brownfield,bugfix,quickfix}-workflow.md   ← the binding layer
  skills/   fl-acceptance-criteria  fl-architecture-design
            fl-pr-review  fl-riverpod  fl-test-contract  fl-test-forensics
  rules/    architecture-principles.md  test-quality.md  (+ engineering-discipline/preferences symlinks)
```

Each profile's `agents/` directory is **the sole binding layer**: driver agents load the profile's
skills, apply its rules, supply stack-specific context, and can proxy any stage command to the
appropriate skill. Each stage in the driver's lifecycle table names the skills to apply and the
output spec artifacts that feed the next stage (the artifact chain). No command or skill references
anything outside the profile by name — stack specifics live exclusively in the agent layer.

### React profile (`react/`)

Stack: **React 19 + Vite + TypeScript + Zustand + TanStack Query + MUI + Vitest**.

Agents bind roles to `oac-*` skills. The `oac-architecture-design` skill owns the full rule corpus
(23 architecture rules + 22 performance rules) and runs the verifiable-unit gate at phase exit
(design-time authoring + verification in one skill). The per-project adaptation seam is
`react/commands/_oac-jira-status-automation.md` (rewrite for your issue tracker, or delete).

### Flutter profile (`flutter/`)

Stack: **Flutter/Dart**, state-management-package agnostic. The core rules cover four-layer
architecture, SSOT, sealed async, and disposal. Package-specific idioms live in the `fl-riverpod`
skill (or an analogous `fl-bloc` / `fl-provider` skill); the agent loads the package skill when it
detects the package in `pubspec.yaml`. The Flutter profile has no `commands/` subdir — it uses the
shared `specflow/commands/` set.

## The agent-as-sole-binding-layer model

```
specflow/commands/   ── PROCESS: 12 stack-neutral stage commands (role-based, no skill names)
         │ invoked by
profiles/agents/     ── BINDING LAYER: one driver per workflow variant; loads skills, applies rules,
         │               supplies stack context; can proxy a stage to its owned skill
profiles/skills/     ── IMPLEMENTATION: self-contained problem-solvers with references/ + examples
profiles/rules/      ── ALWAYS-ON: short, path-gated topic files (no code listings)
```

The commands name nothing but roles. The driver agent does the binding. This keeps the 12 commands
fully reusable across stacks, and localises all stack knowledge to the agent + skill layer.

## How to drive a spec

**Recommended:** invoke the matching driver agent for your stack and change type. The agent drives all
phases in order, enforces gates, and loads the right skills.

| Change type | React agent | Flutter agent |
|---|---|---|
| New feature / port | `oac-feature-workflow` | `fl-feature-workflow` |
| In-place change to existing feature | `oac-brownfield-workflow` | `fl-brownfield-workflow` |
| Bug fix | `oac-bugfix-workflow` | `fl-bugfix-workflow` |
| Small self-contained change | `oac-quickfix-workflow` | `fl-quickfix-workflow` |

**Ad-hoc:** run `/spec-*` stage commands directly. The commands are stack-neutral; you supply the
stack context manually (or the ambient rules + skills provide it).

## Shared stack-agnostic rules

`engineering-discipline.md` and `preferences.md` are the single source of truth for cross-stack
coding discipline and delegation preferences. They live as **real files** in the repo's top-level
`/rules/` directory. Both profile `rules/` directories hold symlinks back to these files. Do not
edit or duplicate them inside a profile.
