
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
