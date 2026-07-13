---
name: design-react-architecture
description: >
  Design code contracts, architecture and test strategy for given user requirements/stories/ACs/NFRs.
---

# design-react-architecture

Design a React feature's architecture before any code exists. Requirements are an **input** (the caller supplies stories, ACs, NFRs and etc.); this skill decides boundaries, interfaces and units, never concrete implementations.

**Produce**

- `contracts/<unit>.md` — one per MODIFY/NEW unit: the single home of every per-unit decision.
- `design.md` — the feature-level record: the **architecture overview** (units, layers, dependency
  arrows), cross-unit decisions, and a unit **index that links each contract, never restates it**.

**Right-size:** ≤2 NEW units and no MODIFY → `design.md` collapses to the unit index, ownership
lines, AC → Verification table, and gate verdict. Contracts are always one per unit.

**Write terse:** later phases re-read `design.md` and every contract — terse prose, reference
requirement/rule IDs instead of restating them; identifiers, paths, and IDs exact; no invented
abbreviations. Human-gated content (gate verdict, justifications) stays in clear full sentences.

## Instructions

1. **Learn the rules** — Read [references/principles.md](./references/principles.md) (R1–R11) — the
   complete rule set governing every decision below. Cite R-IDs in design notes and findings; when
   unsure, re-read the rule, never cite from memory.
2. **Collect the requirements** — Gather stories, ACs, NFRs, and references from the caller. Sketch
   the **requirement flow**: where each fact originates (server, user action, device), what
   transforms it, what renders it. Name units and facts with the requirements Glossary verbatim.
3. **Design the units** — Turn the flow into a draft:
   - **Inventory.** Name every unit the feature needs, searching the codebase by responsibility,
     not name: **EXISTING** (already does the job — reuse as-is, read-only) · **MODIFY** (near fit —
     bounded change; list its external importers) · **NEW** (nothing fits). Greenfield = all NEW.
   - **Decide** ownership, layer, interaction mechanism, and composition per unit, applying the
     principles in priority order — state first, composition last.
   - **Draft** one `contracts/<unit>.md` per MODIFY/NEW unit from
     [templates/unit-contract.md](./templates/unit-contract.md).
4. **Plan the test strategy** — Follow [references/test-strategy.md](./references/test-strategy.md)
   (T1–T5): record the **AC → Verification table** — per criterion its level (the harness tier from
   the owning contract's seam; config NFRs → real provider, pattern bans → CI guard) and its test
   location, with ID-carrying labels. Test authoring downstream becomes mechanical.
5. **Check the design** — Run [references/challenges.md](./references/challenges.md): eight
   severity-tagged adversarial checks (C1–C8), best done by fresh eyes (a subagent given only the
   draft artifacts).
   - Severity fixes the policy: **CRITICAL** must be re-designed (loop back to
     steps 3–4), **HIGH** re-designs or carries a recorded justification, **MEDIUM** fixes or records
     debt, **LOW** is advisory.
6. **Record** — Assemble `design.md` from [templates/design-doc.md](./templates/design-doc.md) and
   run its completeness check. When extending an existing design, append and amend — never renumber
   units or rewrite standing justifications.
