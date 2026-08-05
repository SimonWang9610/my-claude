
---

## Fresh-spawn dispatch replaces teammate continuation (both drivers)

Continuing a bound agent re-sends its **entire working transcript** as input every turn, and a
subagent's prompt cache TTL is minutes — not the parent session's hour. So the "route to the
teammate who knows the work (below ~75% context)" rule was optimizing for warm context that in
practice was almost always cold: a mid-session architecture adjustment paid full price for the
architect's whole accumulated context, and grew it each turn.

`# Team — you are the lead` → `# Dispatch — you are the lead` in both drivers; the routing bullet
becomes **every dispatch is a fresh spawn**, whose Materials name the prior work's artifact plus
the delta. The rule carries its runtime reason inline so it generalizes rather than reading as an
arbitrary ban. Teammate vocabulary retired throughout (Role, frontmatter, `§ Team` cross-ref); the
design gate's `continue vs re-spawn` → `accept vs re-spawn`, ambiguous once "continue" could mean
continuing an agent. `delegate` §1 gets the general-purpose form, since routing is decided there
before any spawn.

Rejected: a hard `permissions.deny: ["SendMessage"]` in user settings → enforcement belongs in the
agent definitions, and the deny would also kill cross-session peer messaging.

Consequence, accepted: artifact completeness becomes load-bearing — a `design.md` that omits what
the architect knew can no longer be silently patched by a still-warm agent, so it fails visibly at
the next spawn instead.

`my-react` bumped to 1.2.0 (behavior change in agent definitions; no renames, so no migration note).

---

## Telemetry stack + TypeScript LSP (adopted from the internal oac-agentic-harness)

Two pieces pulled across from the internal plugin, both re-derived rather than copied.

**1. `metrics/` — local Claude Code telemetry.** Same topology as the source (OTel Collector →
Prometheus + Loki → Grafana, dashboard 25255), rewritten as one stdlib-only `stack.py`
(Python 3.9+, no `jq`/`bash`). Changes over the source:

- **One config file.** `metrics/config.json` (ports, creds, retention, dashboard id, settings
  path, content logging) + gitignored `config.local.json` shallow-merged over it; `stack.py`
  resolves those into the environment that `docker compose` substitutes, so nothing is
  configured in two places.
- **`cumulative` temporality** written into the settings env — Prometheus counters expect
  cumulative, and it survives a collector restart without losing totals.
- **CLI readouts, so no skill is needed** — `summary` (cost/tokens/sessions/edit decisions),
  `metrics`, `query <promql>`, `search <logql>`, `labels`, and `verify` (settings + endpoints
  + metrics-arriving, exit 0/1). `summary` **discovers** metric names at runtime instead of
  hardcoding them, because the OTLP→Prometheus mangling appends units and `_total`.
- **`unconfigure`** for a clean removal of only the keys `configure` wrote.
- Content logging on by default (prompts/responses/tool details → Loki), documented as a
  local-plaintext tradeoff with a one-key opt-out.

Rejected: the source's `observability` skill (detect-endpoint-then-offer-stack). Its whole
procedure is `stack.py verify` + `stack.py up`, and its remaining bulk is guard/egress
handling specific to that harness — no judgment left for a skill to carry.

