
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

**3. Each driver locked to its own command set.** New Hard Rule: specflow-driver **`/spec-*` only** (never `/sf-*`); sflow-driver **`/sf-*` only** (never `/spec-*`); a missing command → STOP, never substitute the other prefix.

Both drivers verified consistent (modulo prefix + intentional description lines).

---

## Token discipline from caveman research (input-side compression)

Researched juliusbrussee/caveman. Its own honest numbers show output-style compression is the
wrong lever for input-dominated agentic sessions (the style skill costs ~1–1.5k input/turn and
nets only 14–21%, sometimes negative). Absorbed the input-side, compounding levers instead:

1. **Subagent return contracts** — `smart-delegation` "Demand compact structured returns" bullet
   now fixes a rigid line-oriented format with a hard item cap (`<path:line> — <symbol> — <≤6-word
   note>`); facts exact, everything else dropped, never abbreviated. Covers both drivers via the
   shared template.
2. **Terse persisted artifacts** — one short rule per artifact-producing skill (duplicated per
   profile, per profile independence): build-acceptance-criteria (hard rule),
   design-react-architecture (**Write terse**), plan-react-tasks (step 6), analyze-react
   (**Style** line), scan-resource (principle), fl-acceptance-criteria (step 10),
   fl-architecture-design (intro), fl-task-design (output format). Common core: terse prose,
   reference IDs instead of restating, technical facts exact, no invented abbreviations.
3. **Tokenizer-realism authoring rule** — new `rules/token-discipline.md` (distributed per-project
   by link.sh like the other rules; NOT in CLAUDE.md, which is symlinked as the global
   ~/.claude/CLAUDE.md): compress what compounds; lazily-loaded references trimmed
   opportunistically only (no bulk rewrite); abbreviations/arrows are fake compression.
4. **Human-facing clarity guardrail** — both drivers' `gate: human` bullet: gate summaries in
   clear full sentences, never fragments; also in the rule and the design skills' gate content.

Rejected: caveman-speak output style, per-turn style skills (net-negative here).

Follow-up (same session) — trimmed the two remaining inter-phase/agent flows:

5. **Slice-scoped delegation inputs** — `smart-delegation` `Materials:` line now demands the
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

1. **audit-code-flows** — note format restructured into one fixed thinking chain per flow:
   entry/exit → GIVEN (origins, preconditions, initial state) → WHEN (trigger + guards) →
   THEN (per-case outcome + state change + propagation) → HOW (transforms, side-effect
   surfaces, mechanisms) → Interacts-with (coupling + direction per related flow). Old
   Data model/Data flow/User flow/Cases covered/State fields folded into the chain — no
   field lost, none duplicated. New output artifact: **flow interaction map** (mermaid or
   table) assembled from the Interacts-with lines; cross-flow touch points recorded
   during tracing, never via a second scan.
2. **build-requirements** — new step 1 **First principles**: recover the problem behind
   the ask (a requested solution is a candidate, not the requirement), surface and check
   the request's assumptions against audit notes/system fundamentals (wrong ones become
   batched questions with evidence + recommended correction), derive requirements from
   problem + invariants, never from current code shape or user belief.
3. **design-react-contracts** — first-principles rule in SKILL.md (units derive from what
   flows require; audit says what exists, never what the design should look like);
   Output discipline gains **no reasoning in artifacts** (decisions only; one-line rule
   citations are the only "why"; unresolved reasoning → Open items) + **fixed shape**
   (code only in designated fenced blocks, all else one-line prose or table rows);
   design.md Flows section standardized: per flow a `### F<n>` with a mermaid
   sequenceDiagram between units (messages labeled `mechanism: fact`, NEW marked, ACs
   cited) + the ground-truth step table. Reconcile step 1 consumes the interaction map
   for blast radius.
