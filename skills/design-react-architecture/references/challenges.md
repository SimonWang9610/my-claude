# Design checks (C1–C8)

Adversarial verification of the draft — try to break it, don't defend it. Best run by fresh eyes: a
subagent given only the draft tables and contracts, not the reasoning behind them. Rule IDs refer to
[principles.md](./principles.md).

Each check carries a **severity** that fixes its resolution policy:

| Severity | Policy |
|----------|--------|
| **CRITICAL** | must be resolved before hand-off — re-design the affected units; no justification can stand |
| **HIGH** | re-design by default; a recorded justification (with a test strategy) may stand |
| **MEDIUM** | fix if the fix is bounded; otherwise record as debt in `design.md` |
| **LOW** | advisory — evaluate, record the outcome, move on |

Any CRITICAL or HIGH finding loops the affected units back to the Design step; re-check after.
Repeat design ⇄ check until the hand-off criteria (bottom) hold.

## The checks

- **C1 · CRITICAL — One source of truth per fact?** (R1, R2)
  Scan the ownership table for dual owners, server facts copied client-side, or stored derivations.
- **C2 · HIGH — Blast radius mapped?**
  Every MODIFY unit lists its external importers, each with a decision: contract kept
  backward-compatible, or importer folded into this scope. An unmapped importer fails.
- **C3 · MEDIUM — Reuse before create?**
  A NEW unit whose responsibility an existing unit already owns is a duplicate — re-tag it
  EXISTING/MODIFY. **Escalates to C1** if the duplicate owns a fact. A MODIFY fighting tangled
  responsibilities goes to C6.
- **C4 · HIGH — Units small and independently verifiable?** (R6, R7)
  A God-unit (≥2 of data-fetch / UI-state / lifecycle, or past the ceiling) splits into a
  render-only component plus named single-purpose hooks. A behaviour reachable only by standing up
  its host has a missing seam — extract it.
- **C5 · MEDIUM — Loosest coupling per interaction?** (R9)
  Prop-drilling where a shared query key serves, a store where props suffice, a central manager
  accumulating unrelated state — each is a downgrade to apply.
- **C6 · LOW — Would a bounded re-architecture pay off?** (R6, R7, R9)
  Where a MODIFY fights the change, don't patch by default: name the root friction, restrict the
  scope to one unit or interface (no creep), weigh the payoff. High → fold the refactor in as its
  own scope with its own contract. Low → design around it cleanly and record the debt.
- **C7 · CRITICAL — Every AC/NFR owned by exactly one unit?**
  Each criterion ID appears in exactly one contract's **Traces to**. A criterion resting on a fact
  the unit doesn't own is *derived* — the unit consumes the owner's interface. **An unowned
  criterion means a missing unit.**
- **C8 · CRITICAL — Does the unit graph produce each behaviour?**
  Walk each primary AC end-to-end — origin → transform → render — naming the unit at every hop and
  the mechanism between hops. An ambiguous handoff (nobody owns the invalidation; two units both
  think they trigger the refetch) fails even when every unit passed C1–C7 in isolation, and the
  failing hop names the unit to re-design.

## Recording — `design.md` ▸ `## Architecture Gate`

One outcome per check; findings name their units:

```markdown
| Check | Outcome |
|-------|---------|
| C1 | PASS |
| C4 | JUSTIFIED — see Justifications |
| C5 | DEBT — DeviceTable coupled to selection store; bounded, recorded |

FINDING — C<n> (<severity>) · <unit>
Reason: [one sentence]  ·  Rule: [R-ID]
Action: [re-design step taken | justification | debt]

JUSTIFICATION — C<n> · <unit>            (HIGH only, under ### Justifications)
Why deferred: [specific reason]
Test strategy without the fix: [how the behaviour stays verifiable]
```

**Hand-off criteria:** no open CRITICAL · every HIGH passed or justified · every MEDIUM passed or
debt-recorded · C6 evaluated. The same checklist can be re-run later against implemented code — a
re-run honours recorded justifications and debt; an absent justification with the finding still
firing is a FAIL.
