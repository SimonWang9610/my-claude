# REFINE-LOG

Grill log per `GRILL.md`. One entry per file: before/after word count, what was cut, why (tied to a token-economy rule or specflow finding). "Confirmed tight" = already lean, no manufactured cuts.

## Order of work
oac-* skills (grill loop) → cohesion pass → drivers + generators adopt the tightened skills.

## Progress
- [x] oac-figma-decompose
- [x] oac-analyze
- [x] oac-acceptance-criteria
- [x] oac-architecture-design
- [x] oac-journey-plan
- [x] oac-task-design
- [x] oac-test-contract
- [x] oac-implementation
- [x] oac-journey-tests
- [x] oac-qa-report
- [x] oac-test-forensics
- [x] cohesion pass
- [x] specflow-driver / sflow-driver
- [x] spec-react-workflow / sf-react-workflow

---

## oac-* skill grill entries

### oac-test-forensics
- `SKILL.md`: 589→589. Confirmed tight.
- `references/gap-classes.md`: 830→815. Cut: reversibility rationale Claude already knows (Cut #2).
- `references/false-positive-signals.md`: 708→693. Cut: matcher-misuse bullets dup of heuristics-pass3-forms "Matcher misuse" → pointer (Cut #5).
- `references/heuristics-behavior-enumeration.md`: 162→162. Confirmed tight (sole owner of stack line, read first).
- `references/heuristics-pass2-shapes.md`: 421→395; `heuristics-pass3-forms.md`: 643→617. Cut: repeated stack-target + "confirm every grep hit" boilerplate (3×→1, kept in first-read file) (Cut #5).
- `references/sources.md`: 244→238. Cut: re-explained JSDOM CSS-var fact (Cut #5); kept citation-integrity caveat.
- Cohesion: placeholder-name note left duplicated across heuristics-pass* on purpose (files can be opened out of sequence). In sync with oac-test-contract (cites rule numbers only, no re-teaching). qa-report §3 already invokes forensics by name (no re-teach).

### oac-architecture-design
- `references/design-procedure.md`: 892→761. Cut: Step-7 verbatim contract schema dup of SKILL skeleton → pointer (Cut #5).
- `references/how-to-use-bundled-rules.md`: 619→599. Cut: "Trigger→rule" table dup of principle-checks.md crosswalk → pointer (Cut #5).
- `references/principle-examples.md`: 1637→1561. Cut: per-P "Crosswalk" lists (7×, dup principle-checks) + decorative Source URLs (7×) (Cut #5/#4). Kept every Rule/Rationale/code pair (multi-card gate-altitude sketches = distinct capability).
- `SKILL.md` (870), `gate-procedure.md` (970), `principle-checks.md` (971): confirmed tight (two-altitude layering, not copies).
- `core/*`: all **22** cards confirmed tight.
- Cohesion / **brief corrections**: core/ has **22** files (not 24 — my brief miscounted); this skill uses **P1–P7** consistently — "P1–P8" is the *Flutter* skill (brief crossed profiles). react/rules/architecture-principles.md is an intentional always-on P1–P7 summary that already points here (two-altitude, not a dup). Flagged-not-cut: single-rule P-lenses (P1/P3/P4/P7) in principle-examples mirror one core card each — maintainer judgment whether they earn keep vs multi-rule lenses (P2/P5).

### oac-task-design
- `SKILL.md`: 661→523. Cut: duplicate kind-enum + field list, dependency diagram, Vitest describe/it fence, Exit-check example strings — all owned by task-anatomy.md (Cut #5), pointers left + kept the "never toHaveBeenCalled alone" caveat. **Correctness fix:** step 5 widened "implementation and test" → "implementation, test, and edge-case" so edge tasks aren't silently excluded from Traces-to/Exit-check.
- `references/edge-cases.md`: 337→307. Cut: intro "not that a mock was called" (dup of Anti-patterns bullet, Cut #3); duplicate skip-if-covered anti-pattern (Cut #3); orphan-rule bullet now redundant with widened SKILL step 5 (Cut #5).
- `references/task-anatomy.md`: 737→698. Cut: "No orphan" + "Observable exit" bullets (dup of SKILL step 5, Cut #5); kept count-formula rationale + all literal templates.
- Cohesion: AC-ID-in-describe/grep convention overlaps acceptance-criteria + test-contract §1–2 — left local, flagged. tasks exitWhen verified intact.

### oac-test-contract
- `SKILL.md`: 573→565. Cut: lead sentence restating the frontmatter's "Prevention half" (Cut #2/#5).
- `references/rules.md`: 1213→1135. Cut: §1/§4 anti-pattern prose restating their own BEFORE example (Cut #3); §1 `vitest run --tag` parenthetical (unused workflow, Cut #4); §2 userEvent sentence dup of SKILL table row 2 (Cut #5). Kept §2/§3/§5/§6 anti-patterns + QueryClientProvider example (each a distinct fact). All six rules verified intact.
- `references/sources.md`: 279→239. Cut: tangential mocking-architecture link (Cut #4); two orphaned "Test Tags" citations. Fixed vocab "Production-shaped"→"Production-typed".
- Total −126 (~6%). Cohesion: **six-rule taxonomy now stated in 3 places — react/rules/test-quality.md (always-on), SKILL table, rules.md; confirm the skill only ADDS authoring detail vs re-owning (cohesion pass).** forensics sync spot-checked OK (no renames); 1:1 finding→rule map vs false-positive-signals.md left for cohesion pass.

### oac-acceptance-criteria
- `SKILL.md`: 661→615. Cut: intro "spine…greppable" sentence + step-3 "stays alongside ACs" + step-5 pattern-ban clause — all owned by ac-format.md (Cut #5).
- `references/ac-format.md`: 620→524. Cut: §4 "Where the IDs go" → pointer (owned by traceability.md §3); §5 "Authoring checklist" → pointer (dup of SKILL "Hard checks") (Cut #5).
- `references/discovery.md`: 599→599. Confirmed tight.
- `references/examples.md`: 778→760. Cut: anti-pattern #1 tangent trimmed (Cut #4); kept the TanStack-Query spy lesson + 3 other distinct anti-patterns.
- `references/rationale.md`: 362→277. Cut: HOW of discovery (owned by discovery.md); "Downstream chain" ASCII + success-metric (owned by traceability.md §3); scope-boundary EARS restatement (Cut #5).
- `references/traceability.md`: 419→419. Confirmed tight — now sole owner of the ID→task→test→coverage-gate pipeline.
- Total −245 (−7%). Cohesion: resolved 3 same-skill dup chains (EARS-stays fact ×3→ac-format §1; ID pipeline ×3→traceability §3; authoring checklist ×2→SKILL Hard checks). All 3 exitWhens verified. Cross-skill: **AC-<story>.<n>/NFR-<n> ID scheme + describe-name traceability also live in task-design/test-contract/test-forensics → cohesion-pass dedup candidate.**

### oac-journey-tests
- `SKILL.md`: 315→300. Cut: intra-file duplicate of J-<n>/"NOT automated" scoping (Cut #6).
- `references/authoring.md`: 780→500. Cut: Stack line dup of SKILL (Cut #5); **entire TanStack Query hook-authoring subsection** (production-hook guidance owned by oac-implementation; a journey test drives UI+MSW, never writes useQuery/useMutation — Cut #4+#5); **Zustand store-access subsection** (doesn't occur in UI-driven journeys; restates arch's state-no-server-data card — Cut #4+#5); TS catch-block subsection (generic TS + owned elsewhere — Cut #2+#5). **[SPOT-CHECK in cohesion pass — largest cut of the run; verify harness/QueryClient wrapper survived.]**
- Cohesion: kept the harness QueryClient({retry:false}) wrapper (flagged overlap w/ test-contract §2/§5, left — journey-tests runs standalone). SKILL "Scope is the plan" line dup of journey-plan SKILL left intact (only the qa-journey-plan.md artifact passes at runtime, not the skill file). exitWhen verified intact.

### oac-implementation
- `SKILL.md`: 931→810. Cut: "Design → implementation handoff" para (Cut #5) — restated what the reference tables already convey via `↔ arch:` tags + "When to open" glosses; closing sentence duplicated the post-Procedure `↔ arch` explanation. `↔ arch` mechanism + scope note retained.
- `references/*`: all 29 cards confirmed tight (read in full) — each one non-obvious idiom, one incorrect/correct pair, no redundant example.
- Cohesion: hf-out-of-react-loop vs rerender-transient-subscribe share a ref-not-setState example but distinct trigger sources (service callback vs Zustand transient subscribe) + cross-reference each other; flagged, not cut. No seam violation with oac-architecture-design — every design-twin rule is `↔ arch:`-tagged and phrased "how in code," not re-teaching the "what." contract-conformance stays impl-scoped.

### oac-figma-decompose
- `SKILL.md`: 805→786. Cut: intro para restating frontmatter's EXISTING/PARTIAL/NEW/~150-token/planning-doc phrasing (Cut #5); kept the two non-obvious directives.
- `references/token-map.md`: 790→574. Cut: worked-example token tables over-enumerated — file is explicit "replace with yours" filler illustrating structure, extra rows taught no new rule (Cut #3/#4). Kept 4-step process, all headers, the resolved≠px / weight-900 / icon-naming facts.
- `references/matching.md`: 508→431. Cut: illustrative layout dir list (Cut #2); `## 3. Tag` restated the EXISTING/PARTIAL/NEW defs owned by SKILL Procedure (Cut #5, pointer + kept the PARTIAL gap-note example).
- `references/figma-extraction.md`: 473→455. Cut: two restatements of facts SKILL Procedure already commits (get_metadata gotcha, fan-out-per-node rule) → pointers (Cut #5).
- Cohesion: reference files were restating SKILL Procedure commitments; replaced with pointers, vocab now consistent. Stays within preflight scope. Templates preserved verbatim.

### oac-analyze
- `SKILL.md`: 540→521. Cut: Mode 1 step 4 pass/fail elaboration owned by repro-test.md gate (Cut #5, pointer left); Mode 2 step 2 inline grep dup of impact.md §1 (Cut #5).
- `references/impact.md`: 316→297. Cut: closing sentence restating the section opener (Cut #5/#6).
- `references/root-cause.md`: 314→285. Cut: trailing "## Record" restating analysis.md field list owned by output-format.md §1 + SKILL step 5 (Cut #5).
- `references/repro-test.md`: 306→306. Confirmed tight (now sole owner of the gate detail).
- `references/output-format.md`: 233→233. Confirmed tight (pure contract + literal templates).
- Total −67 (−3.9%). Cohesion: no overlap with driver analysis procedure (driver holds only the 1-line exitWhen; skill owns per-mode procedure — correct split). Flagged-not-cut: SKILL Mode-2 "Read-only guard" near-restates impact.md §2 (safety-critical, restated at point-of-use per repo pattern).

### oac-journey-plan
- `SKILL.md`: 250→206 words. Cut: steps 1 & 3 restated the schema fields and the approve/revise/skip/add approval protocol that `references/journey-plan.md` already owns verbatim — deferred to the reference (Cut #5). Kept the coverage-check rule (unique) + trigger/exitWhen.
- `references/journey-plan.md`: 208→208. Confirmed tight — literal template/schema + approval protocol; nothing restates another owner.
- Cohesion: SKILL.md closing line vs journey-plan.md opening line are near-duplicate "scope contract" framing but each carries distinct info; flagged, not cut. Stays within design-phase scope (plan+gate, no test authoring).

### oac-qa-report
- `SKILL.md`: 422→422. Confirmed tight — 6 crisp steps, summary-then-pointer pattern, References index matches repo convention.
- `references/audit-catalogue.md`: 1046→984. Cut: markdown TOC (Cut #6); duplicate "optional project extensions…" sentence owned by report-format.md (Cut #5).
- `references/report-format.md`: 675→668. Cut: markdown TOC (Cut #6). Template body byte-for-byte intact.
- `references/severity-model.md`: 425→398. Cut: "What blocks a pass" 3-bullet prose collapsed to a pointer at report-format.md's Disposition block (Cut #5); all three outcome names retained.
- `references/retest-cycle.md`: 221→221. Confirmed tight.
- Cohesion (feeds cohesion pass): **(1)** single-run rule restated in audit-catalogue §0 — also owned by driver Hard Rules + spec-qa exitWhen; ownership to resolve. **(2)** mutation-test definition in audit-catalogue §3 also in oac-test-forensics; cross-skill dedup decision. **(3)** vocab drift: retest-cycle "Changes since last run" (5-bucket) vs report-format "Prior Review Status" (F-id) — accuracy flag.

---

## Cohesion pass

**Actions taken**
- **TOC removal (repo-wide convention).** qa-report's grill cut navigation-only TOCs (Cut #6); 8 more `## Contents`/`## Table of contents` anchor-list blocks survived in other skills (acceptance-criteria/examples, arch/{design-procedure,gate-procedure,principle-checks,how-to-use-bundled-rules,principle-examples}, journey-tests/authoring, test-contract/rules). An agent reads the whole file — internal anchor lists change no behavior. Removed all 8 (~71 lines) + collapsed 4 resulting doubled `---`. One convention now: reference docs carry no TOC.

**Reviewed, kept (usage/intentional two-altitude — not restatement)**
- **AC-ID scheme** (`AC-<story>.<n>`, `NFR-<n>`, `US-<n>`): defined+assigned only in oac-acceptance-criteria; task-design/test-contract/test-forensics *apply* it per-phase (test-task exit-check / authoring rule §1 / detection grep). Shared vocabulary, not duplicated definition.
- **mutation-test**: oac-qa-report/audit-catalogue §3 invokes `oac-test-forensics` *by name* + a one-line summary — delegation, not re-teach.
- **Two-altitude rule files**: `react/rules/test-quality.md` (always-on one-liners) → oac-test-contract/rules.md (code detail); `react/rules/architecture-principles.md` (always-on P1–P7) → oac-architecture-design references. Intentional, each already cross-references the skill.
- **Bottom `## References` index in SKILL.md**: present in all 11 skills; discoverability index, consistent — kept.

**Deferred to the driver/generator pass (spans skill + driver + phase-map — resolving in one place)**
- **Single-suite-run seam** (GRILL's named seam). Discipline "single non-parallel run, no duplicate/coverage/type-check passes" appears 3×: driver Hard Rules, phase-map `spec-qa` exitWhen tail, oac-qa-report/audit-catalogue §0. **Owner = driver Hard Rules** (the driver is the single actor that runs/delegates all test execution — orchestration discipline). Plan: trim the exitWhen tail in **both** phase-maps (already matches what the generator SKILL *examples* emit) and reference-not-restate in audit-catalogue §0; driver keeps the rule. NOTE both phase-maps are intentionally duplicated (self-contained per-flow generators) — edit both.

**Flagged, left (semantic, out of a token-grill's scope)**
- oac-qa-report vocab: retest-cycle.md "Changes since last run" (5-bucket) vs report-format.md "Prior Review Status" (F-id) name the same-ish section differently; a maintainer accuracy call, not a token cut.
- oac-architecture-design: single-rule gate lenses (P1/P3/P4/P7) in principle-examples.md mirror one `core/` card each — maintainer judgment whether they earn their keep vs multi-rule lenses (P2/P5).

---

## Drivers + generators — adopt the tightened skills

Goal: after the skills tightened, remove driver/generator restatement of what a skill or `exitWhen` now owns, and resolve the single-suite seam in one place.

- **Single-suite seam resolved** (owner = driver Hard Rules).
  - `agents/specflow-driver.md`, `agents/sflow-driver.md` — Hard Rule "Run tests sparingly" left as the **sole owner** of "one non-parallel full-suite run, no duplicate/coverage/type-check passes."
  - `skills/spec-react-workflow/references/phase-map.md`, `skills/sf-react-workflow/references/phase-map.md` — trimmed the `spec-qa` exitWhen tail "— no duplicate runs, no extra coverage/type-check passes" (driver owns it). Now matches the trimmed form both generator SKILL examples already emit → phase-map ↔ generator ↔ workflow.yaml consistent.
  - `react/skills/oac-qa-report/references/audit-catalogue.md` §0 — QA build gate kept (red-branch, build-first, run-once, on-failure STOP, per-file re-runs); the generic run-discipline now *references* the driver's single-suite rule instead of restating it as a second owner.
- **Drivers defer driver-led phases to skill + exitWhen.** Both drivers' `analysis`/`describe` bullets restated the phase `exitWhen` (which the driver already reads from `workflow.yaml` in Drive-Loop step 1) + the skill's contract. Trimmed to "invoke the bound skill to the phase's exitWhen, then gate," keeping only the load-bearing verify anchors (bugfix repro test FAILS pre-fix; brownfield impact map; describe = one paragraph + one observable AC). No process knowledge duplicated.
- **No binding changes needed** — the grill renamed no skill and changed no capability, so the phase-map phase→skill bindings and both generators' command/skill mapping remain correct. READMEs (`react/README.md` "22-rule corpus", P1–P7) remain accurate.

## Summary
- 11 oac-* skills grilled (one griller each, conservative cuts + full flag stream) + cohesion pass + drivers/generators.
- **38 files touched, ~2,253 words cut (8.8% of edited files)**; many files confirmed tight (all 22 arch `core/` cards, all 29 impl cards, discovery.md, traceability.md, repro-test.md, output-format.md, retest-cycle.md, several SKILL.md).
- Zero capabilities removed — only restatement, TOCs, over-enumerated filler, and duplicated disciplines. Uncertain items were flagged, not cut.
- One convention enforced repo-wide: reference docs carry no TOC.
- Seam GRILL.md named ("single suite run") resolved: one owner (driver), one attributed reference (qa-report), consistent exitWhen everywhere.
- Open maintainer calls (semantic, left for a human): qa-report retest-cycle vs report-format section naming; arch single-rule gate lenses (P1/P3/P4/P7) vs their `core/` cards.

---

## Boundary-sharpening pass — oac-architecture-design ↔ oac-implementation

Prompted by: design should own architecture/boundaries (what/where/who-owns), implementation should own in-scope mechanics (how). Overlap map (51 cards) found the split already ~94% clean via `↔ arch:` tags — **no shared invariant worth extracting** (a shared module would add a third location for ~40 lines of snippet dup). Fix = sharpen the boundary in place, not extract. 3 edits:

- `references/core/zustand-actions-in-store.md`: removed the `useShallow` multi-field-selector **perf** subsection (~18 lines, a re-render mechanic duplicating `oac-implementation/rerender-zustand-selectors.md`) → one-line pointer; dropped the matching review-flag. Card is now purely the actions-encapsulation *decision*.
- `references/core/query-mutation-invalidation.md`: removed the "The graph, expressed" `onSuccess` code block — **verbatim** copy of `oac-implementation/query-mutation-wiring.md:16-24`. The invalidation-graph *table* already states the decision; the closing "design decides what, impl wires how → query-mutation-wiring" pointer stays.
- `references/core/query-no-effect-fetching.md`: reframed from a code-idiom comparison to a **boundary/ownership decision** (server reads belong to the Query layer; effect-fetching traps data in local state with no single owner). Kept a compact incorrect sketch; deferred the v5 `isPending`-vs-`isLoading` loading-state nuance to `oac-implementation/data-states`.

Not done (deliberate): no `↔ arch:` tag added to `rerender-zustand-selectors` — post-dedup it's a pure mechanic with no real design-decision twin; a forced tag would invent a relationship. Extraction rejected (payoff not real). Net: design cards now hold boundary/what only; the two duplicated mechanics live once, on the impl side.

---

## Change requests (post-grill)

**1. Remove `taskstoissues`/Jira from generators + agents.**
- both `phase-map.md`: dropped the `taskstoissues` row, the `_oac-jira-status-automation` playbook from the `implement` row, the Jira conditional, and the line-9 tracker clause.
- both generator `SKILL.md`: dropped the taskstoissues command mapping / tracker rule + "Jira tracker" conditional; added a graceful-skip guard (if a vendored template still declares the phase → emit `skills: []`, `gate: auto`, skip). This keeps the generator coherent because `sf-init` still scaffolds `taskstoissues` into `.meta.yaml` (out of scope — flagged).
- `specflow-contract.md`: dropped `/spec-taskstoissues`, `issues.md`, the taskstoissues feature-phase row, the `jira_issues:` example, the "Jira integration" mention.
- both drivers: dropped "or tracker transition" from the outward-action stop.

**2. `oac-task-design` emits a parallel-wave plan.** New step 2b derives build waves from the `depends on:` DAG (Wave 1 = no-dep units; Wave n = deps satisfied earlier); assembled `tasks.md` gains a 4th **Parallel plan** section; worked example + `tasks` exitWhen (both phase-maps) updated. Independent units build concurrently, one Work/Test pair each.

**3. Drivers use a Work/Test split at implement.** Added to both drivers: per unit, a **TestAgent** authors the AC test red-before-green (test files only), a separate **WorkAgent** implements to green (never edits the test); the driver re-runs the test AND confirms the test file is byte-unchanged (`git diff`) — no agent grades its own work. Runs across the parallel-wave plan. Reinforced in the `implement` exitWhen (both phase-maps: "authored red-before-green by a separate test agent").

**Downstream ripple — OUT OF SCOPE (generators+agents only), flagged not touched:**
- `sflow/commands/sf-init.md` still scaffolds `taskstoissues: pending` + `jira_issues: []` into `.meta.yaml`.
- `sflow/commands/sf-implement.md:27` "Tracker sync (optional)" step — now a dead branch (no binding emits it).
- `react/README.md:31-32`, `sflow/README.md:57,104,124,152,167-168` still document taskstoissues + the jira playbook as live.
- `react/commands/_oac-jira-status-automation.md` (symlinked `commands/`) — now unreferenced by generators/agents; orphaned.

---

## New skill: oac-implementation-review (author/review split)

Concern: oac-implementation (29 cards) too detailed — bloats the implementer's context, subagents get lost. Fix (confirmed with user): split along the seam the SKILL already drew (Correctness & idioms vs Performance corpus).
- **`oac-implementation` slimmed** 29→**6 cards** (contract-conformance, data-states, query-mutation-wiring, typescript-discipline, hooks-correctness, react19-modern-apis). Dropped the Performance-corpus section; procedure step 7 now "don't pre-optimize — review enforces perf"; description = correctness-only.
- **`oac-implementation-review` (new)** owns the **23-card perf corpus** (`git mv`'d, history preserved) + an architecture-boundary lens that references `oac-architecture-design/principle-checks.md`. Detect-side, mirrors oac-test-contract/oac-test-forensics: severity-tagged findings (`R-<n>`, Critical/Major/Minor), each → the card that fixes it; evidence only, never edits code. `skills/` symlink added.
- **Binding = implement exit gate, before spec-qa** (user's choice: branch-level, not per-unit). Both phase-maps: implement `skills` gains `/oac-implementation-review`; exitWhen gains "branch passes review (no unresolved Critical/Major)". Both drivers: added the **Branch review gate** to the implement block — ReviewAgent over the changed files → Critical/Major loop back to a WorkAgent (bounded), then the human code gate.
- **Cross-refs repaired** (8): design cards' forward pointers to moved perf cards now say `oac-implementation-review` (new `↔ review:` twin tag beside `↔ impl:`); intra-impl pointers (hooks-correctness→hf-effect-cleanup, react19-modern-apis→memo cards) and one review→impl pointer (rerender-memo-boundaries→react19-modern-apis) now name the owning skill.
- `react/README.md` updated (the new pair). Roles now: TestAgent (red) → WorkAgent (green) → ReviewAgent (branch gate).

---

## Promote layering to always-on P8

Ask: move some oac-architecture-design references into `react/rules/architecture-principles.md` (always-on, path-gated `**/*.ts(x)`) as short rules for all TS files. Analysis: P1–P7 already cover the universal state/query/component/testability/token/module concerns; the one gap was **layering** (import direction, service isolation, no cross-feature deep imports) — hard per-file invariants only in the skill (as supporting evidence for the P2/P5 gate lenses).
- `react/rules/architecture-principles.md`: **added P8** (dependencies point one direction; integrations behind services; no deep cross-feature imports) — terse, points to the `core/layer-*.md` cards. Title P1–P7→P1–P8, trigger list + closing pointer updated. Cards NOT moved (two-altitude split preserved).
- Light skill sync: `how-to-use-bundled-rules.md` category 5 tagged ↔ **P8**; `principle-checks.md` notes `layer-*` = always-on **P8** (a per-file rule, NOT a gate lens — lenses stay P1–P7, consistent with P4/P6/P7 which are also non-blocking).
- `react/README.md` P1–P7→P1–P8; memory updated (P8-is-a-rule-not-a-lens distinction).
- Decided AGAINST promoting query-key-factory (narrower; kept skill-only) and the compose-*/zustand-* cards (design-time, would bloat the every-edit budget).

---

## Reconcile agents/skills + update scripts (retire removed, adopt added)

**Inconsistency paved (the big one):** `sf-implement.md` said WorkAgent-builds-then-TestAgent-writes-green — the OPPOSITE of the driver + phase-map's red-before-green. Fixed to `test → red → impl → green` (TestAgent first, WorkAgent never edits the test), pair renamed `(TestAgent, WorkAgent)`, exit gains the review gate + unmodified-test check.

**Adopt what we added:**
- `sf-implement.md`: branch-review step (`oac-implementation-review`) + exit condition; plans over `tasks.md` parallel waves.
- `sf-tasks.md`: Step 2 produces parallel **waves**; exit requires "valid DAG grouped into parallel waves."
- `sflow/README.md` react skills tree: added `oac-analyze`, `oac-journey-plan`, `oac-implementation-review` (was stale).
- Scripts: glob-based, so `skills/oac-implementation-review` symlink (matches `internal-link.sh` convention) auto-adopts; `internal-link.sh react` → "0 linked, 14 already linked" (consistent).

**Retire what we removed (tracker/taskstoissues integration):**
- Deleted the dead aggregation symlink `commands/_oac-jira-status-automation.md` (source `react/commands/` already gone).
- `sf-init.md`: dropped `jira_issues`. `sf-implement.md`: dropped the tracker-sync step + tracker-field input. `sf-qa.md`: dropped the tracker-integration clause. `oac-qa-report/severity-model.md`: dropped tracker-playbook mentions.
- READMEs (root, react, sflow): removed the tracker-playbook bullet/tree line + "Jira" conditional; `taskstoissues` now described as "skip-guarded (React flow has no tracker)".
- `link.sh`: fixed stale `*-workflow-generator` → `*-react-workflow` comment.

**Kept (correct):** `jira-ac-align` (standalone Jira skill, not the taskstoissues flow); `taskstoissues` as a template-faithful phase (sf-init scaffolds from template → generator skip-guards). No dangling symlinks remain; red-before-green consistent across driver + phase-map + sf-implement.
