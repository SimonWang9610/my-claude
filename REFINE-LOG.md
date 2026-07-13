
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
