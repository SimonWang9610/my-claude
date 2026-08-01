# Implementation scorecard — axes, anchors, template

The implementer's scored self-evaluation, one section per batch/wave, **returned in the
report** — the caller (driver) appends it to `impl-scorecard.md` in the spec dir; the
implementer never writes spec artifacts. Scale, verdict-from-minima, disclosure rule,
DEDUCT grammar, and the re-score protocol are defined once in
`${CLAUDE_PLUGIN_ROOT}/skills/design/references/scorecard.md` — this file carries only
the impl axes.

## Axes and anchors

### C — Conformance (the contract kept, observably)

- c1 Public surface name-for-name, type-for-type — no undeclared props, no widened optionals.
- c2 The batch's named tests green; test paths byte-unchanged vs the red baseline ref
  the batch prompt names (no ref given → state so; never assert c2 unverified).
- c3 Stated must-nots hold (grep-verified); MODIFY units' listed importers unbroken.
- c4 Every promised state reachable through the public surface.

`4` all pass (raised narrowest-safe interpretations included) · `3` an importer or
must-not verified indirectly — named · `2` a surface deviation or unreachable promised
state · `1` tests pass only against a proxy of the AC's outcome · `0` batch red or
surface unrecognizable.

### S — Simplicity (diff proportional to its AC)

- s1 Diff scoped to the AC — no unrelated edits, drive-by refactors, or new dead code.
- s2 Reuse honored — no second unit/type/query key/store slice duplicating an existing one.
- s3 The smaller expression chosen — no abstraction serving a single call site.

`4` all pass · `3` one justified widening (named in a line) · `2` a duplicate unit or an
unrelated edit · `1` diff large for its AC with no justification · `0` scope
unrecognizable from the AC.

### R — Runtime (what the diff costs at run time)

- r1 No rule-card violation from `rules/optimize-*.md` on a hot path (per-frame, large
  list, main interaction); capabilities-gated — a rule for an absent library never cites.
- r2 Subscriptions narrowed to consumed facts; teardown paired with setup.
- r3 No pre-optimization of cold paths (clarity first).

`4` all pass · `3` a cold-path nit only · `2` one hot-path violation · `1` a perf NFR
names a budget and the gate's run shows it missed · `0` unbounded growth (leak,
unbounded cache, effect loop).

### H — Honesty (failures surface; deviations raised)

- h1 No silent catch, no masking fallback — unhappy paths behave as contracted.
- h2 Every deviation from the contract carries a DESIGN GAP block — none silent.
- h3 Test seams intact — unit reachable through its contract seam, no detail leaked into
  the public surface to make code pass.

`4` all pass (raised GAPs included) · `3` one seam nit, bounded · `2` a swallowed error
or an unraised deviation · `1` a fallback masks a contracted failure state · `0` a test
seam bypassed or weakened to green the batch.

## Report block (the caller appends it to `impl-scorecard.md`)

```markdown
## Wave <n> · batch <id> — <units>

| Axis | Score /4 | Failed anchors |
|------|----------|----------------|
| C — Conformance | 4 | — |
| S — Simplicity | 3 | s3 |
| R — Runtime | 4 | — |
| H — Honesty | 4 | — |

Verdict: PASS

DEDUCT — S · s3 · `formatLabel` helper has one call site (src/DeviceRow.tsx:12) · rules/build-components.md · OPEN
```
