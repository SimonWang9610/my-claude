# my-claude — spec-driven-development plugins for Claude Code

A [Claude Code](https://claude.com/claude-code) **plugin marketplace** that drives a structured,
spec-driven workflow — `preflight → requirements → design → tasks → implement → validate → qa` —
for **React/TypeScript** and **Flutter/Dart** projects.

It is built on one idea: **skills carry the judgment, agents carry the execution, the driver
agents carry the process, plugins package it.** A skill is a self-contained procedure Claude
loads on demand; some skills have a **companion agent** — an expert with a narrow tool fence and
the skill preloaded — that runs the skill under separation-of-duties or fresh-eyes constraints
the skill alone can't enforce.

## Install

Two self-contained plugins that install independently:

| Plugin | Contents |
|--------|----------|
| `my-react` | all React/TS contract skills + the 2 drivers and 6 worker agents |
| `my-flutter` | the `fl-*` skills + the Flutter rule files (shipped in-plugin, read via `${CLAUDE_PLUGIN_ROOT}/rules/`) |

The install script registers the marketplace and installs the plugins via the `claude plugin` CLI:

```bash
python3 install.py                 # my-react from GitHub marketplace
```

```bash
python3 install.py --flutter --rules   # + my-flutter, + symlink rules/preferences.md into ~/.claude/rules/
```

```bash
python3 install.py --local             # register THIS checkout as the marketplace (for development)
```

Or manually, inside a `claude` session:

```
/plugin marketplace add SimonWang9610/my-claude
/plugin install my-react@my-claude
/plugin install my-flutter@my-claude     # optional, independent
```

For one-off local testing without any install:

```bash
claude --plugin-dir ./plugins/my-react --plugin-dir ./plugins/my-flutter
```

Everything a plugin ships is **namespaced**: skills invoke as `/my-react:<skill>`
(e.g. `/my-react:requirements`, `/my-react:design`), agents address as
`my-react:<agent>`. Namespacing is what keeps the bundle from colliding with global or
project skills — the reason plugins replaced the old symlink installer.

`rules/preferences.md` is the one asset a plugin **cannot** carry: plugins do not inject
always-on context (a plugin CLAUDE.md is ignored). It stays a user-level file — `--rules`
symlinks it for you, or do it yourself:

```bash
ln -s "$(pwd)/rules/preferences.md" ~/.claude/rules/preferences.md
```

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
5. Re-link `rules/preferences.md` (see above) — it is no longer installed for you.

---

Below, each skill is described by its **purpose**, the **why** behind it, and the **pain** it
removes; its companion agent (if any) follows.

---

## Understand code you didn't write

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

## The contract flow — spec to shipped code

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
  authors run the same rubric to *improve* (mechanical checks keep self-evaluation
  honest), the independent evaluator runs it to *verify* with fresh eyes.
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

## Supporting skills

### `figma`

- **Purpose** — turns a Figma screen into a component map (EXISTING / PARTIAL / NEW), extracting
  specs only for what's genuinely new.
- **Why** — most of a screen already exists in the codebase; dumping raw Figma JSON for
  everything wastes effort and buries the actual new work.
- **Pain** — rebuilding components that already exist; design handoffs that don't say what to
  actually build.

### `delegate`

- **Purpose** — routes a piece of work to the cheapest execution that does it well: inline, a
  fork, or a subagent (bound or ad-hoc), and fixes what the spawn must carry back.
- **Why** — a subagent re-pays a cold start; fanning out blindly burns tokens, while keeping
  everything inline floods one context.
- **Pain** — token-wasteful over-delegation; context floods from noisy exploration; a reviewer
  seeing the reasoning that produced the work.

### `jira-align`

- **Purpose** — a three-way reconcile of a JIRA ticket's AC against the spec and the shipped code,
  updating the ticket and posting one alignment comment.
- **Why** — tickets go stale the moment requirements shift mid-development, and a ticket that lies
  about what was built misleads everyone downstream.
- **Pain** — "the ticket doesn't match the code"; AC drift after mid-flight changes.

---

## Flutter

### `review`

- **Purpose** — reviews a Flutter/Dart PR against the architecture rules (P1–P8), Riverpod code-gen
  idioms, Dart 3 patterns, and test-quality rules → a rule-cited severity report.
- **Why** — architectural rules only hold if something checks them on every PR; humans miss them
  under delivery pressure.
- **Pain** — architecture erosion; Riverpod/Dart-3 anti-patterns; tests that don't actually
  assert. (Flutter rules ship inside the `my-flutter` plugin at `rules/`.)

---

## The drivers — orchestration

Two **driver agents** you launch to run a whole spec: `driver` (self-contained —
the phase playbooks live in the agent itself over a `.meta.yaml` ledger, no process commands;
heavy work runs in its teammate agents) and `oac-driver` (drives an external
**specflow** project's `/spec-*` commands). A driver is not tied to one skill — it binds
them all.

- **Purpose** — drive one spec through its phases: run each phase's playbook, delegate
  heavy work to the worker agents, verify every output mechanically, and pause at human gates.
- **Why** — separating orchestration (decide, verify, record) from execution (skills + workers)
  keeps each simple; the driver holds no stack know-how and never does heavy work itself.
- **Pain** — half-run phases; advancing past an open gate; trusting a subagent's word instead of
  verifying; a whole process crammed into one unmaintainable prompt.

```sh
claude --agent my-react:driver --worktree "add a logout button"
```

Implement runs red→green per wave — spawn `tester` (RED) → spawn `implementer`
(green, test paths byte-unchanged) — then an optional `evaluator` pass before the human
gate; a friction/defect DESIGN GAP routes back to `architect` for a fast-path
contract delta, and `e2e` authors the journey tests once the feature assembles. The
driver never advances past an open gate.

---

## The evaluation framework — one rubric system, evaluation as its own step

All evaluation lives in the `evaluate` skill (`skills/evaluate/references/` — one
framework file + three rubrics), applied at two moments: authors run it to **improve**
right after authoring, the evaluator agent runs it to **verify** at gates.

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

## How these are optimized — the mechanisms

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
- **Route to the cheapest execution** — `delegate` picks inline / fork / subagent and the
  model + effort by task complexity, batching work to avoid re-paying a subagent's cold start.
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

## Layout & editing

Edit under `plugins/` directly; `/reload-plugins` (or restart) picks up changes when loaded
via `--plugin-dir` or a local marketplace add.

```
my-claude/
├── .claude-plugin/marketplace.json    the marketplace registry
├── plugins/
│   ├── my-react/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/    the contract skills above
│   │   └── agents/    2 drivers + 6 companion workers
│   └── my-flutter/
│       ├── .claude-plugin/plugin.json
│       ├── skills/    fl-* skills
│       └── rules/     architecture-principles.md · test-quality.md
└── rules/             user-level working discipline — preferences.md (not plugin-shipped)
```

For the full phase lifecycle, the `.meta.yaml` ledger, and human gates, see
**[plugins/my-react/agents/driver.md](plugins/my-react/agents/driver.md)**.
