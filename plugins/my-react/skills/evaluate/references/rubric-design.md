# Design rubric — axes G · F · S · T · B

Binary checks per axis; classes and derivation in [framework.md](./framework.md).
Evidence forms: **grep** (hit shown) · **trace** (ID → artifact §) · **read** (path:line).

## G — Grounding: the design attaches to the real codebase

Scope: the unit inventory + contracts' dependency/importer rows. "Verified" = grep finds
the declaration or an export of it.

| id | class | check | evidence |
|----|-------|-------|----------|
| g1 | cliff | every existing symbol those rows name resolves in the codebase | grep |
| g2 | core | every such symbol carries a `verified <path:line>` mark | read |
| g3 | core | every MODIFY unit lists its importers, each with a decision (kept compatible · migrated in scope) | grep |
| g4 | core | every attachment point names its wiring mechanism (props · query key · selector · context · service event · callback) | trace |
| g5 | core | behavior relied on but not read is marked `ASSUMED` and routed to Open items | trace |

## F — Fit: the design solves the spec'd problem, exactly

| id | class | check | evidence |
|----|-------|-------|----------|
| f1 | cliff | an AC→contract coverage table exists | trace |
| f2 | core | every AC maps to ≥1 contract + flow step, with a test-strategy row | trace |
| f3 | core | every contract surface element traces to ≥1 AC (a justified exception carries its one-line reason) | trace |
| f4 | core | every flow walks origin → transforms → sinks with a named unit at every hop and a named mechanism between hops | trace |
| f5 | polish | each NFR sits on the unit that carries it (a perf budget names its hot path) | trace |

## S — Structure: new decisions keep the design maintainable and scalable

Scope: decisions this design introduces — inherited structure is T's business. Each
failure cites its rule card (`skills/design/rules/`), the mechanism picker
(design skill's design.md) for s2, or the duplicated unit for s5.

| id | class | check | evidence |
|----|-------|-------|----------|
| s1 | cliff | every fact has exactly one owner — server facts consumed via their query, derivations computed at use | read + rule cite |
| s2 | core | dependencies run one way, and each interaction uses the loosest mechanism that serves it | read + cite |
| s3 | core | every split/merge passes the right-size test — units earn their boundary | read + cite |
| s4 | core | each flow declares where an error stops propagating (failure containment) | trace |
| s5 | core | every NEW unit's responsibility is absent from existing units (else it re-tags REUSE/MODIFY; a fact-owning duplicate fails s1 instead) | grep |
| s6 | core | the structure absorbs the spec's named growth — more rows, more consumers, the next feature on the flow — without redrawing boundaries | trace |
| s7 | core | each contract surface accepts only the facts it consumes — an object parameter narrows to the fields used; no fact is duplicated across surfaces | read + cite |

## T — Tradeoffs: choices and inherited debt are recorded decisions

"Significant decision" = any choice a rule card or the mechanism picker leaves open
between ≥2 viable options.

| id | class | check | evidence |
|----|-------|-------|----------|
| t1 | core | each significant decision records chosen ← rejected alternative + one-line consequence | trace |
| t2 | polish | risks and sensitivity points named where one choice constrains another axis | trace |
| t3 | cliff | the inherited-defect ledger covers every existing-scope rule violation on the blast radius, each with a verdict: `INHERIT <cost>` · `FIX-NOW <proposal>` · `QUARANTINE <boundary>` | grep + read |

A complete ledger passes t3 however ugly its contents — the ledger feeds the foundation
signal; its verdicts are judged there, not here.

## B — Buildability: an implementer builds without guessing

| id | class | check | evidence |
|----|-------|-------|----------|
| b1 | cliff | contracts name concrete types/signatures | read |
| b2 | core | every unit's test seam is reachable without standing up its host | trace |
| b3 | core | every existing test in § Blast radius carries a disposition (KEEP · UPDATE + AC · DELETE) | trace |
| b4 | core | each AC's realization spans ≤3 units, or names its reason | trace |
