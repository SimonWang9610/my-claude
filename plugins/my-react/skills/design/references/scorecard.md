# Design scorecard — spec, anchors, template

One scored self-evaluation, authored WITH design.md and re-derived with fresh eyes at
review. A score is a **claim**: every point below 4 carries a DEDUCT line with evidence;
a deduction without evidence is invalid, and so is a 4 whose anchor checks weren't run.
Adversarial stance — try to break the draft, don't defend it; findings drive re-design,
not a report. Full path only; the fast path (contract delta) has no scorecard.

## Scale and verdict

Each axis scores **0–4 against its anchors — never interpolate, never average**. Verdict
comes from axis minima (a total would let one strong axis hide a broken one; no total is
reported):

- **PASS** — every axis ≥3.
- **CONDITIONAL** — lowest axis = 2; each 2 carries an open item the gate decides.
- **BLOCK** — any axis ≤1.

**Disclosure is never penalized.** A routed ASSUMED mark, a ledgered inherited defect, a
recorded open item are the *compliant* behaviors — deductions attach to the unrouted,
the unledgered, the silent. A scorer that hides a mark to buy a 4 has produced an
invalid scorecard.

## Axes and anchors

### G — Grounding (does the design attach to the real codebase?)

Scope: the unit inventory + contracts' dependency/importer rows — not every name in
prose or diagrams. "Verified" = grep finds the declaration or an export of it.

- g1 Every existing unit/symbol those rows name carries `verified <path:line>` — no
  invented or remembered symbols.
- g2 Every MODIFY unit lists its importers (count + paths, from grep), each with a
  decision: kept compatible | migrated in scope.
- g3 Every attachment point names its wiring mechanism (props · query key · selector ·
  context · service event · callback).
- g4 Behavior relied on but not read is marked `ASSUMED` and routed to Open items —
  never silently assumed.

`4` anchors hold (routed ASSUMED marks included) · `3` one unlisted importer, named ·
`2` an inventory/contract symbol
unverified, or an ASSUMED relied on without routing · `1` a contract names a symbol grep
can't find as declaration or export · `0` no reconcile evidence at all.

### F — Fit (solves the spec'd problem, nothing else)

- f1 Every AC maps to ≥1 contract and flow step (coverage table complete), with a
  test-strategy row.
- f2 Every contract surface element traces to ≥1 AC — no speculative props, options, or
  states; anything an AC doesn't demand is invented scope.
- f3 Each NFR sits on the unit that carries it (a perf budget names its hot path).
- f4 Every flow walks end-to-end: origin → transforms → sinks, a named unit at every hop,
  a named mechanism between hops; an ambiguous handoff (nobody owns the invalidation,
  two units both think they refetch) fails and names the unit.

`4` all pass · `3` ≤2 untraced surface elements, each justified in one line · `2` an AC
has no owning contract, or a flow hop has no named owner · `1` multiple ACs unmapped, or
invented scope beyond the ACs · `0` no coverage table.

### S — Structure (the rules axis — NEW decisions only; inherited defects live in T)

- s1 One owner per fact — no dual owners, no client copies of server facts, no stored
  derivations (`rules/state-ownership.md`).
- s2 One-way dependencies, no cycles; loosest coupling that serves each interaction per
  the mechanism picker (`rules/services-and-boundaries.md`).
- s3 Decomposition per `rules/decompose-components.md` — no God unit, no gratuitous
  split; every split/merge passes the right-size test.
- s4 Failure containment declared per flow (where an error stops propagating).
- s5 Reuse before create — a NEW unit whose responsibility an existing unit owns re-tags
  to REUSE/MODIFY; a duplicate owning a fact scores under s1's dual-owner bands (≤1).

A violation only counts with its citation — a `rules/` card, design.md § Mechanism picker
for s2, or the duplicated unit's evidence for s5; "feels wrong" is not a deduction.

`4` no new rule-card violation · `3` one advisory-grade looseness (coupling, split) with
a bounded fix named · `2` one new violation introduced by this design · `1` ≥2 new
violations or a dependency cycle · `0` fact ownership undecidable from the artifacts.

