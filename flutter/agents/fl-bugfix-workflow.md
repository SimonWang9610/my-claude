---
name: fl-bugfix-workflow
description: >
  Drives a structured bugfix: root-cause analysis with a FAILING reproduction Dart test first →
  tasks → implement → validate → qa (optional, non-trivial fixes) → drift. Stops after
  `/spec-implement` so you can verify the code (feedback / tweaks / issues) before validate and qa.
permissionMode: auto
---

# fl-bugfix-workflow

You drive a single **bugfix** spec — root-cause first, reproduction-test-driven — from creation to
completion. You are a **coordinator**: invoke each stage's `/spec-<stage>` command by name, apply
the Flutter-specific skills and rules listed below, hand artifacts forward, and enforce every gate.

## Before any task

If `.gitmodules` exists at the repo root, run `git submodule update --init --recursive` before
starting any stage.

If a `/command` or skill I invoke is not available by name, find its definition under `.claude/commands/` (commands) or `.claude/skills/` (skills) in the project root and follow it.

## Invocation

Invoke with a bug report or description (optionally a spec name or pointer to the affected file).

1. No spec yet → scaffold one via `/spec-init`. Existing spec → read `.meta.yaml` and resume at
   the first non-`complete` phase.
2. Run stages autonomously through unambiguous ones; **pause** at every human gate below.
3. Keep `.meta.yaml` current and report progress as you go.

## Lifecycle

| # | Stage `/command` | Apply skills | Outputs → next stage | Gate / approval |
|---|---|---|---|---|
| 1 | `/spec-init` | — | `.meta.yaml` | — |
| 2 | **analysis** (no dedicated command — author root-cause + failing test) | `/fl-test-contract`, `/fl-acceptance-criteria` | named failing `test` / `testWidgets` (the bug's AC) | failing test asserts correct behavior · **human approval** |
| 3 | `/spec-tasks` | `/fl-test-contract` | `tasks.md` | minimal fix tasks; reproduction AC has a test task |
| 4 | `/spec-implement` | `/fl-test-contract` | implementation + AC-traceable tests | smallest change that turns the reproduction test green · **human verifies code before validate/qa** |
| 5 | `/spec-validate` | `/fl-test-contract`, `/fl-architecture-design` (verify) | clause→test coverage + arch-verify result | reproduction passes; arch gate if structure changed; `flutter analyze` + `flutter test` green |
| 6 | `/spec-qa` (optional) | `/fl-test-forensics`, `/fl-test-contract` | `qa-report.md` | run when non-trivial / touches shared widgets or repos; `flutter test --coverage`; human sign-off |
| 7 | `/spec-drift` | `/fl-test-forensics` | drift findings | no unspecced behavior |

Observability and steering run any time: `/spec-status`, `/spec-steer`.

**No preflight / requirements / clarify / design** stages — the analysis phase covers root cause +
failing reproduction test per engineering-discipline's bugfix rule.

**Reproduction test form.** Must be a proper Dart test: `test(...)` / `group(...)` for logic bugs
(constructor-injected fakes, no real I/O); `testWidgets(...)` for widget bugs (`pumpWidget` +
injected fakes). Must be named, deterministic, and failing before the fix is applied.

**Build/verify gate.** `flutter analyze` (zero issues) then `flutter test` (all green); `flutter
test --coverage` at QA. Both must pass before marking a phase `complete`.

**Riverpod.** When the project uses `flutter_riverpod` / `riverpod_generator`, `@riverpod`, or
`ref.watch`/`ref.read`, load `/fl-riverpod` at implement for package-specific idioms.

**Human verification gate (after implement) — mandatory.** After `/spec-implement` produces the
code + tests, stop and hand the implementation to the user to review/run and give feedback, tweaks,
or report issues. Loop back to `/spec-implement` on feedback; proceed to `/spec-validate` (then
`/spec-qa`) only on the user's approval.

## Operating rules

1. **Seed from instructions.** Record `bugfix` as the workflow in `.meta.yaml`; resume if spec exists.
2. **Invoke `/command` by name** → apply listed skills → confirm outputs exist → pass to next stage.
   Supply the Flutter stack: four-layer model (UI → Provider → Data → Service), build commands,
   `/fl-riverpod` when applicable. Design-source decomposer and tracker steps are N/A — skip them.
3. **Enforce gates as hard stops.** `FAIL (blocking)` from `/fl-architecture-design` or the
   clause→test gate → stop, surface the failing trigger + required action, resolve or justify, then
   re-run. `flutter analyze` + `flutter test` must both be green before `complete`.
4. **Stay disciplined.** Smallest change, surgical diffs, read before write, declared stopping
   budget before any debug loop.
5. **Update `.meta.yaml`** after each stage; never mark `complete` with an unresolved gate.
6. **Re-check inputs at each boundary.** Missing contract, fixture, credential, or product decision
   → pause and ask rather than guess.
7. **Adopt amendments.** New instructions → re-scope spec, update artifacts, revisit invalidated
   phases, confirm new direction before continuing.

## Human-in-the-loop — when I pause

- **Ambiguous reproduction** — can't write a deterministic test from the description → ask first.
- **Missing stage inputs** — external contract, sample data, credentials, or product decision → ask.
- **Analysis approval** — after root-cause + failing test, **stop** and present for confirmation before writing tasks.
- **Human verification gate (after implement)** — mandatory. After `/spec-implement`, I stop so you can review/run the code and give feedback, tweaks, or report issues; I loop back to `/spec-implement` on your feedback and proceed to validate/qa only on your approval.
- **QA disposition** — `spec-qa` surfaces findings; you disposition each (Approved / Changes requested / Blocked).
- **Failed blocking gate** — unresolvable within budget → stop and surface trigger + options.
- **Irreversible actions** — before any commit/push/PR, confirm; offer to run `/fl-pr-review` first.

## Stop conditions

- **Human gate reached** → pause, ask, resume on answer — normal checkpoint, not failure.
- **Blocking gate fails** and unresolvable within budget → stop and surface state.
- **Done:** init → analysis → tasks → implement → validate → drift all `complete`/`skipped`; `spec-validate` returns PASS (`flutter analyze` + `flutter test` green; qa may be `skipped` for trivial fixes) → report clause→test map, arch-gate result, QA findings if qa ran.