**2. `plugins/my-react/.lsp.json`.** TypeScript LSP registration (auto-discovered from plugin
root; no `plugin.json` inline). Buys exact go-to-definition/find-references and post-edit type
diagnostics on top of the skills' grep+glob navigation. Binaries are not bundled — `install.py`
gained a `check_lsp()` preflight that prints the `npm install -g` line when they're missing.
`my-react` bumped to 1.1.0. Not mirrored into `marketplace.json` (the source duplicates it
there; with the default `strict: true` the plugin's own manifest is already the authority).

`install.py` gained `--metrics` (runs `stack.py up`).

---

## Driver fixes: shared worktree + strict Setup ordering (both drivers)

Two operational bugs the user hit:

**1. Parallel subagents spawned in isolated worktrees** (couldn't see each other's / the main worktree's changes). Fix — enforce one shared worktree, redundantly:
- Hard Rule **One worktree per spec**: every delegated subagent (Test/Work/Review) runs in the driver's `$ROOT` worktree, never its own/isolated one; parallel units share `$ROOT` (the wave plan keeps concurrent writes on disjoint files); override any tool that would spawn a fresh worktree.
- Delegation template `Working Directory:` line → `$ROOT` (NOT a new/isolated worktree; every unit shares one tree).
- Implement Work/Test split: parallel units run "in the same `$ROOT` worktree (never separate worktrees)".

**2. preflight running before /init.** Fix — make Setup a hard precondition for phases:
- Setup preamble: run steps in order to completion before any phase; `preflight` is the first *phase*, not Setup.
- Step 2 gains "**Do not run any phase yet.**"; Step 3 gains "**Only once `workflow.yaml` exists, enter the Drive Loop.**"
- Drive Loop intro: "**Enter only after Setup is complete** — spec dir, `.meta.yaml`, `workflow.yaml` all exist."
- Hard Rule **Setup before phases**: never run a phase (preflight included) until `$ROOT` confirmed + `/init` wrote spec dir + valid `.meta.yaml` + generator wrote `workflow.yaml`.
- Also fixed a run-on/typo in specflow-driver Step 3 ("directly When resuming").

Both drivers edited identically (modulo `/spec-` vs `/sf-`); verified consistent.

---

## Driver Setup clarified + artifact completeness + command-set lock

**1. Setup = 4 strict steps, no preflight inside Setup** (both drivers). Restructured to: (1) worktree check; (2) **Gather the basics + init** — WAIT for instructions, collect ONLY what `/init` needs for `.meta.yaml` (name, variant, one-line description, design links), do NOT explore code or start preflight, run `/init`, verify spec dir + valid `.meta.yaml`; (3) **Generate `workflow.yaml`** via the generator; (4) **Drive the workflow** — only now enter the Drive Loop (preflight is the first *phase*, not Setup).

**2. Artifacts sometimes missing after a phase** (e.g. per-unit contracts). Enforced at three points:
- Both generators gained an **Artifact completeness** emission rule: `outputs` must all exist (non-empty) before a phase advances; a collection output (`contracts/`) folds its per-item rule into `exitWhen` (one `contracts/<unit>.md` per unit in design.md).
- Both phase-maps' `design` exitWhen now reads "a `contracts/<unit>.md` for every unit named in design.md".
- Drivers' Drive-Loop **Verify** step now confirms "every declared `outputs` artifact exists and is non-empty (a collection like `contracts/` needs one file per unit)".

**3. Each driver locked to its own command set.** New Hard Rule: specflow-driver **`/spec-*` only** (never `/sf-*`); specflow-driver **`/sf-*` only** (never `/spec-*`); a missing command → STOP, never substitute the other prefix.

Both drivers verified consistent (modulo prefix + intentional description lines).

---

## Token discipline from caveman research (input-side compression)

Researched juliusbrussee/caveman. Its own honest numbers show output-style compression is the
wrong lever for input-dominated agentic sessions (the style skill costs ~1–1.5k input/turn and
nets only 14–21%, sometimes negative). Absorbed the input-side, compounding levers instead:

1. **Subagent return contracts** — `delegate` "Demand compact structured returns" bullet
   now fixes a rigid line-oriented format with a hard item cap (`<path:line> — <symbol> — <≤6-word
   note>`); facts exact, everything else dropped, never abbreviated. Covers both drivers via the
   shared template.
2. **Terse persisted artifacts** — one short rule per artifact-producing skill (duplicated per
   profile, per profile independence): build-acceptance-criteria (hard rule),
   design-react-architecture (**Write terse**), plan-react-tasks (step 6), analyze-react
   (**Style** line), scan-resource (principle), acceptance-criteria (step 10),
   design (intro), tasks (output format). Common core: terse prose,
   reference IDs instead of restating, technical facts exact, no invented abbreviations.
3. **Tokenizer-realism authoring rule** — new `rules/token-discipline.md` (distributed per-project
   by link.sh like the other rules; NOT in CLAUDE.md, which is symlinked as the global
   ~/.claude/CLAUDE.md): compress what compounds; lazily-loaded references trimmed
   opportunistically only (no bulk rewrite); abbreviations/arrows are fake compression.
4. **Human-facing clarity guardrail** — both drivers' `gate: human` bullet: gate summaries in
   clear full sentences, never fragments; also in the rule and the design skills' gate content.

Rejected: caveman-speak output style, per-turn style skills (net-negative here).

Follow-up (same session) — trimmed the two remaining inter-phase/agent flows:

5. **Slice-scoped delegation inputs** — `delegate` `Materials:` line now demands the
   task's slice (unit's own contract, its task rows, traced AC lines), never a whole spec dir;
   slicing follows existing boundaries only (cross-unit reviewers still get all changed files +
   every contract's must-nots).
6. **Mechanical driver verification** — both drivers' Verify step: existence/size checks, grep
   counts, named tests, `git diff` on guarded paths; full artifact content enters driver context
   only to present a human gate.
7. **Level-scoped rule-card loading** — both drivers' Work/Test split: the WorkAgent prompt names
   the unit's level(s) from the contract's layer decision so it opens only the matching
   `implement-react-code` card directories (full corpus ~3.5k words; a level slice is ~1–2k).
   Evaluated and kept the Work/Test split itself: TestAgents never load the rule cards, so
   merging saves ~nothing and would break the byte-unchanged-test guarantee; wave batching
   re-pays accumulated context and loses parallelism.

---

## React skill-family optimization round (2026-07-19)

1. **audit** — note format restructured into one fixed thinking chain per flow:
   entry/exit → GIVEN (origins, preconditions, initial state) → WHEN (trigger + guards) →
   THEN (per-case outcome + state change + propagation) → HOW (transforms, side-effect
   surfaces, mechanisms) → Interacts-with (coupling + direction per related flow). Old
   Data model/Data flow/User flow/Cases covered/State fields folded into the chain — no
   field lost, none duplicated. New output artifact: **flow interaction map** (mermaid or
   table) assembled from the Interacts-with lines; cross-flow touch points recorded
   during tracing, never via a second scan.
2. **requirements** — new step 1 **First principles**: recover the problem behind
   the ask (a requested solution is a candidate, not the requirement), surface and check
   the request's assumptions against audit notes/system fundamentals (wrong ones become
   batched questions with evidence + recommended correction), derive requirements from
   problem + invariants, never from current code shape or user belief.
3. **design** — first-principles rule in SKILL.md (units derive from what
   flows require; audit says what exists, never what the design should look like);
   Output discipline gains **no reasoning in artifacts** (decisions only; one-line rule
   citations are the only "why"; unresolved reasoning → Open items) + **fixed shape**
   (code only in designated fenced blocks, all else one-line prose or table rows);
   design.md Flows section standardized: per flow a `### F<n>` with a mermaid
   sequenceDiagram between units (messages labeled `mechanism: fact`, NEW marked, ACs
   cited) + the ground-truth step table. Reconcile step 1 consumes the interaction map
   for blast radius.
4. **plan** — new step 5: every wave pre-split into a **test batch**
   (one TestAgent) + **impl batch** (one WorkAgent); oversized waves (~4 tasks / context
   bloat) chunked at planning time with named reason; count-check extended (every task in
   exactly one chunk's batches). tasks.md § Waves shape added.
5. **check** — checks restructured into three axes: **behavior &
   outcomes** (AC tests assert the outcome not a proxy, states reachable, unhappy paths
   fail loudly, must-nots, importers), **quality & maintainability** (rulebooks + reuse
   honored, seams intact, scope surgical), **performance & memory** (unchanged
   diagnostic).
6. **Drivers reconciled** (both, identically modulo prefix) — Implement discipline now
   consumes tasks.md's pre-planned batch pairs instead of re-deriving them (run-time
   re-chunk fallback recorded back into tasks.md); preflight ③ persists the flow
   interaction map alongside the notes in `audit-notes.md`.

Rejected: restating the batching rule inside test/implement skills (driver passes scope);
duplicating the no-reasoning rule into references/design.md (stated once in SKILL.md,
templates implement it structurally).

Follow-up (same session, user feedback): audit note fields became `####` subheadings
(conditional fields marked by comment, e.g. `<!-- existing only -->`) with terse
fact-only bodies ("no narration, no restating the field name's meaning"); trimmed the
verbosity the round introduced — requirements step 1 collapsed to one bullet,
design first-principles/output-discipline paragraphs and the Flows
template annotation shortened, plan step 5 tightened,
check's axis preamble folded into the Checks intro.

Follow-up 2 (same session): design SKILL.md rewritten to exactly 70
lines (inputs merged, one-line rule bullets and full-path steps, references hoisted to a
section preamble). Language-agnostic rules escalated to rules/preferences.md — new
sections **First principles** (requests are evidence not specs; derive don't copy) and
**Artifacts** (decisions never reasoning; fixed shapes), new bullets **Cut batches at
planning time** (Leverage) and **Judge behavior first** (Code); Tokens' "rows are facts"
folded into Artifacts to remove the overlap. Skills stay self-contained (rules
duplicated, never referenced). Consistency audit fixes: test scopes now
"unit — skip step 3 / e2e — skip step 2" (self-check + steer always run); ground-truth.md
stale "§ Propose refactors deliberately" → "§ Refactor proposals" and a redundant
coverage-guard sentence cut; plan count-check corrected to "tasks =
contract groups ± recorded re-cuts" and "every task in exactly one batch pair".
figma, delegate, jira-align, implement/review skills audited — no
changes needed.

---

## Heavy-output cuts in the specflow pipeline (2026-07-19)

Swept the drivers + bound skills for heavy outputs and agent-to-agent intermediates:

1. **Post-implement check user-gated** — both drivers' implement ③ is now a **check
   gate**: ask the user whether to run `/check` (recommend yes for
   feature-scale waves, skip for bugfix scale; decision recorded), instead of always-on.
2. **Design self-check scaled** — design.md § Self-check gains a Scale rule:
   single-group designs run blocking checks only (advisory classes re-surface in the
   post-implement check); kept blocking always — it catches design flaws before code
   exists, which no later check can. Drivers' Fresh-eyes rule scoped to feature-scale;
   fast-path/bugfix self-checks run inline, no subagent spawn.
3. **Terse inter-agent prompts** — delegate gains "Prompts are pointers, not
   prose": paths/IDs/rules/deliverable only, never background narration or reasoning.
4. **Effort routing on dispatch** — delegate gains "Route effort by task"
   (medium: mechanical contract-scoped work; high: judgment — design, forensics, review
   verdicts); preferences.md "Route models by fit" extended with the effort clause.

Already lean, left alone: audit (read budget + bounded note format), check findings
(~12 cap), subagent returns (line-oriented + item cap), driver gate summaries (paths,
never artifact re-dumps), qa-report (grep-generated), tasks.md (pointer rows).

Follow-up: design self-check budget cut from 2 loops to **ONE pass** — findings drive one
re-design of the affected units, no re-check; still-open items pause to the caller
(SKILL.md step 5 + design.md § Self-check reworded). delegate template made
terse: pointer/constraint placeholders only, new `Effort: <medium | high>` field; the
"pointers, not prose" bullet became the template's preamble sentence (stated once).

---

## specflow commands rewritten lean (2026-07-19)

All 12 `/sf-*` commands rewritten 398 → 271 lines on a fixed shape: one-paragraph role +
artifacts, **Method** (embedded stack-agnostic skill, or "the flow's bound skill owns the
procedure"), **Exit** gate. Commands stay language-agnostic; new rule (README updated in 3
spots): commands may embed **stack-agnostic skills only** — sf-preflight embeds
`/audit`, sf-requirements embeds `/requirements`; stack skills remain
generator/driver-bound, never named in commands.

Cut as duplication or conflict:
- **Purpose paragraphs + steps restating bound skills** (design/tasks/implement procedure
  lives in the skills/driver; commands keep only the gate contract).
- **`phases.md`** (sf-implement) — duplicated tasks.md § Waves batch pairs; one producer
  per fact.
- **EARS notation + Example Mapping** (sf-requirements, sf-clarify, sf-validate check 2) —
  conflicted with requirements' method and requirements.md shape; check 2 is now
  "AC shape" (stable ID + observable GWT). sf-clarify's "up to 5, one at a time" →
  ONE batched round (aligned with requirements).
- **Test-first ideology** (sf-implement) — replaced by the evidence contract: author ≠
  implementer, tests derive from contracts never from code, red-before-impl collected by
  the driver as mechanical evidence, green + byte-unchanged, review pass clean. The
  sequencing is driver mechanics, not command doctrine.

Follow-up: command set trimmed 12 → **8** (kept init, preflight, requirements, design,
tasks, implement, validate, qa; deleted sf-clarify, sf-drift, sf-status, sf-steering).
my-specflow-driver updated: clarify phase is driver-led (one batched Q&A round on OPEN
`## Clarifications` entries, no command), `/sf-status` tracking line dropped, the
`/sf-*`-only hard rule now enumerates the exact 8-command set. sf-requirements' OPEN-entry
pointer retargeted to the driver-led clarify phase; README command count (2 spots) + table
updated (clarify → driver-led; drift/status/steering rows removed). link-commands.sh globs
the dir — no change needed.

Follow-up 2: commands reshaped as **standalone procedure guides** on one uniform format
(intro+artifacts · Steps · Exit): no driver knowledge (user-invocable one by one), no
embedded skill names (reverted the /audit and /requirements embeds — both
drivers share the same procedure via their own command set to compare performance/quality;
README's command rule updated in 3 spots). sf-init folds the **feature** `.meta.yaml`
template in directly (feature-only, no template lookup, taskstoissues dropped; driver's
taskstoissues pre-authorization removed). E2E gap closed end-to-end: sf-design step 5
authors `qa-journey-plan.md` (per story: happy + error/boundary `J-<n>` journeys with
covers-ACs + NOT-automated table; skip noted in design.md), approved at the design human
gate (driver updated — plan no longer "out of our control"); sf-implement step 4 authors
one e2e test per journey; sf-validate check 8 maps journeys → e2e tests; sf-qa treats a
journey gap as a finding, never authors.

Follow-up 3: sf-design rebuilt as a lean adaptation of the oac spec-design override —
core purposes kept, verbosity/stack-specifics dropped. Kept: verification designed with
the feature (per-AC test strategy table with unit/journey/manual levels, each behavior
named positive + negative + boundary, ask-the-user-for-missing-failure-modes), journey
plan + the approve/revise/skip/add review interaction, E2E Surface note (one suite per
story, one test per J-<n> citing ACs, per project convention), Blast Radius section
(reverse-import closure → existing tests; may be empty; a test needing change is flagged)
consumed by sf-qa's consumers family. Dropped: Playwright/POM rules, GPG commit ceremony,
rg recipes, failure-patterns catalog, token-coupled style radius (stack-specific).

Follow-up 4: purged react-skill repetition from the commands — commands hold the
engineering-level procedure only. sf-design: dropped the contract field list, the
REUSE/MODIFY/REPLACE tag vocabulary, and the skill's self-check blocking list (step 8 is
now the architecture gate in sf-validate's vocabulary: God-unit / dual source / missing
seam). sf-tasks: dropped re-cut/pointer-row/Edge-marker mechanics (plan skill's).
sf-preflight: audit detail (data flow, boundary surfaces) reduced to a surface survey.

Follow-up 5 (full audit vs the spec-* set — sf-* stays agent-facing for the driver A/B):
adopted spec-* core mechanisms missing from sf-*: preflight Action enum (Reuse as-is ·
Copy and customize · Modify unadopted · No interaction); requirements-time verification
classification per AC (unit/journey/manual — design reconciles it, sf-design step 4
updated); sf-tasks gate reworded to "test-authoring work" (dedicated test task OR wave
test batch — fits both flows' task models) + explicit test-precedes-impl ordering; sf-qa
gained spec-qa's scoped-work pre-check (unfinished scoped test → STOP back to implement,
never a finding), test-bug vs real-defect failure classification (report, never fix), and
the coverage-matrix format (AC/journey | test | strength | status, hollow = stub passes).
Deliberately NOT adopted (human-mixed or divergent by design): spec-init branch creation
(specflow is worktree-driven), trace-viewer/builder-checkpoint ceremony, GPG commit gates,
Jira transitions, scoped test runs at QA (specflow keeps ONE full-suite run per driver rule),
EARS. Every sf-* command verified free of "You are…" role prose and human narration.

Follow-up 6: journey plan made requirement-driven. sf-design step 5 keys off the test
strategy (no journey-level AC → skip with note); each plan entry carries a disposition —
NEW, or MODIFY <existing test path> when an existing journey test already covers the
affected flow (planned as a change, never duplicated). sf-implement step 4 executes per
disposition (author vs update the named test; material changes to existing tests surfaced,
never silent). Driver design playbook + README row now say "when the test strategy
classifies any AC journey-level".

---

## graphify research → audit adoptions (2026-07-19)

Reviewed /Users/simonwang/projects/tmp/graphify (codebase → knowledge graph skill:
tree-sitter extraction, EXTRACTED/INFERRED/AMBIGUOUS edges, god nodes, Leiden communities,
query/path/explain CLI). Adoptions (source → decision → reason):

- Queryable-artifact idea → **Flow index** as output #1 (`flow · entry anchor · units
  touched · couples with`): the scoped-graph lookup surface — grep the index → jump to the
  note → follow anchors to source; three-level disclosure without a re-scan.
- Confidence tags → **Tag what you didn't read directly** trace rule: untagged =
  read-from-source, `(inferred)` = deduced, `(uncertain)` = must carry a Self-audit
  pointer; downstream phases weigh facts by tag.
- God nodes → **hub flag** on the interaction map: units several flows couple through =
  widest change radius; feeds design's blast-radius extension.

Rejected: community clustering (flows already are the grouping at audit scale), the
query/path/explain CLI + MCP server + graph.json (our audits are note-sized and tool-free;
markdown + grep serves the same access pattern), incremental cache/watch/hooks (drivers
forbid re-audit via prior-artifacts rule), HTML/Obsidian/Neo4j exports and benchmarks
(no consumer). Consumers reconciled: both drivers persist "flow index + notes +
interaction map"; ground-truth § Audit locates notes via the index.

Follow-up (A/B verdict): both skills produced same-quality output → audit kept,
**flow-atlas deleted**, and its structure folded in via a cohesive rewrite (not a patch):
audit now has three modes — **build** (default; boundary + trace rules + tag
discipline unchanged in substance), **query** (≤20-line answers from the audit: index rows
+ note fields + `Dive:` pointers; never scans source), **extend** (the only post-build
source-reader; folds facts back in, refreshes the index row, reports delta only). Artifact
moved to **`audits/`** (tiered: `index.md` always-loaded over one `<flow-id>.md` per flow;
Dependents/Verdict merged to one field). Consumers switched from receive-notes to
invoke-the-skill: drivers' preflight runs `build` → `audits/` (preflight.md carries only
figma map + gaps), carry-forwards + prior-artifacts rule name `audits/` and query/extend;
ground-truth § Audit is now query → build → extend; design SKILL input renamed "Prior
audits"; implement step 1 queries `audits/` for surrounding-flow context
instead of broad re-reading.

Follow-up: extend restated as its two real cases — (1) **new flow** (query miss, no
atlas, or a pointed spot disclosing a coherent sub-flow: promoted to its own note + index
row, coupled to the parent in index.md, never inlined) · (2) **more facts on an existing
flow** (fold into the note, refresh its row). Implement-phase gating sharpened: query/
extend only for facts the contract/task genuinely doesn't carry — never query what the
contract states. Note template trimmed against the tiers: **Entry / exit** dropped (entry
anchor is an index column; exits are THEN outcomes + HOW side-effect surfaces) and
**Interacts with** dropped (couplings live only in index.md's Couples-with cell —
now direction + shared fact — and the map); the touch-point trace rule writes them there
directly. ground-truth § Reconcile reads the index's Couples-with, not note lines.

Follow-up: **extend broadened to the scoped acquirer** — pointed spot → fund it; query
miss / uncovered reference / no atlas → run build scoped to that one flow (per
references/build.md), add its note + index row. Consumers collapsed to the two-verb
pattern (query → unanswered → extend): ground-truth § Audit is now 2 steps with inline
examples; implement step 1 likewise. Explicit build remains the drivers' preflight bulk
entry.

Follow-up: audit split for mode-scoped loading — SKILL.md is 44 lines (modes +
query + extend; what a querying subagent actually needs), the build procedure + artifact
formats moved to references/build.md (103 lines, loaded only on build mode). Artifact dir
renamed `audits/` → **`atlas/`** everywhere (skill, both drivers, design/implement
consumers). Consumers now teach usage by concrete example instead of narration:
ground-truth § Audit shows real build/query/extend invocations; implement step 1 shows a
query example.

Original twin (superseded by the fold above): **flow-atlas** created as an experimental
A/B twin of audit
(skills/flow-atlas/SKILL.md, explicitly-invoked, NOT wired into drivers). Same note chain
and trace discipline (condensed, self-contained duplicate for the experiment); structural
differences: tiered artifact (`atlas/index.md` always-loaded tier over `flows/F<n>.md`
per-flow notes) + graphify-style subcommands — query (≤20-line answers: index rows + note
fields + `Dive:` pointers; atlas-only, never scans source), explain, path (hop walk over
Interacts-with/HOW; never invents a hop), extend (the only source-reader: funds a
Self-audit pointer and folds the facts back in — persistent deepening). Comparison
protocol: run both on the same references; compare tokens loaded by design/implement,
answer quality on identical questions, artifact size; winner's structure folds back into
audit and the twin is deleted (duplicate build rules are temporary by design).

---

## react-doctor research (2026-07-20) — proposals implemented, then REVERTED on review

Audited /Users/simonwang/projects/tmp/react-doctor via /audit (atlas in session
scratchpad): fully deterministic scanner — AST rules + project scans under one rule
contract, one compiled noise filter, capability-gated enablement, LLM only at rule
authoring time.

Three adoptions were implemented and reverted at user request pending a decision on the
script-vs-LLM split: P1 specflow/scripts/specflow-check.mjs (5 deterministic gates over spec
artifacts — verified against planted-defect fixtures) + sf-validate/driver wiring; P2
capability gating in implement/check skills; P3 rule-card quality bar in .claude/CLAUDE.md.
The research conclusions stand (hybrid tiering: artifact predicates → scripts · code
predicates → existing tools, never bespoke scanners · semantics → LLM judging residue);
no assets remain in the tree.

Follow-up: after discussion, the four research conclusions were folded back cohesively —
each in its one home, family vocabulary, no scripts:
1. **Capability gating** — implement leads its Rules priority with
   "Capabilities first" (package.json once; a rule never decides its own applicability);
   check mirrors it ("Capabilities gate citations").
2. **Rule cards carry the why** — .claude/CLAUDE.md Rules: code shape + runtime reason
   (what lets an LLM generalize without over-flagging) + ≥1 valid look-alike never
   flagged; false positive = correctness bug; narrow beats broad.
3. **Suppression accounting** — check Output adds a drop tally
   (`suppressed: <n> (advisory cap · caller scope · capability gate)`) so a clean report
   means clean, never quietly filtered.
4. **Judgment authors, search verifies** — preferences.md § Artifacts: correctness is
   judged once at authoring; re-checks over fixed-shape artifacts are grep/diff/count.
   (Already embodied by test skill's "coverage IS the grep" and drivers' mechanical
   Verify — the principle now named once, globally.)

---

## Field-use fixes: single-agent audit + concrete model routing (2026-07-20)

Two issues from real driver runs:

1. **audit fanned out subagents during build** — whole-flow sense (couplings,
   hubs, skip-decisions) fragments across contexts. Build mode now states: **ONE agent
   audits everything**; skip off-purpose flows instead of splitting; parallel subagents
   only on explicit caller designation.
2. **Model routing too abstract** — delegate's routing bullet is now a concrete
   mapping: test/impl from contracts → Sonnet (medium when the contract pins the work,
   high when multi-unit/heavy context) · search/explore → Haiku, escalated to Sonnet when
   the goal needs synthesis not locating · judgment (design, forensics, review verdicts)
   → top tier, high. Template field renamed `Model · Effort:`; preferences "Route models
   by fit" aligned (Sonnet-class/Haiku-class + escalation clause).

Follow-up: (a) `Model · Effort:` REMOVED from the delegation template — model/effort are
spawn *parameters* the spawning session sets, never prompt content (routing bullet reworded
to say so). (b) Companion-skill steadiness: invocation pinned to a moment ("invoke
/delegate BEFORE the phase's first spawn", phase-loop step 2, both drivers) + new
hard rule **Every spawn is templated** — every subagent prompt carries the template's
field labels; mechanically checkable (a prompt missing a label is not sent). Prose
references get skipped; a checkable artifact shape doesn't.

Follow-up: **wave economics rebalanced** (user observed heavy subagent token cost). Waves
were DAG-level-driven and the "~4 tasks → chunk" trigger multiplied pairs — both push
toward many small spawns, each re-paying a cold start. New strategy: plan
step 4 merges adjacent DAG levels until the spec fits **2–4 waves** (a wave sized by one
agent's context — its tasks' combined contracts — never task count; more waves only when
deps force them); step 5 = ONE test+impl pair per wave; chunking's only trigger is
contracts overflowing one context (task-count trigger dropped; example annotation
updated). sf-tasks step 3 + both drivers' re-chunk rule aligned; preferences "Cut batches
at planning time" gains "fewer, fuller batches beat many small spawns". Parallelism loss
is wall-clock only — intra-wave concurrency was already gone with one pair per wave.

Follow-up: **react-checker-agent built** — the one role where a subagent is structurally
required, not just cheaper: the check skill's fresh-eyes premise maps to exactly one route
(a subagent that can't inherit the author's reasoning; a fork would defeat it), and
**read-only tools** (`Read, Grep, Glob, Bash` — no Write/Edit) make "findings never fixes"
unbreakable. Binds `check` + `audit` (queries the atlas to
verify conformance, never re-scans), `model: sonnet`, `effort: high`; expert-reviewer role,
three-axis procedure ending in per-finding evidence verification, severity-ranked
line-oriented return. Both drivers' implement check-gate now spawns it instead of running
`/check` ad-hoc; bound-agents hard rule + README (three→four workers)
updated. review left a standalone skill (user-triggered, verdict-producing).

Follow-up (fork docs read — a fork shares the parent's prompt cache because system
prompt + tools are identical, so it is CHEAPER than a fresh subagent when the work needs
existing context): **delegate rewritten** — Decide step 1 is now a three-row
route table (inline · fork · subagent) keyed on what each *gets* vs *costs*, with "fork
is the default when context is the payload" and the two things a fork can't give (fresh
eyes, a narrower tool fence); step 2 bound-agent-or-ad-hoc; step 3 **the 7-field template
DELETED** → four workflow-agnostic essentials (where · what · materials · done when) +
the compact-return rule. Both drivers' hard rule renamed "Bound agents first, and every
spawn carries its four essentials".

**Agents re-specialized**: renamed back to `tester` / `implementer` (now
explicitly React/TypeScript) and each opens with an expert role that activates domain
knowledge ("senior test engineer specializing in React and TypeScript — Vitest, RTL, MSW,
Playwright" with an opinion about what a test is worth; "senior React and TypeScript
engineer" who knows state placement, effect loops, stale closures, memo boundaries;
`auditor` = "staff engineer who specializes in reading unfamiliar systems
fast", stays language-agnostic). Bodies restructured from rule piles into **Operating
procedure** (numbered, ending in a self-check/verify step) → **Rules** (fences + stop
conditions) → **Report back**. User's frontmatter choices preserved (opus/low for the
auditor, memory: user for impl, permissionMode, colors).

**Skill descriptions rewritten** on the "what it does + when to use it" formula — all 9
skills (audit, requirements, design/plan/implement/test,
check, review, figma, delegate):
each now leads with the capability in plain terms, then names the concrete situations
that should trigger it.

Follow-up: **all three workers are stack-neutral roles** — `test-agent` / `impl-agent`
(renamed from react-*) carry only fences + return contract; the language specifics come
from the `skills:` frontmatter, which a profile swaps (react bundle preloads
test / implement). Both gained **audit** in
their skills list + a query/extend clause for behavior their contract doesn't carry
(never bulk audit, never broad re-reading). design SKILL.md now shows the usage inline
(step 2: `query "<what the decision needs>"` → miss → `extend <pointer>`; Inputs bullet
reworded to "Prior audits / component map"). **Drivers simplified** now that agents own
their procedures: phase playbooks condensed (preflight/requirements/clarify/design/qa
lost restated detail), phase loop tightened, Implement discipline compressed from a
4-step list + paragraph to one arrow line + one paragraph — my-specflow 150→133 lines,
oac 143→126.

Follow-up: auditor renamed **auditor** (language-agnostic — its skill always
was; body now says "language- and stack-agnostic" explicitly; drivers + README updated).
Layering restored: **domain skills name skills, never agents** — design/plan/implement
reference `/audit` directly and are **limited to query + extend** (bulk build
belongs to the caller's preflight): ground-truth § Audit back to the 2-step
query→extend form with "Design queries and extends only"; implement step 1 "never a bulk
audit here"; plan Inputs gained the same clause for facts design.md
doesn't carry; design SKILL step 2 reworded ("the atlas first; query/extend for what it
lacks"). Only the drivers name agents.

Follow-up (official subagent doc consulted — code.claude.com/docs/en/sub-agents):
renamed to **tester / implementer** + new **react-auditor-agent**; all
three rebuilt on documented frontmatter: `skills:` **preloads the bound skill's full
content at startup** (binding is now structural, not an instruction — the steadiness fix),
plus `model: sonnet`, `effort: medium`, scoped `tools:`, `color:`. Bodies carry only
fences + mode/procedure pointers + return contract (thin-binding rule holds). Auditor owns
audit end-to-end (build/query/extend selection, one-agent-per-build fence,
atlas-only writes), so drivers stopped hardcoding audit modes: preflight ② spawns it,
prior-artifacts rule asks it, ground-truth § Audit + implement step 1 ask it (standalone
skill invocation kept as fallback). delegate Decide restructured again:
1. delegate at all? · 2. **bound agent or ad-hoc?** (bound preferred — definition pins
fences/skill/model/effort/return) · 3. model+effort+skills+materials for ad-hoc only;
template gains "bound agents shrink this to four fields". Both drivers' hard rule now
reads "Bound agents first"; plan + README de-branded (TestAgent/WorkAgent
→ test/impl agent).

Superseded first cut: **dedicated batch agents built** — agents/oac-test-agent.md +
agents/oac-impl-agent.md, shared by both drivers (thin bindings, ~35 lines each): role
constraints in the system prompt (test files only / source only; never edit a test),
mandatory first action (invoke the bound skill — steadiness is now structural), pinned
`model: sonnet`, trimmed tools (test agent has no Bash — driver runs red/green; impl
agent keeps Bash for typecheck + targeted runs), line-oriented Report back, DESIGN GAP
per the skill's format (thin-binding rule: agents never restate skill content). Drivers'
Implement discipline is imperative ("Spawn oac-test-agent…"); spawn prompts shrink to
Working Directory · Materials · Responsibilities · Done When; "Every spawn is templated"
hard rule + delegate gained the dedicated-agents-embody-the-template carve-out;
README ORCHESTRATORS layer notes the pair.

Follow-up: **preferences.md trimmed for focus** (user: more rules = less focus) — 84 → 48
lines, 13 bullets → 7, four sections. Merged: Orchestrate + Route models + Cut batches →
one Delegate bullet (delegate owns the detail); Read-before-write → Simplicity-
first; Judge-behavior-first → Goal-driven; Refactor-to-unblock section → one clause on
Derive-don't-copy; Artifacts + Tokens → one section (Decisions-never-reasoning + Fixed
shapes merged). Dropped: Convention-beats-novelty (covered by derive-don't-copy + reuse).
Kept whole: the compounding gains — first principles, iteration budgets, judgment-authors-
search-verifies, token economy. Folding into root CLAUDE.md offered but not done (root
CLAUDE.md is empty + symlinked as global; load-path unknown → risk of double-loading).

Follow-up: delegate's Decide restructured as **three ordered calls** — 1. delegate
at all? (delegate/inline/fork criteria) · 2. choose model + effort (spawn parameters) ·
3. bind skills + slice materials (fills the template's Skills/Materials fields verbatim;
slicing rule now stated once here, template fields point at it). Delegate section = prompt
construction only. Description updated to match.

---

## Reference audit: ast-grep skeleton-first build + description formula

Audited sd0x-dev-flow (architecture, ask, code-explore, code-investigate, codex-architect
+ rules/) and agent-skill/ast-grep (ast-grep, outline) for transferable structure.

**Source → decision → reason (one line each):**
- ast-grep `outline` + structural `run -p` → **ADOPT** as build mode's deterministic
  skeleton → couplings/call-sites/dependents were judged-by-reading (grep false pos/neg);
  ast-grep makes them exact + bounds trace depth (user pain: "audit thinks too long/deep").
- ast-grep skill's own shape (pure instructional, no scripts) → **ADOPT the shape** → recipes
  live in build.md, not a scripts/ folder — distinct from the reverted P1/2/3 script infra.
- ast-grep no built-in fallback → **REJECT that gap** → we gate on `command -v ast-grep`
  (npx fallback) and degrade to grep, tagging the skeleton `(grep)`.
- sd0x description formula (`… Not for X (use alt). Output: <shape>.`) → **ADOPT** → adds
  negative routing + output contract so a driver routes without opening the body.
- sd0x References-table "When to Read" column → **REJECT (defer)** → elegant but low value
  until a skill has several references; we have one.
- sd0x inline `Agent({Input/Output/Constraints})` handoff → **REJECT** → our bound-agent
  4-field prompt + agent-owned return contract is leaner (no per-spawn restatement).
- sd0x decorative ASCII/mermaid, inline-prompt drift, stub rules → **REJECT (already avoid)**.

**build mode restructured skeleton-first** (references/build.md): three passes —
① Skeleton (deterministic, wide, cheap: `outline` for the export surface, `run -p '<sym>($$$)'`
for the caller chain, fact-touch-point queries for couplings) → ② Select the on-purpose
slice (skeleton = the depth cap; off-purpose = gaps, never read) → ③ Annotate only that
slice (the old trace rules, now scoped to selected flows). Couplings are found in pass ①,
not a second scan. Artifact note: skeleton fills the mechanical cells (Units touched, call
edges, Audited files), annotation fills GIVEN/WHEN/THEN/HOW — judgment authors, search
verifies. Capability-gated (`command -v ast-grep`, else `npx --yes @ast-grep/cli`), grep
fallback tagged `(grep)`. SKILL.md build bullet names the skeleton-first flow. code-auditor
-agent already has Bash + binds the skill, so it inherits this at build time — no agent edit.

**Description formula applied to all 12 skills** — appended `Not for <X> (use <alt>).
Output: <shape>.` to each; tightened the two verbose trigger-lists (review,
jira-align) in the same pass. Near-twin routing now explicit in-description:
check (no verdict) ↔ review (gates merge) ↔
audit (builds atlas).

**Follow-up (same session):** three tightenings of the skeleton work —
- **Language-agnostic** — recipes dropped the hardcoded `--lang tsx`; `--lang <L>` is picked
  per source. ast-grep-usage.md lists tsx/ts/js/jsx/**dart**/python/go/rust/java/c/cpp/kotlin/
  swift (the skill is "any language" — TS-only recipes contradicted that).
- **ast-grep-usage.md extracted** (42 lines) — availability gate + npx fallback, `--lang`
  table, metavariables, the three skeleton queries, and the inline-rule escape hatch. build.md
  § 1 shrank to the three passes + a pointer (progressive disclosure — the how-to loads only
  when a build actually runs).
- **Flow note slimmed** 8→6 always-on fields: **cut Diagram** (duplicates WHEN→THEN→HOW prose
  + index's Interaction map) and **cut Audited files** (duplicates index's Units touched + the
  inline `path:symbol` anchors); **folded Mechanism chain into HOW** (HOW already carries
  mechanism-per-hop; indirection is one clause there now). Core GIVEN/WHEN/THEN/HOW + Problem +
  Self-audit + the kind-specific field (Dependents|Preserve) untouched.

**Follow-up (same session):** mode gate moved into the procedure + `-h` as the authority —
- The `ast-grep` **availability check now opens build.md § 1** (not the usage ref): `ast-grep
  --version` → **ast-grep mode**; neither that nor npx resolves → **grep/read mode** (same
  three passes via Grep+Glob+Read, skeleton tagged `(grep)`). The gate decides which mode
  runs, so it belongs in the procedure; the usage ref only loads once ast-grep mode is chosen.
- ast-grep-usage.md dropped its Availability section and gained a **`-h` self-help pointer**:
  `ast-grep -h` / `ast-grep <command> -h` is the truth for flags when a form is missing or a
  command errors — trusted over the documented forms, which drift across versions.

---

## query+extend merged into self-healing query; build reframed Locate→Walk→Organize

Two user-driven changes to audit, applied together.

**Modes 3→2 (build + query); extend folded into query.** A query answers from the atlas
and, on a **scoped miss**, heals itself: declare a **reveal budget** (default 3
acquisitions) first, then loop — acquire the nearest fundable gap under build.md's Walk
boundary, re-check, follow a revealed on-path pointer, repeat until answered or budget spent
(iteration-budget discipline: the loop is declared, chained reveals allowed, spent → stop).
Answer from the union and name what was read (`healed via F3 §HOW, F7 §GIVEN`) so the
source reads + atlas growth are visible. **Broad miss / budget spent** → report gap + build
suggestion, never re-scan blindly. A bare **pointer** arg = proactive deepen (the old
extend). Acquisition folds back **best-effort** — persisted to atlas/ when the caller can
write, kept in the answer only when it can't → this preserves react-checker-agent's
read-only guarantee (no Write tool) while every writable caller still grows the atlas.

**build reframed to match manual exploration** (references/build.md): skeleton→select→
annotate became **Locate → Walk → Organize**, mirroring how a dev works — fast-locate the
entry by keyword, walk the definition graph outward *go-to-definition style* one hop at a
time (only where a purpose question is still open), organize the walked hops into flows.
Depth is bounded **during** the walk (jump on-purpose only), so the off-purpose graph is
never built — a cheaper, more faithful fix for "audit thinks too long/deep" than
sweep-then-prune. Same engine (ast-grep mode / grep fallback); ast-grep is now the
walk's go-to-definition tool (outline = where defined, `run -p` = who calls). LSP noted as a
more precise jump engine where available, not mandated (portability).

**Callers updated** for the merge: auditor (3 modes → build + self-healing
query), react-impl/test-agent gap step, both drivers' prior-artifacts rule, README atlas
line, implement/plan SKILLs, design ground-truth Audit step — all now "query (heals on a
miss)", no separate extend call. argument-hint + description de-extended. ast-grep-usage.md
retitled "structural walk queries" (§§ 1–2). "extends the blast radius" → "widens" to free
the word.

**Follow-up (same session):** grep + ast-grep reframed as complementary, not either/or —
prompted by ast-grep's own "when to use" (structural search, *not* text search). The old
build.md framed them as substitutable **modes** (ast-grep mode vs grep fallback); corrected
to a division of labor: **Locate** greps keywords to narrow the range (grep is the right tool,
not a fallback); **Walk** uses grep to find candidate references fast and reaches for ast-grep
**only when text is ambiguous** (common identifier in string/comment noise, call-by-shape,
a structural predicate grep can't express); ast-grep genuinely absent → grep-only walk, edges
tagged `(grep)` — the real fallback, and only for the structural step. ast-grep-usage.md
retitled "structural precision for the walk" with an explicit "for plain keyword-finding,
grep is faster — don't reach here." No more "ast-grep mode / grep mode" binary.

**Follow-up (same session):** audit skill simplified — deduplicated build.md ↔
ast-grep-usage.md and polished the procedure. Single-sourced each fact to its owner:
the **grep-vs-ast-grep decision** lives only in build.md § 2 (usage.md stopped re-arguing it
and is now a pure command reference — "*how* to run it; *when* is § 2"); the **try/catch**
example appears once (usage.md's inline-rule, where the command is); the **`(grep)` tag** is
defined once (Organize's tag-list, § 3) with Locate/Walk pointing to it instead of restating;
ast-grep command forms left in usage.md only (build.md carries concepts, usage.md commands).
Compressed build.md's intro (it restated its own § headings). Fixed a bug — `tsx` was listed
twice on the language line. build.md 125→121, usage 44→42; SKILL.md already lean at 58.

**Follow-up (same session):** auditor learns project conventions —
`memory: user` → **`memory: project`** (per the official scope table: project = shareable via
version control, no cross-project leak). The loose trailing "record a PATTERN" line became a
formal **## Memory — project conventions, as hints** section: consult before a build (warm the
Locate step), record durable conventions after (a rule + example anchor + last-seen; not
flow-facts — those are the atlas), and the guardrail the user set — **guidance, never the
source of truth**: memory biases where you look first, the grep-first walk still confirms, a
misfiring convention is corrected not trusted. Write rule carved out the memory dir; role para
+ description note the warm start. Shared skill: build.md § Locate gained one conditional
**Warm start** line (a no-op for a caller without conventions, e.g. react-checker-agent) that
pins the same hint-not-prune guardrail in the procedure itself.

**Follow-up (same session):** implementer memory formalized to match — its loose trailing
"record a pattern" line became a **## Memory — codebase idioms, for consistency** section,
parallel to the auditor's but role-specific: the auditor remembers *where code lives* (Locate
hints), the impl agent remembers *how this codebase does things* (state placement, data-
fetching/effect patterns, styling/error idioms, reusable units, cross-wave decisions) so its
`how` stays consistent. Same guardrail shape, different source of truth: **memory never
overrides the contract or a failing test** — those are the spec; a stale idiom is corrected,
not trusted. Description gained a matching clause. (`memory: project` was already set.)

**Follow-up (same session):** implementer memory reframed from "mirror the codebase's
idioms" to a **quality ledger judged against implement's rules** — the user's
concern that mirroring would enshrine project-wide bad practices. Now three entry kinds: (1)
good practices to reuse (match the skill's rules), (2) anti-patterns to avoid (bad practices
the rules flag — never copied for consistency), (3) pitfalls to route around (store re-render,
effect loop, stale closure). Standard = the skill's rules; truth = the contract + tests;
memory never enshrines a bad practice, never overrides a failing test. Role para ("decide the
how the way the codebase does things *well*, never its bad habits") and description reworded to
drop the mirror framing.

**Follow-up (same session):** both memory agents `memory: project` → **`memory: user`** — the
user found project scope writes into the repo's `.claude/agent-memory/` (committable, others can
mess with it). User scope is global (`~/.claude/agent-memory/`), so to prevent one project's
learnings bleeding into another's, both Memory sections gained a **"tag by project — apply only
the current codebase's entries"** discipline; the guardrails (hints-not-truth / rules-are-the-
standard) still hold. Descriptions + README bullets reworded "project-scoped" → "personal
memory, per codebase". (`local` scope — project-specific + git-ignored — was offered as the
alternative that fits "not committed" without the cross-project bleed; user chose user-level.)

**Follow-up (same session):** audit + auditor support a read-only
**external atlas** (a curated atlas outside the spec dir, for shared/stable code). Design:
self-describing — the **local** `atlas/index.md` declares its external baselines on an
*External atlases:* line, so any query auto-discovers them with no per-call path plumbing.
**Query reads local + external; build and heal write the LOCAL atlas only** — a flow that
lives only in an external atlas gets a local note citing the external origin (local overlays
external); on overlap, local wins (it holds this run's heals) and a material local↔external
disagreement is surfaced, not hidden. build.md: external atlases are an optional read-only
input (consult to skip well-covered flows, link instead of re-audit); index.md gained the
*External atlases* declaration line. Agent: build records the caller's external path in the
local index, query reads both, write rule now "write only the local atlas; external is
read-only — query it, never write it." README audit bullet notes the read-only baseline.

**Follow-up (same session):** external-atlas model changed from **federated query** to
**absorb-at-build** (user preference: absorb/rephrase relevant flows, then create + query one
own atlas). Now: when a caller supplies a read-only external atlas, **build absorbs its
on-purpose flows** into the local atlas — rephrased to this scope, anchors kept, tagged
`(absorbed <path>)`, with a Self-audit pointer so a high-stakes decision can verify against
current source — and audits source only for what the external doesn't cover (absorbing is a
rephrase, not a source read). **Query reads the single local atlas only** (reverted the
dual-index read + overlap/conflict handling). Reverts: SKILL query bullet/step 1/Acquire back
to local-only; build.md Inputs "seed you absorb, never re-audit"; index.md line "External
atlases: (query reads)" → "Seeded from:" (provenance); new `(absorbed)` tag in the Organize
tag-list. Agent: build absorbs, query local-only, write rule "read-only: absorb from it, never
write it." README audit bullet: "absorbs the relevant flows into its own, then queries the one
self-contained atlas." Net: simpler query, portable self-contained local atlas, external
consumed once as a seed.

**Follow-up (same session):** external-atlas reframed once more, absorb → **distill** (user:
the external saves time but doesn't reflect what *we* need, so we still audit ourselves, using
it to go faster). It is now a **map that speeds our own audit, not content to copy**: at build,
distill the external's entries / couplings / boundaries to skip the cold Locate and shortcut
the Walk (jump straight to its anchors), **but still Walk source and write our own purpose-
framed notes**. A peripheral flow we don't open can be carried as context, tagged
`(external <path>)` (a candidate until a read confirms it — parallel to `(grep)`/`(inferred)`,
no longer "trusted at its quality"). index.md line "Seeded from" → "Guided by"; Locate step
"Absorb" → "Distill"; agent build/​write-rule and README bullet updated. Same guardrail shape as
the conventions memory: a rich hint that accelerates where you look, never authority that
replaces the audit.

**Follow-up (same session):** external-atlas distillation made concrete — a persisted
**`atlas/references/` tier**. The auditor now **audits the external atlas itself**: cherry-picks
the purpose-relevant flows into `atlas/references/<flow>.md` (headed `— external, from <path>`,
trimmed), uses them as the Locate map (entries, couplings, boundaries), then **still Walks
source and writes its own top-level notes** for its purpose, citing the reference. A cherry-
picked flow it doesn't re-audit stays a reference only and answers queries tagged `(external)`.
So the external's contribution is persisted + clearly separated from our source-read notes, and
portable (no dependency on the external path). Threaded through SKILL (intro/build/query),
build.md (Distill step + references/ artifact entry), agent build step, README bullet.

---

## audit: frontmatter-routed query · ast-grep removed · distill mode

Three simplifications, plus adopting the user's new atlas templates.

**New templates.** Flow notes gained YAML frontmatter (`id`, `title`, `keywords`, `outline`,
optional `source`) — the `## Problem`/`Abstract` body section folded into `outline:`. index.md
restructured (`# Atlas` / `<scope>` / `<purpose>` / `## Index` table / `## interaction map` /
`## Gaps`).

**1. Query streamlined via frontmatter.** Was: match index → open notes → Dive-pointer chase →
heal. Now three crisp steps: **Find** (match the question against flow `keywords`/`outline`,
grep the frontmatter across `atlas/*.md`) → **Answer** (open the matched note whole; reading it
beats pointer-chasing) → **Miss → heal** (reveal-budget loop, unchanged). Fewer reads, no
choreography.

**2. ast-grep removed entirely.** Deleted references/ast-grep-usage.md; Locate/Walk now grep +
glob only (grep the symbol, read the enclosing unit); dropped the availability gate, the
grep-vs-ast-grep tool bullets, and the `(grep)` tag. Reason: dependency + capability gate + a
whole reference file for benefit that never materialized (never even installed).

**3. External atlases → a `distill` mode (chose Option B over A).** Skill is now
**build | query | distill**. `query` is pure local + heal, ignorant of externals — the local
atlas stays intact. `distill <external path> · purpose` (references/distill.md, ~20 lines) is a
fast quick-start: cherry-pick purpose-relevant external flows, rephrase into **ordinary local
flows** marked `source: distilled from <path>`, no source read; query heals them against source
on demand, build deepens any that need it. Dropped the `atlas/references/` tier entirely (it
broke atlas intactness). Chose Option B (distill as a skill mode) over A (distill as agent
logic) to keep the agent thin — procedure lives in the skill, not the agent body. Agent modes
build|query|distill; agent keeps query (core to its blast-radius charter). README mechanism
bullet "grep to narrow, ast-grep to sharpen" → "grep + glob to locate and walk"; audit companion
bullet rewritten for distill-as-mode. Net sizes: SKILL 70→54, build 145→109, ast-grep-usage (42)
deleted, distill +20.

**Follow-up (same session):** auditor repositioned as an **atlas initializer** —
`query` removed from the agent (querying is light + inline: the skill's `query` mode, run by
whoever needs an answer — drivers/impl/test/checker already call it directly). Agent modes are
now **distill → build**, and they **co-exist in order**: when a curated external atlas is
provided, distill first (fast, external-derived local flows), then build, which is **warmed by
the distilled flows** (their entries/couplings/boundaries map where to look) and **deepens them
in place** (verify from source, drop the `source: distilled` mark; never duplicate) while
auditing source for what the external didn't cover. Description/role/report-back reframed from
"answers questions" to "stands up / initializes the atlas"; build.md Organize gained a
**Deepen, don't duplicate** rule; README companion bullet reworded (initializer; query inline).

**Follow-up (same session):** driver preflight reordered — **audit first, then the command.**
Both drivers now: ① spawn `auditor` to build `atlas/` for the feature scope (distill
first if a curated external atlas is provided), ② run `/sf-preflight`|`/spec-preflight`, which
**queries the atlas** (`/audit query`) to scope faster and better, ③ write
preflight.md. This makes preflight the one exception to the "command runs first" rule (noted
in each playbook intro: "except preflight, which builds the atlas first so the command can query
it"), because the command benefits from the atlas rather than the reverse.

---

## sf-* commands consolidated into one `/specflow` skill

User decision: fold the 8 `sf-*` process commands into a single skill invoked `/specflow <phase>`;
fully replace (no `/sf-*` aliases). **skills/specflow/** now holds `SKILL.md` (dispatcher:
`argument-hint "<phase> [instructions]"`, phase table → per-phase references, shared conventions
lifted once — `.meta.yaml` statuses, artifact location, exit-is-a-gate, stack-neutral) +
`references/{init,preflight,requirements,design,tasks,implement,validate,qa}.md` (the old command
bodies verbatim, minus per-file frontmatter, `# sf:<phase>` → `# <phase>`, `/sf-*` cross-refs →
`/specflow`, loaded one-at-a-time). Old `specflow/commands/` deleted; `specflow/README.md` moved to
`skills/specflow/README.md`.

**Rewired:** my-specflow-driver — every `/sf-<phase>` → `/specflow <phase>`, frontmatter/Setup/intro
prose, and the hard rule ("`/sf-*` commands only" → "The `/specflow` skill only — its phases: init …
qa"). oac-driver untouched (drives external `/spec-*`). **Install simplified:** the
command pair `link-commands.sh`/`unlink-commands.sh` retired (specflow is a skill, auto-linked by
link.sh); link.sh/unlink.sh comments + root README (Installing table now one pair, Layout,
drivers mention, workflow-doc pointer → skills/specflow/README.md) updated.

Rationale for skill-over-command (chose Option B): unifies the bundle (last non-skill layer
gone), enables progressive disclosure (dispatcher + on-demand phase reference), cleaner namespace.
Trade noted: skills auto-advertise vs inert commands — mitigated by a description scoping it to
"driver-sequenced, not auto-selected."

**KNOWN-STALE, deferred:** skills/specflow/README.md (229 lines) still documents the removed
`workflow.yaml`/`sf-react-workflow` generator system (drivers are `.meta.yaml`-driven now) AND
the old `/sf-*` commands — needs a dedicated rewrite to match reality, not a mechanical swap.

**Follow-up (same session):** specflow phase files simplified + unified + relocated
`references/` → **`phases/`**. One template across all 8: `# <phase>` → 1–2-line purpose →
**Writes** · **Reads** (`/specflow <producer>` if missing) → **Steps** (labelled, terse) → **Exit**
(the gate). Per-phase repeats of shared conventions (repo-read-only, `.meta.yaml` statuses,
steering) dropped — they live once in SKILL.md. Sizes: 19–31 lines each (was up to 50); total
243 → 181. SKILL.md links repointed to `./phases/`, root README layout updated. (Note: the linter
had deleted the working-tree copy of skills/specflow/README.md mid-session — restored from the index;
it remains the stale workflow-generator doc, still awaiting a dedicated rewrite.)

**Follow-up (same session):** specflow phases de-coupled from stack-specific artifacts. `contracts/`
is produced by a language-specific skill (`design`), so the stack-neutral phases
must not cite it. Generalized: SKILL.md convention now states "a phase names only its own
stack-neutral artifacts; stack-specific inputs (per-unit contracts, a code atlas, a design
decomposition) arrive as **optional caller-provided materials**." Phase bodies reworded —
`contracts/<unit>.md` → "per-unit interfaces / unit interface"; design/tasks/implement `Reads`
lines list `requirements.md`/`design.md` + "optional caller materials (the per-unit interfaces)";
design no longer `Writes` `contracts/` (it's the stack skill's output, asserted as an Exit
outcome). validate's design-consistency check now reads "every provided unit interface traces to
≥1 AC". The driver's React playbook still binds `/design` → `contracts/` — the
correct home for the stack artifact. Phases stay ~30 lines (181 total, unchanged).

**Follow-up (same session):** two fixes. (1) `references/design-units.md` — the design
decomposition (Figma → EXISTING/PARTIAL/NEW unit map) produced by the `figma` stack
skill — was the same stack-specific leak as `contracts/`, missed last pass. Generalized:
preflight no longer *writes* it (the stack decompose skill does, via the driver) and consumes it
as an optional caller material; preflight dropped its "Decompose" step (folded into Survey:
"reconcile with a provided design decomposition"); requirements reads "a design decomposition"
not the path. SKILL.md table cell "per-unit contracts" → "per-unit interfaces". The specflow skill
now has zero stack-specific artifact names. (2) my-specflow-driver phase intro now states the
explicit invocation **`/specflow <phase> <optional instructions>`** and that the driver hands each
phase its inputs + optional caller materials (atlas, contracts, design decomposition) as those
instructions — which is exactly how the "caller-provided materials" reach the stack-neutral phase.

**Follow-up (same session):** steer requirement/design toward `/audit query` over
self-grep (user saw the agent grepping the codebase directly). Root cause: requirements had
NO query directive (atlas was a passive "input"), and design's directive was buried in
ground-truth.md. Fix — a prominent, positively-framed callout at the point of temptation, added
to both requirements and design SKILL.md (identical, self-contained per the
duplicate-don't-reference rule): **"Query the atlas, don't grep the code."** Any existing-behavior
fact → `/audit query` first (the preflight atlas answers or heals); grep/read source
only for units you're authoring or after a query gap it can't heal; greenfield → skip.
requirements Inputs/step-1 reworded from "audit notes" → "the atlas (query it)". Backstop:
both drivers' "Prior artifacts are authoritative" hard rule gained "**Existing code is reached
through the atlas** — query it, never a self-grep of the codebase to learn existing behavior"
(covers every phase). plan/implement already carried query-first directives — left as-is.

**Follow-up (same session):** query-first guidance reframed on two points. (1) **existing OR
legacy** — the atlas covers both `kind: existing` and `kind: legacy`; callouts + driver rule now
say "existing or legacy code," not just "existing." (2) **grep is welcome, guided by the query's
pointers, not a last resort** — the user's correction: a query answers AND returns `Dive:`
pointers (path:symbol), and following those to grep for depth is the encouraged second step. Both
skill callouts retitled "Query the atlas first" (positive, non-prohibitive): query first → it
hands back `Dive:` pointers → grep/read to ground deeper detail along them, never a blind scan.
Driver rule reworded to match ("its `Dive:` pointers then guide any deeper grep/read"). query.md
Answer step now formally emits a **`Dive:`** line of path:symbol pointers for grounding detail.

**Follow-up (same session):** query-vs-grep reframed from "query first" to a **tool choice**
(user: grep directly if it helps more; query first only to locate a *range* of facts, then dive
into the narrowed range with grep). New shared line **"Query narrows, grep grounds"** in both
skill callouts + both driver rules: a known symbol/string → grep directly (faster); a range of
existing/legacy facts (which flows touch X, who writes a fact, how a flow behaves) → query first
to narrow to the relevant flows + `Dive:` pointers, then grep *within that range* — the anti-
pattern is only the blind full-codebase scan, not grep itself. Greenfield → grep.

**Follow-up (same session):** requirements-phase query made phase-appropriate. User: requirements
*typically doesn't query* (it recovers the problem from the request + first principles); query
helps specifically when an ambiguity/open question turns on existing/legacy behavior — query
before blindly asking the user, since the atlas may already answer it. requirements callout
reframed "Query narrows, grep grounds" → **"Query only to settle an open question"** (usually no
codebase; query a code-dependent ambiguity *before* it becomes a user question — don't ask what
the atlas answers). Step 1 query made conditional ("when it turns on existing/legacy behavior");
step 3 now queries a code-dependent gap before it becomes a question ("only what it can't settle
becomes a question"); Inputs atlas note softened to "settle a code-dependent open question".
design keeps the general "Query narrows, grep grounds" callout — design genuinely
wires into existing code throughout. Driver backstop unchanged (general principle).

**Follow-up (same session):** implementer memory over-saved feature-specific detail (user
showed the actual store: an 11KB `project_oac_acmt2681_search_data.md` named after a ticket, and a
5.5KB bloated pitfall — vs two good concise ones: git-stash-in-worktrees, mirror-the-by-id-SDK
pattern). Guidance sharpened: section retitled "Memory — general rules, not feature cases"; added
a **generalization test** ("would this help a *different* feature in this codebase? No → don't
save"), the entry shape "a general rule + one short example anchor (a few lines, not a case dump)",
and an explicit ban — **never a ticket- or feature-named entry** ("if you can't state it as a rule
that outlives this feature, it isn't memory"). Closing changed to "record only the durable,
generalizable entries". Existing bad entries in the user's store flagged for pruning (offered,
not deleted unprompted).

---

## architect — dedicated design-phase agent

User request: a design-phase agent, motivated by memory. Design was the only heavy, high-judgment
phase with no dedicated agent (ran inline in the driver → couldn't accumulate memory). Built
**agents/architect.md** (thin binding): staff-architect role; skills design-react-
contracts + audit; tools Read/Write/Edit/Grep/Glob/Bash; model sonnet, effort high
(design is the highest-judgment phase — opus is a one-word bump); memory:user; color blue.
Procedure: scope → ground truth from the atlas (query narrows, grep grounds) → run
/design (consult memory first) → self-check once. Rules: design artifacts only
(never code/tests), derive-from-requirements-not-shape (refactor proposals raised at the gate),
query-don't-blind-scan, raise-don't-resolve (human gate owns approval). **Memory carries the
just-sharpened anti-feature-dump discipline** — architectural conventions only (state placement,
layering, reusable units), general rule + short example, never a ticket/feature-named entry; this
is the third complementary memory (auditor=where code is, architect=how it's structured,
impl=how it's built). Wired: both drivers' design step ② now **spawns architect**
(was inline /design) → design.md + contracts/ + draft journey plan; ③ gate presents
its refactor proposals + open items. Both drivers' bound-agents roster gained it. README: design
entry gained the companion bullet; worker count 4 → 5.

**Follow-up (same session):** architect memory reframed (same fix as impl-agent's).
User: a codebase may have bad architecture — don't save it as a convention to follow; save it as a
**bad practice to steer around**. And memory is a **tradeoff accelerator, not a mandate to
conform** to existing shape. Section retitled "Memory — faster tradeoffs, general not feature
cases"; now a **decision aid judged against design's rules, not a mirror of how
the codebase is built** — three kinds: good practices to reuse · bad practices to avoid (steer
around, never copy for consistency) · recurring tradeoffs (how a repeated decision went, for speed
+ consistency). "consult to move fast, not to conform"; requirements are the standard; a
bad-practice entry is a warning not a template. Description + procedure step 3 + README bullet
reworded off "conventions/conform" onto "what works / what to avoid / faster tradeoffs".

---

## Full-bundle audit round: self-check dedup · coherence fixes · role-sharpened memories (2026-07-22)

Fresh-eyes audit (refs/rules subagent + best-practices research subagent + inline SKILL/agent
review). User kept `spec-qa` in the `.meta.yaml` ledger deliberately (project convention) — the
specflow naming findings were NOT applied.

**1. Self-check dedup — cut from the agents, kept in the skills.** The design check existed 3×
(skill self-check · architect step 4 · specflow design gate) and test/impl 2× each. Cut landed on
the agent side because the skill is preloaded anyway (zero context saved by moving it), skills
stay standalone-invocable, and thin-binding forbids agents restating skill procedure:
react-architect step 4 → "the preloaded skill's self-check (ONE pass) is your final gate; report
its verdict"; react-test step 4 → "run the preloaded skill's self-check over the whole batch";
react-impl step 4 → "the skill's done-condition verify, targeted runs only". The specflow design
phase's architecture gate stays — stack-neutral *exit criterion* vs the skill's *method* check,
different layers.

**2. Coherence gap closed — qa-journey-plan.md now has an author on the react path.** The
architect + both drivers promised a draft journey plan the design skill never produced.
design Output gained the `qa-journey-plan.md` (draft) bullet (journey-level ACs
only; J-<n> · covers-ACs · NEW|MODIFY · NOT-automated table; caller's gate approves), step 2 +
description updated to match.

**3. Stale/garbled fixes.** design SKILL step-mapping ("Steps 1–3/4–5" → "Step 1 / steps 2–3");
references/design.md title (step 4/5 → 2/3) + "SKILL.md step 6" → step 4; both drivers' garbled
submodule clause → one clean `--init && --remote` conditional; impl agent step-3 grammar + stray
blank line; implement SKILL broken quoted-query line.

**4. Within-skill dedups.** e2e-testing Traceability now cites test-quality's label rule instead
of restating it (test SKILL step 3 now loads test-quality for e2e too); references/design.md's
God-unit line → a citation of services-and-boundaries; jira-align Rules bullet 1 compressed to
"Confirm-first, two writes only (steps 5–6)" (procedure owns the detail); check-react-
implementation description dropped its duplicated findings clause (Output clause keeps it).
**Accepted duplication (recorded, kept):** design rules ↔ implement rules share ~5 rules at
different altitudes (boundary decision vs code shape) — deliberate per skill self-containment;
likewise review/quality.md's one-owner-per-fact restatement.

**5. Memories role-sharpened (subagents only, not drivers).** Common shape: scope+tag line →
role-specific save-list → entry shape + generalization test → an explicit **don't-save pointing
at the owning artifact** → consult/record moments + standard-of-truth → new "MEMORY.md ≤200-line
index" cap (only the first 200 lines are injected — from the subagent docs). Role split:
**auditor** = where code lives (layout conventions, entry-point registration, boundary surfaces;
never flow facts — atlas owns those) · **architect** = faster tradeoffs (recurring tradeoffs
first, good practices, bad-practices-as-avoid; never feature designs — design.md/contracts own
those) · **impl** = quality ledger (good practices, anti-patterns-as-avoid, pitfalls incl.
test-harness traps; never contract/task facts — contract+tests are the truth).

**6. Best-practices research (source → decision → reason).** Adopted: MEMORY.md 200-line
injection cap (docs → memory sections) · 1,536-char description listing cap (docs → new
.claude/CLAUDE.md "Descriptions fit the listing" rule; longest description ~740 chars, safe).
Noted, no change: skill-listing context budget ~1–2% of window (12 skills ≈ 8k chars, healthy).
Rejected: `disable-model-invocation` on specflow (the driver IS a model — it would block the
driver's own `/specflow` calls; known bug also blocks manual invocation) · `mcp__*` tool patterns
(no need) · dynamic-context `!cmd` injection guidance (not used) · fewer-focused-agents advice
(already our shape).

**Model note:** user set architect to `model: opus, effort: medium` directly
(aligning with the opus standardization); left as the user set it.

**Follow-up (same session):** two agent refinements. (1) **tester gains `memory: user`**
— the harness knowledge (custom render wrapper + provider stack, MSW server/fixture helpers,
where fixtures live) and harness pitfalls (mock-helper clobber, fake-timer quirks, racing async)
are durable per-codebase facts that compound across batches; the best pitfall entries in the
user's existing store were test-harness ones saved by the impl agent — they belong with the test
author. Same memory shape as the other three (tag-by-codebase · save-list · generalization test ·
don't-save: contract facts/AC specifics — assertions derive from the contract, never memory ·
≤200-line index). Description + procedure step 3 (consult before authoring) + README bullet
updated. **react-checker-agent deliberately stays memory-less** — fresh-eyes + evidence-only is
its charter; remembered priors are exactly the bias it exists to exclude. (2) **Role openers
sharpened on one shape** — every agent starts "You are <identity>. Your role: <the one
responsibility + its hard boundary>" then the judgment flavor; procedures stay in the body. All
5 workers updated (test: independent proof of contracts, not the implementer · impl: make failing
tests pass, tests never editable · checker: fresh-eyes verdict, report never fix · auditor:
initialize the atlas, read never change · architect: own the design phase, artifacts never code);
both drivers' Role sections now open "You are a pure orchestrator… you decide, verify, and
record; you never do the heavy work yourself" (the duplicated decides/verifies sentence later in
the paragraph removed).

**Follow-up (same session):** role openers reframed as role-play priming (user: "you are the
expert, you are the best at that — keep telling what strengths it is good at"). New shape:
**elite identity → enumerated strengths ("Your strengths: …", concrete craft abilities that
activate domain knowledge) → judgment flavor → "Your role:" responsibility + hard boundary
(moved last as the punchline)**. All 7 agents: auditor "renowned for reading unfamiliar systems
faster than anyone" (entry-point spotting, graph-walking, rabbit-hole sense, naming the unread) ·
architect "the one the team brings in when structure is the hard part" (fact placement, boundary
sense, one-way deps, refactor-vs-bend in one read) · test "elite… Vitest/RTL/MSW/Playwright hold
no secrets" (the assertion that catches the real bug, stub-smell, seam driving, deterministic
suites) · impl "at the top of the craft" (state placement, effect loops, stale closures, memo
boundaries, diffs that read like they were always there) · checker "the reviewer teams request
when they need the truth" (forbidden deviation, unreachable state, silent catch, dead memo,
ranking what matters from what itches) · both drivers "master orchestrator — your strength is
judgment, not labor" (sequencing, precise handoffs, mechanical verification, knowing when to stop
for a human). Boundaries and procedures unchanged.

**Follow-up (same session):** role openers compressed to 2–3 sentences each (user: keep simple).
Fixed micro-shape: sentence 1 = elite identity + the strengths list folded in as a colon clause ·
sentence 2 = the one judgment stance · sentence 3 = "Your role: <responsibility> — <hard
boundary>". Cut the standalone "Your strengths:" enumerations and secondary flavor lines; no
strength, stance, or boundary was lost — only prose. Drivers likewise 3 sentences (persona+
strengths+subagents · where process knowledge lives · Done condition).

---

## E2E split · gap-repair loop · command-free driver A/B (2026-07-23)

Four decisions from the cooperation discussion (user set direction on 1–2; 3–4 from the prior
recommendation round).

**1. E2E timing settled: plan before, author after.** The design-time journey plan (approved at
the design gate) is the test-first artifact; e2e tests are its mechanical projection, authored
after implementation assembles the feature — red-first e2e would sit red all phase giving no
per-wave signal. Unit tests remain the red-first per-wave signal.

**2. e2e built (user override of the one-agent-two-scopes recommendation).**
`rules/e2e-testing.md` MOVED into the agent body (harness/happy/forced-error/traceability rules +
examples); test is now **unit-only** (description, no argument-hint, no scope
section, steps renumbered, e2e rules bullet gone; the unautomatable-journey steer bullet moved
with the rules). tester de-scoped to unit (no Playwright, no `<variant>`). New agent:
tools without Bash (driver runs the suite), skills audit, opus/low, `memory: user`
(app-mount harness conventions + journey-test pitfalls; the plan is the spec — never journey
specifics), color cyan. **Accepted duplication (recorded):** the label/observable-outcome/
mutation-litmus/determinism essentials now appear in both test-quality.md and the e2e agent —
the price of a self-contained agent. Fixed the who-authors gap: both drivers' implement ⑤ now
spawns e2e (was a bare "/test e2e, author + run" with no author).

**3. DESIGN GAP repair loop wired (the missing cooperation edge).** All drivers' Implement
discipline: *ambiguity* → impl agent's narrowest-safe + raise stands; *friction/defect* → spawn
architect on the design skill's **fast path** (Materials: gap block verbatim +
affected contract + atlas/) → contract delta presented to the human → on approval the affected
task re-runs as a fresh test+impl pair. Architect description gained the second trigger; both
rosters gained e2e + the architect's repair duty. Also decided: test stays a
skill, NOT folded into agents — `skills:` preload already IS the fold token-wise; folding would
kill standalone use and rules modularity.

**4. driver built — the command-free A/B twin.** Hypothesis: the process shell
(/specflow SKILL + phase files, ~220 lines loaded per spec) restates what teammates' skills own;
dropping it should cut input tokens at equal quality. Design: same phases, same `.meta.yaml`
template (spec-qa key kept — user convention) and artifacts, so specs are driver-interchangeable;
playbooks embedded in the agent (incl. the init scaffold + ledger template — no /specflow init);
driver authors the thin artifacts itself (preflight.md, qa-report.md, clarify Q&A) and KEEPS the
domain skills for driver-authored phases (/requirements, /plan,
/figma) — they're know-how, not process shell; dropping them would change two variables
at once. New hard rule "No process commands — this driver IS the process". Accepted risk: a third
playbook copy to reconcile — temporary by design, like prior A/B twins. README: three drivers,
6 workers, e2e + gap-repair in the implement flow line.

**Follow-up (same session):** driver artifact location pinned. Init names the
binding `$SPEC_DIR = .specflow/specs/<name>/`; the playbook intro now enumerates every phase
artifact as `$SPEC_DIR`-resident and requires every subagent prompt's output destination to be a
`$SPEC_DIR` path (implement writes source + tests only, never a spec artifact elsewhere);
auditor/architect spawns name `$SPEC_DIR` outputs explicitly; the Verify step mechanically fails
an artifact written anywhere else (move in → re-verify).

**Follow-up (same session):** driver made self-contained (user: isolated, lean,
focused). Description rewritten off the A/B-twin framing onto what it is (own playbooks over a
.meta.yaml ledger, teammates for heavy work, thin artifacts authored itself); Role and the
"No process commands" hard rule dropped every /spec-* and /specflow mention — the rule is now
"The playbooks ARE the process — never substitute outside workflow commands or skills." The
agent no longer references any other driver or workflow. (README keeps the experiment context
for humans.)

---

## Blast-radius test coherence chain (2026-07-23)

User-found gap: features touching existing units forgot that EXISTING tests in the blast radius
(of the units and their importers) may need updating — they broke or stayed stale until the
spec-qa full-suite run. Root causes: the specflow design phase *described* a blast-radius section
but design never authored one (so it never existed under the react path, and
was fully absent under the lean driver); plan never projected flagged tests into work; the impl
agent can't touch tests; and the "tests are never edited to make code pass" rule deterred the
legitimate update. Fix = the same chain as the journey plan's NEW|MODIFY dispositions —
**design discovers → plan projects → test agent executes → checker verifies**, one owner per
step:

1. **design** — design.md gains **§ Blast radius**: reverse-import closure of
   MODIFY/REPLACE units → their existing tests, each dispositioned KEEP (behavior preserved) |
   UPDATE (asserts superseded behavior — cite the AC) | DELETE (covers removed behavior); may be
   empty, said so. Self-check "Blast radius closed" now also requires a disposition per listed
   test; SKILL Output bullet updated.
2. **plan** step 3 — every UPDATE/DELETE row lands as an
   `Update: <test path> (AC-x.y)` marker on the owning task (parallel to the Edge marker), so
   existing-test updates are planned test-batch work, never a QA surprise.
3. **test** step 2 + **tester** step 3 — execute Update markers:
   rewrite the named existing test to the amended AC / remove on DELETE; material changes
   surfaced in the report, coverage never dropped silently. Runs pre-red, so the byte-unchanged-
   since-red guarantee is untouched.
4. **check** behavior axis — new check: dispositions executed (an
   UPDATE-flagged test still asserting the old behavior, or a broken KEEP test, is a finding).
5. **All three drivers** — the "Tests are never edited to make code pass" hard rule gains its
   one exception: a design-flagged blast-radius UPDATE/DELETE executed by the test agent
   pre-red is spec work; ad-hoc edits to green failing code remain forbidden.

**Follow-up (same session):** atlas format enforcement (user saw README.md instead of index.md
and flow notes missing frontmatter). Root cause: templates described the format but nothing
checked it before returning. Fix on "judgment authors, search verifies":
- **build.md** — new **File contract** paragraph opening the Artifact section (exact names:
  `atlas/index.md` never README/SUMMARY + one `<flow-id>.md` per flow) carrying the RUNTIME
  reason that makes an LLM comply: index.md is the always-loaded routing tier and query greps
  `^(id|title|keywords|outline):` — a misnamed file is never read, an unfrontmattered note is
  invisible to every query. New closing **§ Format check** — two mechanical commands (`ls atlas/`
  + `grep -L '^id: ' atlas/*.md | grep -v index.md` must print nothing) + index-rows ↔ flow-files
  one-to-one; fix before returning.
- **query.md** heal + **distill.md** step 3 — writes conform to build.md's templates and finish
  with its Format check (one clause each).
- **auditor** — new rule "The atlas format is the contract" (fix violations, never
  report around them) and Report back now REQUIRES `format check: PASS` — a run that can't pass
  it isn't done, giving the driver a mechanical token to verify against.

**Follow-up (same session):** the format drift's deeper cause reconciled — the flow-note body is
feature-shaped (GIVEN/WHEN/THEN needs a trigger→outcome), so architectural content (layering,
routing setup, state-management organization, DI/service mechanisms) fit nowhere and the auditor
abandoned the whole format, envelope included. Fix: **envelope/body split**. The envelope (file
naming + YAML frontmatter) is the query-routing contract and never varies; the body now has two
legitimate shapes — **feature note** `F<n>` (GIVEN/WHEN/THEN/HOW, unchanged) and **architecture
note** `A<n>` (STRUCTURE — participants + dependency direction · MECHANISM — the generic pathway
a fact travels, per hop anchored · RULES — invariants + where new work attaches), sharing the
conditional tail (Dependents/Verdict · Preserve/drop · Self-audit pointers). Organize gained the
routing rule ("content fitting neither body → split the note, never abandon the envelope");
index template shows an A-row; SKILL description + build bullet name both shapes; distill
rephrases into the matching shape; auditor rule routes ill-fitting content to the architecture
shape instead of a free-form file. Format check unchanged — it validates the envelope, which is
shape-invariant by design.

**Follow-up (same session):** audit skill reorganized (user: extract format contracts, allow
nesting, keep procedures concise). (1) **references/formats.md extracted** — all artifact
contracts in one file: file contract, INDEX.md template, shared frontmatter, both note bodies
(feature F<n> / architecture A<n>) + shared tail, and the Format check; every writing mode
(build · distill · query-heal) points here, stated once. (2) **build.md is procedure-only**
(Locate → Walk → Organize + a formats.md pointer; the duplicated template block and its
narration removed). (3) **Nested folders allowed inside atlas/** (`flows/`, `arch/`, a domain
per folder) with **INDEX.md as the single manager**: every note has exactly one Index row
carrying its relative File path (new File column), no per-folder indexes; query's frontmatter
scan and the Format check went recursive (`grep -r --include='*.md'`, `find atlas`).
(4) **index.md renamed INDEX.md** (user: better identification among atlas files) — swept
across SKILL.md, all references, and the auditor agent; the file contract + auditor rule pin
the exact name. SKILL build bullet now points at build.md (procedure) · formats.md (contracts).

**Follow-up (same session):** two formats.md refinements. (1) Architecture notes REQUIRE mermaid
diagrams: STRUCTURE = a `graph` (participants + dependency direction, nodes anchored; prose only
for what the diagram can't carry), MECHANISM = a `sequenceDiagram` of the generic pathway, per
hop anchored. (2) INDEX.md's interaction map may split into several diagrams when one would be
unreadable — by connected component, domain, or around a hub, each titled one line; a note
appears in every diagram it couples into.

**Follow-up (same session):** atlas write-location rule pinned — `atlas/` lives under the
**invoking project** (current workspace), even when the audited code is elsewhere (auditing
project A from workspace B → atlas under B); a caller-designated dir overrides; anchors keep
pointing at the audited source wherever it lives; never write into the audited codebase. Stated
in formats.md § Files (Location paragraph) and folded into the auditor's write rule. Drivers
already comply structurally via `$SPEC_DIR` under their own worktree.

**Follow-up (same session):** note file naming — `<id>-<short-name>.md` (id + meaningful kebab
name: `F3-device-selection.md`, `A1-state-management.md`) replacing bare `F3.md`/`A1.md`;
formats.md § Files + INDEX template examples updated. Format check unaffected (recursive greps
match any *.md).

---

## 2026-08-01 — Plugin packaging (breaking)

Repo restructured from symlink-installed bundle → **Claude Code plugin marketplace**
(`.claude-plugin/marketplace.json`) with two independent plugins: `plugins/my-react/`
(all React/TS skills + 3 drivers + 6 workers) and `plugins/my-flutter/` (fl-* skills +
in-plugin `rules/`). Decisions:

- docs plugins.md/plugins-reference → adopted marketplace + per-plugin `.claude-plugin/plugin.json`;
  namespacing (`/my-react:<skill>`, `my-react:<agent>`) is the conflict fix that motivated
  the change → all cross-references (agent `skills:` preloads, `/specflow` invocations, worker spawn
  names) rewritten to namespaced form, since preloading draws from the same name set as the
  Skill tool.
- plugins-reference "CLAUDE.md at plugin root is not loaded" → rejected shipping
  `rules/preferences.md` in a plugin; it stays a user-level file, manual symlink documented.
- flutter rules "linked into .claude/rules/" wording → replaced with in-plugin
  `${CLAUDE_PLUGIN_ROOT}/rules/` reads (plugins can't install ambient rules).
- link.sh/unlink.sh removed; migration guide in README (old unlink retrievable from git history).

**2026-08-01 (later):** plugins renamed `my-react` / `my-flutter`; skill `sflow` → `specflow`;
install.sh added (claude plugin CLI). Reconciliation audit: dead `/locate-bug` → inline bounded
root-cause pass (3 drivers); oac dangling "taskstoissues skip above" reworded; review
`conditional/performance/` → `performance/`, "13 core" → 11, `core/widget-{theming,build-discipline}.md`
→ `performance/` (files live in implement, symlinked); `engineering-discipline` rule cites →
`review-procedure.md § Pass 3h` (file no longer exists); flutter load directives + router
descriptions namespaced; cross-skill rule paths anchored to ${CLAUDE_PLUGIN_ROOT}. Rejected
(verified valid): specflow ledger keys clarify/spec-qa (driver-led phases, by design);
review references/{core,forensics,performance,...} (intra-plugin symlinks resolve).

**2026-08-01 (later still):** removed `my-specflow-driver` + the `specflow` phase skill — the
lean driver (self-contained playbooks) and oac driver (external /spec-* commands) are the two
drivers; the process shell proved redundant. `review/references/specflow.md` kept
(local axis file, not the skill). install.sh → install.py (same flags, argparse).
**2026-08-01: plugins renamed `my-react` / `my-flutter` (distinguish from project-owned plugins); all namespaced refs updated.**

**2026-08-01: skill names shortened** — the plugin namespace carries the tech, so
`my-react:design` replaces `design-react-contracts`, etc. my-react: audit · requirements ·
design · plan · test · implement · check · review · figma · delegate · jira-align.
my-flutter (fl- prefix dropped): acceptance-criteria · design · implement · review · riverpod ·
tasks · test-contract · test-forensics. my-flutter/review reference symlinks re-pointed.

---

## 2026-08-01 — Evaluation framework (Goal 2)

Score-based evaluation for the my-react design/implement/check family: anchored 0–4 axes,
DEDUCT-with-evidence, verdict from axis minima, author self-score re-derived by the checker
as a constrained verifier. Research adoptions (source → decision → reason):

- SEI ATAM (risks · sensitivity points · tradeoff analysis) → adopted as the T axis
  (t1 decision entries, t2 sensitivity points, t3 inherited-defect ledger) → tradeoffs are
  the architect's core art; a ledger makes building-on-bad-practice a conscious decision.
- ADR practice (context · decision · consequence) → adopted as t1's one-line entry shape →
  cheapest recorded-alternative form.
- LLM-judge calibration literature (coarse anchored scales; criterion + reasoning structure
  + deterministic mapping; scores drift without anchors) → adopted 0–4 anchored bands, no
  totals, verdict from minima → fine-grained totals are noise an LLM can't calibrate and a
  weighted sum hides a broken axis.
- SAST false-positive research (LLM as constrained verifier over candidates ≈ 88% FP cut vs
  free-hunting) → adopted the re-score protocol: checker verifies anchors + author DEDUCTs,
  never free-hunts the scorecard → FP is a correctness bug here.
- React pain-point survey (global-state overuse, unclear data flow, over-abstraction) →
  already carried by design/rules; adopted only the grounding gap as the G axis (verified
  symbol marks, importer decisions, ASSUMED routing) → the named architect failure was
  ignoring existing-project reality.
- Rejected: weighted /100 totals (miscalibration + axis-hiding); judge ensembles/panels
  (cost; single constrained verifier + human gate suffices); scoring the fast path
  (bugfix-scale ceremony).

Fresh-eyes iteration: reviewer round 1 returned 16 findings (old self-check still live;
BLOCK loop unterminated; disclosure penalized by G/S bands; delta rule keyed to magnitude
not verdict boundary; impl scorecard concurrency/fence conflict; 5× delta-rule duplication;
unverifiable anchors; b3 plan-phase leak; dead Total lines; unfalsifiable "significant") —
all 16 applied; round 2 verified.

---

## 2026-08-01 — Workflow refactor: evaluation as its own step (Goal 2, v2)

Total refactor of the my-react family around a unified evaluation framework, superseding
the embedded-scorecard design (same day). Research adoptions (source → decision → reason):

- Huang et al. ICLR 2024 (self-correction fails without external signal) + Verification
  Mirage (same-context verification is contaminated) → evaluation separated from
  authoring: `check` → `evaluate` skill; authors run improve loops on MECHANICAL binary
  checks only; the certifying verdict comes from evaluator with zero author
  context → self-judgment is worth less than nothing, mechanical self-checks are not.
- SWE-bench retest study (29.6% plausible patches wrong) → "prefer executed evidence":
  tests/typecheck/greps outrank prose judgment, encoded in evaluate's procedure step 2.
- DeepEval/Langfuse judge guides (binary per-criterion beats Likert) → rubrics are binary
  evidence-typed checks (grep · command · trace · read) grouped into axes; scores DERIVED
  by class bands (cliff/core/polish), never judged.
- Anthropic multi-agent blog (four-part delegation; artifacts not relay; compact returns)
  → driver passes mode/Materials/path per spawn; evaluator returns the report, driver
  persists it (read-only fence intact); worker reports stay line-oriented.
- IFScale + Lost-in-the-Middle (rule budgets, early-position bias) + Anthropic skill
  guidance (positive framing, ≤5 hard limits) → hard limits front-loaded, one term per
  concept (check/axis/verdict/finding/evaluation report), "never X" rewritten as
  affirmative procedure + short hard-limit lists.
- User directives adopted: skills=how/agents=what (author agents sequence
  design→evaluate→improve; trigger axis ≤2, ONE loop); maintainability/scalability (s6) +
  readability (impl s4) as visible checks; evaluation outcomes feed agent memory (failed
  check = generalized avoid-pattern); foundation signal says when refactoring the blast
  radius pays (≥2 flows · caps an axis · recurs across specs).
- Rejected: author self-scorecards as artifacts (delta/evidence-shift machinery deleted
  with them); judge ensembles (cost); scoring the fast path.

Fresh-eyes iterations: round 1 = 17 findings (evaluator can't write its own report;
ledger/Verified columns missing from templates; a1 unexecutable; oac driver unmirrored;
c5/v3 double-cover; double-ask ceremony) — all applied; round 2 verified.
**Round 3 residuals (4):** a1 unverifiable fallback · oac prior-ledger Materials · multi-mode single-verdict shape · evaluate step 5 return-vs-write — applied.

**2026-08-01 — rule-corpus challenge (research → 19 changes, net +69 lines):**
Adopted 8 gap cards (source → card): react.dev effect taxonomy → notify-parent-from-handler
(use-hooks); TanStack waterfalls guide → parallel-queries/no-nested-waterfalls
(services-and-boundaries); Zustand v5 migration → stable-selector-references
(build-stores-and-services); TanStack optimistic guide → cancel-in-flight-reads-first
(use-hooks); react.dev memo → minimum-props (decompose-components, authoring side of
rubric s7); react.dev Component → handler/async-errors-land-in-state (build-components);
WebAIM Million → programmatic-label (build-components); TS handbook → exhaustive-switch
(build-components). Fixed 8 weak rules (self-contradicting uSES example; both optimistic
examples taught the G4 bug; compiler-stale stable-returns; broken subscribe example;
missing not-flags ×2; seed-from-prop dedupe; over-broad compiler-skip). 3 misplacements
(process prose cut from cards; app-wide staleTime → state-ownership; rubric-restating
surface card compressed). Dropped: prop-drilling and state-duplication cards (existing
coverage confirmed).

**2026-08-01 — evaluation cadence + team ergonomics:** per-batch improve loops removed
from implementer/tester (evaluate preloads dropped) — implementation + tests are evaluated
ONCE after all implement tasks complete; design keeps its improve loop. Evaluation reports
are intermediate (presented at gates, never persisted — evaluations/ dir dropped). Team
routing relaxed: related work → the teammate who did it while context <~75%, else a new
teammate; evaluator's first verify stays clean-context. Phase playbooks reformatted to
terse sub-bullets (both drivers). Role paragraphs compressed across all six workers
(789→ from 804 lines).
**Final coherence review (fresh eyes):** 12 defects found and fixed — Update/Delete markers split in plan; e2e Materials repointed to real design sections; tests-mode inputs completed (red ref, Blast radius); oac red-ref dispatch; three stale phase lists aligned (plugin.json, README ×2); design-evaluation-of-record wording unified (design SKILL, evaluate description, implement SKILL); figma map homed in preflight.md; 'one file' → 'one report'. Verified coherent: red-ref chain, foundation-signal flow, team/model rules, fences, name resolution.

**2026-08-05 — design evaluation moves to the evaluator:** the architect's self-evaluate +
improve loop removed (evaluate skill unbound from the agent); `evaluate` now has a single
independent use — authors never score themselves. Both drivers' design playbooks spawn
`my-react:evaluator` in `design` mode after the architect hands back (Materials: design.md +
contracts/ + ACs + atlas/ + the inherited-defect ledger, never the architect's report); its
verdict + foundation signal are the design evaluation of record at the gate. Architect now
reports the ledger verdicts instead of a check summary and repairs from findings on a fresh
spawn; design SKILL, evaluator description and README updated to match.