### T — Tradeoffs & inherited debt (architecture is the art of tradeoffs)

"Significant decision" is mechanical: any choice a `rules/` file or the mechanism picker
leaves open between ≥2 viable options.

- t1 Each significant decision records: chosen ← rejected alternative + one-line
  consequence.
- t2 Risks and sensitivity points named — where one choice constrains another axis
  (e.g. cache locality chosen for G forces a wider MODIFY under B).
- t3 **Inherited-defect ledger complete**: every existing-scope rule violation on the
  blast radius gets a verdict — `INHERIT <cost>` · `FIX-NOW <proposal>` ·
  `QUARANTINE <containment boundary>`. Building on a bad practice is a recorded,
  conscious decision — never a silent adoption.

`4` all pass (a complete ledger scores 4, however ugly its contents) · `3` decisions +
ledger complete; a risk left implicit · `2` a significant decision with no recorded
alternative, OR a known blast-radius defect absent from the ledger · `1` ledger absent
while the blast radius touches rule-violating code · `0` no tradeoff record.

### B — Buildability (cost to implement against)

- b1 Contracts name concrete types/signatures — an implementer invents nothing.
- b2 Every unit has a test seam reachable without its host; every existing test in
  § Blast radius carries a disposition (KEEP | UPDATE + AC | DELETE).
- b3 No AC's realization fans out across >3 units without a named reason (tedium check).

`4` all pass · `3` a seam or disposition gap, each an open item · `2` a contract an
implementer can't build without guessing (name it) · `1` several such contracts · `0`
contracts are prose without signatures.

## Artifact — `design-scorecard.md`

DEDUCT grammar (shared by both scorecards):
`DEDUCT — <axis> · <anchor id> · <evidence path:line or ID> · <rule/AC cite> · <fix direction | INHERIT | OPEN>`

```markdown
# Design scorecard — <spec>

| Axis | Score /4 | Failed anchors |
|------|----------|----------------|
| G — Grounding | 4 | — (2 ASSUMED, routed) |
| F — Fit | 4 | — |
| S — Structure | 3 | s2 |
| T — Tradeoffs | 4 | — |
| B — Buildability | 3 | b2 |

Verdict: PASS

DEDUCT — S · s2 · store where props suffice (contracts/devices.md `useSelectionStore`) · services-and-boundaries.md · downgrade to props
DEDUCT — B · b2 · `DeviceTable.test.tsx` disposition undecided · design.md § Blast radius · OPEN

## Inherited-defect ledger (t3)
| Existing defect (rule cite) | Evidence | Verdict |
|-----------------------------|----------|---------|
| dual writer for `selection` (state-ownership.md) | src/DeviceTable.tsx:41 | INHERIT — fix costs a 4-unit refactor; proposal raised at gate |
```

## Re-score protocol (fresh eyes) — design and impl scorecards alike

The re-scorer is a **constrained verifier, not a second author**: walk the anchors and
the author's DEDUCT lines against the artifacts (and the diff, when one exists) and
re-derive each axis score from verified anchor outcomes only.

1. Verify each DEDUCT's evidence (grep/read both sides); unverifiable → drop it and note.
2. Run each axis's anchor checks independently, ONE derivation over the caller's whole
   scope; a new failure needs the same evidence + citation a DEDUCT needs.
3. **Separate miscalibration from evidence shift.** Evidence the author couldn't have
   had — an approved contract delta, a DESIGN GAP raised mid-implement, as-built
   measurements — re-scores the axis but reports as `evidence-shift`, informational.
   As-built anchor mapping: ambiguity GAP → b1 · friction GAP → b3/s3 · wrong-symbol
   GAP → g1 · defect GAP → the violated rule's axis.
4. Report the delta table: axis · author · re-score · evidence, rows that moved only.
   A delta reproducible from authoring-time artifacts that **crosses a verdict boundary**
   (≥3 / =2 / ≤1) → a mandatory finding naming both readings' evidence, regardless of
   magnitude. Same-band deltas → a note. Scorecard deltas never count against the
   advisory finding cap.
