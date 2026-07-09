---
name: oac-architecture-design
description: >
  Records the architecture decisions for a feature in design.md + contracts/ — where each
  piece of state lives and who owns it, server data as the TanStack Query source of truth,
  Zustand store shape, component composition, and layering — then runs the verifiable-unit
  gate. Reach for it when structuring components, hooks, stores, query keys, or write paths,
  or extending an existing design (React 19 + TS + Zustand + TanStack Query v5).
---

# oac-architecture-design

Turn the requirements + clarifications artifacts (paths the caller supplies) into
`design.md` plus one `contracts/<unit>.md` per unit, then a gate verdict.

**Perspective — this is a decision navigator.** Every `core/` rule is an architecture
*decision* you make and record in `design.md`/`contracts/` — where state lives and who owns
it, the server-state path, the store shape, the composition and layer boundaries. The rules
are grouped by **decision area** (`state-` → `zustand-` → `query-` → `compose-` → `layer-`);
several carry a coding-discipline twin in the `oac-implementation` skill that governs the code
honoring the decision (marked in the rule index). This is a **design-time authoring
discipline**, not a retro reviewer: decide before any TypeScript exists so every blocking
trigger is a non-issue at the gate. A seam missing from the design cannot be tested in the
code — catch it here.

**Produce**
- `design.md` — layer map, state-ownership decisions, server-state path, Zustand
  shape, composition notes, and an `## Architecture Gate` section.
- `contracts/<unit>.md` — one per unit (skeleton below).
- a gate verdict per unit: PASS, an extraction plan, or a recorded justification.

## Procedure

1. **Load the rule index.** Open `references/how-to-use-bundled-rules.md` — the 22
   `core/` rules in priority order (`state-` → `zustand-` → `query-` → `compose-` →
   `layer-`). Keep it at hand; open the specific `core/<name>.md` before you commit a
   decision — never cite a rule from memory.
2. **Author `design.md`.** Work `references/design-procedure.md` steps 1–7 in order,
   recording each decision as you go.
3. **Write one contract per unit** in the shape below.
4. **Gate at hand-off.** Run `references/gate-procedure.md` over the three blocking
   triggers; write PASS / extraction plan / justification into `design.md`. The
   caller may re-run the same gate later against implemented code.

## Contract skeleton — `contracts/<unit>.md`

Every unit from Step 1 gets a contract stating its public surface concretely — enough
that implementation and tests can be written against it without re-deriving the design:

```markdown
## <UnitName> — contract
- **Kind / layer:** component | hook | store | api | service · <feature folder>
- **Public API** (name the exact types — no `any`):
  - component → `interface <Unit>Props { … }`; what it renders; callbacks it fires
  - hook → `use<Unit>(args: …): { … }` — the full return type
  - store → state shape + action signatures (intent-named)
  - service → `create<Unit>(opts): <Unit>` + lifecycle (create/destroy) + events
- **States it must expose:** loading · empty · error · success · disabled — each
  mapped to an observable signal (rendered text, role/aria state, enabled control)
  the ACs assert against. Use discriminated unions, not scattered booleans.
- **Traces to:** AC-<story>.<n>, … (the criteria this unit satisfies)
- **Testability seam:** how it runs in isolation — `render(<Unit/>)` behind a
  providers wrapper / `renderHook(() => use<Unit>())` with controlled inputs /
  direct service call. Never requires a module-level mock of its host.
- **Depends on:** <inward-pointing units only — ui → hooks/store → api/services>
```

## The verifiable-unit gate (at hand-off)

> Does each spec behavior map onto an independently verifiable unit —
> renderable/invocable in isolation without mocking its host?

Three blocking triggers — hard blocks until each is resolved:

| # | Trigger | Fires when |
|---|---------|-----------|
| 1 | God-component / God-hook | a component past ~400 LOC, or a hook mixing ≥2 of CRUD/data-fetch, UI-state, lifecycle side-effects |
| 2 | Server-state-in-Zustand / dual-source | a server-derived field in Zustand or `localStorage`, a `useEffect` mirroring server data into state, or two owners for one fact |
| 3 | Testability seam missing | a behavior reachable only by mocking its entire host hook/component |

For each trigger emit **PASS**, an **extraction plan**, or a **recorded
justification** — output formats and the confirm-against-rules procedure are in
`references/gate-procedure.md`. If steps 1–3 were applied, all three are non-issues.

## References

| Resource | Path | Open when |
|----------|------|-----------|
| Rule index — 22 core rules, priority order | `references/how-to-use-bundled-rules.md` | first; kept open through authoring |
| Design procedure (7 steps) + contract detail | `references/design-procedure.md` | authoring `design.md` + `contracts/` |
| Core rules (right/wrong per rule) | `references/core/` | confirming one specific decision |
| Gate lenses P1–P7 — right/wrong sketches (each a named cluster of the 22 core rules) | `references/principle-examples.md` | quick pattern lookup while authoring |
| Gate lenses P1–P7 — violation signals + rule crosswalk | `references/principle-checks.md` | scanning a surface for a defect at the gate |

> **P1–P7 are gate lenses, not a rival rule list** — each groups a slice of the 22 `core/` rules for the verifiable-unit scan. The `core/` rules are the single rule vocabulary; the P-lenses are how the gate reads them.
| Gate procedure + report formats | `references/gate-procedure.md` | running the gate |
