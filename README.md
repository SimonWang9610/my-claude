# my-claude — spec-driven-development plugins for Claude Code

## 1 · What is this

A [Claude Code](https://claude.com/claude-code) **plugin marketplace** carrying three
self-contained plugins. `my-react` drives a structured, spec-driven workflow —
`preflight → requirements → clarify → design → tasks → implement → spec-qa` — from a request
to shipped, evaluated code.

| Plugin | Contents | Status |
|--------|----------|--------|
| `my-react` | 9 React/TS contract skills + 1 driver agent + 6 worker agents + the evaluation framework | stable |
| `my-flutter` | 8 `fl-`derived skills + the Flutter rule files (read via `${CLAUDE_PLUGIN_ROOT}/rules/`) | ⚠️ **work in progress — incomplete** (no agents, no evaluation framework yet) |
| `my-workflow` | language- and framework-agnostic software workflow for Claude Code **and GitHub Copilot**, led by the `drive-spec` skill in your session, which brings in `spec-architect`, `spec-tester`, `spec-implementer` and `spec-reviewer` when a task warrants it and saves the spec artifacts under `specs/<task>/`; every other skill does one step and works alone — `rephrase`, `audit-truth`, `decide` (+ `scaffold-project-structure`, `design-component`, `analyze-ui-state`), `build`, `verify`, `critique`; adapts to how much you specify and uses the stack knowledge you have installed — see [plugins/my-workflow/README.md](plugins/my-workflow/README.md) (renamed from `my-spec`) | new |

It is built on one idea: **skills carry the judgment, agents carry the execution, the driver
agents carry the process, plugins package it.** A skill is a self-contained procedure Claude
loads on demand; some skills have a **companion agent** — an expert with a narrow tool fence and
the skill preloaded — that runs the skill under separation-of-duties or fresh-eyes constraints
the skill alone can't enforce. Everything a plugin ships is **namespaced**
(`/my-react:<skill>`, `my-react:<agent>`), so it never collides with your global or
project configuration.

## 2 · Install & update

`setup.py` installs any of this repo's plugins (`my-react`, `my-flutter`, `my-workflow`) for
Claude Code, GitHub Copilot, or both. Run it with no arguments and it asks which tools, then which
plugins; plugins already installed for the chosen tools are not offered again:

```bash
python3 setup.py
```

The same choices on the command line, plus uninstall and a status table:

```bash
python3 setup.py install --tools claude,copilot --plugins my-workflow,my-react
```

```bash
python3 setup.py uninstall --tools copilot --plugins my-react
```

```bash
python3 setup.py status
```

- **Claude Code** installs through the `claude plugin` CLI (marketplace install, then update). When the
  `claude` command is missing or does not work, for example with only the VS Code extension, or with
  `--link`, it symlinks
  `~/.claude/skills/<plugin>` to the plugin folder, which Claude Code loads as `<plugin>@skills-dir`.
  Extras: `--local` (this checkout as the marketplace), `--aliases`, `--metrics`.
- **GitHub Copilot** reads these Claude-format plugins directly (`.claude-plugin/plugin.json`,
  `skills/`, `agents/`, `hooks/hooks.json`). With a working `copilot` CLI, setup runs
  `copilot plugin marketplace add` and `copilot plugin install`; VS Code Copilot Chat picks up
  CLI-installed plugins. Without it, setup adds the plugin folders to VS Code's `chat.pluginLocations`
  and turns on `chat.plugins.enabled`, editing your user `settings.json` in place (comments kept, a
  `.my-claude.bak` backup written first), so `git pull` updates the plugins with no reinstall.
- **Portability rules** that keep one plugin folder valid for both tools: agents are named
  `<name>.agent.md` (Claude Code reads any `*.md`; the Copilot CLI documents `.agent.md`), skills and
  references link to sibling files with relative Markdown links rather than `${CLAUDE_PLUGIN_ROOT}`, and
  Claude-only agent fields (`skills:`, `memory`, `permissionMode`, `effort`, `color`) are ignored by
  Copilot, so an agent's body names the skills it uses. Skills are invoked as `/<plugin>:<skill>` in
  Claude Code and Copilot alike (VS Code prefixes plugin skills with the plugin name); a skill's own
  `name` field stays unprefixed, since Copilot refuses to load a prefixed one.
- `--update` re-offers already-installed plugins (to update them); `--copy` copies instead of
  symlinking. Files that are not this installer's are never overwritten, and each run removes dangling
  links into this repo left by older installers.

The installer is a small stdlib-only package: `setup.py` drives `scripts/claude.py`,
`scripts/copilot.py`, `scripts/extras.py` (rules, aliases, metrics, LSP check), `scripts/jsonc.py`
(comment-preserving VS Code settings edits), and `scripts/common.py` (paths, plugin discovery from the
marketplace manifest, safe symlinks, prompts).

Or manually, inside a `claude` session:

```
/plugin marketplace add SimonWang9610/my-claude
/plugin install my-react@my-claude
/plugin install my-flutter@my-claude     # optional, independent
/plugin install my-workflow@my-claude    # optional, independent
```

For one-off local testing without any install:

```bash
claude --plugin-dir ./plugins/my-react --plugin-dir ./plugins/my-flutter --plugin-dir ./plugins/my-workflow
```

### Updating to a new version

Plugin versions are pinned in each `.claude-plugin/plugin.json`; you receive updates when
that version bumps. To upgrade an installed plugin:

```bash
claude plugin marketplace update my-claude
```

```bash
claude plugin update my-react@my-claude
```

then restart Claude Code (or `/reload-plugins`) to apply. Local `--plugin-dir` checkouts
need no update step — edit and `/reload-plugins`. Breaking renames between versions are
listed in this README's migration notes; skill/agent names are the stable API, so a
version that renames them will always say so here.

Coding principles ship with `my-workflow` as
[`shared/principles.md`](plugins/my-workflow/shared/principles.md), which its build and decide skills
follow. The old user-level `rules/preferences.md` is merged into it and removed; setup clears a
leftover link.

### TypeScript language server

`my-react` registers a TypeScript LSP ([`plugins/my-react/.lsp.json`](plugins/my-react/.lsp.json)),
giving Claude exact go-to-definition, find-references, and type diagnostics pushed into
context after each edit — precision the skills' grep+glob navigation can't reach on its own.
The binaries are **not** bundled; `setup.py` warns when they're missing:

```bash
npm install -g typescript-language-server typescript
```

Without them the plugin still works — Claude Code lists the server in the `/plugin` Errors tab
and everything else loads. If another enabled plugin already claims `.ts`/`.tsx`, the first
server registered wins and this one stays idle; that is harmless when both point at the same
binary.

### Telemetry (optional)

[`metrics/`](metrics/README.md) is a local sink for Claude Code's OpenTelemetry output —
OTel Collector → Prometheus + Loki → Grafana — driven by one stdlib-only Python script:

```bash
python3 metrics/stack.py up && python3 metrics/stack.py verify
```

That starts the containers, points `~/.claude/settings.json` at them (backing it up first),
and imports the dashboard; `verify` proves metrics are actually arriving. Cost, tokens,
sessions, and edit accept/reject rates are readable without Grafana —
`stack.py summary --since 24h`, `stack.py query '<promql>'`, `stack.py search '<logql>'`.
Everything is configured from [`metrics/config.json`](metrics/config.json). Telemetry is
machine-level, so this lives in the repo rather than inside a plugin.

### Migrating from the symlink install (breaking change)

The `link.sh` / `unlink.sh` symlink installer is removed. To migrate:

1. Remove old links: delete the symlinks in `<dest>/.claude/{skills,agents,rules}` that point
   into this repo (the historical `unlink.sh` still works: `git show <pre-plugin-sha>:unlink.sh | bash -s -- --global`).
2. Remove the managed `# >>> my-claude workflow agents >>>` block from your shell rc if you
   installed aliases.
3. Install the plugins as above.
4. Rename invocations: `/requirements` → `/my-react:requirements`, driver agent
   → `my-react:driver`, `/review` → `/my-flutter:review`, etc.
   The `/sflow` phase skill and `my-specflow-driver` are removed — the lean driver embeds the
   phase playbooks.
5. `rules/preferences.md` is gone; its rules live in my-workflow's coding principles.

---

## 3 · Using the skills and agents individually

Every piece works standalone — invoke a skill in any session, or address an agent
directly. The quick map (my-react):

| I want to… | Invoke |
|------------|--------|
| understand unfamiliar/legacy code (build or query the atlas) | `/my-react:audit` · agent `my-react:auditor` |
| turn a request into a testable spec | `/my-react:requirements` |
| break a Figma screen into buildable components | `/my-react:figma` |
| design contracts for approved ACs | `/my-react:design` · agent `my-react:architect` |
| evaluate a design / a diff / a test suite | `/my-react:evaluate <mode>` · agent `my-react:evaluator` |
| turn an approved design into ordered tasks | `/my-react:plan` |
| author unit tests against contracts | `/my-react:test` · agent `my-react:tester` (E2E: agent `my-react:e2e`) |
| implement against contracts / fix a bug | `/my-react:implement` · agent `my-react:implementer` |
| review a PR before merge | `/my-react:review` |

Agents run via the Agent tool or `claude --agent my-react:<name>`; each carries its own
tool fence, preloaded skills, and report format — your prompt only needs where · what ·
materials · done-when.

Below, each skill is described by its **purpose**, the **why** behind it, and the **pain** it
removes; its companion agent (if any) follows.

---

### Understand code you did not write

### `audit` · companion **auditor**

- **Purpose** — reverse-engineers existing/legacy code into a queryable **atlas** (a flow index
  over per-flow GIVEN/WHEN/THEN/HOW notes), then answers questions from it and heals itself on a
  miss by reading exactly the missing spot.
- **Why** — understanding is expensive work worth banking: a one-shot exploration evaporates in
  an agent's context, while an atlas persists, is queryable, and *deepens* instead of being
  re-derived every phase.
- **Pain** — re-reading the same unfamiliar code each phase; blast-radius guesswork ("what else
  writes this fact?"); audits that read too deep because nothing bounds them.
- **auditor** — *initializes* the atlas as one bounded, single-context audit: **build**
  from source, and a fast **distill** of any curated external atlas (distill first, then build
  deepens from that map). Writes only its own `atlas/`; querying it afterwards is the skill's
  `query` mode, run inline by whoever needs an answer. Keeps a **personal memory** of each
  codebase's conventions for a warm start next time.

---

### The contract flow — spec to shipped code

### `requirements`

- **Purpose** — turns a request or idea into `requirements.md`: user stories with stable AC/NFR
  ids phrased as observable Given/When/Then outcomes.
- **Why** — a request is evidence of a problem, not the spec; recovering the real problem and
  burning down ambiguity up front is a clarify phase that never has to run.
- **Pain** — vague scope; solution-shaped asks that hide the real need; ambiguity discovered late
  during implementation.

### `design` · companion **architect**

- **Purpose** — turns ACs into React **contracts** (per-unit API, data flow, state) plus the
  architecture wiring them, as `design.md` + `contracts/`.
- **Why** — deciding unit boundaries and where a fact lives *before* code is written is far
  cheaper than discovering them mid-implementation; an implementer should build without guessing.
- **Pain** — "where does this state belong?"; re-litigating boundaries while coding; designs an
  implementer can't act on.
- **architect** — runs the design phase as one bounded, high-judgment audit: queries
  the atlas for existing-code facts, authors `design.md` + `contracts/` (+ a draft journey plan),
  and raises refactor proposals for the gate. Keeps a **personal memory** of each codebase's
  architecture — good practices to reuse and bad ones to steer around (general rules, not feature
  cases) — to make design tradeoffs faster, never to conform a sound design to existing shape.

### `plan`

- **Purpose** — projects an approved design into `tasks.md`: dependency-ordered tasks in 2–4
  waves, each pre-split into a test batch and an impl batch.
- **Why** — assignments decided while the whole plan is in view parallelize cleanly; deciding
  them ad hoc during implementation thrashes.
- **Pain** — unclear task order; serial work that could have run in parallel; re-deriving batches
  mid-flight.

### `test` · companions **tester** + **e2e**

- **Purpose** — authors unit tests that prove contracts (Vitest · RTL · MSW), each named for the
  AC it verifies. E2E journey tests are the e2e agent's own charter (its rules live in the agent).
- **Why** — a test written first, red, by someone other than the implementer proves behavior
  instead of ratifying whatever the code happens to do.
- **Pain** — tests that pass against a stub; coverage that doesn't map to ACs; author marking
  their own homework.
- **tester** — a test-files-only tool fence (it cannot touch source), so red-first is
  structural, not a promise; remembers each codebase's test-harness conventions and pitfalls
  (custom render wrapper, MSW helpers, flaky traps) so authoring starts warm.
- **e2e** — authors journey tests from the approved `qa-journey-plan.md` after
  implementation assembles the feature (one test per J-<n>, happy + forced-error, NEW|MODIFY
  dispositions); carries its own e2e rules — whole-app-slice harness, UI-only driving — and
  remembers each codebase's app-mount harness.

### `implement` · companion **implementer**

- **Purpose** — writes React/TS source against a contract until the batch's failing tests pass,
  raising DESIGN GAPs instead of silently deviating.
- **Why** — the contract fixes the *what*; level-specific rules for using/building/optimizing
  hooks, components, stores, and services keep the *how* correct.
- **Pain** — silent deviation from the design; stale-closure, effect-loop, and needless-re-render
  bugs; reinventing a unit that already exists.
- **implementer** — a source-only fence (never edits a test) + a **personal memory** of
  each codebase's good practices, anti-patterns, and pitfalls (judged against the skill's rules)
  so quality compounds across waves.

### `evaluate` · companion **evaluator**

- **Purpose** — evaluates a design, an implementation diff, or a test suite against its
  binary evidence-typed rubric: per-axis scores, severity-ranked findings, a mechanical
  PASS / CONDITIONAL / BLOCK verdict, and for designs a foundation signal on when
  refactoring the blast radius pays.
- **Why** — evaluation separated from authoring is what makes a verdict trustworthy:
  authors never score themselves, so the independent evaluator runs every mode with
  fresh eyes — the design once the architect hands it back, implementation + tests once
  over the whole diff after implementation completes.
- **Pain** — bugs that "look correct"; unfounded quality claims; not knowing whether
  fixing inherited debt is worth it before building on top of it.
- **evaluator** — a read-only tool fence (no Write/Edit), zero author
  context by construction; its report is what the gate reads.

### `review`

- **Purpose** — reviews a PR/branch/diff on three axes (spec ↔ code honesty, behavior, quality)
  and returns severity findings + a block/pass merge verdict.
- **Why** — a merge decision belongs to a human informed by an evidence-backed verdict, not to
  the author's confidence.
- **Pain** — merges that drift from spec; unverified "fixed" claims; review notes with no clear
  gate.

---

### Supporting skills

### `figma`

- **Purpose** — turns a Figma screen into a component map (EXISTING / PARTIAL / NEW), extracting
  specs only for what's genuinely new.
- **Why** — most of a screen already exists in the codebase; dumping raw Figma JSON for
  everything wastes effort and buries the actual new work.
- **Pain** — rebuilding components that already exist; design handoffs that don't say what to
  actually build.

---

### Flutter (`my-flutter` — ⚠️ work in progress, incomplete)

### `review`

- **Purpose** — reviews a Flutter/Dart PR against the architecture rules (P1–P8), Riverpod code-gen
  idioms, Dart 3 patterns, and test-quality rules → a rule-cited severity report.
- **Why** — architectural rules only hold if something checks them on every PR; humans miss them
  under delivery pressure.
- **Pain** — architecture erosion; Riverpod/Dart-3 anti-patterns; tests that don't actually
  assert. (Flutter rules ship inside the `my-flutter` plugin at `rules/`.)

---

## 4 · The whole workflow — drivers orchestrate everything

One command runs the entire pipeline — audit → requirements → design (independently
evaluated) → tasks → red→green waves → one independent implementation+tests
evaluation → E2E → QA —
with a human gate at every consequential boundary:

```bash
claude --agent my-react:driver --worktree "add a logout button"
```

One **driver agent** you launch to run a whole spec: `driver` (self-contained — the phase
playbooks live in the agent itself over a `.meta.yaml` ledger, no process commands; heavy work
runs in its teammate agents). The driver is not tied to one skill — it binds them all.

- **Purpose** — drive one spec through its phases: run each phase's playbook, delegate
  heavy work to the worker agents, verify every output mechanically, and pause at human gates.
- **Why** — separating orchestration (decide, verify, record) from execution (skills + workers)
  keeps each simple; the driver holds no stack know-how and never does heavy work itself.
- **Pain** — half-run phases; advancing past an open gate; trusting a subagent's word instead of
  verifying; a whole process crammed into one unmaintainable prompt.

Implement runs red→green per wave — spawn `tester` (RED) → spawn `implementer`
(green, test paths byte-unchanged) — then ONE independent `evaluator` verify of the whole implement diff before the human
gate (bugfix scale skips it); a friction/defect DESIGN GAP routes back to `architect` for a fast-path
contract delta, and `e2e` authors the journey tests once the feature assembles. The
driver never advances past an open gate.

---

### The evaluation framework — one rubric system, evaluation as its own step

All evaluation lives in the `evaluate` skill (`skills/evaluate/references/` — one
framework file + three rubrics), always run by the evaluator agent, never by the author:
**design** once the architect hands it back (foundation signal included), then
**implementation** + **tests** once, after all implementation tasks complete.
Reports are intermediate, presented at gates and never persisted.

- **Binary evidence-typed checks, grouped into axes** — design: Grounding · Fit ·
  Structure (maintainability, scalability) · Tradeoffs · Buildability; implementation:
  Conformance · Simplicity & readability · Runtime · Honesty; tests: Coverage ·
  Assertion strength · Discipline. Each check names its evidence form (grep · command ·
  trace · read); executed evidence outranks prose judgment.
- **Scores and verdicts are derived, never judged** — axis bands by failure class (all
  pass = 4 · polish-only = 3 · one core = 2 · two+ core = 1 · any cliff = 0); verdict
  from axis minima (PASS all ≥3 · CONDITIONAL a 2 · BLOCK any ≤1). Disclosure scores clean: checks fail on the silent version only.
- **The foundation signal says when refactoring pays** — every inherited defect on the
  blast radius gets an INHERIT / FIX-NOW / QUARANTINE verdict at design time, and the
  evaluation marks it REFACTOR NOW when it sits on ≥2 flows, caps an axis, or recurs
  across specs — solidify the foundation before building on it, consciously.
- **Evaluation outcomes feed agent memory** — a failed check is already a generalized
  pattern (saved as *avoid*); a pass earned by a codebase pattern saves as the practice
  that earned it.

---

### How these are optimized — the mechanisms

Cross-cutting techniques the skills and agents share, developed to keep them cheap to run and
correct without heavy oversight.

**Efficiency — fewer tokens, less re-work**

- **Queryable, self-healing atlas** — `audit` banks understanding once; later phases
  *query* it instead of re-scanning, and a query heals itself on a miss (a bounded reveal budget)
  rather than dead-ending. Understanding compounds instead of evaporating each phase.
- **Bounded exploration** — the audit walks the definition graph on-purpose, one hop at a time,
  capping depth *during* the walk (Locate → Walk → Organize) so the off-purpose graph is never
  built and a read can't run away.
- **grep + glob to locate and walk** — keyword search narrows to the candidate entries, then the
  walk follows definitions hop by hop by grepping symbols and reading — no heavier tooling needed.
- **Route to the cheapest execution** — the driver picks inline or a spawn, and the model +
  effort, per dispatch by task complexity, batching work to avoid re-paying a subagent's cold start.
- **Progressive disclosure + terse prompts** — SKILL.md stays lean; heavy procedure lives in
  lazy-loaded `references/` (opened only in the mode that needs it); inter-agent prompts carry
  four essentials — where · what · materials · done-when. Skills load on every trigger, so every
  line earns its cost.
- **Declared iteration budgets** — every loop (a query's reveal chain, a red→green fix) names its
  stopping point up front; spent → stop and surface what was tried. No blind loops.

**Correctness — by construction, not by instruction**

- **Narrow tool fences** — the test agent writes tests only, the impl agent source only, the
  evaluator reads only. Red-first, author ≠ implementer, and findings-never-fixes become
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

## 5 · Layout & editing

Edit under `plugins/` directly; `/reload-plugins` (or restart) picks up changes when loaded
via `--plugin-dir` or a local marketplace add.

```
my-claude/
├── .claude-plugin/marketplace.json    the marketplace registry
├── plugins/
│   ├── my-react/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .lsp.json  TypeScript language server registration
│   │   ├── skills/    the contract skills above
│   │   └── agents/    1 driver + 6 companion workers
│   ├── my-flutter/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/    fl-* skills
│   │   └── rules/     architecture-principles.md · test-quality.md
│   └── my-workflow/
│       ├── .claude-plugin/plugin.json
│       ├── skills/    drive-spec (spec and lead) · one step each: rephrase · audit-truth · decide (+ 3 design parts) · build · verify · critique
│       ├── agents/    spec-architect · spec-implementer · spec-tester · spec-reviewer · code-auditor
│       ├── shared/    conventions.md (ids, questions, output, knowledge, diagrams) · principles.md · kinds.md · atlas.md
│       ├── templates/ spec · design · review
│       └── hooks/ + scripts/  prompt hook (routing hints)
├── metrics/           local telemetry stack + stack.py (not plugin-shipped)
```

For the full phase lifecycle, the `.meta.yaml` ledger, and human gates, see
**[plugins/my-react/agents/driver.agent.md](plugins/my-react/agents/driver.agent.md)**.
