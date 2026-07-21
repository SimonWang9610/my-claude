# my-claude — a spec-driven-development bundle for Claude Code

A reusable [Claude Code](https://claude.com/claude-code) bundle that drives a structured,
spec-driven workflow — `preflight → requirements → design → tasks → implement → validate → qa` —
for **React/TypeScript** and **Flutter/Dart** projects.

It is built on one idea: **skills carry the judgment, agents carry the execution, commands
carry the process, scripts install it.** A skill is a self-contained procedure Claude loads on
demand; some skills have a **companion agent** — an expert with a narrow tool fence and the
skill preloaded — that runs the skill under separation-of-duties or fresh-eyes constraints the
skill alone can't enforce. Below, each skill is described by its **purpose**, the **why** behind
it, and the **pain** it removes; its companion agent (if any) follows.

---

## Understand code you didn't write

### `audit-code-flows` · companion **code-auditor-agent**

- **Purpose** — reverse-engineers existing/legacy code into a queryable **atlas** (a flow index
  over per-flow GIVEN/WHEN/THEN/HOW notes), then answers questions from it and heals itself on a
  miss by reading exactly the missing spot.
- **Why** — understanding is expensive work worth banking: a one-shot exploration evaporates in
  an agent's context, while an atlas persists, is queryable, and *deepens* instead of being
  re-derived every phase.
- **Pain** — re-reading the same unfamiliar code each phase; blast-radius guesswork ("what else
  writes this fact?"); audits that read too deep because nothing bounds them.
- **code-auditor-agent** — runs a bounded single-context audit and writes only its own
  `atlas/`. Given a curated **external atlas** (read-only, e.g. a shared one outside the spec),
  it **distills** it — cherry-picking the purpose-relevant flows into its own `atlas/references/`
  as a map — but still reads source and writes its own purpose-framed notes, the atlas it
  queries. Keeps a **personal memory** of each codebase's conventions for a warm start next time.

---

## The contract flow — spec to shipped code

### `build-requirements`

- **Purpose** — turns a request or idea into `requirements.md`: user stories with stable AC/NFR
  ids phrased as observable Given/When/Then outcomes.
- **Why** — a request is evidence of a problem, not the spec; recovering the real problem and
  burning down ambiguity up front is a clarify phase that never has to run.
- **Pain** — vague scope; solution-shaped asks that hide the real need; ambiguity discovered late
  during implementation.

### `design-react-contracts`

- **Purpose** — turns ACs into React **contracts** (per-unit API, data flow, state) plus the
  architecture wiring them, as `design.md` + `contracts/`.
- **Why** — deciding unit boundaries and where a fact lives *before* code is written is far
  cheaper than discovering them mid-implementation; an implementer should build without guessing.
- **Pain** — "where does this state belong?"; re-litigating boundaries while coding; designs an
  implementer can't act on.

### `plan-react-contracts`

- **Purpose** — projects an approved design into `tasks.md`: dependency-ordered tasks in 2–4
  waves, each pre-split into a test batch and an impl batch.
- **Why** — assignments decided while the whole plan is in view parallelize cleanly; deciding
  them ad hoc during implementation thrashes.
- **Pain** — unclear task order; serial work that could have run in parallel; re-deriving batches
  mid-flight.

### `test-react-contracts` · companion **react-test-agent**

- **Purpose** — authors tests that prove contracts (Vitest · RTL · MSW · Playwright), each named
  for the AC it verifies.
- **Why** — a test written first, red, by someone other than the implementer proves behavior
  instead of ratifying whatever the code happens to do.
- **Pain** — tests that pass against a stub; coverage that doesn't map to ACs; author marking
  their own homework.
- **react-test-agent** — a test-files-only tool fence (it cannot touch source), so red-first is
  structural, not a promise.

### `implement-react-contracts` · companion **react-impl-agent**

- **Purpose** — writes React/TS source against a contract until the batch's failing tests pass,
  raising DESIGN GAPs instead of silently deviating.
- **Why** — the contract fixes the *what*; level-specific rules for using/building/optimizing
  hooks, components, stores, and services keep the *how* correct.
- **Pain** — silent deviation from the design; stale-closure, effect-loop, and needless-re-render
  bugs; reinventing a unit that already exists.
- **react-impl-agent** — a source-only fence (never edits a test) + a **personal memory** of
  each codebase's good practices, anti-patterns, and pitfalls (judged against the skill's rules)
  so quality compounds across waves.

### `check-react-implementation` · companion **react-checker-agent**

- **Purpose** — a fresh-eyes conformance check of a diff on three axes — behavior/ACs,
  maintainability, performance & memory — returning severity-classified findings, never fixes.
- **Why** — the author is the worst judge of their own work; a checker given the artifacts but
  not the reasoning catches what the author rationalized away.
- **Pain** — bugs that "look correct"; self-review blind spots; findings quietly "fixed" instead
  of surfaced.
- **react-checker-agent** — a read-only tool fence (no Write/Edit), so "findings, never fixes" is
  unbreakable by construction.

### `review-react-changes`

- **Purpose** — reviews a PR/branch/diff on three axes (spec ↔ code honesty, behavior, quality)
  and returns severity findings + a block/pass merge verdict.
- **Why** — a merge decision belongs to a human informed by an evidence-backed verdict, not to
  the author's confidence.
- **Pain** — merges that drift from spec; unverified "fixed" claims; review notes with no clear
  gate.

---

## Supporting skills

### `decompose-figma`

- **Purpose** — turns a Figma screen into a component map (EXISTING / PARTIAL / NEW), extracting
  specs only for what's genuinely new.
- **Why** — most of a screen already exists in the codebase; dumping raw Figma JSON for
  everything wastes effort and buries the actual new work.
- **Pain** — rebuilding components that already exist; design handoffs that don't say what to
  actually build.

### `smart-delegation`

- **Purpose** — routes a piece of work to the cheapest execution that does it well: inline, a
  fork, or a subagent (bound or ad-hoc), and fixes what the spawn must carry back.
- **Why** — a subagent re-pays a cold start; fanning out blindly burns tokens, while keeping
  everything inline floods one context.
- **Pain** — token-wasteful over-delegation; context floods from noisy exploration; a reviewer
  seeing the reasoning that produced the work.

### `jira-ac-align`

- **Purpose** — a three-way reconcile of a JIRA ticket's AC against the spec and the shipped code,
  updating the ticket and posting one alignment comment.
- **Why** — tickets go stale the moment requirements shift mid-development, and a ticket that lies
  about what was built misleads everyone downstream.
- **Pain** — "the ticket doesn't match the code"; AC drift after mid-flight changes.

---

## Flutter

### `fl-pr-review`

- **Purpose** — reviews a Flutter/Dart PR against the architecture rules (P1–P8), Riverpod code-gen
  idioms, Dart 3 patterns, and test-quality rules → a rule-cited severity report.
- **Why** — architectural rules only hold if something checks them on every PR; humans miss them
  under delivery pressure.
- **Pain** — architecture erosion; Riverpod/Dart-3 anti-patterns; tests that don't actually
  assert. (Flutter rules live in `flutter/rules/`, dormant — not linked by default.)

---

## The drivers — orchestration

Two **driver agents** you launch to run a whole spec: `my-specflow-driver` (drives this bundle's
`/sf-*` commands) and `oac-specflow-driver` (drives an external **specflow** project's `/spec-*`
commands). A driver is not tied to one skill — it binds them all.

- **Purpose** — drive one spec through its phases: run each phase's command + playbook, delegate
  heavy work to the worker agents, verify every output mechanically, and pause at human gates.
- **Why** — separating orchestration (decide, verify, record) from execution (skills + workers)
  keeps each simple; the driver holds no stack know-how and never does heavy work itself.
- **Pain** — half-run phases; advancing past an open gate; trusting a subagent's word instead of
  verifying; a whole process crammed into one unmaintainable prompt.

```sh
my-specflow-driver "add a logout button"                              # if aliases were installed
claude --agent my-specflow-driver --worktree "add a logout button"    # raw
```

Implement runs red→green per wave — spawn `react-test-agent` (RED) → spawn `react-impl-agent`
(green, test paths byte-unchanged) — then an optional `react-checker-agent` pass before the human
gate; the driver never advances past an open gate.

---

## How these are optimized — the mechanisms

Cross-cutting techniques the skills and agents share, developed to keep them cheap to run and
correct without heavy oversight.

**Efficiency — fewer tokens, less re-work**

- **Queryable, self-healing atlas** — `audit-code-flows` banks understanding once; later phases
  *query* it instead of re-scanning, and a query heals itself on a miss (a bounded reveal budget)
  rather than dead-ending. Understanding compounds instead of evaporating each phase.
- **Bounded exploration** — the audit walks the definition graph on-purpose, one hop at a time,
  capping depth *during* the walk (Locate → Walk → Organize) so the off-purpose graph is never
  built and a read can't run away.
- **grep to narrow, ast-grep to sharpen** — fast text search finds candidates; structural search
  is reserved for where text is ambiguous — complementary, not either/or, with a grep-only path
  when ast-grep is absent.
- **Route to the cheapest execution** — `smart-delegation` picks inline / fork / subagent and the
  model + effort by task complexity, batching work to avoid re-paying a subagent's cold start.
- **Progressive disclosure + terse prompts** — SKILL.md stays lean; heavy procedure lives in
  lazy-loaded `references/` (opened only in the mode that needs it); inter-agent prompts carry
  four essentials — where · what · materials · done-when. Skills load on every trigger, so every
  line earns its cost.
- **Declared iteration budgets** — every loop (a query's reveal chain, a red→green fix) names its
  stopping point up front; spent → stop and surface what was tried. No blind loops.

**Correctness — by construction, not by instruction**

- **Narrow tool fences** — the test agent writes tests only, the impl agent source only, the
  checker reads only. Red-first, author ≠ implementer, and findings-never-fixes become
  *structural*, not a promise that can slip.
- **Judgment authors, search verifies** — mechanical facts (call edges, anchors, couplings) come
  from tools; judgment fills only what tools can't (a flow's GIVEN/WHEN/THEN/HOW), so what's
  verifiable is verified rather than re-argued.
- **Fixed-shape artifacts** — every output lands in a declared template, so a driver verifies it
  by grep / diff / count, never by re-judging or trusting a subagent's word.
- **Memory as hints, not truth** — the auditor remembers where things live; the impl agent
  remembers good/bad/pitfall patterns judged against the skill's rules. Memory biases where you
  look or how you build — it never prunes a search or overrides the contract and tests.
- **Thin-binding agents** — an agent body is role + procedure + fence + return contract; the stack
  know-how is preloaded from its `skills:`, never restated, so bindings stay steady and the agent
  stays small.
- **Description-as-router** — each skill's description states capability + when-to-use +
  not-for (→ alternative) + output, so an orchestrator routes to the right skill without opening
  its body.

---

## Installing — the scripts

The bundle is flat: `skills/ agents/ rules/` are real directories and the `/sf-*` command files
live in `sflow/commands/`. Two script pairs relative-symlink them, per entry, into a destination
`.claude/` — kept separate so the commands never install by accident:

| Script pair | Source → Destination |
|-------------|----------------------|
| `link.sh` / `unlink.sh` | `skills/* agents/* rules/*` → `<dest>/.claude/{skills,agents,rules}/` |
| `link-commands.sh` / `unlink-commands.sh` | `sflow/commands/*` → `<dest>/.claude/commands/` |

The `/sf-*` commands get their **own** pair because, installed globally, they shadow a project's
own `/spec-*` set — so link them only where an sflow workflow is actually used. Links are relative;
an existing correct link is skipped; a foreign real file or an outside-pointing link is never
clobbered; re-running is safe. `unlink*` removes only symlinks that resolve back into this repo.

```sh
./link.sh --global                        # skills+agents+rules → ~/.claude
./link.sh --project ../myapp              # → ../myapp/.claude
./link-commands.sh --project ../myapp     # add the /sf-* commands to that project only
./unlink.sh --project ../myapp            # remove skills+agents+rules
./unlink.sh --global --aliases            # remove links + the managed rc block
```

`link.sh --aliases` also writes a **shell function per driver** into your rc file, so you can
launch a driver by name (`my-specflow-driver "..."`); `--no-aliases` skips the prompt.

> **Windows:** in-repo symlinks need `core.symlinks=true` (enable Developer Mode, then
> `git checkout -- .`). **Submodules** are synced by the driver's Setup on session start.

---

## Layout & editing

Edit `skills/ agents/ rules/` and `sflow/commands/` directly — links are per-entry, so a new
skill/agent/rule appears after one `./link.sh` (a new command after one `./link-commands.sh`);
removals need the matching `./unlink*.sh`.

```
my-claude/
├── skills/    the skills above (real dirs)
├── agents/    2 drivers + 4 companion workers (real files)
├── rules/     shared working-discipline rules — preferences.md
├── sflow/     /sf-* stage commands (sflow/commands/) + the full workflow README
├── flutter/   Flutter profile — rules/ (dormant, not linked by default)
└── *.sh       link/unlink installers (bundle + commands, separate pairs)
```

For the full phase lifecycle, the `.meta.yaml` ledger, and human gates, see
**[sflow/README.md](sflow/README.md)**.