4. **plan-react-contracts** — new step 5: every wave pre-split into a **test batch**
   (one TestAgent) + **impl batch** (one WorkAgent); oversized waves (~4 tasks / context
   bloat) chunked at planning time with named reason; count-check extended (every task in
   exactly one chunk's batches). tasks.md § Waves shape added.
5. **check-react-implementation** — checks restructured into three axes: **behavior &
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
verbosity the round introduced — build-requirements step 1 collapsed to one bullet,
design-react-contracts first-principles/output-discipline paragraphs and the Flows
template annotation shortened, plan-react-contracts step 5 tightened,
check-react-implementation's axis preamble folded into the Checks intro.

Follow-up 2 (same session): design-react-contracts SKILL.md rewritten to exactly 70
lines (inputs merged, one-line rule bullets and full-path steps, references hoisted to a
section preamble). Language-agnostic rules escalated to rules/preferences.md — new
sections **First principles** (requests are evidence not specs; derive don't copy) and
**Artifacts** (decisions never reasoning; fixed shapes), new bullets **Cut batches at
planning time** (Leverage) and **Judge behavior first** (Code); Tokens' "rows are facts"
folded into Artifacts to remove the overlap. Skills stay self-contained (rules
duplicated, never referenced). Consistency audit fixes: test-react-contracts scopes now
"unit — skip step 3 / e2e — skip step 2" (self-check + steer always run); ground-truth.md
stale "§ Propose refactors deliberately" → "§ Refactor proposals" and a redundant
coverage-guard sentence cut; plan-react-contracts count-check corrected to "tasks =
contract groups ± recorded re-cuts" and "every task in exactly one batch pair".
decompose-figma, smart-delegation, jira-ac-align, implement/review skills audited — no
changes needed.

---

## Heavy-output cuts in the specflow pipeline (2026-07-19)

Swept the drivers + bound skills for heavy outputs and agent-to-agent intermediates:

1. **Post-implement check user-gated** — both drivers' implement ③ is now a **check
   gate**: ask the user whether to run `/check-react-implementation` (recommend yes for
   feature-scale waves, skip for bugfix scale; decision recorded), instead of always-on.
2. **Design self-check scaled** — design.md § Self-check gains a Scale rule:
   single-group designs run blocking checks only (advisory classes re-surface in the
   post-implement check); kept blocking always — it catches design flaws before code
   exists, which no later check can. Drivers' Fresh-eyes rule scoped to feature-scale;
   fast-path/bugfix self-checks run inline, no subagent spawn.
3. **Terse inter-agent prompts** — smart-delegation gains "Prompts are pointers, not
   prose": paths/IDs/rules/deliverable only, never background narration or reasoning.
4. **Effort routing on dispatch** — smart-delegation gains "Route effort by task"
   (medium: mechanical contract-scoped work; high: judgment — design, forensics, review
   verdicts); preferences.md "Route models by fit" extended with the effort clause.

Already lean, left alone: audit (read budget + bounded note format), check findings
(~12 cap), subagent returns (line-oriented + item cap), driver gate summaries (paths,
never artifact re-dumps), qa-report (grep-generated), tasks.md (pointer rows).

Follow-up: design self-check budget cut from 2 loops to **ONE pass** — findings drive one
re-design of the affected units, no re-check; still-open items pause to the caller
(SKILL.md step 5 + design.md § Self-check reworded). smart-delegation template made
terse: pointer/constraint placeholders only, new `Effort: <medium | high>` field; the
"pointers, not prose" bullet became the template's preamble sentence (stated once).

---

## sflow commands rewritten lean (2026-07-19)

All 12 `/sf-*` commands rewritten 398 → 271 lines on a fixed shape: one-paragraph role +
artifacts, **Method** (embedded stack-agnostic skill, or "the flow's bound skill owns the
procedure"), **Exit** gate. Commands stay language-agnostic; new rule (README updated in 3
spots): commands may embed **stack-agnostic skills only** — sf-preflight embeds
`/audit-code-flows`, sf-requirements embeds `/build-requirements`; stack skills remain
generator/driver-bound, never named in commands.

Cut as duplication or conflict:
- **Purpose paragraphs + steps restating bound skills** (design/tasks/implement procedure
  lives in the skills/driver; commands keep only the gate contract).
- **`phases.md`** (sf-implement) — duplicated tasks.md § Waves batch pairs; one producer
  per fact.
- **EARS notation + Example Mapping** (sf-requirements, sf-clarify, sf-validate check 2) —
  conflicted with build-requirements' method and requirements.md shape; check 2 is now
  "AC shape" (stable ID + observable GWT). sf-clarify's "up to 5, one at a time" →
  ONE batched round (aligned with build-requirements).
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
embedded skill names (reverted the /audit-code-flows and /build-requirements embeds — both
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
(sflow is worktree-driven), trace-viewer/builder-checkpoint ceremony, GPG commit gates,
Jira transitions, scoped test runs at QA (sflow keeps ONE full-suite run per driver rule),
EARS. Every sf-* command verified free of "You are…" role prose and human narration.

Follow-up 6: journey plan made requirement-driven. sf-design step 5 keys off the test
strategy (no journey-level AC → skip with note); each plan entry carries a disposition —
NEW, or MODIFY <existing test path> when an existing journey test already covers the
affected flow (planned as a change, never duplicated). sf-implement step 4 executes per
disposition (author vs update the named test; material changes to existing tests surfaced,
never silent). Driver design playbook + README row now say "when the test strategy
classifies any AC journey-level".

---

## graphify research → audit-code-flows adoptions (2026-07-19)

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

Follow-up (A/B verdict): both skills produced same-quality output → audit-code-flows kept,
**flow-atlas deleted**, and its structure folded in via a cohesive rewrite (not a patch):
audit-code-flows now has three modes — **build** (default; boundary + trace rules + tag
discipline unchanged in substance), **query** (≤20-line answers from the audit: index rows
+ note fields + `Dive:` pointers; never scans source), **extend** (the only post-build
source-reader; folds facts back in, refreshes the index row, reports delta only). Artifact
moved to **`audits/`** (tiered: `index.md` always-loaded over one `<flow-id>.md` per flow;
Dependents/Verdict merged to one field). Consumers switched from receive-notes to
invoke-the-skill: drivers' preflight runs `build` → `audits/` (preflight.md carries only
figma map + gaps), carry-forwards + prior-artifacts rule name `audits/` and query/extend;
ground-truth § Audit is now query → build → extend; design SKILL input renamed "Prior
audits"; implement-react-contracts step 1 queries `audits/` for surrounding-flow context
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

Follow-up: audit-code-flows split for mode-scoped loading — SKILL.md is 44 lines (modes +
query + extend; what a querying subagent actually needs), the build procedure + artifact
formats moved to references/build.md (103 lines, loaded only on build mode). Artifact dir
renamed `audits/` → **`atlas/`** everywhere (skill, both drivers, design/implement
consumers). Consumers now teach usage by concrete example instead of narration:
ground-truth § Audit shows real build/query/extend invocations; implement step 1 shows a
query example.

Original twin (superseded by the fold above): **flow-atlas** created as an experimental
A/B twin of audit-code-flows
(skills/flow-atlas/SKILL.md, explicitly-invoked, NOT wired into drivers). Same note chain
and trace discipline (condensed, self-contained duplicate for the experiment); structural
differences: tiered artifact (`atlas/index.md` always-loaded tier over `flows/F<n>.md`
per-flow notes) + graphify-style subcommands — query (≤20-line answers: index rows + note
fields + `Dive:` pointers; atlas-only, never scans source), explain, path (hop walk over
Interacts-with/HOW; never invents a hop), extend (the only source-reader: funds a
Self-audit pointer and folds the facts back in — persistent deepening). Comparison
protocol: run both on the same references; compare tokens loaded by design/implement,
answer quality on identical questions, artifact size; winner's structure folds back into
audit-code-flows and the twin is deleted (duplicate build rules are temporary by design).

---

## react-doctor research (2026-07-20) — proposals implemented, then REVERTED on review

Audited /Users/simonwang/projects/tmp/react-doctor via /audit-code-flows (atlas in session
scratchpad): fully deterministic scanner — AST rules + project scans under one rule
contract, one compiled noise filter, capability-gated enablement, LLM only at rule
authoring time.

Three adoptions were implemented and reverted at user request pending a decision on the
script-vs-LLM split: P1 sflow/scripts/sflow-check.mjs (5 deterministic gates over spec
artifacts — verified against planted-defect fixtures) + sf-validate/driver wiring; P2
capability gating in implement/check skills; P3 rule-card quality bar in .claude/CLAUDE.md.
The research conclusions stand (hybrid tiering: artifact predicates → scripts · code
predicates → existing tools, never bespoke scanners · semantics → LLM judging residue);
no assets remain in the tree.

Follow-up: after discussion, the four research conclusions were folded back cohesively —
each in its one home, family vocabulary, no scripts:
1. **Capability gating** — implement-react-contracts leads its Rules priority with
   "Capabilities first" (package.json once; a rule never decides its own applicability);
   check-react-implementation mirrors it ("Capabilities gate citations").
2. **Rule cards carry the why** — .claude/CLAUDE.md Rules: code shape + runtime reason
   (what lets an LLM generalize without over-flagging) + ≥1 valid look-alike never
   flagged; false positive = correctness bug; narrow beats broad.
3. **Suppression accounting** — check-react-implementation Output adds a drop tally
   (`suppressed: <n> (advisory cap · caller scope · capability gate)`) so a clean report
   means clean, never quietly filtered.
4. **Judgment authors, search verifies** — preferences.md § Artifacts: correctness is
   judged once at authoring; re-checks over fixed-shape artifacts are grep/diff/count.
   (Already embodied by test skill's "coverage IS the grep" and drivers' mechanical
   Verify — the principle now named once, globally.)

---

## Field-use fixes: single-agent audit + concrete model routing (2026-07-20)

Two issues from real driver runs:

1. **audit-code-flows fanned out subagents during build** — whole-flow sense (couplings,
   hubs, skip-decisions) fragments across contexts. Build mode now states: **ONE agent
   audits everything**; skip off-purpose flows instead of splitting; parallel subagents
   only on explicit caller designation.
2. **Model routing too abstract** — smart-delegation's routing bullet is now a concrete
   mapping: test/impl from contracts → Sonnet (medium when the contract pins the work,
   high when multi-unit/heavy context) · search/explore → Haiku, escalated to Sonnet when
   the goal needs synthesis not locating · judgment (design, forensics, review verdicts)
   → top tier, high. Template field renamed `Model · Effort:`; preferences "Route models
   by fit" aligned (Sonnet-class/Haiku-class + escalation clause).

Follow-up: (a) `Model · Effort:` REMOVED from the delegation template — model/effort are
spawn *parameters* the spawning session sets, never prompt content (routing bullet reworded
to say so). (b) Companion-skill steadiness: invocation pinned to a moment ("invoke
/smart-delegation BEFORE the phase's first spawn", phase-loop step 2, both drivers) + new
hard rule **Every spawn is templated** — every subagent prompt carries the template's
field labels; mechanically checkable (a prompt missing a label is not sent). Prose
references get skipped; a checkable artifact shape doesn't.

Follow-up: **wave economics rebalanced** (user observed heavy subagent token cost). Waves
were DAG-level-driven and the "~4 tasks → chunk" trigger multiplied pairs — both push
toward many small spawns, each re-paying a cold start. New strategy: plan-react-contracts
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
unbreakable. Binds `check-react-implementation` + `audit-code-flows` (queries the atlas to
verify conformance, never re-scans), `model: sonnet`, `effort: high`; expert-reviewer role,
three-axis procedure ending in per-finding evidence verification, severity-ranked
line-oriented return. Both drivers' implement check-gate now spawns it instead of running
`/check-react-implementation` ad-hoc; bound-agents hard rule + README (three→four workers)
updated. review-react-changes left a standalone skill (user-triggered, verdict-producing).

Follow-up (fork docs read — a fork shares the parent's prompt cache because system
prompt + tools are identical, so it is CHEAPER than a fresh subagent when the work needs
existing context): **smart-delegation rewritten** — Decide step 1 is now a three-row
route table (inline · fork · subagent) keyed on what each *gets* vs *costs*, with "fork
is the default when context is the payload" and the two things a fork can't give (fresh
eyes, a narrower tool fence); step 2 bound-agent-or-ad-hoc; step 3 **the 7-field template
DELETED** → four workflow-agnostic essentials (where · what · materials · done when) +
the compact-return rule. Both drivers' hard rule renamed "Bound agents first, and every
spawn carries its four essentials".

**Agents re-specialized**: renamed back to `react-test-agent` / `react-impl-agent` (now
explicitly React/TypeScript) and each opens with an expert role that activates domain
knowledge ("senior test engineer specializing in React and TypeScript — Vitest, RTL, MSW,
Playwright" with an opinion about what a test is worth; "senior React and TypeScript
engineer" who knows state placement, effect loops, stale closures, memo boundaries;
`code-auditor-agent` = "staff engineer who specializes in reading unfamiliar systems
fast", stays language-agnostic). Bodies restructured from rule piles into **Operating
procedure** (numbered, ending in a self-check/verify step) → **Rules** (fences + stop
conditions) → **Report back**. User's frontmatter choices preserved (opus/low for the
auditor, memory: user for impl, permissionMode, colors).

**Skill descriptions rewritten** on the "what it does + when to use it" formula — all 9
skills (audit-code-flows, build-requirements, design/plan/implement/test-react-contracts,
check-react-implementation, review-react-changes, decompose-figma, smart-delegation):
each now leads with the capability in plain terms, then names the concrete situations
that should trigger it.

Follow-up: **all three workers are stack-neutral roles** — `test-agent` / `impl-agent`
(renamed from react-*) carry only fences + return contract; the language specifics come
from the `skills:` frontmatter, which a profile swaps (react bundle preloads
test-react-contracts / implement-react-contracts). Both gained **audit-code-flows** in
their skills list + a query/extend clause for behavior their contract doesn't carry
(never bulk audit, never broad re-reading). design SKILL.md now shows the usage inline
(step 2: `query "<what the decision needs>"` → miss → `extend <pointer>`; Inputs bullet
reworded to "Prior audits / component map"). **Drivers simplified** now that agents own
their procedures: phase playbooks condensed (preflight/requirements/clarify/design/qa
lost restated detail), phase loop tightened, Implement discipline compressed from a
4-step list + paragraph to one arrow line + one paragraph — my-specflow 150→133 lines,
oac 143→126.

Follow-up: auditor renamed **code-auditor-agent** (language-agnostic — its skill always
was; body now says "language- and stack-agnostic" explicitly; drivers + README updated).
Layering restored: **domain skills name skills, never agents** — design/plan/implement
reference `/audit-code-flows` directly and are **limited to query + extend** (bulk build
belongs to the caller's preflight): ground-truth § Audit back to the 2-step
query→extend form with "Design queries and extends only"; implement step 1 "never a bulk
audit here"; plan-react-contracts Inputs gained the same clause for facts design.md
doesn't carry; design SKILL step 2 reworded ("the atlas first; query/extend for what it
lacks"). Only the drivers name agents.

Follow-up (official subagent doc consulted — code.claude.com/docs/en/sub-agents):
renamed to **react-test-agent / react-impl-agent** + new **react-auditor-agent**; all
three rebuilt on documented frontmatter: `skills:` **preloads the bound skill's full
content at startup** (binding is now structural, not an instruction — the steadiness fix),
plus `model: sonnet`, `effort: medium`, scoped `tools:`, `color:`. Bodies carry only
fences + mode/procedure pointers + return contract (thin-binding rule holds). Auditor owns
audit-code-flows end-to-end (build/query/extend selection, one-agent-per-build fence,
atlas-only writes), so drivers stopped hardcoding audit modes: preflight ② spawns it,
prior-artifacts rule asks it, ground-truth § Audit + implement step 1 ask it (standalone
skill invocation kept as fallback). smart-delegation Decide restructured again:
1. delegate at all? · 2. **bound agent or ad-hoc?** (bound preferred — definition pins
fences/skill/model/effort/return) · 3. model+effort+skills+materials for ad-hoc only;
template gains "bound agents shrink this to four fields". Both drivers' hard rule now
reads "Bound agents first"; plan-react-contracts + README de-branded (TestAgent/WorkAgent
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
hard rule + smart-delegation gained the dedicated-agents-embody-the-template carve-out;
README ORCHESTRATORS layer notes the pair.

Follow-up: **preferences.md trimmed for focus** (user: more rules = less focus) — 84 → 48
lines, 13 bullets → 7, four sections. Merged: Orchestrate + Route models + Cut batches →
one Delegate bullet (smart-delegation owns the detail); Read-before-write → Simplicity-
first; Judge-behavior-first → Goal-driven; Refactor-to-unblock section → one clause on
Derive-don't-copy; Artifacts + Tokens → one section (Decisions-never-reasoning + Fixed
shapes merged). Dropped: Convention-beats-novelty (covered by derive-don't-copy + reuse).
Kept whole: the compounding gains — first principles, iteration budgets, judgment-authors-
search-verifies, token economy. Folding into root CLAUDE.md offered but not done (root
CLAUDE.md is empty + symlinked as global; load-path unknown → risk of double-loading).

Follow-up: smart-delegation's Decide restructured as **three ordered calls** — 1. delegate
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
Output: <shape>.` to each; tightened the two verbose trigger-lists (fl-pr-review,
jira-ac-align) in the same pass. Near-twin routing now explicit in-description:
check-react-implementation (no verdict) ↔ review-react-changes (gates merge) ↔
audit-code-flows (builds atlas).

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

Two user-driven changes to audit-code-flows, applied together.

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

**Callers updated** for the merge: code-auditor-agent (3 modes → build + self-healing
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

**Follow-up (same session):** code-auditor-agent learns project conventions —
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

**Follow-up (same session):** react-impl-agent memory formalized to match — its loose trailing
"record a pattern" line became a **## Memory — codebase idioms, for consistency** section,
parallel to the auditor's but role-specific: the auditor remembers *where code lives* (Locate
hints), the impl agent remembers *how this codebase does things* (state placement, data-
fetching/effect patterns, styling/error idioms, reusable units, cross-wave decisions) so its
`how` stays consistent. Same guardrail shape, different source of truth: **memory never
overrides the contract or a failing test** — those are the spec; a stale idiom is corrected,
not trusted. Description gained a matching clause. (`memory: project` was already set.)

**Follow-up (same session):** react-impl-agent memory reframed from "mirror the codebase's
idioms" to a **quality ledger judged against implement-react-contracts's rules** — the user's
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

**Follow-up (same session):** audit-code-flows + code-auditor-agent support a read-only
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
