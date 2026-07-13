---
name: analyze-react
description: >
  Produces an evidence-grounded analysis.md before any fix is written. Defect mode: locates the ROOT cause in the real
  code (unit + line, symptom vs. cause), phrases the fix as an AC-<story>.<n>, and
  authors a NAMED failing Vitest reproduction test that must fail pre-fix. In-place
  mode: maps the change surface and blast radius — which units/hooks/stores the change
  touches, their external importers, and which adopted/shared components are read-only.
  Reach for it before fixing a bug or altering existing code: "root cause this",
  "reproduce the bug", "impact analysis", "what does this change touch".
---

# analyze-react

Ground a change in evidence before a line of fix code is written. Pick ONE mode from the work
the caller states, run its procedure, and record the result in the `analysis.md` the caller
names. Stack: React 19 + TypeScript + Vite + Zustand + TanStack Query v5 + MUI; tests Vitest +
React Testing Library + MSW + userEvent.

- **Input:** the affected code the caller points you at, plus the defect report or change intent.
- **Output:** the `analysis.md` at the caller-supplied path (contents per the chosen mode).

## Mode 1 — Defect / root-cause (repro-first)

Use when the work is a bug or defect. Symptom is not cause; a test that passes before the fix
proves nothing.

1. **Reproduce & locate the root** — trace the failing path through the real code to the exact
   unit + line that is wrong. Distinguish the observed symptom from the causing unit.
   → `references/root-cause.md`.
2. **Phrase the AC** — state the correct behavior as one `AC-<story>.<n>` in observable
   Given/When/Then form, using the `oac-acceptance-criteria` observable-phrasing contract.
3. **Author the failing repro test** — a NAMED, DETERMINISTIC Vitest + RTL test whose `describe`
   label carries the AC-ID (so `grep -r "AC-3.2" src/` finds it). It obeys the `oac-test-contract`
   rules. Skeleton → `references/repro-test.md`.
4. **RUN it — it must FAIL, for the stated reason, before any fix exists.**
   → `references/repro-test.md` (gate).
5. **Record** root cause (unit + line), the AC, and the repro test's file path in `analysis.md`.
   → `references/output-format.md` §1.

## Mode 2 — In-place change / impact-first

Use when the work alters existing behavior with no defect to reproduce. Map what the change
touches before touching it.

1. **Change surface** — list the existing units/components/hooks/stores/query-keys the change
   edits, each with its path.
2. **Blast radius** — for each touched unit, reverse-import search its external importers;
   those consumers are what a change can break. → `references/impact.md` §1.
3. **Read-only guard** — flag every adopted/shared component among them. An adopted shared unit
   is read-only: it must be COPIED, never modified in place, without the caller's explicit
   approval. → `references/impact.md` §2.
4. **Record** the surface + a Unit | Touched-as | External Importers | Read-only? action table in
   `analysis.md`. → `references/output-format.md` §2.

## References

- [references/root-cause.md](references/root-cause.md) — the trace-to-root procedure; symptom-vs-cause tests.
- [references/repro-test.md](references/repro-test.md) — named/deterministic failing Vitest + RTL skeleton with the AC-ID in the label.
- [references/impact.md](references/impact.md) — reverse-import blast-radius search and the read-only adopted-component rule.
- [references/output-format.md](references/output-format.md) — the `analysis.md` layout for each mode.
